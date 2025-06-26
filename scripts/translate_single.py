#!/usr/bin/env python3
"""
Single Language Pair Translation Script
Only handles translation, not evaluation
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
    setup_logging, get_translation_config,
    load_test_cases, translate_text, save_translation_result
)

def translate_single_pair(source_lang, target_lang, run_id=None, delay=1.0, max_lines=None):
    """Translate a single language pair"""
    
    logger = setup_logging()
    
    # Generate run_id if not provided
    if not run_id:
        run_id = datetime.now().strftime("%Y%m%d_%H%M")
    
    logger.info(f"🔄 Single Pair Translation: {source_lang} → {target_lang}")
    logger.info(f"📅 Run ID: {run_id}")
    logger.info("=" * 50)
    
    # Check API configuration
    translation_config = get_translation_config()
    
    if not translation_config['api_key']:
        logger.error("❌ Translation API key not configured. Please check your .env file.")
        logger.error("Example .env content:")
        logger.error("TRANSLATION_API_KEY=your_actual_key_here")
        logger.error("TRANSLATION_API_URL=https://your.api.endpoint/v1/chat/completions")
        return False
    
    # Load test cases
    test_cases = load_test_cases(source_lang)
    if not test_cases:
        logger.error(f"❌ No test cases found for {source_lang}")
        logger.error(f"Please run: python data/setup_testcases.py")
        return False
    
    if max_lines:
        test_cases = test_cases[:max_lines]
        logger.info(f"📝 Processing first {len(test_cases)} lines only")
    else:
        logger.info(f"📝 Processing all {len(test_cases)} test cases")
    
    logger.info(f"📁 Results will be saved to run: {run_id}")
    logger.info(f"⏱️  Using {delay}s delay between API calls")
    
    successful = 0
    failed = 0
    start_time = time.time()
    
    for line_num, source_text in enumerate(test_cases, 1):
        logger.info(f"\n🔄 Line {line_num}/{len(test_cases)}")
        logger.info(f"📝 Source: {source_text}")
        
        # Translation
        logger.info("🔄 Translating...")
        translation_result = translate_text(source_lang, target_lang, source_text)
        
        if not translation_result["success"]:
            logger.error(f"❌ Translation failed: {translation_result['error']}")
            failed += 1
            continue
        
        translation = translation_result["translation"]
        logger.info(f"✅ Translation: {translation}")
        successful += 1
        
        # Save translation result
        try:
            save_translation_result(source_lang, target_lang, line_num, source_text, 
                                  translation, run_id=run_id)
            logger.info(f"💾 Translation saved")
        except Exception as e:
            logger.error(f"❌ Failed to save translation: {e}")
        
        # Progress
        elapsed = time.time() - start_time
        remaining = len(test_cases) - line_num
        eta_seconds = (elapsed / line_num) * remaining if line_num > 0 else 0
        eta_str = time.strftime("%H:%M:%S", time.gmtime(eta_seconds))
        logger.info(f"📈 Progress: {line_num}/{len(test_cases)}, Success: {successful}, Failed: {failed}, ETA: {eta_str}")
        
        # Rate limiting
        if line_num < len(test_cases):
            logger.info(f"⏸️  Waiting {delay}s...")
            time.sleep(delay)
    
    # Summary
    total_time = time.time() - start_time
    logger.info("\n" + "=" * 50)
    logger.info("🎉 Single Pair Translation Complete!")
    logger.info(f"📊 Total processed: {len(test_cases)}")
    logger.info(f"✅ Successful: {successful}")
    logger.info(f"❌ Failed: {failed}")
    logger.info(f"📈 Success rate: {successful/(successful+failed)*100:.1f}%" if (successful+failed) > 0 else "📈 Success rate: 0%")
    logger.info(f"⏱️  Total time: {time.strftime('%H:%M:%S', time.gmtime(total_time))}")
    logger.info(f"📁 Results: data/translations/{run_id}/{source_lang}-{target_lang}/")
    
    return successful > 0

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Single Language Pair Translation')
    parser.add_argument('source', type=str, help='Source language code (en, zh, ja, pt, es)')
    parser.add_argument('target', type=str, help='Target language code (en, zh, ja, pt, es)')
    parser.add_argument('--run-id', type=str, help='Run ID (default: current datetime YYYYMMDD_HHMM)')
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
    
    success = translate_single_pair(
        args.source, 
        args.target, 
        run_id=args.run_id,
        delay=args.delay,
        max_lines=args.lines
    )
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 