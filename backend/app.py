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
from services import TranslationService, EvaluationService
from batch import run_batch_translation, run_batch_evaluation, run_live_translation_and_evaluation
from examples import EXAMPLES

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

# ========= New Routes =========

@app.route('/batch')
def batch_index():
    """Render batch evaluation dashboard."""
    return render_template('batch.html', languages=LANGUAGES)

@app.route('/api/examples')
def api_examples():
    """Return a dictionary of example sentences for the playground."""
    return jsonify(EXAMPLES)

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
    logger.info(f"Starting Flask app on {FLASK_CONFIG['host']}:{FLASK_CONFIG['port']}, debug={FLASK_CONFIG['debug']}")
    app.run(debug=FLASK_CONFIG['debug'], port=FLASK_CONFIG['port'], host=FLASK_CONFIG['host']) 