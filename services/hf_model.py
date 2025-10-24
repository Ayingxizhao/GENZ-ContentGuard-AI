"""
Hugging Face model service implementation with regex-based explainability
Refactored from app.py to provide modular interface
"""
import os
import re
import logging
import httpx
from typing import Dict, Any
from gradio_client import Client
from dotenv import load_dotenv
from .model_service import BaseModelService
from .explainability_service import get_explainability_service

load_dotenv()

# Configuration
HF_SPACE_ID = os.getenv("HF_SPACE_ID", "Ayingxizhao/contentguard-model")
HF_API_NAME = os.getenv("HF_API_NAME", "/predict")
if HF_API_NAME and not HF_API_NAME.startswith('/'):
    HF_API_NAME = '/' + HF_API_NAME
HF_TOKEN = os.getenv("HF_TOKEN")

# Lazy client initialization
_hf_client = None


def get_hf_client():
    """Get or create HF client instance"""
    global _hf_client
    if _hf_client is None:
        kwargs = {}
        if HF_TOKEN:
            kwargs["hf_token"] = HF_TOKEN
        _hf_client = Client(HF_SPACE_ID, **kwargs)
    return _hf_client


def _normalize_result(space_result: Any) -> Dict[str, Any]:
    """
    Normalize HF Space output to standard schema
    
    Expected schema:
      - analysis: str
      - is_malicious: bool
      - confidence: 'NN.NN%'
      - probabilities: { safe: 'NN.NN%', malicious: 'NN.NN%' }
      - model_type: str
    """
    # If already in expected format, passthrough
    if isinstance(space_result, dict) and {
        'analysis', 'is_malicious', 'confidence', 'probabilities'
    }.issubset(space_result.keys()):
        space_result.setdefault('model_type', 'ContentGuard Model (Free)')
        return space_result

    # Handle your Space's schema
    if isinstance(space_result, dict) and {
        'is_malicious', 'confidence'
    }.issubset(space_result.keys()):
        try:
            conf_str = str(space_result.get('confidence', '0%')).strip()
            conf_val = float(conf_str.replace('%', '').strip())
        except Exception:
            conf_val = 0.0
        
        is_mal = bool(space_result.get('is_malicious', False))
        mal_pct = conf_val if is_mal else max(0.0, 100.0 - conf_val)
        safe_pct = 100.0 - mal_pct

        # Build analysis text
        explanation = space_result.get('explanation')
        toxic_type = space_result.get('toxic_type')
        risk_level = space_result.get('risk_level')
        
        if explanation:
            analysis_text = str(explanation)
        else:
            if is_mal:
                parts = ["Malicious content detected"]
                if toxic_type:
                    parts.append(f"({toxic_type})")
                if risk_level:
                    parts.append(f"risk: {risk_level}")
                analysis_text = ' '.join(parts)
            else:
                analysis_text = 'Content appears safe'

        normalized = {
            'analysis': analysis_text,
            'is_malicious': is_mal,
            'confidence': f"{conf_val:.2f}%",
            'probabilities': {
                'safe': f"{safe_pct:.2f}%",
                'malicious': f"{mal_pct:.2f}%",
            },
            'model_type': 'ContentGuard Model (Free)'
        }
        
        # Optional detailed analysis
        details = {}
        if explanation:
            details['explanation'] = str(explanation)
        if risk_level:
            details['risk_level'] = str(risk_level)
        if toxic_type:
            details['toxic_type'] = str(toxic_type)
        if details:
            normalized['detailed_analysis'] = details
        
        return normalized

    # Common alternative: label/score or probabilities list
    analysis_text = None
    is_mal = None
    conf_pct = None
    probs = None

    if isinstance(space_result, dict):
        label = space_result.get('label') or space_result.get('prediction')
        score = space_result.get('score') or space_result.get('confidence')
        # Probabilities could be nested
        probs_raw = space_result.get('probabilities') or space_result.get('probs')
        if isinstance(probs_raw, dict) and 'safe' in probs_raw and 'malicious' in probs_raw:
            probs = {
                'safe': f"{float(probs_raw['safe']) * 100:.2f}%" if isinstance(probs_raw['safe'], (int, float)) else str(probs_raw['safe']),
                'malicious': f"{float(probs_raw['malicious']) * 100:.2f}%" if isinstance(probs_raw['malicious'], (int, float)) else str(probs_raw['malicious']),
            }
            # Confidence = max prob
            try:
                conf_val = max(float(str(probs_raw['safe'])), float(str(probs_raw['malicious'])))
                conf_pct = f"{conf_val * 100:.2f}%"
            except Exception:
                conf_pct = None
            is_mal = float(str(probs_raw.get('malicious', 0))) >= float(str(probs_raw.get('safe', 0)))
        if label is not None:
            is_mal = (str(label).lower() in ['malicious', 'toxic', 'unsafe', '1', 'true'])
            analysis_text = 'Malicious content detected' if is_mal else 'Content appears safe'
        if score is not None and conf_pct is None:
            try:
                conf_pct = f"{float(score) * 100:.2f}%"
            except Exception:
                conf_pct = str(score)

    # Another common format: list like [{'label': 'malicious', 'score': 0.87}, ...]
    if isinstance(space_result, list) and space_result and isinstance(space_result[0], dict) and 'label' in space_result[0] and 'score' in space_result[0]:
        # Find safe/malicious entries if present
        entries = {d['label'].lower(): float(d['score']) for d in space_result if 'label' in d and 'score' in d}
        p_safe = entries.get('safe')
        p_mal = entries.get('malicious')
        if p_safe is not None and p_mal is not None:
            probs = {'safe': f"{p_safe * 100:.2f}%", 'malicious': f"{p_mal * 100:.2f}%"}
            is_mal = p_mal >= p_safe
            conf_pct = f"{(p_mal if is_mal else p_safe) * 100:.2f}%"
            analysis_text = 'Malicious content detected' if is_mal else 'Content appears safe'

    # Fallbacks
    if probs is None:
        # If nothing to compute, set neutral 50/50
        probs = {'safe': '50.00%', 'malicious': '50.00%'}
    if is_mal is None:
        is_mal = False
    if conf_pct is None:
        conf_pct = probs['malicious'] if is_mal else probs['safe']
    if analysis_text is None:
        analysis_text = 'Malicious content detected' if is_mal else 'Content appears safe'

    return {
        'analysis': analysis_text,
        'is_malicious': bool(is_mal),
        'confidence': conf_pct,
        'probabilities': probs,
        'model_type': 'ContentGuard Model (Free)'
    }


class HuggingFaceModelService(BaseModelService):
    """Hugging Face Space model service with regex-based explainability"""
    
    def __init__(self):
        """Initialize HF model service with explainability"""
        self.explainability_service = get_explainability_service()
    
    def predict(self, text: str, enable_explainability: bool = True) -> Dict[str, Any]:
        """
        Analyze text using HF Space with regex-based explainability
        
        Args:
            text: Content to analyze
            enable_explainability: Whether to include explainability data
            
        Returns:
            Normalized analysis result with explainability
        """
        try:
            # Get base prediction from HF model
            client = get_hf_client()
            result = client.predict(text, api_name="/predict")
            normalized = _normalize_result(result)
            
            # Add regex-based explainability if enabled
            if enable_explainability:
                explainability_data = self.explainability_service.analyze_text(
                    text, 
                    is_malicious=normalized.get('is_malicious', False)
                )
                normalized['explainability'] = explainability_data
                
                logging.info(
                    f"HF model with explainability: {explainability_data.get('total_matches', 0)} "
                    f"toxic phrases detected"
                )
            
            return normalized
            
        except Exception as e:
            logging.error(f"HF model prediction failed: {str(e)}")
            raise RuntimeError(f"HF Space call failed: {str(e)}")
    
    def get_model_name(self) -> str:
        """Return model display name"""
        return "ContentGuard Model (Free)"
