#!/usr/bin/env python3
"""
Batch Operations Script
Provides comprehensive batch translation and evaluation operations
"""

import os
import sys
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_command(cmd, description):
    """Run a command and handle output"""
    print(f"\n🔄 {description}")
    print(f"💻 Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✅ Success!")
        if result.stdout:
            print(f"📤 Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"📥 Error details: {e.stderr.strip()}")
        return False

def batch_translate_all():
    """Translate all language pairs"""
    languages = ['en', 'zh', 'ja', 'pt', 'es']
    run_id = datetime.now().strftime("%Y%m%d_%H%M")
    
    print(f"🌍 Starting batch translation for all language pairs")
    print(f"📅 Run ID: {run_id}")
    print("=" * 60)
    
    success_count = 0
    total_pairs = 0
    
    for source in languages:
        for target in languages:
            if source != target:
                total_pairs += 1
                cmd = [
                    sys.executable, 'scripts/translate_single.py',
                    source, target,
                    '--run-id', run_id,
                    '--lines', '5',  # Limit to 5 lines for demo
                    '--delay', '0.5'
                ]
                
                if run_command(cmd, f"Translating {source} → {target}"):
                    success_count += 1
    
    print("\n" + "=" * 60)
    print(f"🎉 Batch Translation Complete!")
    print(f"✅ Successful: {success_count}/{total_pairs}")
    print(f"📁 Results saved to: data/translations/{run_id}/")
    
    return run_id if success_count > 0 else None

def batch_evaluate_all(translation_run_id):
    """Evaluate all translated language pairs"""
    languages = ['en', 'zh', 'ja', 'pt', 'es']
    eval_run_id = datetime.now().strftime("%Y%m%d_%H%M")
    
    print(f"⭐ Starting batch evaluation for all language pairs")
    print(f"📥 Translation Run ID: {translation_run_id}")
    print(f"📤 Evaluation Run ID: {eval_run_id}")
    print("=" * 60)
    
    success_count = 0
    total_pairs = 0
    
    for source in languages:
        for target in languages:
            if source != target:
                # Check if translation exists
                translation_dir = Path(f"data/translations/{translation_run_id}/{source}-{target}")
                if not translation_dir.exists():
                    print(f"⚠️  Skipping {source} → {target} (no translation found)")
                    continue
                
                total_pairs += 1
                cmd = [
                    sys.executable, 'scripts/evaluate_single.py',
                    source, target, translation_run_id,
                    '--eval-run-id', eval_run_id,
                    '--delay', '0.5'
                ]
                
                if run_command(cmd, f"Evaluating {source} → {target}"):
                    success_count += 1
    
    print("\n" + "=" * 60)
    print(f"🎉 Batch Evaluation Complete!")
    print(f"✅ Successful: {success_count}/{total_pairs}")
    print(f"📁 Results saved to: data/evaluations/{eval_run_id}/")
    
    return eval_run_id if success_count > 0 else None

def translate_single_pair(source, target, lines=15):
    """Translate a single language pair"""
    run_id = datetime.now().strftime("%Y%m%d_%H%M")
    
    cmd = [
        sys.executable, 'scripts/translate_single.py',
        source, target,
        '--run-id', run_id,
        '--lines', str(lines)
    ]
    
    if run_command(cmd, f"Translating {source} → {target}"):
        return run_id
    return None

def evaluate_single_pair(source, target, translation_run_id):
    """Evaluate a single language pair"""
    eval_run_id = datetime.now().strftime("%Y%m%d_%H%M")
    
    cmd = [
        sys.executable, 'scripts/evaluate_single.py',
        source, target, translation_run_id,
        '--eval-run-id', eval_run_id
    ]
    
    if run_command(cmd, f"Evaluating {source} → {target}"):
        return eval_run_id
    return None

def start_web_interface():
    """Start the web interface"""
    print("\n🌐 Starting web interface...")
    cmd = [sys.executable, 'run_app.py']
    
    try:
        subprocess.Popen(cmd)
        print("✅ Web interface started!")
        print("🔗 Visit: http://localhost:8888")
        print("📊 Batch Dashboard: http://localhost:8888/batch")
    except Exception as e:
        print(f"❌ Error starting web interface: {e}")

def main():
    parser = argparse.ArgumentParser(description='Batch Translation and Evaluation Operations')
    parser.add_argument('operation', choices=[
        'translate-all', 'evaluate-all', 'full-pipeline',
        'translate-single', 'evaluate-single', 'web'
    ], help='Operation to perform')
    
    parser.add_argument('--source', type=str, help='Source language (for single operations)')
    parser.add_argument('--target', type=str, help='Target language (for single operations)')
    parser.add_argument('--translation-run-id', type=str, help='Translation run ID (for evaluation)')
    parser.add_argument('--lines', type=int, default=15, help='Number of lines to process')
    
    args = parser.parse_args()
    
    print("🚀 Batch Operations Script")
    print("=" * 60)
    
    if args.operation == 'translate-all':
        batch_translate_all()
    
    elif args.operation == 'evaluate-all':
        if not args.translation_run_id:
            print("❌ Error: --translation-run-id is required for evaluate-all")
            return 1
        batch_evaluate_all(args.translation_run_id)
    
    elif args.operation == 'full-pipeline':
        print("🔄 Running full pipeline: translate → evaluate → web")
        translation_run_id = batch_translate_all()
        if translation_run_id:
            eval_run_id = batch_evaluate_all(translation_run_id)
            if eval_run_id:
                start_web_interface()
        else:
            print("❌ Translation failed, stopping pipeline")
            return 1
    
    elif args.operation == 'translate-single':
        if not args.source or not args.target:
            print("❌ Error: --source and --target are required for translate-single")
            return 1
        translate_single_pair(args.source, args.target, args.lines)
    
    elif args.operation == 'evaluate-single':
        if not args.source or not args.target or not args.translation_run_id:
            print("❌ Error: --source, --target, and --translation-run-id are required")
            return 1
        evaluate_single_pair(args.source, args.target, args.translation_run_id)
    
    elif args.operation == 'web':
        start_web_interface()
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 