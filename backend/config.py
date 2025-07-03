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
    'es': 'Español',
    'ko': '한국어'
}

# Default version tag (can be overridden via env)
DEFAULT_VERSION = os.environ.get("RESULT_VERSION", "v1")

# Translation API configuration (single model, backward compatible)
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

# Multi-model translation configuration
def get_multi_translation_configs():
    """获取多个翻译API配置，最多支持9个模型"""
    configs = {}
    
    # Load up to 9 model configurations
    for i in range(1, 9):
        api_key = os.environ.get(f'TRANSLATION_API_KEY_{i}')
        api_url = os.environ.get(f'TRANSLATION_API_URL_{i}')
        model = os.environ.get(f'TRANSLATION_MODEL_{i}')
        model_name = os.environ.get(f'TRANSLATION_MODEL_NAME_{i}')
        
        # Skip if any required config is missing
        if not all([api_key, api_url, model]):
            continue
            
        # Use model name if provided, otherwise use model ID
        display_name = model_name if model_name else model
        
        configs[f'model_{i}'] = {
            'id': f'model_{i}',
            'name': display_name,
            'api_key': api_key,
            'api_url': api_url,
            'model': model,
            'stream': os.environ.get(f'TRANSLATION_STREAM_{i}', 'true').lower() == 'true',
            'temperature': float(os.environ.get(f'TRANSLATION_TEMPERATURE_{i}', '0.0')),
            'max_length': int(os.environ.get(f'TRANSLATION_MAX_LENGTH_{i}', '16384')),
            'top_p': float(os.environ.get(f'TRANSLATION_TOP_P_{i}', '1.0')),
            'num_beams': int(os.environ.get(f'TRANSLATION_NUM_BEAMS_{i}', '1')),
            'do_sample': os.environ.get(f'TRANSLATION_DO_SAMPLE_{i}', 'false').lower() == 'true'
        }
    
    # Fallback to single model config if no multi-model configs found
    if not configs:
        single_config = get_translation_config()
        if single_config['api_key'] and single_config['api_url'] and single_config['model']:
            configs['model_1'] = {
                'id': 'model_1',
                'name': single_config['model'],
                **single_config
            }
    
    return configs

# Evaluation API configuration
def get_evaluation_config():
    """获取评估API配置"""
    return {
        'api_key': os.environ.get('EVALUATION_API_KEY'),
        'api_url': os.environ.get('EVALUATION_API_URL'),
        'model': os.environ.get('EVALUATION_MODEL')
    }

# Multi-evaluator configuration
def get_multi_evaluation_configs():
    """获取多个评估API配置，最多支持2个评估模型"""
    configs = {}
    
    # Primary evaluator (backward compatible)
    primary_config = get_evaluation_config()
    if primary_config['api_key'] and primary_config['api_url'] and primary_config['model']:
        display_name = os.environ.get('EVALUATION_MODEL_NAME', primary_config['model'])
        configs['evaluator_1'] = {
            'id': 'evaluator_1',
            'name': display_name,
            **primary_config
        }
    
    # Secondary evaluator
    api_key_2 = os.environ.get('EVALUATION_API_KEY_2')
    api_url_2 = os.environ.get('EVALUATION_API_URL_2')
    model_2 = os.environ.get('EVALUATION_MODEL_2')
    
    if api_key_2 and api_url_2 and model_2:
        display_name_2 = os.environ.get('EVALUATION_MODEL_NAME_2', model_2)
        configs['evaluator_2'] = {
            'id': 'evaluator_2',
            'name': display_name_2,
            'api_key': api_key_2,
            'api_url': api_url_2,
            'model': model_2
        }
    
    return configs

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
    'es': 'female-shaonv',   # 西班牙语使用英文声音
    'ko': 'female-shaonv'  # 韩语暂用英文女声
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