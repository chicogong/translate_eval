from flask import Flask, render_template, request, jsonify
import os
import json
import logging
from pathlib import Path
import glob
import re
from typing import List, Dict
import threading

from config import LANGUAGES, DEFAULT_VERSION, PROJECT_ROOT, FLASK_CONFIG
from utils import setup_logging, format_run_id, validate_language_pair, detect_language
from services import TranslationService, EvaluationService, MultiModelTranslationService, MultiEvaluationService
from batch import run_batch_translation, run_batch_evaluation, run_live_translation_and_evaluation
from examples import EXAMPLES
from tts_service import TTSService

# 简化日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates', static_folder='static')

# Initialize services
translation_service = TranslationService()
evaluation_service = EvaluationService()
multi_model_service = MultiModelTranslationService()
multi_evaluation_service = MultiEvaluationService()
tts_service = TTSService()

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

@app.route('/batch')
def batch_index():
    """Render batch evaluation dashboard."""
    return render_template('batch.html', languages=LANGUAGES)

@app.route('/compare')
def compare_index():
    """Render multi-model comparison page."""
    return render_template('compare.html', languages=LANGUAGES)

@app.route('/api/models', methods=['GET'])
def api_get_models():
    """Get available translation models"""
    try:
        models = multi_model_service.get_available_models()
        return jsonify({"success": True, "models": models})
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/translate/compare', methods=['POST'])
def api_compare_translate():
    """API endpoint for multi-model translation comparison"""
    data = request.get_json()
    source_lang = data.get('source_lang') or 'auto'
    target_lang = data.get('target_lang') or 'en'
    text = data.get('text', '').strip()
    model_ids = data.get('model_ids', [])
    
    # Optional parameters
    stream = data.get('stream')
    temperature = data.get('temperature')
    max_length = data.get('max_length')
    top_p = data.get('top_p')
    
    logger.info(f"Multi-model translation API called: {source_lang} -> {target_lang}, models: {model_ids}")
    
    # Auto detect language if needed
    if source_lang in ['auto', '', None]:
        source_lang = detect_language(text)
        logger.info(f"Auto-detected source language: {source_lang}")
    
    # Validate required parameters
    if not text:
        logger.warning("Missing text in multi-model translation request")
        return jsonify({"success": False, "error": "Text is required"})
    
    if not model_ids or len(model_ids) == 0:
        logger.warning("No model IDs provided")
        return jsonify({"success": False, "error": "At least one model ID is required"})
    
    if len(model_ids) > 6:
        logger.warning("Too many model IDs provided")
        return jsonify({"success": False, "error": "Maximum 6 models are supported"})
    
    # Validate language pair
    is_valid, error_msg = validate_language_pair(source_lang, target_lang)
    if not is_valid:
        logger.warning(f"Invalid language pair: {error_msg}")
        return jsonify({"success": False, "error": error_msg})
    
    # Call multi-model translation service
    result = multi_model_service.translate_with_multiple_models(
        source_lang=source_lang,
        target_lang=target_lang,
        text=text,
        model_ids=model_ids,
        stream=stream,
        temperature=temperature,
        max_length=max_length,
        top_p=top_p
    )
    
    logger.info(f"Multi-model translation result: success={result['success']}")
    return jsonify(result)

@app.route('/api/evaluators', methods=['GET'])
def api_get_evaluators():
    """Get available evaluators"""
    try:
        evaluators = multi_evaluation_service.get_available_evaluators()
        return jsonify({"success": True, "evaluators": evaluators})
    except Exception as e:
        logger.error(f"Error getting evaluators: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/evaluate/compare', methods=['POST'])
def api_compare_evaluate():
    """API endpoint for multi-evaluator translation evaluation"""
    data = request.get_json()
    source_lang = data.get('source_lang')
    target_lang = data.get('target_lang')
    source_text = data.get('source_text', '').strip()
    translations = data.get('translations', {})
    
    logger.info(f"Multi-evaluator evaluation API called: {source_lang} -> {target_lang}")
    
    # Validate required parameters
    if not source_text:
        logger.warning("Missing source text in multi-evaluation request")
        return jsonify({"success": False, "error": "Source text is required"})
    
    if not translations:
        logger.warning("No translations provided for evaluation")
        return jsonify({"success": False, "error": "Translations are required"})
    
    # Validate language pair
    is_valid, error_msg = validate_language_pair(source_lang, target_lang)
    if not is_valid:
        logger.warning(f"Invalid language pair: {error_msg}")
        return jsonify({"success": False, "error": error_msg})
    
    # Call multi-evaluation service
    result = multi_evaluation_service.evaluate_multiple_translations(
        source_lang=source_lang,
        target_lang=target_lang,
        source_text=source_text,
        translations=translations
    )
    
    logger.info(f"Multi-evaluator evaluation result: success={result['success']}")
    return jsonify(result)

@app.route('/api/examples')
def api_examples():
    """Return a dictionary of example sentences for the playground."""
    return jsonify(EXAMPLES)

@app.route('/api/history')
def api_history():
    """Get translation and evaluation history"""
    try:
        data_dir = Path('data')
        translations_dir = data_dir / 'translations'
        evaluations_dir = data_dir / 'evaluations'
        
        history = []
        
        # Get all translation runs
        if translations_dir.exists():
            for run_dir in sorted(translations_dir.iterdir(), reverse=True):
                if run_dir.is_dir():
                    run_id = run_dir.name
                    run_info = {
                        'run_id': run_id,
                        'type': 'translation',
                        'timestamp': run_id,  # Assuming format YYYYMMDD_HHMM
                        'language_pairs': []
                    }
                    
                    # Count language pairs and items
                    total_items = 0
                    for lang_pair_dir in run_dir.iterdir():
                        if lang_pair_dir.is_dir():
                            lang_pair = lang_pair_dir.name
                            item_count = len(list(lang_pair_dir.glob('*.json')))
                            run_info['language_pairs'].append({
                                'pair': lang_pair,
                                'items': item_count
                            })
                            total_items += item_count
                    
                    run_info['total_items'] = total_items
                    if total_items > 0:
                        history.append(run_info)
        
        # Get all evaluation runs
        if evaluations_dir.exists():
            for run_dir in sorted(evaluations_dir.iterdir(), reverse=True):
                if run_dir.is_dir():
                    run_id = run_dir.name
                    run_info = {
                        'run_id': run_id,
                        'type': 'evaluation',
                        'timestamp': run_id,
                        'language_pairs': []
                    }
                    
                    # Count language pairs and calculate average scores
                    total_items = 0
                    total_score = 0
                    score_count = 0
                    
                    for lang_pair_dir in run_dir.iterdir():
                        if lang_pair_dir.is_dir():
                            lang_pair = lang_pair_dir.name
                            pair_scores = []
                            
                            for eval_file in lang_pair_dir.glob('*.json'):
                                try:
                                    with open(eval_file, 'r', encoding='utf-8') as f:
                                        eval_data = json.load(f)
                                        if isinstance(eval_data.get('evaluation_score'), (int, float)):
                                            pair_scores.append(eval_data['evaluation_score'])
                                except:
                                    continue
                            
                            if pair_scores:
                                avg_score = sum(pair_scores) / len(pair_scores)
                                run_info['language_pairs'].append({
                                    'pair': lang_pair,
                                    'items': len(pair_scores),
                                    'avg_score': round(avg_score, 2)
                                })
                                total_items += len(pair_scores)
                                total_score += sum(pair_scores)
                                score_count += len(pair_scores)
                    
                    run_info['total_items'] = total_items
                    run_info['avg_score'] = round(total_score / score_count, 2) if score_count > 0 else None
                    if total_items > 0:
                        history.append(run_info)
        
        # Sort by timestamp (newest first)
        history.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({"success": True, "history": history[:20]})  # Limit to 20 most recent
        
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/tts', methods=['POST'])
def api_text_to_speech():
    """Text-to-Speech API endpoint using MiniMax"""
    data = request.get_json()
    text = data.get('text', '').strip()
    language = data.get('language', 'zh')
    
    logger.info(f"TTS API called: language={language}, text_length={len(text)}")
    
    # Validate required parameters
    if not text:
        logger.warning("Missing text in TTS request")
        return jsonify({"success": False, "error": "Text is required"})
    
    # Validate language
    if language not in ['en', 'zh', 'ja', 'pt', 'es', 'ko']:
        logger.warning(f"Unsupported language for TTS: {language}")
        return jsonify({"success": False, "error": f"Unsupported language: {language}"})
    
    # Call TTS service
    result = tts_service.text_to_speech(text, language)
    logger.info(f"TTS API result: success={result['success']}")
    
    if result['success']:
        # Return audio data as base64
        return jsonify({
            "success": True,
            "audio_data": result['audio_data'],
            "format": result['format'],
            "voice_id": result['voice_id']
        })
    else:
        return jsonify({"success": False, "error": result['error']})

@app.route('/api/tts/voices', methods=['GET'])
def api_get_tts_voices():
    """Get available TTS voices"""
    language = request.args.get('language')
    result = tts_service.get_supported_voices(language)
    return jsonify(result)

@app.route('/api/playground-run', methods=['POST'])
def api_playground_run():
    """Run translation and evaluation for a list of texts from the playground."""
    data = request.get_json()
    source_lang = data.get('source_lang')
    target_lang = data.get('target_lang')
    texts = data.get('texts', [])

    if not all([source_lang, target_lang, texts]):
        return jsonify({"success": False, "error": "source_lang, target_lang, and a list of texts are required."}), 400

    if len(texts) > 20:
         return jsonify({"success": False, "error": "Please provide 20 lines or fewer to process at once."}), 400

    try:
        results = run_live_translation_and_evaluation(source_lang, target_lang, texts)
        avg_score = round(sum(r['evaluation_score'] for r in results if isinstance(r.get('evaluation_score'), int)) / len(results), 2)
        return jsonify({"success": True, "results": results, "avg_score": avg_score, "avg_bleu": None})
    except Exception as e:
        logger.error(f"Playground run failed: {e}", exc_info=True)
        return jsonify({"success": False, "error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    # 生产环境配置
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 8888))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    logger.info(f"Starting Flask app on {host}:{port}, debug={debug}")
    app.run(debug=debug, port=port, host=host) 