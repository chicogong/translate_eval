from flask import Flask, render_template, request, jsonify
import os
import json
import requests
import logging
from pathlib import Path
from dotenv import load_dotenv
import glob
import re
from typing import List, Dict

# Load environment variables
load_dotenv()

# Setup logging
def setup_logging():
    """配置日志系统"""
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Get logging configuration from environment
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    log_file = os.environ.get('LOG_FILE', 'logs/app.log')
    log_format = os.environ.get('LOG_FORMAT', 
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d in %(funcName)s] - %(message)s'
    )
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format,
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

# Initialize logging
logger = setup_logging()

app = Flask(__name__, template_folder='templates', static_folder='static')

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Language mapping
LANGUAGES = {
    'en': 'English',
    'zh': '中文',
    'ja': '日本語',
    'pt': 'Português',
    'es': 'Español'
}

def get_translation_config():
    """获取翻译API配置"""
    config = {
        'api_key': os.environ.get('TRANSLATION_API_KEY'),
        'api_url': os.environ.get('TRANSLATION_API_URL'),
        'model': os.environ.get('TRANSLATION_MODEL')
    }
    
    if not config['api_key']:
        logger.error("Translation API key not found in environment variables")
    
    logger.debug(f"Translation API config loaded: url={config['api_url']}, model={config['model']}")
    return config

def get_evaluation_config():
    """获取评估API配置"""
    config = {
        'api_key': os.environ.get('EVALUATION_API_KEY'),
        'api_url': os.environ.get('EVALUATION_API_URL'),
        'model': os.environ.get('EVALUATION_MODEL')
    }
    
    if not config['api_key']:
        logger.error("Evaluation API key not found in environment variables")
    
    logger.debug(f"Evaluation API config loaded: url={config['api_url']}, model={config['model']}")
    return config

def translate_text(source_lang: str, target_lang: str, text: str) -> dict:
    """Translate text using the API"""
    logger.info(f"Starting translation: {source_lang} -> {target_lang}, text length: {len(text)}")
    
    config = get_translation_config()
    if not config['api_key']:
        logger.error("Translation API key not available")
        return {"success": False, "error": "Translation API key not found"}
    
    # Load prompt template
    prompt_file = PROJECT_ROOT / f"evaluation/prompts/{source_lang}-{target_lang}.txt"
    if not prompt_file.exists():
        logger.error(f"Prompt file not found: {prompt_file}")
        return {"success": False, "error": f"Prompt file not found: {prompt_file}"}
    
    try:
        prompt_template = prompt_file.read_text(encoding="utf-8")
        system_prompt = prompt_template.split("SOURCE TEXT:")[0].strip()
        user_content = text
        logger.debug(f"Loaded prompt template from {prompt_file}")
    except Exception as e:
        logger.error(f"Error reading prompt file {prompt_file}: {e}")
        return {"success": False, "error": f"Error reading prompt: {e}"}
    
    # Make API call
    payload = {
        'model': config['model'],
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_content}
        ]
    }
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {config["api_key"]}'}
    
    try:
        logger.debug(f"Making translation API call to {config['api_url']} with model {config['model']}")
        response = requests.post(config['api_url'], headers=headers, data=json.dumps(payload), timeout=60)
        response.raise_for_status()
        response_data = response.json()
        
        if "choices" in response_data and response_data["choices"]:
            translation = response_data["choices"][0]["message"]["content"]
            logger.info(f"Translation successful, result length: {len(translation)}")
            return {"success": True, "translation": translation}
        else:
            logger.error(f"Invalid API response: {response_data}")
            return {"success": False, "error": "Invalid API response"}
    except requests.exceptions.RequestException as e:
        logger.error(f"Translation API request failed: {e}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error during translation: {e}")
        return {"success": False, "error": str(e)}

def evaluate_translation(source_lang: str, target_lang: str, source_text: str, translation: str) -> dict:
    """Evaluate translation quality using LLM"""
    logger.info(f"Starting evaluation: {source_lang} -> {target_lang}")
    
    config = get_evaluation_config()
    if not config['api_key']:
        logger.error("Evaluation API key not available")
        return {"success": False, "error": "Evaluation API key not found"}
    
    # Load evaluator prompt
    eval_prompt_path = PROJECT_ROOT / "evaluation/prompts/evaluator-prompt.txt"
    if not eval_prompt_path.exists():
        logger.error(f"Evaluator prompt not found: {eval_prompt_path}")
        return {"success": False, "error": "Evaluator prompt not found"}
    
    try:
        eval_prompt_template = eval_prompt_path.read_text(encoding="utf-8")
        eval_prompt = eval_prompt_template.replace("{{source_lang}}", LANGUAGES.get(source_lang, source_lang))
        eval_prompt = eval_prompt.replace("{{target_lang}}", LANGUAGES.get(target_lang, target_lang))
        eval_prompt = eval_prompt.replace("{{source_text}}", source_text)
        eval_prompt = eval_prompt.replace("{{translation_text}}", translation)
        logger.debug(f"Loaded evaluator prompt from {eval_prompt_path}")
    except Exception as e:
        logger.error(f"Error reading evaluator prompt {eval_prompt_path}: {e}")
        return {"success": False, "error": f"Error reading evaluator prompt: {e}"}
    
    # Make API call
    payload = {
        'model': config['model'],
        'messages': [{'role': 'user', 'content': eval_prompt}]
    }
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {config["api_key"]}'}
    
    try:
        logger.debug(f"Making evaluation API call to {config['api_url']} with model {config['model']}")
        response = requests.post(config['api_url'], headers=headers, data=json.dumps(payload), timeout=60)
        response.raise_for_status()
        eval_data = response.json()
        
        if "choices" in eval_data and eval_data["choices"]:
            eval_result_str = eval_data["choices"][0]["message"]["content"].strip()
            
            # Parse score and justification
            score = "N/A"
            justification = "No justification provided."
            
            lines = eval_result_str.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith("SCORE:"):
                    try:
                        score = int(line.split("SCORE:")[1].strip())
                        logger.debug(f"Parsed evaluation score: {score}")
                    except (ValueError, IndexError):
                        logger.warning(f"Failed to parse score from line: {line}")
                        score = "N/A"
                elif line.startswith("JUSTIFICATION:"):
                    justification = line.split("JUSTIFICATION:")[1].strip()
                    logger.debug(f"Parsed justification length: {len(justification)}")
            
            logger.info(f"Evaluation successful, score: {score}")
            return {"success": True, "score": score, "justification": justification}
        else:
            logger.error(f"Invalid evaluation response: {eval_data}")
            return {"success": False, "error": "Invalid evaluation response"}
    except requests.exceptions.RequestException as e:
        logger.error(f"Evaluation API request failed: {e}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error during evaluation: {e}")
        return {"success": False, "error": str(e)}

@app.route('/')
def index():
    """Main page"""
    logger.info("Serving main page")
    return render_template('index.html', languages=LANGUAGES)

@app.route('/api/translate', methods=['POST'])
def api_translate():
    """API endpoint for translation"""
    data = request.get_json()
    source_lang = data.get('source_lang')
    target_lang = data.get('target_lang')
    text = data.get('text', '').strip()
    
    logger.info(f"Translation API called: {source_lang} -> {target_lang}")
    
    if not all([source_lang, target_lang, text]):
        logger.warning("Missing required parameters in translation request")
        return jsonify({"success": False, "error": "Missing required parameters"})
    
    if source_lang == target_lang:
        logger.warning("Source and target languages are the same")
        return jsonify({"success": False, "error": "Source and target languages must be different"})
    
    result = translate_text(source_lang, target_lang, text)
    logger.info(f"Translation API result: success={result['success']}")
    return jsonify(result)

@app.route('/api/evaluate', methods=['POST'])
def api_evaluate():
    """API endpoint for translation evaluation"""
    data = request.get_json()
    source_lang = data.get('source_lang')
    target_lang = data.get('target_lang')
    source_text = data.get('source_text', '').strip()
    translation = data.get('translation', '').strip()
    
    logger.info(f"Evaluation API called: {source_lang} -> {target_lang}")
    
    if not all([source_lang, target_lang, source_text, translation]):
        logger.warning("Missing required parameters in evaluation request")
        return jsonify({"success": False, "error": "Missing required parameters"})
    
    result = evaluate_translation(source_lang, target_lang, source_text, translation)
    logger.info(f"Evaluation API result: success={result['success']}")
    return jsonify(result)

# ========= Batch Evaluation Utilities =========

def collect_results(source_lang: str, target_lang: str):
    """Collect all result dicts for a language pair.
    Supports both new-style JSON result files (preferred) and legacy plain-text files.
    Returns a list of dicts (may be partial info for legacy files).
    """
    results_path = PROJECT_ROOT / f"data/results/{source_lang}-{target_lang}"
    if not results_path.exists():
        return []

    result_dicts: List[Dict] = []
    pattern = "test_suite_line_*_result.txt"
    for file_path in results_path.glob(pattern):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    continue
                # If content looks like JSON (starts with { or [), attempt to parse
                if content[0] in "[{":
                    result = json.loads(content)
                else:
                    # Legacy plain text translation; build minimal dict
                    # Extract line number from filename
                    m = re.search(r"line_(\d+)_", file_path.name)
                    line_num = int(m.group(1)) if m else 0
                    result = {
                        "source_lang": source_lang,
                        "target_lang": target_lang,
                        "line_number": line_num,
                        "source_text": "N/A",
                        "translation": content,
                        "evaluation_score": None,
                        "justification": "Legacy result – no evaluation data",
                    }
                result_dicts.append(result)
        except json.JSONDecodeError:
            logger.warning(f"Skipping non-JSON result file {file_path} (invalid JSON)")
        except Exception as e:
            logger.error(f"Failed to read result file {file_path}: {e}")

    result_dicts.sort(key=lambda x: x.get("line_number", 0))
    return result_dicts

# Helper to compute aggregate stats
def summarize_results(results: List[Dict]):
    """Return average score and BLEU over numeric entries."""
    scores = [r.get("evaluation_score") for r in results if isinstance(r.get("evaluation_score"), (int, float))]
    bleus = [r.get("bleu_score") for r in results if isinstance(r.get("bleu_score"), (int, float))]
    avg_score = round(sum(scores) / len(scores), 2) if scores else None
    avg_bleu = round(sum(bleus) / len(bleus), 4) if bleus else None
    return {"avg_score": avg_score, "avg_bleu": avg_bleu, "count": len(results)}

# ========= New Routes =========

@app.route('/batch')
def batch_index():
    """Render batch evaluation dashboard."""
    return render_template('batch.html', languages=LANGUAGES)

@app.route('/api/results', methods=['GET'])
def api_results():
    """Return aggregated results for a given language pair.
    Query params: source_lang, target_lang.
    """
    source_lang = request.args.get('source_lang')
    target_lang = request.args.get('target_lang')

    if not source_lang or not target_lang:
        return jsonify({"success": False, "error": "source_lang and target_lang are required."}), 400

    if source_lang == target_lang:
        return jsonify({"success": False, "error": "source_lang and target_lang must be different."}), 400

    results = collect_results(source_lang, target_lang)
    if not results:
        return jsonify({"success": False, "error": "No results found for the specified language pair."})

    summary = summarize_results(results)
    return jsonify({"success": True, **summary, "results": results})

if __name__ == '__main__':
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', 8888))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    logger.info(f"Starting Flask app on {host}:{port}, debug={debug}")
    app.run(debug=debug, port=port, host=host) 