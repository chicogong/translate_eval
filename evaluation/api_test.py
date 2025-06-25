#!/usr/bin/env python3
"""
API连接测试脚本
"""

import os
import json
import requests
import logging
from pathlib import Path
from dotenv import load_dotenv

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent

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
    log_file = log_dir / 'api_test.log'
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

def get_translation_config():
    """获取翻译API配置"""
    config = {
        'api_key': os.environ.get('TRANSLATION_API_KEY'),
        'api_url': os.environ.get('TRANSLATION_API_URL'),
        'model': os.environ.get('TRANSLATION_MODEL')
    }
    
    if not config['api_key']:
        logger.error("Translation API key not found in environment variables")
    
    logger.debug(f"Translation API config loaded: url={config['api_url']}, model={config['model']}")
    return config

def get_evaluation_config():
    """获取评估API配置"""
    config = {
        'api_key': os.environ.get('EVALUATION_API_KEY'),
        'api_url': os.environ.get('EVALUATION_API_URL'),
        'model': os.environ.get('EVALUATION_MODEL')
    }
    
    if not config['api_key']:
        logger.error("Evaluation API key not found in environment variables")
    
    logger.debug(f"Evaluation API config loaded: url={config['api_url']}, model={config['model']}")
    return config

def test_translation_api():
    """测试翻译API"""
    logger.info("Testing translation API")
    
    config = get_translation_config()
    if not config['api_key']:
        logger.error("Could not find TRANSLATION_API_KEY in the .env file.")
        logger.error("Please ensure your .env file is set up correctly.")
        return False

    logger.info(f"Using API key: ...{config['api_key'][-8:]}")  # Print last few chars of key for verification

    # Test translation
    payload = {
        'model': config['model'],
        'messages': [
            {
                'role': 'system',
                'content': 'You are a helpful assistant for translation.'
            },
            {
                'role': 'user',
                'content': 'Translate "Hello, world!" to Chinese.'
            }
        ]
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {config["api_key"]}'
    }

    logger.info(f"Target URL: {config['api_url']}")
    logger.info(f"Translation Model: {config['model']}")
    logger.info("Sending translation request...")

    try:
        response = requests.post(config['api_url'], headers=headers, data=json.dumps(payload), timeout=30)
        
        logger.info(f"Response Status Code: {response.status_code}")

        # Check if the response was successful
        if response.status_code == 200:
            logger.info("✅ Translation API test successful!")
            response_data = response.json()
            if "choices" in response_data and response_data["choices"]:
                translation = response_data["choices"][0]["message"]["content"]
                logger.info(f"Translation result: {translation}")
            else:
                logger.warning("Response format unexpected")
            return True
        else:
            logger.error("❌ Translation API test failed!")
            try:
                error_data = response.json()
                logger.error(f"Error response: {json.dumps(error_data, indent=2)}")
            except json.JSONDecodeError:
                logger.error(f"Raw error response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Network error during translation test: {e}")
        return False

def test_evaluation_api():
    """测试评估API"""
    logger.info("Testing evaluation API")
    
    config = get_evaluation_config()
    if not config['api_key']:
        logger.error("Evaluation API key not available")
        return False

    # Test evaluation
    payload = {
        'model': config['model'],
        'messages': [
            {
                'role': 'user',
                'content': '''Please evaluate this translation from English to Chinese:
Source: "Hello, world!"
Translation: "你好，世界！"

Rate the translation quality from 1-10 and provide justification.
Format your response as:
SCORE: [number]
JUSTIFICATION: [your analysis]'''
            }
        ]
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {config["api_key"]}'
    }

    logger.info(f"Evaluation Model: {config['model']}")
    logger.info("Sending evaluation request...")

    try:
        response = requests.post(config['api_url'], headers=headers, data=json.dumps(payload), timeout=30)
        
        logger.info(f"Response Status Code: {response.status_code}")

        # Check if the response was successful
        if response.status_code == 200:
            logger.info("✅ Evaluation API test successful!")
            response_data = response.json()
            if "choices" in response_data and response_data["choices"]:
                evaluation = response_data["choices"][0]["message"]["content"]
                logger.info(f"Evaluation result: {evaluation}")
            else:
                logger.warning("Response format unexpected")
            return True
        else:
            logger.error("❌ Evaluation API test failed!")
            try:
                error_data = response.json()
                logger.error(f"Error response: {json.dumps(error_data, indent=2)}")
            except json.JSONDecodeError:
                logger.error(f"Raw error response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Network error during evaluation test: {e}")
        return False

def main():
    """主函数"""
    logger.info("🧪 API Connection Test")
    logger.info("=" * 50)
    
    # Test both APIs
    translation_success = test_translation_api()
    logger.info("-" * 30)
    evaluation_success = test_evaluation_api()
    
    logger.info("=" * 50)
    if translation_success and evaluation_success:
        logger.info("🎉 All API tests passed!")
        return 0
    else:
        logger.error("❌ Some API tests failed!")
        if not translation_success:
            logger.error("- Translation API test failed")
        if not evaluation_success:
            logger.error("- Evaluation API test failed")
        return 1

if __name__ == "__main__":
    exit(main()) 