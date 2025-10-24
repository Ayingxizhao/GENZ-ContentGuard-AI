"""
Google Gemini model service implementation
Uses Gemini 2.5 Flash (finetuned) for content analysis with explainability
"""
import os
import json
import logging
from typing import Dict, Any
from dotenv import load_dotenv
from .model_service import BaseModelService

load_dotenv()

# Lazy import to avoid startup errors if SDK not installed
_genai = None
_model = None


def get_gemini_model():
    """Get or create Gemini model instance"""
    global _genai, _model
    
    if _model is None:
        try:
            import google.generativeai as genai
            _genai = genai
            
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in environment variables")
            
            genai.configure(api_key=api_key)
            
            # Configure model with JSON response mode
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 2048,  # Increased for explainability data
                "response_mime_type": "application/json",
            }
            
            _model = genai.GenerativeModel(
                'gemini-2.5-flash',
                generation_config=generation_config
            )
            
        except ImportError:
            raise RuntimeError("google-generativeai package not installed. Run: pip install google-generativeai")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Gemini model: {str(e)}")
    
    return _model


def load_prompt_template() -> str:
    """Load prompt template from file"""
    prompt_path = os.path.join(os.path.dirname(__file__), 'gemini_prompt.txt')
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logging.error(f"Failed to load prompt template: {str(e)}")
        # Fallback minimal prompt
        return """Analyze this text for malicious content. Return JSON with: is_malicious (bool), confidence (0-100), analysis (string), risk_level (LOW/MEDIUM/HIGH), toxic_type (string or null), highlighted_phrases (array).

Text: {text}"""


class GeminiModelService(BaseModelService):
    """Google Gemini model service with explainability"""
    
    def __init__(self):
        self.prompt_template = load_prompt_template()
    
    def predict(self, text: str, enable_explainability: bool = True) -> Dict[str, Any]:
        """
        Analyze text using Gemini API with explainability
        
        Args:
            text: Content to analyze
            enable_explainability: Whether to include explainability data
            
        Returns:
            Normalized analysis result with explainability
        """
        try:
            model = get_gemini_model()
            
            # Format prompt with text
            prompt = self.prompt_template.format(text=text)
            
            # Generate response
            response = model.generate_content(prompt)
            
            # Check if response was blocked or had an error
            if not response.text:
                error_msg = "Gemini returned empty response"
                if hasattr(response, 'prompt_feedback'):
                    error_msg += f". Prompt feedback: {response.prompt_feedback}"
                logging.error(error_msg)
                raise RuntimeError(error_msg)
            
            # Parse JSON response
            response_text = response.text.strip()
            
            # Log raw response for debugging
            logging.info(f"Raw Gemini response: {response_text[:200]}...")
            
            # Try multiple extraction strategies
            # 1. Check for markdown code blocks
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0].strip()
            
            # 2. Find JSON object boundaries (always do this as fallback)
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')
            
            if start_idx == -1 or end_idx == -1:
                # No valid JSON found
                logging.error(f"No JSON object found in response: {response_text}")
                raise json.JSONDecodeError("No JSON object found", response_text, 0)
            
            # Extract JSON portion
            response_text = response_text[start_idx:end_idx+1]
            
            # Log the extracted text for debugging
            logging.info(f"Extracted JSON: {response_text[:200]}...")
            
            result = json.loads(response_text)
            
            # Normalize to standard schema
            normalized = self._normalize_gemini_result(result, enable_explainability)
            return normalized
            
        except json.JSONDecodeError as e:
            logging.error(f"JSON parse error: {str(e)}")
            logging.error(f"Attempted to parse: {response_text[:500] if 'response_text' in locals() else 'N/A'}")
            raise RuntimeError(f"Failed to parse Gemini response: {str(e)}")
        except Exception as e:
            logging.error(f"Gemini prediction failed: {str(e)}")
            logging.error(f"Response text (if available): {response_text[:500] if 'response_text' in locals() else 'N/A'}")
            raise RuntimeError(f"Gemini API call failed: {str(e)}")
    
    def _normalize_gemini_result(self, result: Dict[str, Any], enable_explainability: bool = True) -> Dict[str, Any]:
        """
        Normalize Gemini output to standard schema with explainability
        
        Args:
            result: Raw Gemini response
            enable_explainability: Whether to include explainability data
            
        Returns:
            Normalized result matching HF schema with explainability
        """
        try:
            is_mal = bool(result.get('is_malicious', False))
            
            # Parse confidence
            conf_val = float(result.get('confidence', 0))
            if conf_val > 100:
                conf_val = 100.0
            elif conf_val < 0:
                conf_val = 0.0
            
            # Calculate probabilities
            if is_mal:
                mal_pct = conf_val
                safe_pct = 100.0 - conf_val
            else:
                safe_pct = conf_val
                mal_pct = 100.0 - conf_val
            
            normalized = {
                'analysis': result.get('analysis', 'Analysis completed'),
                'is_malicious': is_mal,
                'confidence': f"{conf_val:.2f}%",
                'probabilities': {
                    'safe': f"{safe_pct:.2f}%",
                    'malicious': f"{mal_pct:.2f}%",
                },
                'model_type': 'Gemini 2.5 Flash (Finetuned)'
            }
            
            # Add detailed analysis if available
            details = {}
            if result.get('risk_level'):
                details['risk_level'] = result['risk_level']
            if result.get('toxic_type'):
                details['toxic_type'] = result['toxic_type']
            if result.get('explanation'):
                details['explanation'] = result['explanation']
            
            if details:
                normalized['detailed_analysis'] = details
            
            # Add explainability data if enabled and available
            if enable_explainability and 'highlighted_phrases' in result:
                highlighted_phrases = result['highlighted_phrases']
                
                # Build category summary
                category_summary = {}
                severity_breakdown = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
                
                for phrase in highlighted_phrases:
                    category = phrase.get('category', 'general_toxicity')
                    severity = phrase.get('severity', 'LOW')
                    category_summary[category] = category_summary.get(category, 0) + 1
                    severity_breakdown[severity] = severity_breakdown.get(severity, 0) + 1
                
                normalized['explainability'] = {
                    'highlighted_phrases': highlighted_phrases,
                    'categories_detected': category_summary,
                    'severity_breakdown': severity_breakdown,
                    'total_matches': len(highlighted_phrases)
                }
            
            return normalized
            
        except Exception as e:
            logging.error(f"Failed to normalize Gemini result: {str(e)}")
            # Return safe fallback
            return {
                'analysis': 'Analysis completed with errors',
                'is_malicious': False,
                'confidence': '0.00%',
                'probabilities': {
                    'safe': '50.00%',
                    'malicious': '50.00%',
                },
                'model_type': 'Gemini 2.5 Flash (Finetuned)'
            }
    
    def get_model_name(self) -> str:
        """Return model display name"""
        return "Gemini 2.5 Flash (Finetuned)"
