#!/usr/bin/env python3
"""
Multi-Model Translation Service Tests
测试多模型翻译服务的各种功能
"""

import unittest
import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'backend'))

# Import the modules to test
from backend.services import MultiModelTranslationService
from backend.config import get_multi_translation_configs


class TestMultiModelTranslationService(unittest.TestCase):
    """多模型翻译服务单元测试"""
    
    def setUp(self):
        """设置测试环境"""
        # Mock configuration for testing
        self.mock_configs = {
            'model_1': {
                'id': 'model_1',
                'name': 'Test Model 1',
                'api_key': 'test_api_key_1',
                'api_url': 'https://api.test1.com/v1/chat/completions',
                'model': 'test-model-1',
                'stream': False,
                'temperature': 0.0,
                'max_length': 16384,
                'top_p': 1.0,
                'num_beams': 1,
                'do_sample': False
            },
            'model_2': {
                'id': 'model_2',
                'name': 'Test Model 2',
                'api_key': 'test_api_key_2',
                'api_url': 'https://api.test2.com/v1/chat/completions',
                'model': 'test-model-2',
                'stream': False,
                'temperature': 0.0,
                'max_length': 16384,
                'top_p': 1.0,
                'num_beams': 1,
                'do_sample': False
            },
            'model_3': {
                'id': 'model_3',
                'name': 'Test Model 3',
                'api_key': 'test_api_key_3',
                'api_url': 'https://api.test3.com/v1/chat/completions',
                'model': 'test-model-3',
                'stream': False,
                'temperature': 0.0,
                'max_length': 16384,
                'top_p': 1.0,
                'num_beams': 1,
                'do_sample': False
            }
        }
    
    @patch('backend.services.get_multi_translation_configs')
    def test_init_with_configs(self, mock_get_configs):
        """测试服务初始化"""
        mock_get_configs.return_value = self.mock_configs
        service = MultiModelTranslationService()
        self.assertEqual(service.configs, self.mock_configs)
    
    @patch('backend.services.get_multi_translation_configs')
    def test_get_available_models(self, mock_get_configs):
        """测试获取可用模型列表"""
        mock_get_configs.return_value = self.mock_configs
        service = MultiModelTranslationService()
        
        models = service.get_available_models()
        
        self.assertEqual(len(models), 3)
        self.assertEqual(models[0]['id'], 'model_1')
        self.assertEqual(models[0]['name'], 'Test Model 1')
        self.assertEqual(models[0]['model'], 'test-model-1')
    
    @patch('backend.services.get_multi_translation_configs')
    def test_empty_configs(self, mock_get_configs):
        """测试空配置的情况"""
        mock_get_configs.return_value = {}
        service = MultiModelTranslationService()
        
        models = service.get_available_models()
        self.assertEqual(len(models), 0)
    
    @patch('backend.services.get_multi_translation_configs')
    def test_invalid_model_ids(self, mock_get_configs):
        """测试无效模型ID"""
        mock_get_configs.return_value = self.mock_configs
        service = MultiModelTranslationService()
        
        result = service.translate_with_multiple_models(
            'zh', 'en', 'test text', ['invalid_model_1', 'invalid_model_2']
        )
        
        self.assertFalse(result['success'])
        self.assertIn('No valid model IDs provided', result['error'])
    
    @patch('backend.services.get_multi_translation_configs')
    def test_empty_model_ids(self, mock_get_configs):
        """测试空模型ID列表"""
        mock_get_configs.return_value = self.mock_configs
        service = MultiModelTranslationService()
        
        result = service.translate_with_multiple_models(
            'zh', 'en', 'test text', []
        )
        
        self.assertFalse(result['success'])
        self.assertIn('No valid model IDs provided', result['error'])
    
    @patch('backend.services.get_multi_translation_configs')
    @patch('backend.services.requests.post')
    def test_successful_translation(self, mock_post, mock_get_configs):
        """测试成功的翻译"""
        mock_get_configs.return_value = self.mock_configs
        service = MultiModelTranslationService()
        
        # Mock successful API responses
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'choices': [
                {'message': {'content': 'Translated text'}}
            ]
        }
        mock_post.return_value = mock_response
        
        result = service.translate_with_multiple_models(
            'zh', 'en', 'test text', ['model_1', 'model_2']
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(len(result['results']), 2)
        self.assertEqual(result['summary']['total_models'], 2)
        self.assertEqual(result['summary']['successful_models'], 2)
        self.assertEqual(result['summary']['success_rate'], 1.0)
        
        # Check individual results
        for model_id in ['model_1', 'model_2']:
            model_result = result['results'][model_id]
            self.assertTrue(model_result['success'])
            self.assertEqual(model_result['translation'], 'Translated text')
            self.assertEqual(model_result['model_id'], model_id)
    
    @patch('backend.services.get_multi_translation_configs')
    @patch('backend.services.requests.post')
    def test_partial_failure(self, mock_post, mock_get_configs):
        """测试部分失败的情况"""
        mock_get_configs.return_value = self.mock_configs
        service = MultiModelTranslationService()
        
        # Mock mixed responses - one success, one failure
        def side_effect(*args, **kwargs):
            if 'api.test1.com' in kwargs.get('url', args[0]):
                # Success response
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.raise_for_status.return_value = None
                mock_response.json.return_value = {
                    'choices': [
                        {'message': {'content': 'Translated text'}}
                    ]
                }
                return mock_response
            else:
                # Failure response
                raise Exception("API Error")
        
        mock_post.side_effect = side_effect
        
        result = service.translate_with_multiple_models(
            'zh', 'en', 'test text', ['model_1', 'model_2']
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(len(result['results']), 2)
        self.assertEqual(result['summary']['total_models'], 2)
        self.assertEqual(result['summary']['successful_models'], 1)
        self.assertEqual(result['summary']['success_rate'], 0.5)
        
        # Check individual results
        self.assertTrue(result['results']['model_1']['success'])
        self.assertFalse(result['results']['model_2']['success'])
    
    @patch('backend.services.get_multi_translation_configs')
    @patch('backend.services.requests.post')
    def test_stream_translation(self, mock_post, mock_get_configs):
        """测试流式翻译"""
        # Enable streaming for one model
        stream_configs = self.mock_configs.copy()
        stream_configs['model_1']['stream'] = True
        
        mock_get_configs.return_value = stream_configs
        service = MultiModelTranslationService()
        
        # Mock stream response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.iter_lines.return_value = [
            'data: {"choices": [{"delta": {"content": "Hello"}}]}',
            'data: {"choices": [{"delta": {"content": " world"}}]}',
            'data: [DONE]'
        ]
        mock_post.return_value = mock_response
        
        result = service.translate_with_multiple_models(
            'zh', 'en', 'test text', ['model_1']
        )
        
        self.assertTrue(result['success'])
        self.assertTrue(result['results']['model_1']['success'])
        self.assertEqual(result['results']['model_1']['translation'], 'Hello world')
    
    @patch('backend.services.get_multi_translation_configs')
    @patch('backend.services.requests.post')
    def test_invalid_api_response(self, mock_post, mock_get_configs):
        """测试无效API响应"""
        mock_get_configs.return_value = self.mock_configs
        service = MultiModelTranslationService()
        
        # Mock invalid response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'error': 'Invalid request'
        }
        mock_post.return_value = mock_response
        
        result = service.translate_with_multiple_models(
            'zh', 'en', 'test text', ['model_1']
        )
        
        self.assertTrue(result['success'])
        self.assertFalse(result['results']['model_1']['success'])
        self.assertIn('Invalid API response', result['results']['model_1']['error'])
    
    @patch('backend.services.get_multi_translation_configs')
    def test_parameter_inheritance(self, mock_get_configs):
        """测试参数继承"""
        mock_get_configs.return_value = self.mock_configs
        service = MultiModelTranslationService()
        
        with patch('backend.services.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                'choices': [
                    {'message': {'content': 'Translated text'}}
                ]
            }
            mock_post.return_value = mock_response
            
            # Test with custom parameters
            result = service.translate_with_multiple_models(
                'zh', 'en', 'test text', ['model_1'],
                temperature=0.5, top_p=0.8, max_length=1000
            )
            
            # Check that custom parameters were used
            call_args = mock_post.call_args
            request_data = json.loads(call_args[1]['data'])
            self.assertEqual(request_data['temperature'], 0.5)
            self.assertEqual(request_data['top_p'], 0.8)
            self.assertEqual(request_data['max_length'], 1000)
    
    @patch('backend.services.get_multi_translation_configs')
    @patch('backend.services.get_translation_prompt')
    def test_prompt_usage(self, mock_get_prompt, mock_get_configs):
        """测试提示词使用"""
        mock_get_configs.return_value = self.mock_configs
        mock_get_prompt.return_value = "System prompt for translation"
        service = MultiModelTranslationService()
        
        with patch('backend.services.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                'choices': [
                    {'message': {'content': 'Translated text'}}
                ]
            }
            mock_post.return_value = mock_response
            
            result = service.translate_with_multiple_models(
                'zh', 'en', 'test text', ['model_1']
            )
            
            # Check that prompt was generated correctly
            mock_get_prompt.assert_called_with('zh', 'en')
            
            # Check that messages were structured correctly
            call_args = mock_post.call_args
            request_data = json.loads(call_args[1]['data'])
            messages = request_data['messages']
            self.assertEqual(len(messages), 2)
            self.assertEqual(messages[0]['role'], 'system')
            self.assertEqual(messages[0]['content'], 'System prompt for translation')
            self.assertEqual(messages[1]['role'], 'user')
            self.assertIn('test text', messages[1]['content'])


class TestMultiModelConfig(unittest.TestCase):
    """多模型配置测试"""
    
    @patch.dict('os.environ', {
        'TRANSLATION_API_KEY_1': 'key1',
        'TRANSLATION_API_URL_1': 'url1',
        'TRANSLATION_MODEL_1': 'model1',
        'TRANSLATION_MODEL_NAME_1': 'Model 1',
        'TRANSLATION_API_KEY_2': 'key2',
        'TRANSLATION_API_URL_2': 'url2',
        'TRANSLATION_MODEL_2': 'model2',
    }, clear=True)
    def test_multi_model_config_loading(self):
        """测试多模型配置加载"""
        from backend.config import get_multi_translation_configs
        
        configs = get_multi_translation_configs()
        
        # Should have 2 models
        self.assertEqual(len(configs), 2)
        
        # Check model 1
        self.assertEqual(configs['model_1']['id'], 'model_1')
        self.assertEqual(configs['model_1']['name'], 'Model 1')
        self.assertEqual(configs['model_1']['api_key'], 'key1')
        self.assertEqual(configs['model_1']['api_url'], 'url1')
        self.assertEqual(configs['model_1']['model'], 'model1')
        
        # Check model 2 (should use model name as display name)
        self.assertEqual(configs['model_2']['id'], 'model_2')
        self.assertEqual(configs['model_2']['name'], 'model2')
        self.assertEqual(configs['model_2']['api_key'], 'key2')
    
    @patch.dict('os.environ', {
        'TRANSLATION_API_KEY_1': 'key1',
        'TRANSLATION_API_URL_1': 'url1',
        # Missing MODEL_1 - should be skipped
        'TRANSLATION_API_KEY_2': 'key2',
        'TRANSLATION_API_URL_2': 'url2',
        'TRANSLATION_MODEL_2': 'model2',
    }, clear=True)
    def test_incomplete_config_skipped(self):
        """测试不完整的配置被跳过"""
        from backend.config import get_multi_translation_configs
        
        configs = get_multi_translation_configs()
        
        # Should only have model_2
        self.assertEqual(len(configs), 1)
        self.assertIn('model_2', configs)
        self.assertNotIn('model_1', configs)
    
    @patch.dict('os.environ', {}, clear=True)
    @patch('backend.config.get_translation_config')
    def test_fallback_to_single_config(self, mock_get_single_config):
        """测试回退到单模型配置"""
        mock_get_single_config.return_value = {
            'api_key': 'single_key',
            'api_url': 'single_url',
            'model': 'single_model'
        }
        
        from backend.config import get_multi_translation_configs
        
        configs = get_multi_translation_configs()
        
        # Should have 1 model from fallback
        self.assertEqual(len(configs), 1)
        self.assertEqual(configs['model_1']['api_key'], 'single_key')
        self.assertEqual(configs['model_1']['name'], 'single_model')


class TestHunyuanTranslation(unittest.TestCase):
    """混元翻译测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.hunyuan_config = {
            'model_hunyuan': {
                'id': 'model_hunyuan',
                'name': 'Hunyuan Translation',
                'api_key': 'test_hunyuan_key',
                'api_url': 'http://hunyuanapi.xxx.com/openapi/v1/translations',
                'model': 'hunyuan-translation-lite',
                'stream': False,
                'temperature': 0.0,
                'max_length': 16384,
                'top_p': 1.0,
                'num_beams': 1,
                'do_sample': False,
                'moderation': False
            }
        }
    
    @patch('backend.services.get_multi_translation_configs')
    def test_hunyuan_model_detection(self, mock_get_configs):
        """测试混元模型检测"""
        mock_get_configs.return_value = self.hunyuan_config
        service = MultiModelTranslationService()
        
        config = self.hunyuan_config['model_hunyuan']
        self.assertTrue(service._is_hunyuan_translation_model(config))
        
        # Test with non-hunyuan model
        regular_config = {
            'model': 'gpt-3.5-turbo',
            'api_url': 'https://api.openai.com/v1/chat/completions'
        }
        self.assertFalse(service._is_hunyuan_translation_model(regular_config))
    
    @patch('backend.services.get_multi_translation_configs')
    @patch('backend.services.requests.post')
    def test_hunyuan_translation_success(self, mock_post, mock_get_configs):
        """测试混元翻译成功"""
        mock_get_configs.return_value = self.hunyuan_config
        service = MultiModelTranslationService()
        
        # Mock successful Hunyuan response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'choices': [
                {'message': {'content': 'Hello world'}}
            ]
        }
        mock_post.return_value = mock_response
        
        result = service.translate_with_multiple_models(
            'zh', 'en', '你好世界', ['model_hunyuan']
        )
        
        self.assertTrue(result['success'])
        self.assertTrue(result['results']['model_hunyuan']['success'])
        self.assertEqual(result['results']['model_hunyuan']['translation'], 'Hello world')
        
        # Check that the request was made with correct Hunyuan format
        call_args = mock_post.call_args
        headers = call_args[1]['headers']
        self.assertEqual(headers['X-TC-Action'], 'ChatTranslations')
        self.assertEqual(headers['X-TC-Version'], '2023-09-01')
        self.assertIn('X-TC-Timestamp', headers)
        
        request_data = json.loads(call_args[1]['data'])
        self.assertEqual(request_data['model'], 'hunyuan-translation-lite')
        self.assertEqual(request_data['target'], 'en')
        self.assertEqual(request_data['text'], '你好世界')
        self.assertEqual(request_data['stream'], False)
        self.assertEqual(request_data['moderation'], False)
    
    @patch('backend.services.get_multi_translation_configs')
    @patch('backend.services.requests.post')
    def test_hunyuan_language_mapping(self, mock_post, mock_get_configs):
        """测试混元翻译语言代码映射"""
        mock_get_configs.return_value = self.hunyuan_config
        service = MultiModelTranslationService()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'choices': [
                {'message': {'content': 'Test translation'}}
            ]
        }
        mock_post.return_value = mock_response
        
        # Test zh -> zh-CN mapping
        result = service.translate_with_multiple_models(
            'en', 'zh', 'Hello', ['model_hunyuan']
        )
        
        call_args = mock_post.call_args
        request_data = json.loads(call_args[1]['data'])
        self.assertEqual(request_data['target'], 'zh-CN')
    
    @patch('backend.services.get_multi_translation_configs')
    @patch('backend.services.requests.post')
    def test_hunyuan_translation_error(self, mock_post, mock_get_configs):
        """测试混元翻译错误处理"""
        mock_get_configs.return_value = self.hunyuan_config
        service = MultiModelTranslationService()
        
        # Mock API error
        mock_post.side_effect = Exception("API Error")
        
        result = service.translate_with_multiple_models(
            'zh', 'en', '你好', ['model_hunyuan']
        )
        
        self.assertTrue(result['success'])  # Overall success
        self.assertFalse(result['results']['model_hunyuan']['success'])  # Individual failure
        self.assertIn('Hunyuan translation error', result['results']['model_hunyuan']['error'])
    
    @patch('backend.services.get_multi_translation_configs')
    @patch('backend.services.requests.post')
    def test_hunyuan_invalid_response(self, mock_post, mock_get_configs):
        """测试混元翻译无效响应"""
        mock_get_configs.return_value = self.hunyuan_config
        service = MultiModelTranslationService()
        
        # Mock invalid response format
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'error': 'Invalid request'
        }
        mock_post.return_value = mock_response
        
        result = service.translate_with_multiple_models(
            'zh', 'en', '你好', ['model_hunyuan']
        )
        
        self.assertTrue(result['success'])
        self.assertFalse(result['results']['model_hunyuan']['success'])
        self.assertIn('Invalid Hunyuan translation response format', result['results']['model_hunyuan']['error'])


if __name__ == '__main__':
    unittest.main() 