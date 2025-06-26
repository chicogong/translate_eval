#!/usr/bin/env python3
"""
Single Language Pair Evaluation Script
Only handles evaluation of existing translations
"""

import os
import sys
import time
import argparse
from datetime import datetime
from pathlib import Path

# Add parent directory to path to import evaluation modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from evaluation.eval import (
    setup_logging, get_evaluation_config,
    load_translation_results, evaluate_translation, save_evaluation_result
)

def evaluate_single_pair(source_lang, target_lang, translation_run_id, eval_run_id=None, delay=1.0, max_lines=None):
    """Evaluate a single language pair's translations"""
    
    logger = setup_logging()
    
    # Generate eval_run_id if not provided
    if not eval_run_id:
        eval_run_id = datetime.now().strftime("%Y%m%d_%H%M")
    
    logger.info(f"⭐ Single Pair Evaluation: {source_lang} → {target_lang}")
    logger.info(f"📥 Translation Run ID: {translation_run_id}")
    logger.info(f"📤 Evaluation Run ID: {eval_run_id}")
    logger.info("=" * 50)
    
    # Check API configuration
    evaluation_config = get_evaluation_config()
    
    if not evaluation_config['api_key']:
        logger.error("❌ Evaluation API key not configured. Please check your .env file.")
        logger.error("Example .env content:")
        logger.error("EVALUATION_API_KEY=your_actual_key_here")
        logger.error("EVALUATION_API_URL=https://your.api.endpoint/v1/chat/completions")
        return False
    
    # Load translation results
    translation_results = load_translation_results(source_lang, target_lang, translation_run_id)
    if not translation_results:
        logger.error(f"❌ No translation results found for {source_lang}-{target_lang} run {translation_run_id}")
        logger.error(f"Please run translation first: python scripts/translate_single.py {source_lang} {target_lang}")
        return False
    
    if max_lines:
        translation_results = translation_results[:max_lines]
        logger.info(f"📝 Processing first {len(translation_results)} translations only")
    else:
        logger.info(f"📝 Processing all {len(translation_results)} translations")
    
    logger.info(f"📁 Results will be saved to run: {eval_run_id}")
    logger.info(f"⏱️  Using {delay}s delay between API calls")
    
    successful = 0
    failed = 0
    start_time = time.time()
    
    for i, translation_data in enumerate(translation_results, 1):
        line_num = translation_data['line_number']
        source_text = translation_data['source_text']
        translation = translation_data['translation']
        
        logger.info(f"\n⭐ Line {i}/{len(translation_results)} (Original Line {line_num})")
        logger.info(f"📝 Source: {source_text}")
        logger.info(f"🔄 Translation: {translation}")
        
        # Evaluation
        logger.info("⭐ Evaluating...")
        eval_result = evaluate_translation(source_lang, target_lang, source_text, translation)
        
        if eval_result["success"]:
            score = eval_result["score"]
            justification = eval_result["justification"]
            logger.info(f"⭐ Score: {score}/10")
            logger.info(f"💬 Justification: {justification}")
            successful += 1
        else:
            logger.warning(f"⚠️  Evaluation failed: {eval_result['error']}")
            score = "N/A"
            justification = f"Evaluation failed: {eval_result['error']}"
            failed += 1
        
        # Save evaluation result
        try:
            save_evaluation_result(source_lang, target_lang, line_num, source_text, 
                                 translation, score, justification, eval_run_id=eval_run_id)
            logger.info(f"💾 Evaluation saved")
        except Exception as e:
            logger.error(f"❌ Failed to save evaluation: {e}")
        
        # Progress
        elapsed = time.time() - start_time
        remaining = len(translation_results) - i
        eta_seconds = (elapsed / i) * remaining if i > 0 else 0
        eta_str = time.strftime("%H:%M:%S", time.gmtime(eta_seconds))
        logger.info(f"📈 Progress: {i}/{len(translation_results)}, Success: {successful}, Failed: {failed}, ETA: {eta_str}")
        
        # Rate limiting
        if i < len(translation_results):
            logger.info(f"⏸️  Waiting {delay}s...")
            time.sleep(delay)
    
    # Summary
    total_time = time.time() - start_time
    logger.info("\n" + "=" * 50)
    logger.info("🎉 Single Pair Evaluation Complete!")
    logger.info(f"📊 Total processed: {len(translation_results)}")
    logger.info(f"✅ Successful: {successful}")
    logger.info(f"❌ Failed: {failed}")
    logger.info(f"📈 Success rate: {successful/(successful+failed)*100:.1f}%" if (successful+failed) > 0 else "📈 Success rate: 0%")
    logger.info(f"⏱️  Total time: {time.strftime('%H:%M:%S', time.gmtime(total_time))}")
    logger.info(f"📁 Results: data/evaluations/{eval_run_id}/{source_lang}-{target_lang}/")
    
    return successful > 0

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Single Language Pair Evaluation')
    parser.add_argument('source', type=str, help='Source language code (en, zh, ja, pt, es)')
    parser.add_argument('target', type=str, help='Target language code (en, zh, ja, pt, es)')
    parser.add_argument('translation_run_id', type=str, help='Translation run ID to evaluate')
    parser.add_argument('--eval-run-id', type=str, help='Evaluation run ID (default: current datetime YYYYMMDD_HHMM)')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between API calls in seconds (default: 1.0)')
    parser.add_argument('--lines', type=int, help='Max number of lines to process (default: all)')
    
    args = parser.parse_args()
    
    # Validation
    languages = ['en', 'zh', 'ja', 'pt', 'es']
    if args.source not in languages:
        print(f"❌ Invalid source language: {args.source}. Supported: {languages}")
        return 1
    
    if args.target not in languages:
        print(f"❌ Invalid target language: {args.target}. Supported: {languages}")
        return 1
    
    if args.source == args.target:
        print("❌ Source and target languages must be different")
        return 1
    
    success = evaluate_single_pair(
        args.source, 
        args.target, 
        args.translation_run_id,
        eval_run_id=args.eval_run_id,
        delay=args.delay,
        max_lines=args.lines
    )
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 