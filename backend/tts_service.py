"""
MiniMax Text-to-Speech Service
"""

import requests
import json
import logging
import base64
from typing import Optional, Dict
from config import get_tts_config, TTS_VOICE_MAPPING

logger = logging.getLogger(__name__)

class TTSService:
    """MiniMax文字转语音服务"""
    
    def __init__(self):
        self.config = get_tts_config()
    
    def text_to_speech(self, text: str, language: str = 'zh') -> Dict:
        """
        将文字转换为语音
        
        Args:
            text: 要转换的文字
            language: 语言代码 (en, zh, ja, pt, es)
            
        Returns:
            dict: 包含success状态、音频数据和耗时信息的字典
        """
        logger.info(f"Starting TTS conversion: language={language}, text_length={len(text)}")
        
        if not self.config['api_key'] or not self.config['group_id']:
            logger.error("MiniMax API key or Group ID not available")
            return {"success": False, "error": "MiniMax API credentials not found"}
        
        if not text or len(text.strip()) == 0:
            logger.warning("Empty text provided for TTS")
            return {"success": False, "error": "Text is required"}
        
        # 限制文本长度（MiniMax限制）
        if len(text) > 2000:
            logger.warning(f"Text too long ({len(text)} chars), truncating to 2000")
            text = text[:2000]
        
        try:
            # 根据语言选择合适的声音
            voice_id = TTS_VOICE_MAPPING.get(language, 'male-qn-qingse')
            
            # 准备请求数据
            request_data = {
                "model": self.config['model'],
                "text": text,
                "stream": False,
                "voice_setting": {
                    "voice_id": voice_id,
                    "speed": self.config['voice_setting']['speed'],
                    "vol": self.config['voice_setting']['vol'],
                    "pitch": self.config['voice_setting']['pitch']
                },
                "audio_setting": {
                    "sample_rate": 32000,
                    "bitrate": 128000,
                    "format": "mp3"
                }
            }
            
            headers = {
                'Authorization': f'Bearer {self.config["api_key"]}',
                'Content-Type': 'application/json'
            }
            
            # 添加Group ID到URL参数
            url = f"{self.config['api_url']}?GroupId={self.config['group_id']}"
            
            logger.info(f"TTS API Request: {url} | Data: {json.dumps(request_data, ensure_ascii=False)}")
            
            response = requests.post(
                url,
                headers=headers,
                data=json.dumps(request_data, ensure_ascii=False).encode('utf-8'),
                timeout=30
            )
            
            response.raise_for_status()
            response_data = response.json()
            
            logger.info(f"TTS API Response: status={response.status_code} | data={json.dumps(response_data, ensure_ascii=False)}")
            
            # 检查响应格式
            # MiniMax API 返回格式: {"data": {"audio": "base64_data"}, "base_resp": {"status_code": 0}}
            if ('data' in response_data and 
                'audio' in response_data['data'] and 
                'base_resp' in response_data and 
                response_data['base_resp'].get('status_code') == 0):
                
                audio_base64 = response_data['data']['audio']
                logger.info(f"TTS conversion successful, audio data length: {len(audio_base64)}")
                
                return {
                    "success": True,
                    "audio_data": audio_base64,
                    "format": "mp3",
                    "voice_id": voice_id,
                    "text_length": len(text)
                }
            else:
                # 记录详细的错误信息
                status_code = response_data.get('base_resp', {}).get('status_code', 'unknown')
                status_msg = response_data.get('base_resp', {}).get('status_msg', 'unknown')
                logger.error(f"TTS API error - status_code: {status_code}, status_msg: {status_msg}")
                logger.error(f"Full response: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
                return {
                    "success": False, 
                    "error": f"TTS API error: {status_msg} (code: {status_code})"
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"TTS API request failed: {e}")
            return {
                "success": False, 
                "error": f"API request failed: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error during TTS conversion: {e}")
            return {
                "success": False, 
                "error": f"Unexpected error: {str(e)}"
            }
    
    def get_supported_voices(self, language: str = None) -> Dict:
        """
        获取支持的声音列表
        
        Args:
            language: 可选的语言过滤
            
        Returns:
            dict: 支持的声音信息
        """
        voices = {
            'zh': [
                {'id': 'male-qn-qingse', 'name': '青涩青年男声', 'gender': 'male'},
                {'id': 'female-shaonv', 'name': '少女女声', 'gender': 'female'},
                {'id': 'male-qn-jingying', 'name': '精英男声', 'gender': 'male'},
                {'id': 'female-yujie', 'name': '御姐女声', 'gender': 'female'}
            ],
            'en': [
                {'id': 'female-shaonv', 'name': 'Young Female', 'gender': 'female'},
                {'id': 'male-qn-qingse', 'name': 'Young Male', 'gender': 'male'}
            ],
            'ja': [
                {'id': 'female-yujie', 'name': 'Japanese Female', 'gender': 'female'},
                {'id': 'male-qn-qingse', 'name': 'Japanese Male', 'gender': 'male'}
            ],
            'ko': [
                {'id': 'female-shaonv', 'name': 'Korean Female (placeholder)', 'gender': 'female'},
                {'id': 'male-qn-qingse', 'name': 'Korean Male (placeholder)', 'gender': 'male'}
            ]
        }
        
        if language and language in voices:
            return {"success": True, "voices": voices[language]}
        
        return {"success": True, "voices": voices} 