#!/usr/bin/env python3
"""
Quick Start Script for Translation Evaluation Tool
Provides an interactive guide for new users
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header():
    print("🚀 Translation Evaluation Tool - Quick Start")
    print("=" * 60)
    print("Welcome! This script will help you get started quickly.")
    print()

def check_requirements():
    print("📋 Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Check if requirements are installed
    try:
        import flask
        import requests
        import python_dotenv
        print("✅ Required packages installed")
    except ImportError as e:
        print(f"❌ Missing package: {e.name}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    return True

def check_env_file():
    print("\n🔧 Checking environment configuration...")
    
    if not os.path.exists('.env'):
        print("⚠️  .env file not found")
        print("   Please copy .env.example to .env and configure your API keys")
        return False
    
    # Check if API keys are configured
    from dotenv import load_dotenv
    load_dotenv()
    
    translation_key = os.getenv('TRANSLATION_API_KEY')
    evaluation_key = os.getenv('EVALUATION_API_KEY')
    
    if not translation_key or translation_key == 'your_actual_api_key_here':
        print("⚠️  Translation API key not configured")
        return False
    
    if not evaluation_key or evaluation_key == 'your_actual_api_key_here':
        print("⚠️  Evaluation API key not configured")
        return False
    
    print("✅ Environment configuration looks good")
    return True

def setup_test_data():
    print("\n📁 Setting up test data...")
    
    if not os.path.exists('data/testcases/en/test_suite.txt'):
        print("   Generating test cases...")
        try:
            subprocess.run([sys.executable, 'data/setup_testcases.py'], check=True)
            print("✅ Test cases generated")
        except subprocess.CalledProcessError:
            print("❌ Failed to generate test cases")
            return False
    else:
        print("✅ Test cases already exist")
    
    return True

def run_demo_translation():
    print("\n🔄 Running demo translation...")
    
    try:
        cmd = [
            sys.executable, 'scripts/translate_single.py',
            'en', 'zh', '--lines', '2'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Extract run ID from output
        run_id = None
        for line in result.stdout.split('\n'):
            if 'Run ID:' in line:
                run_id = line.split('Run ID:')[1].strip()
                break
        
        if run_id:
            print(f"✅ Demo translation completed (Run ID: {run_id})")
            return run_id
        else:
            print("⚠️  Translation completed but couldn't extract run ID")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Demo translation failed: {e}")
        return None

def run_demo_evaluation(translation_run_id):
    print("\n⭐ Running demo evaluation...")
    
    try:
        cmd = [
            sys.executable, 'scripts/evaluate_single.py',
            'en', 'zh', translation_run_id
        ]
        subprocess.run(cmd, check=True)
        print("✅ Demo evaluation completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Demo evaluation failed: {e}")
        return False

def start_web_interface():
    print("\n🌐 Starting web interface...")
    
    try:
        # Start in background
        subprocess.Popen([sys.executable, 'run_app.py'])
        print("✅ Web interface started!")
        print()
        print("🔗 Access the application:")
        print("   • Main Interface: http://localhost:8888")
        print("   • Batch Dashboard: http://localhost:8888/batch")
        print()
        return True
    except Exception as e:
        print(f"❌ Failed to start web interface: {e}")
        return False

def show_next_steps():
    print("🎯 Next Steps:")
    print("   1. Visit http://localhost:8888/batch to see the evaluation results")
    print("   2. Try the 'View Sample Data' button to see demo results")
    print("   3. Use the batch operation buttons to run more translations")
    print("   4. Explore the main interface at http://localhost:8888")
    print()
    print("📚 Useful Commands:")
    print("   • python scripts/batch_operations.py full-pipeline")
    print("   • python scripts/translate_single.py en zh --lines 5")
    print("   • python scripts/cleanup.py")
    print()
    print("🆘 Need Help?")
    print("   • Check README.md for detailed documentation")
    print("   • Review the troubleshooting section")
    print("   • Ensure your API keys are properly configured")

def main():
    print_header()
    
    # Step 1: Check requirements
    if not check_requirements():
        print("\n❌ Requirements check failed. Please fix the issues above.")
        return 1
    
    # Step 2: Check environment
    if not check_env_file():
        print("\n❌ Environment check failed. Please configure your .env file.")
        return 1
    
    # Step 3: Setup test data
    if not setup_test_data():
        print("\n❌ Test data setup failed.")
        return 1
    
    # Ask user if they want to run demo
    print("\n🤔 Would you like to run a quick demo? (y/n): ", end="")
    response = input().strip().lower()
    
    if response in ['y', 'yes']:
        # Step 4: Run demo translation
        translation_run_id = run_demo_translation()
        
        if translation_run_id:
            # Step 5: Run demo evaluation
            run_demo_evaluation(translation_run_id)
    
    # Step 6: Start web interface
    start_web_interface()
    
    # Step 7: Show next steps
    print()
    show_next_steps()
    
    print("\n🎉 Quick start completed! Enjoy using the Translation Evaluation Tool!")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 