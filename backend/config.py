import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Language mapping
LANGUAGES = {
    'en': 'English',
    'zh': '中文',
    'ja': '日本語',
    'pt': 'Português',
    'es': 'Español'
}

# Default version tag (can be overridden via env)
DEFAULT_VERSION = os.environ.get("RESULT_VERSION", "v1")

# Translation API configuration
def get_translation_config():
    """获取翻译API配置"""
    return {
        'api_key': os.environ.get('TRANSLATION_API_KEY'),
        'api_url': os.environ.get('TRANSLATION_API_URL'),
        'model': os.environ.get('TRANSLATION_MODEL'),
        'stream': os.environ.get('TRANSLATION_STREAM', 'true').lower() == 'true',
        'temperature': float(os.environ.get('TRANSLATION_TEMPERATURE', '0.0')),
        'max_length': int(os.environ.get('TRANSLATION_MAX_LENGTH', '16384')),
        'top_p': float(os.environ.get('TRANSLATION_TOP_P', '1.0')),
        'num_beams': int(os.environ.get('TRANSLATION_NUM_BEAMS', '1')),
        'do_sample': os.environ.get('TRANSLATION_DO_SAMPLE', 'false').lower() == 'true'
    }

# Evaluation API configuration
def get_evaluation_config():
    """获取评估API配置"""
    return {
        'api_key': os.environ.get('EVALUATION_API_KEY'),
        'api_url': os.environ.get('EVALUATION_API_URL'),
        'model': os.environ.get('EVALUATION_MODEL')
    }

# Flask configuration
FLASK_CONFIG = {
    'host': os.environ.get('FLASK_HOST', '127.0.0.1'),
    'port': int(os.environ.get('FLASK_PORT', 8888)),
    'debug': os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
}

# Logging configuration
LOGGING_CONFIG = {
    'level': os.environ.get('LOG_LEVEL', 'INFO').upper(),
    'file': os.environ.get('LOG_FILE', 'logs/app.log'),
    'format': os.environ.get('LOG_FORMAT', 
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d in %(funcName)s] - %(message)s'
    )
} 