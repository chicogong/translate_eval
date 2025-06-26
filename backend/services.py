"""
Translation and Evaluation Services
"""

import json
import requests
import logging
from typing import Dict, Generator, Optional
from config import get_translation_config, get_evaluation_config
from prompts import get_translation_prompt, get_evaluation_prompt

logger = logging.getLogger(__name__)

class TranslationService:
    """翻译服务"""
    
    def __init__(self):
        self.config = get_translation_config()
    
    def translate_text(self, source_lang: str, target_lang: str, text: str, 
                      stream: Optional[bool] = None, temperature: Optional[float] = None,
                      max_length: Optional[int] = None, top_p: Optional[float] = None) -> dict:
        """翻译文本，支持流式和非流式"""
        logger.info(f"Starting translation: {source_lang} -> {target_lang}, text length: {len(text)}")
        
        if not self.config['api_key']:
            logger.error("Translation API key not available")
            return {"success": False, "error": "Translation API key not found"}
        
        # 使用传入的参数或配置默认值
        use_stream = stream if stream is not None else self.config['stream']
        use_temperature = temperature if temperature is not None else self.config['temperature']
        use_max_length = max_length if max_length is not None else self.config['max_length']
        use_top_p = top_p if top_p is not None else self.config['top_p']
        
        try:
            system_prompt = get_translation_prompt(source_lang, target_lang)
            user_content = f"翻译为{target_lang}（仅输出译文内容）：\n\n{text}"
            logger.debug(f"Using translation prompt for {source_lang}-{target_lang}")
            
            # 记录完整的请求内容
            request_data = {
                'model': self.config['model'],
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_content}
                ],
                'stream': use_stream,
                'temperature': use_temperature,
                'max_length': use_max_length,
                'top_p': use_top_p,
                'num_beams': self.config['num_beams'],
                'delete_prompt_from_output': 1,
                'do_sample': self.config['do_sample']
            }
            
            logger.info(f"Translation request data: {json.dumps(request_data, ensure_ascii=False, indent=2)}")
            
        except Exception as e:
            logger.error(f"Error preparing translation request: {e}")
            return {"success": False, "error": f"Error preparing request: {e}"}
        
        # 根据是否流式选择不同的处理方式
        if use_stream:
            return self._translate_stream(request_data)
        else:
            return self._translate_non_stream(request_data)
    
    def _translate_non_stream(self, request_data: dict) -> dict:
        """非流式翻译"""
        headers = {
            'Content-Type': 'application/json', 
            'Authorization': f'Bearer {self.config["api_key"]}'
        }
        
        try:
            logger.debug(f"Making non-stream translation API call to {self.config['api_url']}")
            response = requests.post(
                self.config['api_url'], 
                headers=headers, 
                data=json.dumps(request_data), 
                timeout=60
            )
            response.raise_for_status()
            response_data = response.json()
            
            # 记录完整的响应内容
            logger.info(f"Translation response data: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
            
            if "choices" in response_data and response_data["choices"]:
                translation = response_data["choices"][0]["message"]["content"]
                logger.info(f"Translation successful, result length: {len(translation)}")
                return {"success": True, "translation": translation}
            else:
                logger.error(f"Invalid API response: {response_data}")
                return {"success": False, "error": "Invalid API response"}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Translation API request failed: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error during translation: {e}")
            return {"success": False, "error": str(e)}
    
    def _translate_stream(self, request_data: dict) -> dict:
        """流式翻译"""
        headers = {
            'Content-Type': 'application/json', 
            'Authorization': f'Bearer {self.config["api_key"]}'
        }
        
        try:
            logger.debug(f"Making stream translation API call to {self.config['api_url']}")
            response = requests.post(
                self.config['api_url'], 
                headers=headers, 
                data=json.dumps(request_data), 
                timeout=60,
                stream=True
            )
            response.raise_for_status()
            
            # 处理SSE流式响应，兼容 OpenAI / DeepSeek / 自建代理多种格式
            full_translation = ""
            for raw_line in response.iter_lines(decode_unicode=True):
                if not raw_line:
                    continue  # 跳过 keep-alive 空行
                line = raw_line.strip()

                # 部分代理不会带 "data:" 前缀，做兼容
                if line.startswith('data:'):
                    data_str = line[len('data:'):].strip()
                else:
                    data_str = line

                # 结束标记
                if data_str in ('[DONE]', 'DONE'):
                    break

                # 尝试解析 JSON
                try:
                    data_json = json.loads(data_str)
                except json.JSONDecodeError:
                    logger.debug(f"Skipping non-JSON stream chunk: {data_str[:80]}")
                    continue

                # OpenAI / DeepSeek 格式：choices -> delta -> content
                choices = data_json.get("choices")
                if choices and isinstance(choices, list):
                    delta = choices[0].get("delta", {})
                    content_piece = delta.get("content") or ""
                else:
                    # 兼容其他接口：直接 text 字段
                    content_piece = data_json.get("text", "")

                if content_piece:
                    full_translation += content_piece
                    logger.debug(f"Stream chunk: {content_piece}")
            
            logger.info(f"Stream translation completed. Full length: {len(full_translation)}")
            
            if full_translation.strip():
                return {"success": True, "translation": full_translation}
            # 如果流模式失败尝试 fallback 到非流式
            logger.warning("No content received from stream, falling back to non-stream API call")
            return self._translate_non_stream({k: v for k, v in request_data.items() if k != 'stream'})
        except requests.exceptions.RequestException as e:
            logger.error(f"Stream translation API request failed: {e}")
            # fallback 到非流式
            return self._translate_non_stream({k: v for k, v in request_data.items() if k != 'stream'})
        except Exception as e:
            logger.error(f"Unexpected error during stream translation: {e}")
            return {"success": False, "error": str(e)}


class EvaluationService:
    """评估服务"""
    
    def __init__(self):
        self.config = get_evaluation_config()
    
    def evaluate_translation(self, source_lang: str, target_lang: str, 
                           source_text: str, translation: str) -> dict:
        """评估翻译质量"""
        logger.info(f"Starting evaluation: {source_lang} -> {target_lang}")
        
        if not self.config['api_key']:
            logger.error("Evaluation API key not available")
            return {"success": False, "error": "Evaluation API key not found"}
        
        try:
            eval_prompt = get_evaluation_prompt(source_lang, target_lang, source_text, translation)
            logger.debug(f"Using evaluation prompt for {source_lang}-{target_lang}")
            
            # 记录完整的请求内容
            request_data = {
                'model': self.config['model'],
                'messages': [{'role': 'user', 'content': eval_prompt}]
            }
            
            logger.info(f"Evaluation request data: {json.dumps(request_data, ensure_ascii=False, indent=2)}")
            
        except Exception as e:
            logger.error(f"Error preparing evaluation request: {e}")
            return {"success": False, "error": f"Error preparing evaluation request: {e}"}
        
        headers = {
            'Content-Type': 'application/json', 
            'Authorization': f'Bearer {self.config["api_key"]}'
        }
        
        try:
            logger.debug(f"Making evaluation API call to {self.config['api_url']}")
            response = requests.post(
                self.config['api_url'], 
                headers=headers, 
                data=json.dumps(request_data), 
                timeout=60
            )
            response.raise_for_status()
            eval_data = response.json()
            
            # 记录完整的响应内容
            logger.info(f"Evaluation response data: {json.dumps(eval_data, ensure_ascii=False, indent=2)}")
            
            if "choices" in eval_data and eval_data["choices"]:
                eval_result_str = eval_data["choices"][0]["message"]["content"].strip()
                
                # 解析评分和理由
                score = "N/A"
                justification = "No justification provided."
                
                lines = eval_result_str.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith("SCORE:"):
                        try:
                            score = int(line.split("SCORE:")[1].strip())
                            logger.debug(f"Parsed evaluation score: {score}")
                        except (ValueError, IndexError):
                            logger.warning(f"Failed to parse score from line: {line}")
                            score = "N/A"
                    elif line.startswith("JUSTIFICATION:"):
                        justification = line.split("JUSTIFICATION:")[1].strip()
                        logger.debug(f"Parsed justification length: {len(justification)}")
                
                logger.info(f"Evaluation successful, score: {score}")
                return {"success": True, "score": score, "justification": justification}
            else:
                logger.error(f"Invalid evaluation response: {eval_data}")
                return {"success": False, "error": "Invalid evaluation response"}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Evaluation API request failed: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error during evaluation: {e}")
            return {"success": False, "error": str(e)} 