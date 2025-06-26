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

# MiniMax TTS configuration
def get_tts_config():
    """获取MiniMax TTS API配置"""
    return {
        'api_key': os.environ.get('MINIMAX_API_KEY'),
        'group_id': os.environ.get('MINIMAX_GROUP_ID'),
        'api_url': 'https://api.minimax.chat/v1/t2a_v2',
        'model': 'speech-01-turbo',
        'voice_setting': {
            'voice_id': 'male-qn-qingse',  # 默认声音
            'speed': 1.0,
            'vol': 1.0,
            'pitch': 0
        }
    }

# Language to voice mapping for MiniMax TTS
TTS_VOICE_MAPPING = {
    'en': 'female-shaonv',  # 英文女声
    'zh': 'male-qn-qingse',  # 中文男声
    'ja': 'female-yujie',   # 日文女声
    'pt': 'female-shaonv',  # 葡萄牙语使用英文声音
    'es': 'female-shaonv'   # 西班牙语使用英文声音
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