#!/usr/bin/env python3
"""
Test runner for Translation Evaluation Tool
运行翻译评估工具的测试套件
"""

import sys
import unittest
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'backend'))

def run_all_tests():
    """运行所有测试"""
    print("🚀 Starting Translation Evaluation Tool Test Suite...")
    print("=" * 60)
    
    # Discover and run tests
    loader = unittest.TestLoader()
    suite = loader.discover(str(project_root / 'tests'), pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        return False

def run_tts_tests():
    """只运行TTS相关测试"""
    print("🎵 Running TTS Service Tests...")
    print("-" * 40)
    
    # Import and run TTS tests specifically
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName('tests.test_tts_service')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_multi_model_tests():
    """只运行多模型翻译测试"""
    print("🤖 Running Multi-Model Translation Tests...")
    print("-" * 40)
    
    # Import and run multi-model tests specifically
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName('tests.test_multi_model_service')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def test_encoding_fix():
    """测试编码修复"""
    print("🔧 Testing encoding fix...")
    
    try:
        # Test Chinese text encoding
        import json
        chinese_text = "你好呀，这是一个测试！"
        
        request_data = {
            "text": chinese_text,
            "language": "zh"
        }
        
        # Test UTF-8 encoding
        json_bytes = json.dumps(request_data, ensure_ascii=False).encode('utf-8')
        decoded_data = json.loads(json_bytes.decode('utf-8'))
        
        if decoded_data['text'] == chinese_text:
            print("  ✅ UTF-8 encoding test passed")
            return True
        else:
            print("  ❌ UTF-8 encoding test failed")
            return False
            
    except Exception as e:
        print(f"  ❌ Encoding test error: {e}")
        return False

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run tests for Translation Evaluation Tool')
    parser.add_argument('--tts-only', action='store_true', help='Run only TTS tests')
    parser.add_argument('--multi-model-only', action='store_true', help='Run only multi-model translation tests')
    parser.add_argument('--encoding-only', action='store_true', help='Run only encoding tests')
    
    args = parser.parse_args()
    
    success = True
    
    if args.encoding_only:
        success = test_encoding_fix()
    elif args.tts_only:
        success = run_tts_tests()
    elif args.multi_model_only:
        success = run_multi_model_tests()
    else:
        # Run encoding test first
        if not test_encoding_fix():
            success = False
        
        # Then run all tests
        if not run_all_tests():
            success = False
    
    sys.exit(0 if success else 1) 