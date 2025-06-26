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

def load_test_cases(lang: str) -> list:
    """Load test cases for a specific language"""
    test_file = PROJECT_ROOT / f"data/testcases/{lang}/test_suite.txt"
    if not test_file.exists():
        logger.warning(f"Test file not found: {test_file}")
        return []
    
    with open(test_file, 'r', encoding='utf-8') as f:
        test_cases = [line.strip() for line in f if line.strip()]
    
    logger.info(f"Loaded {len(test_cases)} test cases from {test_file}")
    return test_cases

def save_result(source_lang: str, target_lang: str, line_num: int, 
                source_text: str, translation: str, score: int, 
                justification: str, bleu_score: float = None, version: str = RESULT_VERSION):
    """Save translation result to file"""
    results_dir = PROJECT_ROOT / f"data/results/{version}/{source_lang}-{target_lang}"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    result_file = results_dir / f"test_suite_line_{line_num}_result.json"
    
    result_data = {
        "source_lang": source_lang,
        "target_lang": target_lang,
        "line_number": line_num,
        "source_text": source_text,
        "translation": translation,
        "evaluation_score": score,
        "justification": justification,
        "bleu_score": bleu_score,
        "timestamp": datetime.now().isoformat()
    }
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    
    logger.debug(f"Saved result to {result_file}")

def save_translation_result(source_lang: str, target_lang: str, line_number: int, 
                          source_text: str, translation: str, run_id: str):
    """Save translation result to file"""
    translations_dir = PROJECT_ROOT / f"data/translations/{run_id}/{source_lang}-{target_lang}"
    translations_dir.mkdir(parents=True, exist_ok=True)
    
    result_file = translations_dir / f"line_{line_number}_translation.json"
    
    translation_data = {
        "source_lang": source_lang,
        "target_lang": target_lang,
        "line_number": line_number,
        "source_text": source_text,
        "translation": translation,
        "run_id": run_id,
        "timestamp": datetime.now().isoformat()
    }
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(translation_data, f, ensure_ascii=False, indent=2)
    
    logger.debug(f"Translation saved to {result_file}")

def save_evaluation_result(source_lang: str, target_lang: str, line_number: int, 
                         source_text: str, translation: str, score: int, 
                         justification: str, eval_run_id: str):
    """Save evaluation result to file"""
    evaluations_dir = PROJECT_ROOT / f"data/evaluations/{eval_run_id}/{source_lang}-{target_lang}"
    evaluations_dir.mkdir(parents=True, exist_ok=True)
    
    result_file = evaluations_dir / f"line_{line_number}_evaluation.json"
    
    evaluation_data = {
        "source_lang": source_lang,
        "target_lang": target_lang,
        "line_number": line_number,
        "source_text": source_text,
        "translation": translation,
        "evaluation_score": score,
        "justification": justification,
        "eval_run_id": eval_run_id,
        "timestamp": datetime.now().isoformat(),
        "bleu_score": None  # Can be calculated later if needed
    }
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(evaluation_data, f, ensure_ascii=False, indent=2)
    
    logger.debug(f"Evaluation saved to {result_file}")

def load_translation_results(source_lang: str, target_lang: str, run_id: str) -> list:
    """Load translation results from a specific run"""
    translations_dir = PROJECT_ROOT / f"data/translations/{run_id}/{source_lang}-{target_lang}"
    
    if not translations_dir.exists():
        logger.warning(f"Translation directory not found: {translations_dir}")
        return []
    
    results = []
    json_files = sorted(translations_dir.glob("*.json"))
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                results.append(data)
        except Exception as e:
            logger.warning(f"Failed to load translation result {json_file}: {e}")
    
    # Sort by line number
    results.sort(key=lambda x: x.get('line_number', 0))
    logger.info(f"Loaded {len(results)} translation results from {translations_dir}")
    return results

def load_evaluation_results(source_lang: str, target_lang: str, eval_run_id: str) -> list:
    """Load evaluation results from a specific run"""
    evaluations_dir = PROJECT_ROOT / f"data/evaluations/{eval_run_id}/{source_lang}-{target_lang}"
    
    if not evaluations_dir.exists():
        logger.warning(f"Evaluation directory not found: {evaluations_dir}")
        return []
    
    results = []
    json_files = sorted(evaluations_dir.glob("*.json"))
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                results.append(data)
        except Exception as e:
            logger.warning(f"Failed to load evaluation result {json_file}: {e}")
    
    # Sort by line number
    results.sort(key=lambda x: x.get('line_number', 0))
    logger.info(f"Loaded {len(results)} evaluation results from {evaluations_dir}")
    return results

def generate_report(version: str = RESULT_VERSION):
    """Generate a summary report from result files"""
    logger.info("Generating evaluation report")
    
    results_dir = PROJECT_ROOT / "data/results" / version
    if not results_dir.exists():
        logger.warning("No results directory found")
        return
    
    report_file = PROJECT_ROOT / f"docs/Test_Report_{version}.md"
    report_file.parent.mkdir(exist_ok=True)
    
    all_results = []
    
    # Collect all result files
    for lang_pair_dir in results_dir.iterdir():
        if lang_pair_dir.is_dir():
            for result_file in lang_pair_dir.glob("test_suite_line_*_result.json"):
                try:
                    with open(result_file, 'r', encoding='utf-8') as f:
                        result_data = json.load(f)
                        all_results.append(result_data)
                except Exception as e:
                    logger.error(f"Error reading result file {result_file}: {e}")
    
    logger.info(f"Collected {len(all_results)} results for report")
    
    # Generate markdown report
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# Translation Evaluation Report\n\n")
        f.write(f"**Report Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("| Src | Tgt | Line | Score | Justification | Source Text (truncated) | Result File | Status |\n")
        f.write("|-----|-----|------|-------|---------------|-------------------------|-------------|--------|\n")
        
        for result in sorted(all_results, key=lambda x: (x['source_lang'], x['target_lang'], x['line_number'])):
            source_text_truncated = result['source_text'][:50] + "..." if len(result['source_text']) > 50 else result['source_text']
            justification_truncated = result['justification'][:50] + "..." if len(result['justification']) > 50 else result['justification']
            
            f.write(f"| {result['source_lang']} | {result['target_lang']} | {result['line_number']} | "
                   f"{result['evaluation_score']} | {justification_truncated} | {source_text_truncated} | "
                   f"`data/results/{version}/{result['source_lang']}-{result['target_lang']}/test_suite_line_{result['line_number']}_result.json` | Success |\n")
    
    logger.info(f"Report generated: {report_file}")

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