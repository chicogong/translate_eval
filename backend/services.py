"""
Translation and Evaluation Services
"""

import json
import requests
import logging
from typing import Dict, Generator, Optional, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import get_translation_config, get_evaluation_config, get_multi_translation_configs, get_multi_evaluation_configs
from prompts import get_translation_prompt, get_evaluation_prompt
from hunyuan_service import HunyuanTranslationService

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


class MultiModelTranslationService:
    """多模型翻译服务"""
    
    def __init__(self):
        self.configs = get_multi_translation_configs()
        logger.info(f"Initialized multi-model translation service with {len(self.configs)} models")
    
    def get_available_models(self) -> List[Dict]:
        """获取可用的模型列表"""
        models = []
        for config_id, config in self.configs.items():
            models.append({
                'id': config['id'],
                'name': config['name'],
                'model': config['model']
            })
        return models
    
    def translate_with_multiple_models(self, source_lang: str, target_lang: str, text: str, 
                                     model_ids: List[str], stream: Optional[bool] = None,
                                     temperature: Optional[float] = None,
                                     max_length: Optional[int] = None, 
                                     top_p: Optional[float] = None) -> Dict:
        """使用多个模型进行翻译对比"""
        logger.info(f"Starting multi-model translation: {source_lang} -> {target_lang}, models: {model_ids}")
        
        # 验证模型ID
        valid_model_ids = []
        for model_id in model_ids:
            if model_id in self.configs:
                valid_model_ids.append(model_id)
            else:
                logger.warning(f"Model ID {model_id} not found in configurations")
        
        if not valid_model_ids:
            return {"success": False, "error": "No valid model IDs provided"}
        
        # 并行翻译
        results = {}
        with ThreadPoolExecutor(max_workers=len(valid_model_ids)) as executor:
            # 提交所有翻译任务
            future_to_model = {}
            for model_id in valid_model_ids:
                future = executor.submit(
                    self._translate_single_model, 
                    model_id, source_lang, target_lang, text, 
                    stream, temperature, max_length, top_p
                )
                future_to_model[future] = model_id
            
            # 收集结果
            for future in as_completed(future_to_model):
                model_id = future_to_model[future]
                try:
                    result = future.result()
                    results[model_id] = result
                    logger.info(f"Translation completed for model {model_id}: success={result['success']}")
                except Exception as e:
                    logger.error(f"Translation failed for model {model_id}: {e}")
                    results[model_id] = {"success": False, "error": str(e)}
        
        # 计算成功率
        successful_translations = sum(1 for r in results.values() if r['success'])
        total_translations = len(results)
        
        return {
            "success": True,
            "results": results,
            "summary": {
                "total_models": total_translations,
                "successful_models": successful_translations,
                "success_rate": successful_translations / total_translations if total_translations > 0 else 0
            }
        }
    
    def _translate_single_model(self, model_id: str, source_lang: str, target_lang: str, 
                               text: str, stream: Optional[bool] = None,
                               temperature: Optional[float] = None,
                               max_length: Optional[int] = None, 
                               top_p: Optional[float] = None) -> Dict:
        """使用单个模型进行翻译"""
        config = self.configs[model_id]
        
        # 检查是否为混元翻译模型
        if HunyuanTranslationService.is_hunyuan_model(config):
            return HunyuanTranslationService.translate(config, source_lang, target_lang, text)
        
        # 使用传入的参数或配置默认值
        use_stream = stream if stream is not None else config['stream']
        use_temperature = temperature if temperature is not None else config['temperature']
        use_max_length = max_length if max_length is not None else config['max_length']
        use_top_p = top_p if top_p is not None else config['top_p']
        
        try:
            system_prompt = get_translation_prompt(source_lang, target_lang)
            user_content = f"翻译为{target_lang}（仅输出译文内容）：\n\n{text}"
            
            # 记录完整的请求内容
            request_data = {
                'model': config['model'],
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_content}
                ],
                'stream': use_stream,
                'temperature': use_temperature,
                'max_length': use_max_length,
                'top_p': use_top_p,
                'num_beams': config['num_beams'],
                'delete_prompt_from_output': 1,
                'do_sample': config['do_sample']
            }
            
            logger.debug(f"Model {model_id} translation request: {json.dumps(request_data, ensure_ascii=False)}")
            
        except Exception as e:
            logger.error(f"Error preparing translation request for model {model_id}: {e}")
            return {"success": False, "error": f"Error preparing request: {e}", "model_name": config['name']}
        
        # 根据是否流式选择不同的处理方式
        if use_stream:
            return self._translate_stream_single_model(config, request_data)
        else:
            return self._translate_non_stream_single_model(config, request_data)
    
    def _translate_non_stream_single_model(self, config: Dict, request_data: Dict) -> Dict:
        """单个模型非流式翻译"""
        headers = {
            'Content-Type': 'application/json', 
            'Authorization': f'Bearer {config["api_key"]}'
        }
        
        try:
            response = requests.post(
                config['api_url'], 
                headers=headers, 
                data=json.dumps(request_data), 
                timeout=60
            )
            response.raise_for_status()
            response_data = response.json()
            
            if "choices" in response_data and response_data["choices"]:
                translation = response_data["choices"][0]["message"]["content"]
                return {
                    "success": True, 
                    "translation": translation,
                    "model_name": config['name'],
                    "model_id": config['id']
                }
            else:
                return {
                    "success": False, 
                    "error": "Invalid API response",
                    "model_name": config['name'],
                    "model_id": config['id']
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False, 
                "error": str(e),
                "model_name": config['name'],
                "model_id": config['id']
            }
        except Exception as e:
            return {
                "success": False, 
                "error": str(e),
                "model_name": config['name'],
                "model_id": config['id']
            }
    
    def _translate_stream_single_model(self, config: Dict, request_data: Dict) -> Dict:
        """单个模型流式翻译"""
        headers = {
            'Content-Type': 'application/json', 
            'Authorization': f'Bearer {config["api_key"]}'
        }
        
        try:
            response = requests.post(
                config['api_url'], 
                headers=headers, 
                data=json.dumps(request_data), 
                timeout=60,
                stream=True
            )
            response.raise_for_status()
            
            # 处理SSE流式响应
            full_translation = ""
            for raw_line in response.iter_lines(decode_unicode=True):
                if not raw_line:
                    continue
                line = raw_line.strip()

                if line.startswith('data:'):
                    data_str = line[len('data:'):].strip()
                else:
                    data_str = line

                if data_str in ('[DONE]', 'DONE'):
                    break

                try:
                    data_json = json.loads(data_str)
                except json.JSONDecodeError:
                    continue

                choices = data_json.get("choices")
                if choices and isinstance(choices, list):
                    delta = choices[0].get("delta", {})
                    content_piece = delta.get("content") or ""
                else:
                    content_piece = data_json.get("text", "")

                if content_piece:
                    full_translation += content_piece
            
            if full_translation.strip():
                return {
                    "success": True, 
                    "translation": full_translation,
                    "model_name": config['name'],
                    "model_id": config['id']
                }
            
            # fallback 到非流式
            logger.warning(f"No content received from stream for model {config['name']}, falling back to non-stream")
            return self._translate_non_stream_single_model(config, {k: v for k, v in request_data.items() if k != 'stream'})
            
        except requests.exceptions.RequestException as e:
            # fallback 到非流式
            return self._translate_non_stream_single_model(config, {k: v for k, v in request_data.items() if k != 'stream'})
        except Exception as e:
            return {
                "success": False, 
                "error": str(e),
                "model_name": config['name'],
                "model_id": config['id']
            } 


class MultiEvaluationService:
    """多评估服务"""
    
    def __init__(self):
        self.configs = get_multi_evaluation_configs()
        logger.info(f"Initialized multi-evaluation service with {len(self.configs)} evaluators")
    
    def get_available_evaluators(self) -> List[Dict]:
        """获取可用的评估模型列表"""
        evaluators = []
        for config_id, config in self.configs.items():
            evaluators.append({
                'id': config['id'],
                'name': config['name'],
                'model': config['model']
            })
        return evaluators
    
    def evaluate_multiple_translations(self, source_lang: str, target_lang: str, 
                                      source_text: str, translations: Dict[str, Dict]) -> Dict:
        """使用多个评估模型评估多个翻译结果"""
        logger.info(f"Starting multi-evaluation for {len(translations)} translations")
        
        if not self.configs:
            return {"success": False, "error": "No evaluators configured"}
        
        # 过滤出成功的翻译结果
        successful_translations = {k: v for k, v in translations.items() if v.get('success', False)}
        
        if not successful_translations:
            return {"success": False, "error": "No successful translations to evaluate"}
        
        # 并行评估所有翻译结果
        evaluation_results = {}
        with ThreadPoolExecutor(max_workers=len(self.configs) * len(successful_translations)) as executor:
            # 提交所有评估任务
            future_to_key = {}
            for translation_key, translation_result in successful_translations.items():
                translation_text = translation_result['translation']
                for evaluator_id in self.configs.keys():
                    future = executor.submit(
                        self._evaluate_single_translation,
                        evaluator_id, source_lang, target_lang, 
                        source_text, translation_text
                    )
                    future_to_key[future] = (translation_key, evaluator_id)
            
            # 收集结果
            for future in as_completed(future_to_key):
                translation_key, evaluator_id = future_to_key[future]
                try:
                    result = future.result()
                    
                    if translation_key not in evaluation_results:
                        evaluation_results[translation_key] = {}
                    
                    evaluation_results[translation_key][evaluator_id] = result
                    logger.info(f"Evaluation completed for {translation_key} by {evaluator_id}")
                except Exception as e:
                    logger.error(f"Evaluation failed for {translation_key} by {evaluator_id}: {e}")
                    if translation_key not in evaluation_results:
                        evaluation_results[translation_key] = {}
                    evaluation_results[translation_key][evaluator_id] = {
                        "success": False, 
                        "error": str(e),
                        "evaluator_name": self.configs[evaluator_id]['name']
                    }
        
        # 计算综合评分
        processed_results = {}
        for translation_key, evaluator_results in evaluation_results.items():
            scores = []
            justifications = []
            evaluator_details = []
            
            for evaluator_id, result in evaluator_results.items():
                evaluator_details.append({
                    'evaluator_id': evaluator_id,
                    'evaluator_name': self.configs[evaluator_id]['name'],
                    'success': result['success'],
                    'score': result.get('score', 'N/A'),
                    'justification': result.get('justification', 'No justification provided'),
                    'error': result.get('error', None)
                })
                
                if result['success'] and isinstance(result.get('score'), (int, float)):
                    scores.append(result['score'])
                    justifications.append(result.get('justification', ''))
            
            # 计算平均分
            avg_score = sum(scores) / len(scores) if scores else 0
            
            processed_results[translation_key] = {
                'average_score': round(avg_score, 2),
                'evaluator_count': len(evaluator_results),
                'successful_evaluations': len(scores),
                'evaluator_details': evaluator_details,
                'combined_justification': self._combine_justifications(justifications)
            }
        
        return {
            "success": True,
            "results": processed_results,
            "summary": {
                "total_translations": len(successful_translations),
                "total_evaluators": len(self.configs),
                "evaluations_performed": sum(len(er) for er in evaluation_results.values())
            }
        }
    
    def _evaluate_single_translation(self, evaluator_id: str, source_lang: str, target_lang: str,
                                   source_text: str, translation: str) -> Dict:
        """使用单个评估模型评估翻译"""
        config = self.configs[evaluator_id]
        
        try:
            eval_prompt = get_evaluation_prompt(source_lang, target_lang, source_text, translation)
            
            request_data = {
                'model': config['model'],
                'messages': [{'role': 'user', 'content': eval_prompt}]
            }
            
            logger.debug(f"Evaluator {evaluator_id} request: {json.dumps(request_data, ensure_ascii=False)}")
            
        except Exception as e:
            logger.error(f"Error preparing evaluation request for {evaluator_id}: {e}")
            return {
                "success": False, 
                "error": f"Error preparing request: {e}",
                "evaluator_name": config['name']
            }
        
        headers = {
            'Content-Type': 'application/json', 
            'Authorization': f'Bearer {config["api_key"]}'
        }
        
        try:
            response = requests.post(
                config['api_url'], 
                headers=headers, 
                data=json.dumps(request_data), 
                timeout=60
            )
            response.raise_for_status()
            eval_data = response.json()
            
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
                        except (ValueError, IndexError):
                            logger.warning(f"Failed to parse score from line: {line}")
                            score = "N/A"
                    elif line.startswith("JUSTIFICATION:"):
                        justification = line.split("JUSTIFICATION:")[1].strip()
                
                return {
                    "success": True, 
                    "score": score, 
                    "justification": justification,
                    "evaluator_name": config['name'],
                    "evaluator_id": evaluator_id
                }
            else:
                return {
                    "success": False, 
                    "error": "Invalid evaluation response",
                    "evaluator_name": config['name'],
                    "evaluator_id": evaluator_id
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False, 
                "error": str(e),
                "evaluator_name": config['name'],
                "evaluator_id": evaluator_id
            }
        except Exception as e:
            return {
                "success": False, 
                "error": str(e),
                "evaluator_name": config['name'],
                "evaluator_id": evaluator_id
            }
    
    def _combine_justifications(self, justifications: List[str]) -> str:
        """合并多个评估理由"""
        if not justifications:
            return "No justifications available."
        
        if len(justifications) == 1:
            return justifications[0]
        
        combined = []
        for i, justification in enumerate(justifications, 1):
            if justification.strip():
                combined.append(f"Judge {i}: {justification.strip()}")
        
        return "\n\n".join(combined) if combined else "No justifications available." 