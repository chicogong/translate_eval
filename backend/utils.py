"""
Utility functions and logging setup
"""

import logging
from pathlib import Path
from config import LOGGING_CONFIG
from langdetect import detect

def setup_logging():
    """配置日志系统"""
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, LOGGING_CONFIG['level']),
        format=LOGGING_CONFIG['format'],
        handlers=[
            logging.FileHandler(LOGGING_CONFIG['file'], encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def format_run_id(run_id: str) -> str:
    """格式化运行ID为可读格式"""
    # Convert YYYYMMDD_HHMM to readable format
    import re
    if re.match(r'^\d{8}_\d{4}$', run_id):
        date = run_id[:8]
        time = run_id[9:]
        year = date[:4]
        month = date[4:6]
        day = date[6:8]
        hour = time[:2]
        minute = time[2:4]
        
        return f"{year}-{month}-{day} {hour}:{minute}"
    return run_id

def escape_html(text: str) -> str:
    """转义HTML字符"""
    if not text:
        return ''
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#039;'))

def validate_language_pair(source_lang: str, target_lang: str) -> tuple[bool, str]:
    """验证语言对"""
    from config import LANGUAGES
    
    if not source_lang or not target_lang:
        return False, "Source and target languages are required"
    
    if source_lang not in LANGUAGES:
        return False, f"Unsupported source language: {source_lang}"
    
    if target_lang not in LANGUAGES:
        return False, f"Unsupported target language: {target_lang}"
    
    if source_lang == target_lang:
        return False, "Source and target languages must be different"
    
    return True, ""

LANG_MAP = {
    'zh-cn': 'zh',
    'zh-tw': 'zh',
    'zh': 'zh',
    'en': 'en',
    'ja': 'ja',
    'es': 'es',
    'pt': 'pt'
}

def detect_language(text: str) -> str:
    """自动检测文本语言，返回简化语言代码(zh,en,ja,es,pt)"""
    try:
        lang_code = detect(text)
        return LANG_MAP.get(lang_code, lang_code)
    except Exception:
        return 'en' 