"""
Hunyuan Translation Service
混元翻译服务的独立实现
"""

import json
import requests
import logging
import time
from typing import Dict

logger = logging.getLogger(__name__)

class HunyuanTranslationService:
    """混元翻译服务"""
    
    @staticmethod
    def is_hunyuan_model(config: Dict) -> bool:
        """检查是否为混元翻译模型"""
        return (
            'hunyuan' in config.get('model', '').lower() or
            'hunyuanapi.woa.com' in config.get('api_url', '')
        )
    
    @staticmethod
    def translate(config: Dict, source_lang: str, target_lang: str, text: str) -> Dict:
        """混元翻译方法"""
        try:
            # 混元翻译的特殊请求格式
            cur_time = int(time.time())
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {config['api_key']}",
                "X-TC-Action": "ChatTranslations",
                "X-TC-Version": "2023-09-01",
                "X-TC-Timestamp": str(cur_time)
            }
            
            # 语言代码映射
            lang_mapping = {
                'zh': 'zh-CN',
                'en': 'en',
                'ja': 'ja',
                'ko': 'ko',
                'fr': 'fr',
                'de': 'de',
                'es': 'es',
                'pt': 'pt',
                'ru': 'ru',
                'it': 'it'
            }
            
            target_lang_code = lang_mapping.get(target_lang, target_lang)
            
            payload = {
                "model": config['model'],
                "target": target_lang_code,
                "text": text,
                "stream": False,
                "moderation": config.get('moderation', False)  # 默认关闭审核以提高速度
            }
            
            logger.debug(f"Hunyuan translation request: {json.dumps(payload, ensure_ascii=False)}")
            
            response = requests.post(
                config['api_url'],
                headers=headers,
                data=json.dumps(payload),
                timeout=60
            )
            response.raise_for_status()
            response_data = response.json()
            
            logger.debug(f"Hunyuan translation response: {json.dumps(response_data, ensure_ascii=False)}")
            
            # 解析混元翻译的响应格式
            if "choices" in response_data and response_data["choices"]:
                choice = response_data["choices"][0]
                if "message" in choice and "content" in choice["message"]:
                    translation = choice["message"]["content"]
                    return {
                        "success": True,
                        "translation": translation,
                        "model_name": config['name'],
                        "model_id": config['id']
                    }
            
            return {
                "success": False,
                "error": "Invalid Hunyuan translation response format",
                "model_name": config['name'],
                "model_id": config['id']
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Hunyuan translation request failed: {str(e)}",
                "model_name": config['name'],
                "model_id": config['id']
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Hunyuan translation error: {str(e)}",
                "model_name": config['name'],
                "model_id": config['id']
            } 