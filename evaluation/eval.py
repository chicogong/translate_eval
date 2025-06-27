#!/usr/bin/env python3
"""
Translation Evaluation Tool
批量翻译评估脚本
"""

import os
import sys
import json
import time
import argparse
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import nltk
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

# Project root & default version
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.services import TranslationService, EvaluationService
from backend.utils import (load_test_cases, save_translation_result,
                           save_evaluation_result, load_translation_results,
                           load_evaluation_results, generate_report)

# Version identifier for result directory (overridden in main)
RESULT_VERSION = os.environ.get('RESULT_VERSION', 'v1')

# Load environment variables
load_dotenv(PROJECT_ROOT / '.env')

# Setup logging
def setup_logging():
    """配置日志系统"""
    # Create logs directory if it doesn't exist
    log_dir = PROJECT_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Get logging configuration from environment
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    log_file = log_dir / 'eval.log'
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

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    logger.info("Downloading NLTK punkt tokenizer")
    nltk.download('punkt')

def main():
    """Main function"""
    global RESULT_VERSION
    parser = argparse.ArgumentParser(description='Translation Evaluation Tool')
    parser.add_argument('--source', type=str, help='Source language code')
    parser.add_argument('--target', type=str, help='Target language code')
    parser.add_argument('--line', type=int, help='Specific line number to process')
    parser.add_argument('--delay', type=float, default=2.0, help='Delay between API calls (seconds)')
    parser.add_argument('--version', type=str, default=RESULT_VERSION, help='Version tag for result directory (default v1)')
    
    args = parser.parse_args()
    RESULT_VERSION = args.version

    translation_service = TranslationService()
    evaluation_service = EvaluationService()
    
    # Check if API keys are available
    if not translation_service.config.get('api_key') or not evaluation_service.config.get('api_key'):
        logger.error("API keys not found. Please create a .env file with your API keys.")
        logger.error("You can use .env.example as a template.")
        sys.exit(1)
    
    logger.info("🚀 Translation Evaluation Tool")
    logger.info("=" * 50)
    
    # Define language pairs
    languages = ['en', 'zh', 'ja', 'pt', 'es']
    
    if args.source and args.target:
        # Process specific language pair
        if args.source not in languages or args.target not in languages:
            logger.error(f"Supported languages are {languages}")
            sys.exit(1)
        
        if args.source == args.target:
            logger.error("Source and target languages must be different")
            sys.exit(1)
        
        language_pairs = [(args.source, args.target)]
    else:
        # Process all language pairs
        language_pairs = []
        for src in languages:
            for tgt in languages:
                if src != tgt:
                    language_pairs.append((src, tgt))
    
    logger.info(f"Processing {len(language_pairs)} language pairs with {args.delay}s delay")
    
    total_processed = 0
    total_successful = 0
    
    for src_lang, tgt_lang in language_pairs:
        logger.info(f"📝 Processing {src_lang} → {tgt_lang}")
        
        # Load test cases
        test_cases = load_test_cases(src_lang)
        if not test_cases:
            logger.warning(f"No test cases found for {src_lang}")
            continue
        
        if args.line:
            if args.line > len(test_cases):
                logger.error(f"Line {args.line} not found (max: {len(test_cases)})")
                continue
            test_cases = [test_cases[args.line - 1]]
            line_numbers = [args.line]
        else:
            line_numbers = list(range(1, len(test_cases) + 1))
        
        for i, (line_num, source_text) in enumerate(zip(line_numbers, test_cases)):
            logger.info(f"🔄 Processing line {line_num}: {source_text[:50]}...")
            
            # Translate
            translation_result = translation_service.translate_text(src_lang, tgt_lang, source_text)
            if not translation_result.get("success"):
                logger.error(f"Translation failed: {translation_result.get('error')}")
                total_processed += 1
                continue
            
            translation = translation_result["translation"]
            logger.info(f"📄 Translation: {translation[:50]}...")
            
            # Evaluate
            eval_result = evaluation_service.evaluate_translation(src_lang, tgt_lang, source_text, translation)
            if eval_result.get("success"):
                score = eval_result["score"]
                justification = eval_result["justification"]
                logger.info(f"⭐ Score: {score}/10")
            else:
                logger.warning(f"Evaluation failed: {eval_result.get('error')}")
                score = "N/A"
                justification = f"Evaluation failed: {eval_result.get('error')}"
            
            # Calculate BLEU score (if reference available)
            bleu_score = None
            # Note: BLEU calculation would need reference translations
            
            # Save result
            save_result(src_lang, tgt_lang, line_num, source_text, 
                       translation, score, justification, bleu_score, version=RESULT_VERSION)
            
            total_processed += 1
            if eval_result.get("success"):
                total_successful += 1
            
            # Rate limiting
            if i < len(test_cases) - 1:  # Don't delay after the last item
                logger.debug(f"Waiting {args.delay} seconds...")
                time.sleep(args.delay)
    
    # Generate report
    generate_report(version=RESULT_VERSION)
    
    logger.info("🎉 Evaluation Complete!")
    logger.info(f"Total processed: {total_processed}")
    logger.info(f"Successful evaluations: {total_successful}")
    if total_processed > 0:
        success_rate = total_successful/total_processed*100
        logger.info(f"Success rate: {success_rate:.1f}%")

if __name__ == "__main__":
    main() 