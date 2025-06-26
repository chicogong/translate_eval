from flask import Flask, render_template, request, jsonify
import os
import json
import logging
from pathlib import Path
import glob
import re
from typing import List, Dict

from config import LANGUAGES, DEFAULT_VERSION, PROJECT_ROOT, FLASK_CONFIG
from utils import setup_logging, format_run_id, validate_language_pair, detect_language
from services import TranslationService, EvaluationService

# Initialize logging
logger = setup_logging()

app = Flask(__name__, template_folder='templates', static_folder='static')

# Initialize services
translation_service = TranslationService()
evaluation_service = EvaluationService()



@app.route('/')
def index():
    """Main page"""
    logger.info("Serving main page")
    return render_template('index.html', languages=LANGUAGES)

@app.route('/api/translate', methods=['POST'])
def api_translate():
    """API endpoint for translation with enhanced parameter support"""
    data = request.get_json()
    source_lang = data.get('source_lang') or 'auto'
    target_lang = data.get('target_lang') or 'en'
    text = data.get('text', '').strip()
    
    # Optional parameters for translation control
    stream = data.get('stream')  # None means use config default
    temperature = data.get('temperature')  # None means use config default
    max_length = data.get('max_length')  # None means use config default
    top_p = data.get('top_p')  # None means use config default
    
    logger.info(f"Translation API called: {source_lang} -> {target_lang}, stream={stream}, temp={temperature}")
    
    # Auto detect language if needed
    if source_lang in ['auto', '', None]:
        source_lang = detect_language(text)
        logger.info(f"Auto-detected source language: {source_lang}")
    
    # Validate required parameters
    if not text:
        logger.warning("Missing text in translation request")
        return jsonify({"success": False, "error": "Text is required"})
    
    # Validate language pair
    is_valid, error_msg = validate_language_pair(source_lang, target_lang)
    if not is_valid:
        logger.warning(f"Invalid language pair: {error_msg}")
        return jsonify({"success": False, "error": error_msg})
    
    # Call translation service with parameters
    result = translation_service.translate_text(
        source_lang=source_lang,
        target_lang=target_lang,
        text=text,
        stream=stream,
        temperature=temperature,
        max_length=max_length,
        top_p=top_p
    )
    
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
    
    # Validate required parameters
    if not all([source_text, translation]):
        logger.warning("Missing required parameters in evaluation request")
        return jsonify({"success": False, "error": "Source text and translation are required"})
    
    # Validate language pair
    is_valid, error_msg = validate_language_pair(source_lang, target_lang)
    if not is_valid:
        logger.warning(f"Invalid language pair: {error_msg}")
        return jsonify({"success": False, "error": error_msg})
    
    # Call evaluation service
    result = evaluation_service.evaluate_translation(source_lang, target_lang, source_text, translation)
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
    logger.info(f"Starting Flask app on {FLASK_CONFIG['host']}:{FLASK_CONFIG['port']}, debug={FLASK_CONFIG['debug']}")
    app.run(debug=FLASK_CONFIG['debug'], port=FLASK_CONFIG['port'], host=FLASK_CONFIG['host']) 