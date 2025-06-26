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

# Default version tag (can be overridden via env)
DEFAULT_VERSION = os.environ.get("RESULT_VERSION", "v1")

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

def get_translation_prompt(source_lang: str, target_lang: str) -> str:
    """Get translation prompt for language pair"""
    # Translation prompts for different language pairs
    prompts = {
        "en-zh": "You are an expert English to Chinese translator. Translate the following English text into natural, fluent Chinese. Use Simplified Chinese characters and maintain the technical accuracy of the original text.",
        "zh-en": "You are an expert Chinese to English translator. Translate the following Chinese text into natural, fluent English. Maintain the technical accuracy and formal tone of the original text.",
        "en-ja": "You are an expert English to Japanese translator. Translate the following English text into natural, fluent Japanese. Use appropriate formal language and maintain technical accuracy.",
        "ja-en": "You are an expert Japanese to English translator. Translate the following Japanese text into natural, fluent English. Maintain the technical accuracy and formal tone.",
        "en-es": "You are an expert English to Spanish translator. Translate the following English text into natural, fluent Spanish. Maintain technical accuracy and use formal language.",
        "es-en": "You are an expert Spanish to English translator. Translate the following Spanish text into natural, fluent English. Maintain technical accuracy and formal tone.",
        "en-pt": "You are an expert English to Portuguese translator. Translate the following English text into natural, fluent Portuguese. Maintain technical accuracy and use formal language.",
        "pt-en": "You are an expert Portuguese to English translator. Translate the following Portuguese text into natural, fluent English. Maintain technical accuracy and formal tone.",
        "zh-ja": "You are an expert Chinese to Japanese translator. Translate the following Chinese text into natural, fluent Japanese. Use appropriate formal language.",
        "ja-zh": "You are an expert Japanese to Chinese translator. Translate the following Japanese text into natural, fluent Chinese using Simplified Chinese characters.",
        "zh-es": "You are an expert Chinese to Spanish translator. Translate the following Chinese text into natural, fluent Spanish. Maintain technical accuracy.",
        "es-zh": "You are an expert Spanish to Chinese translator. Translate the following Spanish text into natural, fluent Chinese using Simplified Chinese characters.",
        "zh-pt": "You are an expert Chinese to Portuguese translator. Translate the following Chinese text into natural, fluent Portuguese. Maintain technical accuracy.",
        "pt-zh": "You are an expert Portuguese to Chinese translator. Translate the following Portuguese text into natural, fluent Chinese using Simplified Chinese characters.",
        "ja-es": "You are an expert Japanese to Spanish translator. Translate the following Japanese text into natural, fluent Spanish. Maintain technical accuracy.",
        "es-ja": "You are an expert Spanish to Japanese translator. Translate the following Spanish text into natural, fluent Japanese. Use appropriate formal language.",
        "ja-pt": "You are an expert Japanese to Portuguese translator. Translate the following Japanese text into natural, fluent Portuguese. Maintain technical accuracy.",
        "pt-ja": "You are an expert Portuguese to Japanese translator. Translate the following Portuguese text into natural, fluent Japanese. Use appropriate formal language.",
        "es-pt": "You are an expert Spanish to Portuguese translator. Translate the following Spanish text into natural, fluent Portuguese. Maintain technical accuracy.",
        "pt-es": "You are an expert Portuguese to Spanish translator. Translate the following Portuguese text into natural, fluent Spanish. Maintain technical accuracy."
    }
    
    lang_pair = f"{source_lang}-{target_lang}"
    return prompts.get(lang_pair, f"Translate the following text from {source_lang} to {target_lang}.")

def translate_text(source_lang: str, target_lang: str, text: str) -> dict:
    """Translate text using the API"""
    logger.info(f"Starting translation: {source_lang} -> {target_lang}, text length: {len(text)}")
    
    config = get_translation_config()
    if not config['api_key']:
        logger.error("Translation API key not available")
        return {"success": False, "error": "Translation API key not found"}
    
    # Get translation prompt
    try:
        system_prompt = get_translation_prompt(source_lang, target_lang)
        user_content = text
        logger.debug(f"Using translation prompt for {source_lang}-{target_lang}")
    except Exception as e:
        logger.error(f"Error getting translation prompt: {e}")
        return {"success": False, "error": f"Error getting prompt: {e}"}
    
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

def get_evaluation_prompt(source_lang: str, target_lang: str, source_text: str, translation: str) -> str:
    """Get evaluation prompt for translation quality assessment"""
    source_lang_name = LANGUAGES.get(source_lang, source_lang)
    target_lang_name = LANGUAGES.get(target_lang, target_lang)
    
    prompt = f"""You are an expert linguistic evaluator. Your task is to assess the quality of a machine translation.
You will be given a source text and a translation.
Evaluate the translation based on two criteria:
1. **Accuracy:** Does the translation faithfully convey the meaning of the source text?
2. **Fluency:** Is the translation natural and grammatically correct in the target language?

Provide a single score from 1 to 10, where 1 is very poor and 10 is perfect.
The score should be an integer.
Also provide a one-sentence justification for your score.

Format your response EXACTLY as follows:
SCORE: [number]
JUSTIFICATION: [your justification]

Example Response:
SCORE: 8
JUSTIFICATION: The translation is accurate but sounds slightly unnatural in one phrase.

---

SOURCE TEXT ({source_lang_name}):
{source_text}

---

TRANSLATION ({target_lang_name}):
{translation}"""
    
    return prompt

def evaluate_translation(source_lang: str, target_lang: str, source_text: str, translation: str) -> dict:
    """Evaluate translation quality using LLM"""
    logger.info(f"Starting evaluation: {source_lang} -> {target_lang}")
    
    config = get_evaluation_config()
    if not config['api_key']:
        logger.error("Evaluation API key not available")
        return {"success": False, "error": "Evaluation API key not found"}
    
    # Get evaluation prompt
    try:
        eval_prompt = get_evaluation_prompt(source_lang, target_lang, source_text, translation)
        logger.debug(f"Using evaluation prompt for {source_lang}-{target_lang}")
    except Exception as e:
        logger.error(f"Error getting evaluation prompt: {e}")
        return {"success": False, "error": f"Error getting evaluation prompt: {e}"}
    
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

def collect_results(source_lang: str, target_lang: str, version: str = DEFAULT_VERSION):
    """Collect all result dicts for a language pair.
    Supports both new-style JSON result files (preferred) and legacy plain-text files.
    Returns a list of dicts (may be partial info for legacy files).
    """
    results_path = PROJECT_ROOT / f"data/results/{version}/{source_lang}-{target_lang}"
    if not results_path.exists():
        return []

    result_dicts: List[Dict] = []
    patterns = ["test_suite_line_*_result.json", "test_suite_line_*_result.txt"]
    for pat in patterns:
        for file_path in results_path.glob(pat):
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
    version = request.args.get('version', DEFAULT_VERSION)

    if not source_lang or not target_lang:
        return jsonify({"success": False, "error": "source_lang and target_lang are required."}), 400

    if source_lang == target_lang:
        return jsonify({"success": False, "error": "source_lang and target_lang must be different."}), 400

    results = collect_results(source_lang, target_lang, version=version)
    if not results:
        return jsonify({"success": False, "error": "No results found for the specified language pair."})

    summary = summarize_results(results)
    return jsonify({"success": True, "version": version, **summary, "results": results})

@app.route('/api/available-runs')
def api_available_runs():
    """Get available translation and evaluation runs"""
    try:
        translation_runs = []
        evaluation_runs = []
        
        # Get translation runs
        translations_dir = Path('data/translations')
        if translations_dir.exists():
            for run_dir in translations_dir.iterdir():
                if run_dir.is_dir():
                    translation_runs.append(run_dir.name)
        
        # Get evaluation runs
        evaluations_dir = Path('data/evaluations')
        if evaluations_dir.exists():
            for run_dir in evaluations_dir.iterdir():
                if run_dir.is_dir():
                    evaluation_runs.append(run_dir.name)
        
        # Sort by date (newest first)
        translation_runs.sort(reverse=True)
        evaluation_runs.sort(reverse=True)
        
        return jsonify({
            'success': True,
            'translation_runs': translation_runs,
            'evaluation_runs': evaluation_runs
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error getting available runs: {str(e)}'
        })

@app.route('/api/evaluation-results')
def api_evaluation_results():
    """Get evaluation results for a specific run and language pair"""
    try:
        eval_run_id = request.args.get('eval_run_id')
        source_lang = request.args.get('source_lang')
        target_lang = request.args.get('target_lang')
        
        if not all([eval_run_id, source_lang, target_lang]):
            return jsonify({
                'success': False,
                'error': 'eval_run_id, source_lang, and target_lang are required'
            })
        
        if source_lang == target_lang:
            return jsonify({
                'success': False,
                'error': 'source_lang and target_lang must be different'
            })
        
        # Load evaluation results
        evaluations_dir = Path(f'data/evaluations/{eval_run_id}/{source_lang}-{target_lang}')
        if not evaluations_dir.exists():
            return jsonify({
                'success': False,
                'error': f'No evaluation results found for {source_lang}-{target_lang} run {eval_run_id}'
            })
        
        results = []
        for json_file in evaluations_dir.glob('*.json'):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    results.append(data)
            except Exception as e:
                logger.warning(f"Failed to load {json_file}: {e}")
        
        # Sort by line number
        results.sort(key=lambda x: x.get('line_number', 0))
        
        # Calculate summary
        summary = summarize_results(results)
        
        return jsonify({
            'success': True,
            'eval_run_id': eval_run_id,
            'results': results,
            **summary
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error loading evaluation results: {str(e)}'
        })

@app.route('/api/batch-translate', methods=['POST'])
def api_batch_translate():
    """Start batch translation process"""
    try:
        data = request.get_json()
        source_lang = data.get('source_lang')
        target_lang = data.get('target_lang')
        lines = data.get('lines', 15)
        
        if not all([source_lang, target_lang]):
            return jsonify({
                'success': False,
                'error': 'source_lang and target_lang are required'
            })
        
        if source_lang == target_lang:
            return jsonify({
                'success': False,
                'error': 'source_lang and target_lang must be different'
            })
        
        # Generate run ID
        from datetime import datetime
        run_id = datetime.now().strftime("%Y%m%d_%H%M")
        
        # Import and run translation script
        import subprocess
        import sys
        
        cmd = [
            sys.executable, 'scripts/translate_single.py',
            source_lang, target_lang,
            '--run-id', run_id,
            '--lines', str(lines)
        ]
        
        # Run in background
        process = subprocess.Popen(cmd, cwd=PROJECT_ROOT)
        
        return jsonify({
            'success': True,
            'run_id': run_id,
            'message': f'Batch translation started for {source_lang}-{target_lang}',
            'processed': lines
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error starting batch translation: {str(e)}'
        })

@app.route('/api/batch-evaluate', methods=['POST'])
def api_batch_evaluate():
    """Start batch evaluation process"""
    try:
        data = request.get_json()
        source_lang = data.get('source_lang')
        target_lang = data.get('target_lang')
        translation_run_id = data.get('translation_run_id')
        
        if not all([source_lang, target_lang, translation_run_id]):
            return jsonify({
                'success': False,
                'error': 'source_lang, target_lang, and translation_run_id are required'
            })
        
        if source_lang == target_lang:
            return jsonify({
                'success': False,
                'error': 'source_lang and target_lang must be different'
            })
        
        # Generate evaluation run ID
        from datetime import datetime
        eval_run_id = datetime.now().strftime("%Y%m%d_%H%M")
        
        # Import and run evaluation script
        import subprocess
        import sys
        
        cmd = [
            sys.executable, 'scripts/evaluate_single.py',
            source_lang, target_lang, translation_run_id,
            '--eval-run-id', eval_run_id
        ]
        
        # Run in background
        process = subprocess.Popen(cmd, cwd=PROJECT_ROOT)
        
        return jsonify({
            'success': True,
            'eval_run_id': eval_run_id,
            'translation_run_id': translation_run_id,
            'message': f'Batch evaluation started for {source_lang}-{target_lang}',
            'processed': 15  # Assuming all test cases
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error starting batch evaluation: {str(e)}'
        })

@app.route('/api/validate-results')
def validate_results():
    """Validate result files before displaying"""
    try:
        version = request.args.get('version', 'v2')
        source_lang = request.args.get('source_lang')
        target_lang = request.args.get('target_lang')
        
        if not source_lang or not target_lang:
            return jsonify({
                'success': False,
                'error': 'Missing source_lang or target_lang parameter'
            })
        
        # Check if results directory exists
        results_dir = Path(f'data/results/{version}/{source_lang}-{target_lang}')
        if not results_dir.exists():
            return jsonify({
                'success': False,
                'error': f'No results found for {source_lang}-{target_lang} version {version}'
            })
        
        # Check JSON files
        json_files = list(results_dir.glob('*.json'))
        if not json_files:
            return jsonify({
                'success': False,
                'error': f'No result files found in {results_dir}'
            })
        
        # Validate file formats
        valid_files = 0
        invalid_files = []
        total_results = 0
        
        required_fields = ['source_lang', 'target_lang', 'line_number', 
                         'source_text', 'translation', 'score', 'justification']
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if all(field in data for field in required_fields):
                    valid_files += 1
                    total_results += 1
                else:
                    invalid_files.append({
                        'file': json_file.name,
                        'error': 'Missing required fields'
                    })
                    
            except json.JSONDecodeError:
                invalid_files.append({
                    'file': json_file.name,
                    'error': 'Invalid JSON format'
                })
            except Exception as e:
                invalid_files.append({
                    'file': json_file.name,
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'validation': {
                'total_files': len(json_files),
                'valid_files': valid_files,
                'invalid_files': len(invalid_files),
                'total_results': total_results,
                'errors': invalid_files[:5]  # Show first 5 errors
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Validation error: {str(e)}'
        })

if __name__ == '__main__':
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', 8888))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    logger.info(f"Starting Flask app on {host}:{port}, debug={debug}")
    app.run(debug=debug, port=port, host=host) 