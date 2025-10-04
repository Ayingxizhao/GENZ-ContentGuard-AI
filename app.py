from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from gradio_client import Client
import os
import time
import logging
import traceback
import re
import httpx
import json

app = Flask(__name__)
CORS(app)

# Basic logging
logging.basicConfig(level=logging.INFO)

# Initialize Gradio client (configurable via env) lazily to avoid blocking startup
HF_SPACE_ID = os.getenv("HF_SPACE_ID", "Ayingxizhao/contentguard-model")
HF_API_NAME = os.getenv("HF_API_NAME", "/predict")
# Normalize api name to start with '/'
if HF_API_NAME and not HF_API_NAME.startswith('/'):
    HF_API_NAME = '/' + HF_API_NAME
HF_TOKEN = os.getenv("HF_TOKEN")  # if the Space is private
_hf_client = None

def get_hf_client():
    global _hf_client
    if _hf_client is None:
        # Pass token if provided (handles private Spaces)
        kwargs = {}
        if HF_TOKEN:
            kwargs["hf_token"] = HF_TOKEN
        _hf_client = Client(HF_SPACE_ID, **kwargs)
    return _hf_client

def _space_base_url(space_id: str) -> str:
    """Return https base URL for a Space from repo id or full URL."""
    sid = (space_id or '').strip()
    if not sid:
        raise ValueError("HF_SPACE_ID is empty")
    if sid.startswith('http://') or sid.startswith('https://'):
        return sid.rstrip('/')
    # repo id like org/name -> subdomain org-name.hf.space
    sub = re.sub(r"[^a-zA-Z0-9-]", "-", sid)
    return f"https://{sub}.hf.space"

def _fetch_space_config():
    base = _space_base_url(HF_SPACE_ID)
    headers = {}
    if HF_TOKEN:
        headers["Authorization"] = f"Bearer {HF_TOKEN}"
    with httpx.Client(timeout=10.0) as client:
        r = client.get(f"{base}/config", headers=headers)
        r.raise_for_status()
        return r.json()

def _predict_via_rest(text: str):
    """Fallback: call Space REST endpoint directly: POST /api/predict/<api_name>."""
    base = _space_base_url(HF_SPACE_ID)
    api_cfg = (HF_API_NAME or '').strip()
    # If provided as fn_index:N then call /api/predict with fn_index
    fn_index = None
    if api_cfg.lower().startswith('fn_index:'):
        try:
            fn_index = int(api_cfg.split(':', 1)[1])
        except Exception:
            fn_index = None

    # If set to auto or invalid, try to discover from /config
    if api_cfg in ('', 'auto') or (api_cfg and api_cfg[0] != '/' and fn_index is None):
        try:
            cfg = _fetch_space_config()
            # Prefer named_endpoints if present
            ne = (cfg or {}).get('named_endpoints') or {}
            # Pick first named endpoint
            if isinstance(ne, dict) and ne:
                name, meta = next(iter(ne.items()))
                if isinstance(meta, dict) and 'fn_index' in meta:
                    fn_index = meta['fn_index']
            # Fallback: first dependency fn_index
            if fn_index is None:
                deps = (cfg or {}).get('dependencies') or []
                if isinstance(deps, list) and deps:
                    meta = deps[0]
                    if isinstance(meta, dict) and 'fn_index' in meta:
                        fn_index = meta['fn_index']
        except Exception as e:
            logging.warning("Failed to auto-discover Space config: %s", str(e))

    headers = {"Content-Type": "application/json"}
    if HF_TOKEN:
        headers["Authorization"] = f"Bearer {HF_TOKEN}"
    payload = {"data": [text]}

    with httpx.Client(timeout=15.0) as client:
        if fn_index is not None:
            # Use unified endpoint
            url = f"{base}/api/predict"
            payload["fn_index"] = fn_index
            r = client.post(url, json=payload, headers=headers)
            r.raise_for_status()
            return r.json()
        else:
            # Use named endpoint path
            api = api_cfg.lstrip('/') if api_cfg else 'predict'
            url = f"{base}/call/predict"
            r = client.post(url, json=payload, headers=headers)
            r.raise_for_status()
            return r.json()

def _normalize_result(space_result):
    """Normalize HF Space output to the UI schema.

    Expected UI fields:
      - analysis: str
      - is_malicious: bool
      - confidence: 'NN.NN%'
      - probabilities: { safe: 'NN.NN%', malicious: 'NN.NN%' }
      - model_type: str
    """
    # If the Space already returns the expected schema, passthrough
    if isinstance(space_result, dict) and {
        'analysis', 'is_malicious', 'confidence', 'probabilities'
    }.issubset(space_result.keys()):
        # Ensure model_type present
        space_result.setdefault('model_type', 'HF-Space')
        return space_result

    # Direct support for your Space schema
    # Example:
    # {
    #   "is_malicious": true,
    #   "risk_level": "HIGH",
    #   "confidence": "98.4%",
    #   "toxic_type": "toxic",
    #   "explanation": "Detected toxic content"
    # }
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
            'model_type': 'HF-Space'
        }
        # Optional detailed analysis for tabs
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
        'model_type': 'HF-Space'
    }


@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json() or {}
        text = (data.get('content') or '').strip()
        title = (data.get('title') or '').strip()
        combined = f"{title} {text}".strip() if title else text
        
        if not combined:
            return jsonify({"error": "No content provided"}), 400
        
        # Gradio 3.x SSE v3 protocol: POST /queue/join -> stream /queue/data
        base_url = "https://ayingxizhao-contentguard-model.hf.space"
        headers = {"Content-Type": "application/json"}
        if HF_TOKEN:
            headers["Authorization"] = f"Bearer {HF_TOKEN}"
        
        # Step 1: POST to /queue/join to enqueue the request
        join_response = httpx.post(
            f"{base_url}/queue/join",
            json={
                "data": [combined],
                "fn_index": 2,  # from /config: dependency id 2 is "predict"
                "session_hash": "random_session_" + str(time.time())
            },
            headers=headers,
            timeout=10.0
        )
        join_response.raise_for_status()
        join_data = join_response.json()
        event_id = join_data.get("event_id")
        if not event_id:
            raise ValueError("No event_id returned from /queue/join")
        
        # Step 2: Stream /queue/data?session_hash=... to get result
        session_hash = join_data.get("session_hash") or ("random_session_" + str(time.time()))
        result = None
        with httpx.stream("GET", f"{base_url}/queue/data?session_hash={session_hash}", headers=headers, timeout=30.0) as stream_resp:
            stream_resp.raise_for_status()
            for line in stream_resp.iter_lines():
                line = line.strip()
                if not line or line.startswith(":"):
                    continue
                if line.startswith("data: "):
                    payload = line[6:]
                    try:
                        event = json.loads(payload)
                        if isinstance(event, dict):
                            # Gradio SSE v3 sends: {"msg": "process_completed", "output": {"data": [...]}, "success": true}
                            if event.get("msg") == "process_completed" and event.get("success"):
                                output = event.get("output") or {}
                                data_list = output.get("data", [])
                                result = data_list[0] if data_list else {}
                                break
                    except Exception:
                        continue
        
        if result is None:
            raise RuntimeError("No result from Space SSE stream")

        normalized = _normalize_result(result)
        return jsonify(normalized)
    
    except Exception as e:
        logging.error("/analyze failed: %s\n%s", str(e), traceback.format_exc())
        return jsonify({
            "error": str(e),
            "hint": "Check Space availability or HF_TOKEN if private"
        }), 502

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/space_info', methods=['GET'])
def space_info():
    """Debug endpoint to inspect available HF Space APIs."""
    try:
        client = get_hf_client()
        info = client.view_api()
        return jsonify({
            "space_id": HF_SPACE_ID,
            "api_name_config": HF_API_NAME,
            "endpoints": info
        })
    except Exception as e:
        logging.error("/space_info failed: %s\n%s", str(e), traceback.format_exc())
        return jsonify({"error": str(e)}), 502
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    HF_SPACE_ID = os.getenv("HF_SPACE_ID", "Ayingxizhao/contentguard-model")
    hf_client = Client(HF_SPACE_ID)
    app.run(host='0.0.0.0', port=port)