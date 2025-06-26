#!/usr/bin/env python3
"""
TTS Service Tests
测试TTS服务的各种功能
"""

import unittest
import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'backend'))

# Import the modules to test
from backend.tts_service import TTSService
from backend.config import get_tts_config


class TestTTSService(unittest.TestCase):
    """TTS服务单元测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.tts_service = TTSService()
        
        # Mock configuration for testing
        self.mock_config = {
            'api_key': 'test_api_key',
            'group_id': 'test_group_id',
            'api_url': 'https://api.minimax.chat/v1/t2a_v2',
            'model': 'speech-01',
            'voice_setting': {
                'voice_id': 'male-qn-qingse',
                'speed': 1.0,
                'vol': 1.0,
                'pitch': 0.0
            }
        }
    
    @patch('backend.tts_service.get_tts_config')
    def test_init_with_config(self, mock_get_config):
        """测试服务初始化"""
        mock_get_config.return_value = self.mock_config
        service = TTSService()
        self.assertEqual(service.config, self.mock_config)
    
    def test_missing_credentials(self):
        """测试缺少API凭证的情况"""
        with patch.object(self.tts_service, 'config', {'api_key': '', 'group_id': ''}):
            result = self.tts_service.text_to_speech("test", "zh")
            self.assertFalse(result['success'])
            self.assertIn('credentials not found', result['error'])
    
    def test_empty_text(self):
        """测试空文本输入"""
        with patch.object(self.tts_service, 'config', self.mock_config):
            result = self.tts_service.text_to_speech("", "zh")
            self.assertFalse(result['success'])
            self.assertIn('Text is required', result['error'])
            
            result = self.tts_service.text_to_speech("   ", "zh")
            self.assertFalse(result['success'])
            self.assertIn('Text is required', result['error'])
    
    def test_text_length_limit(self):
        """测试文本长度限制"""
        long_text = "测试" * 1000  # 2000 characters
        
        with patch.object(self.tts_service, 'config', self.mock_config):
            with patch('backend.tts_service.requests.post') as mock_post:
                # Mock successful response with correct format
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.raise_for_status.return_value = None
                mock_response.json.return_value = {
                    'data': {'audio': 'base64_audio_data'},
                    'base_resp': {'status_code': 0, 'status_msg': 'success'}
                }
                mock_post.return_value = mock_response
                
                result = self.tts_service.text_to_speech(long_text, "zh")
                
                # Check that the request was made with truncated text
                call_args = mock_post.call_args
                request_data = json.loads(call_args[1]['data'].decode('utf-8'))
                self.assertEqual(len(request_data['text']), 2000)
    
    def test_language_voice_mapping(self):
        """测试语言声音映射"""
        test_cases = [
            ('zh', 'male-qn-qingse'),
            ('en', 'female-shaonv'),
            ('ja', 'female-yujie'),
            ('pt', 'female-shaonv'),
            ('es', 'female-shaonv'),
            ('unknown', 'male-qn-qingse')  # fallback
        ]
        
        with patch.object(self.tts_service, 'config', self.mock_config):
            with patch('backend.tts_service.requests.post') as mock_post:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.raise_for_status.return_value = None
                mock_response.json.return_value = {
                    'data': {'audio': 'base64_audio_data'},
                    'base_resp': {'status_code': 0, 'status_msg': 'success'}
                }
                mock_post.return_value = mock_response
                
                for language, expected_voice in test_cases:
                    result = self.tts_service.text_to_speech("测试文本", language)
                    
                    # Check the voice_id in the request
                    call_args = mock_post.call_args
                    request_data = json.loads(call_args[1]['data'].decode('utf-8'))
                    self.assertEqual(request_data['voice_setting']['voice_id'], expected_voice)
    
    @patch('backend.tts_service.requests.post')
    def test_chinese_text_encoding(self, mock_post):
        """测试中文文本编码（修复的主要问题）"""
        with patch.object(self.tts_service, 'config', self.mock_config):
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                'data': {'audio': 'base64_audio_data'},
                'base_resp': {'status_code': 0, 'status_msg': 'success'}
            }
            mock_post.return_value = mock_response
            
            chinese_text = "你好呀，这是一个测试！"
            result = self.tts_service.text_to_speech(chinese_text, "zh")
            
            # Verify the request was made
            self.assertTrue(mock_post.called)
            
            # Check that data is properly encoded as bytes
            call_args = mock_post.call_args
            request_data_bytes = call_args[1]['data']
            self.assertIsInstance(request_data_bytes, bytes)
            
            # Decode and check the content
            request_data = json.loads(request_data_bytes.decode('utf-8'))
            self.assertEqual(request_data['text'], chinese_text)
            self.assertEqual(request_data['voice_setting']['voice_id'], 'male-qn-qingse')
            
            # Check that the result is successful
            self.assertTrue(result['success'])
            self.assertEqual(result['audio_data'], 'base64_audio_data')
    
    @patch('backend.tts_service.requests.post')
    def test_japanese_text_encoding(self, mock_post):
        """测试日文文本编码"""
        with patch.object(self.tts_service, 'config', self.mock_config):
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                'data': {'audio': 'base64_audio_data'},
                'base_resp': {'status_code': 0, 'status_msg': 'success'}
            }
            mock_post.return_value = mock_response
            
            japanese_text = "こんにちは、テストです！"
            result = self.tts_service.text_to_speech(japanese_text, "ja")
            
            # Check encoding
            call_args = mock_post.call_args
            request_data_bytes = call_args[1]['data']
            self.assertIsInstance(request_data_bytes, bytes)
            
            request_data = json.loads(request_data_bytes.decode('utf-8'))
            self.assertEqual(request_data['text'], japanese_text)
            self.assertTrue(result['success'])
    
    @patch('backend.tts_service.requests.post')
    def test_api_error_handling(self, mock_post):
        """测试API错误处理"""
        with patch.object(self.tts_service, 'config', self.mock_config):
            # Test HTTP error
            mock_post.side_effect = Exception("Connection error")
            result = self.tts_service.text_to_speech("test", "en")
            self.assertFalse(result['success'])
            self.assertIn('Connection error', result['error'])
    
    @patch('backend.tts_service.requests.post')
    def test_invalid_api_response(self, mock_post):
        """测试无效API响应"""
        with patch.object(self.tts_service, 'config', self.mock_config):
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            # Invalid response format - missing data.audio or wrong status_code
            mock_response.json.return_value = {
                'error': 'Invalid request',
                'base_resp': {'status_code': 1, 'status_msg': 'error'}
            }
            mock_post.return_value = mock_response
            
            result = self.tts_service.text_to_speech("test", "en")
            self.assertFalse(result['success'])
            self.assertIn('TTS API error', result['error'])
    
    @patch('backend.tts_service.requests.post')
    def test_api_status_error(self, mock_post):
        """测试API状态错误"""
        with patch.object(self.tts_service, 'config', self.mock_config):
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            # API returned error status
            mock_response.json.return_value = {
                'data': {'audio': ''},
                'base_resp': {'status_code': 1001, 'status_msg': 'Invalid parameters'}
            }
            mock_post.return_value = mock_response
            
            result = self.tts_service.text_to_speech("test", "en")
            self.assertFalse(result['success'])
            self.assertIn('Invalid parameters', result['error'])
            self.assertIn('1001', result['error'])
    
    def test_get_supported_voices(self):
        """测试获取支持的声音列表"""
        # Test all voices
        result = self.tts_service.get_supported_voices()
        self.assertTrue(result['success'])
        self.assertIn('voices', result)
        self.assertIn('zh', result['voices'])
        self.assertIn('en', result['voices'])
        
        # Test specific language
        result = self.tts_service.get_supported_voices('zh')
        self.assertTrue(result['success'])
        self.assertIsInstance(result['voices'], list)
        self.assertTrue(len(result['voices']) > 0)
        
        # Check voice structure
        voice = result['voices'][0]
        self.assertIn('id', voice)
        self.assertIn('name', voice)
        self.assertIn('gender', voice)
    
    def test_request_headers_and_url(self):
        """测试请求头和URL构造"""
        with patch.object(self.tts_service, 'config', self.mock_config):
            with patch('backend.tts_service.requests.post') as mock_post:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.raise_for_status.return_value = None
                mock_response.json.return_value = {
                    'data': {'audio': 'base64_audio_data'},
                    'base_resp': {'status_code': 0, 'status_msg': 'success'}
                }
                mock_post.return_value = mock_response
                
                self.tts_service.text_to_speech("test", "en")
                
                # Check URL construction
                call_args = mock_post.call_args
                expected_url = f"{self.mock_config['api_url']}?GroupId={self.mock_config['group_id']}"
                self.assertEqual(call_args[0][0], expected_url)
                
                # Check headers
                headers = call_args[1]['headers']
                self.assertEqual(headers['Authorization'], f"Bearer {self.mock_config['api_key']}")
                self.assertEqual(headers['Content-Type'], 'application/json')


class TestTTSIntegration(unittest.TestCase):
    """TTS集成测试"""
    
    def test_voice_mapping_completeness(self):
        """测试声音映射的完整性"""
        from backend.config import LANGUAGES, TTS_VOICE_MAPPING
        
        # 确保所有支持的语言都有声音映射
        for lang_code in LANGUAGES.keys():
            self.assertIn(lang_code, TTS_VOICE_MAPPING, 
                         f"Language {lang_code} missing from TTS_VOICE_MAPPING")
    
    def test_config_structure(self):
        """测试配置结构"""
        config = get_tts_config()
        
        required_keys = ['api_key', 'group_id', 'api_url', 'model', 'voice_setting']
        for key in required_keys:
            self.assertIn(key, config, f"Missing required config key: {key}")
        
        # Test voice_setting structure
        voice_setting = config['voice_setting']
        voice_required_keys = ['voice_id', 'speed', 'vol', 'pitch']
        for key in voice_required_keys:
            self.assertIn(key, voice_setting, f"Missing voice_setting key: {key}")


if __name__ == '__main__':
    # Create tests directory if it doesn't exist
    tests_dir = Path(__file__).parent
    tests_dir.mkdir(exist_ok=True)
    
    # Run tests
    unittest.main(verbosity=2) 