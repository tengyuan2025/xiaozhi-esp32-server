import httpx
import openai
from openai.types import CompletionUsage
from config.logger import setup_logging
from core.utils.util import check_model_key
from core.providers.llm.base import LLMProviderBase

TAG = __name__
logger = setup_logging()


class LLMProvider(LLMProviderBase):
    def __init__(self, config):
        self.model_name = config.get("model_name")
        self.api_key = config.get("api_key")
        if "base_url" in config:
            self.base_url = config.get("base_url")
        else:
            self.base_url = config.get("url")
        # 增加timeout的配置项，单位为秒
        timeout = config.get("timeout", 300)
        self.timeout = int(timeout) if timeout else 300

        # 处理额外参数
        self.extra_params = config.get("extra_params", {})

        param_defaults = {
            "max_tokens": (500, int),
            "temperature": (0.7, lambda x: round(float(x), 1)),
            "top_p": (1.0, lambda x: round(float(x), 1)),
            "frequency_penalty": (0, lambda x: round(float(x), 1)),
        }

        for param, (default, converter) in param_defaults.items():
            value = config.get(param)
            try:
                setattr(
                    self,
                    param,
                    converter(value) if value not in (None, "") else default,
                )
            except (ValueError, TypeError):
                setattr(self, param, default)

        logger.debug(
            f"意图识别参数初始化: {self.temperature}, {self.max_tokens}, {self.top_p}, {self.frequency_penalty}"
        )

        model_key_msg = check_model_key("LLM", self.api_key)
        if model_key_msg:
            logger.bind(tag=TAG).error(model_key_msg)
        
        # 检查代理设置并根据域名决定是否使用代理
        import os
        from urllib.parse import urlparse
        
        http_proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
        https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
        
        # 解析目标域名
        parsed_url = urlparse(self.base_url)
        domain = parsed_url.hostname
        
        # 只对claude.ai和anthropic.com域名使用代理
        use_proxy = domain and (domain.endswith('claude.ai') or domain.endswith('anthropic.com'))
        
        logger.bind(tag=TAG).info(f"LLM客户端初始化 - API Base URL: {self.base_url}")
        logger.bind(tag=TAG).info(f"目标域名: {domain}, 是否使用代理: {use_proxy}")
        logger.bind(tag=TAG).info(f"系统环境代理设置 - HTTP_PROXY: {http_proxy}, HTTPS_PROXY: {https_proxy}")
        
        # 根据域名决定是否使用代理
        if use_proxy:
            # 使用系统代理设置
            self.client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url, timeout=httpx.Timeout(self.timeout))
            logger.bind(tag=TAG).info("使用代理连接")
        else:
            # 强制不使用代理
            http_client = httpx.Client(
                timeout=httpx.Timeout(self.timeout),
                proxies={
                    "http://": None,
                    "https://": None,
                    "all://": None
                },
                limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
                http2=True,
                verify=True
            )
            self.client = openai.OpenAI(
                api_key=self.api_key, 
                base_url=self.base_url, 
                http_client=http_client
            )
            logger.bind(tag=TAG).info("强制直连，完全禁用代理")
    
    def _filter_reasoning_content(self, text):
        """过滤掉豆包模型的reasoning内容，只保留最终回答"""
        # 豆包的reasoning通常包含推理过程，我们只需要最终的用户回答部分
        # 如果包含推理标记，尝试提取最终答案
        if '推理' in text or '因为' in text or '所以' in text:
            # 简单启发式：取最后一个句号之后的内容，或者最短的有意义回答
            sentences = text.split('。')
            for i in range(len(sentences)-1, -1, -1):
                sentence = sentences[i].strip()
                if sentence and len(sentence) < 100 and not any(word in sentence for word in ['因为', '所以', '推理', '分析']):
                    return sentence + '。' if not sentence.endswith('。') else sentence
        return text

    def response(self, session_id, dialogue, **kwargs):
        try:
            # 构建请求参数
            request_params = {
                "model": self.model_name,
                "messages": dialogue,
                "stream": True,
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "temperature": kwargs.get("temperature", self.temperature),
                "top_p": kwargs.get("top_p", self.top_p),
                "frequency_penalty": kwargs.get(
                    "frequency_penalty", self.frequency_penalty
                ),
            }
            
            # 添加额外参数
            request_params.update(self.extra_params)
            
            # 打印请求URL和参数，检查网络路径
            logger.bind(tag=TAG).info(f"LLM请求URL: {self.base_url}/chat/completions")
            logger.bind(tag=TAG).info(f"LLM请求参数: model={request_params['model']}, "
                                    f"max_tokens={request_params['max_tokens']}, "
                                    f"temperature={request_params['temperature']}, "
                                    f"messages_count={len(request_params['messages'])}")
            
            # 检查httpx客户端的代理配置
            if hasattr(self.client._client, '_mounts'):
                logger.bind(tag=TAG).info(f"HTTPx客户端配置: {self.client._client._mounts}")
            
            logger.bind(tag=TAG).debug(f"LLM完整请求参数: {request_params}")
            
            # 记录请求开始时间
            import time
            request_start = time.time()
            logger.bind(tag=TAG).info(f"开始发送LLM请求 - {request_start}")
            
            responses = self.client.chat.completions.create(**request_params)
            
            # 记录首个响应时间
            first_response_time = time.time()
            logger.bind(tag=TAG).info(f"收到首个响应 - 耗时: {first_response_time - request_start:.3f}秒")

            is_active = True
            full_response = ""  # 收集完整响应
            chunk_count = 0
            first_content_time = None
            
            for chunk in responses:
                chunk_count += 1
                chunk_time = time.time()
                
                try:
                    # 记录原始chunk数据
                    logger.bind(tag=TAG).debug(f"LLM响应chunk #{chunk_count} - 时间: {chunk_time - request_start:.3f}s: {chunk}")
                    
                    # 检查是否存在有效的choice且content不为空
                    delta = (
                        chunk.choices[0].delta
                        if getattr(chunk, "choices", None)
                        else None
                    )
                    content = delta.content if hasattr(delta, "content") else ""
                except IndexError:
                    content = ""
                
                if content and first_content_time is None:
                    first_content_time = chunk_time
                    logger.bind(tag=TAG).info(f"🤖 LLM首次响应 - 耗时: {first_content_time - request_start:.3f}秒")
                
                if content:
                    full_response += content  # 累积完整响应
                    
                    # 过滤豆包的reasoning内容
                    filtered_content = content
                    if "reasoning_content" in str(chunk):
                        # 如果chunk包含reasoning_content，跳过这部分
                        logger.bind(tag=TAG).debug(f"检测到reasoning内容，已过滤")
                        continue
                    
                    # 处理标签跨多个chunk的情况
                    if "<think>" in filtered_content:
                        is_active = False
                        filtered_content = filtered_content.split("<think>")[0]
                    if "</think>" in filtered_content:
                        is_active = True
                        filtered_content = filtered_content.split("</think>")[-1]
                    
                    if is_active and filtered_content:
                        yield filtered_content
            
            # 统计信息
            total_time = time.time() - request_start
            logger.bind(tag=TAG).info(f"LLM响应统计 - 总chunk数: {chunk_count}, 首响应: {first_response_time - request_start:.3f}s, 首内容: {(first_content_time - request_start):.3f}s, 总耗时: {total_time:.3f}s")
            
            # 过滤reasoning内容再记录
            filtered_response = self._filter_reasoning_content(full_response)
            logger.bind(tag=TAG).info(f"LLM完整响应（已过滤reasoning）: {filtered_response}")

        except Exception as e:
            logger.bind(tag=TAG).error(f"Error in response generation: {e}")

    def response_with_functions(self, session_id, dialogue, functions=None):
        try:
            # 构建请求参数
            request_params = {
                "model": self.model_name,
                "messages": dialogue,
                "stream": True,
                "tools": functions
            }
            
            # 打印请求URL和参数
            logger.bind(tag=TAG).info(f"LLM函数调用请求URL: {self.base_url}/chat/completions")
            logger.bind(tag=TAG).info(f"LLM函数调用请求参数: model={request_params['model']}, "
                                    f"messages_count={len(request_params['messages'])}, "
                                    f"tools_count={len(functions) if functions else 0}")
            logger.bind(tag=TAG).debug(f"LLM函数调用完整请求参数: {request_params}")
            
            # 记录函数调用请求开始时间
            import time
            request_start = time.time()
            logger.bind(tag=TAG).info(f"开始发送LLM函数调用请求 - {request_start}")
            
            stream = self.client.chat.completions.create(**request_params)
            
            # 记录首个响应时间
            first_response_time = time.time()
            logger.bind(tag=TAG).info(f"收到首个函数调用响应 - 耗时: {first_response_time - request_start:.3f}秒")

            full_response = ""  # 收集完整响应
            function_calls = []  # 收集函数调用
            chunk_count = 0
            for chunk in stream:
                chunk_count += 1
                chunk_time = time.time()
                
                # 只记录有内容的chunk
                logger.bind(tag=TAG).debug(f"LLM函数调用响应chunk #{chunk_count}: {chunk}")
                
                # 检查是否存在有效的choice且content不为空
                if getattr(chunk, "choices", None):
                    content = chunk.choices[0].delta.content
                    tool_calls = chunk.choices[0].delta.tool_calls
                    
                    if content:
                        full_response += content
                        if chunk_count <= 5 or len(content) > 1:  # 只记录前5个或有意义的内容
                            logger.bind(tag=TAG).info(f"收到内容chunk #{chunk_count}: '{content}' - {chunk_time - request_start:.3f}s")
                    if tool_calls:
                        function_calls.append(tool_calls)
                        logger.bind(tag=TAG).info(f"收到工具调用 #{chunk_count}: {tool_calls} - {chunk_time - request_start:.3f}s")
                    
                    yield content, tool_calls
                # 存在 CompletionUsage 消息时，生成 Token 消耗 log
                elif isinstance(getattr(chunk, "usage", None), CompletionUsage):
                    usage_info = getattr(chunk, "usage", None)
                    logger.bind(tag=TAG).info(
                        f"Token 消耗（时间: {chunk_time - request_start:.3f}s）：输入 {getattr(usage_info, 'prompt_tokens', '未知')}，"
                        f"输出 {getattr(usage_info, 'completion_tokens', '未知')}，"
                        f"共计 {getattr(usage_info, 'total_tokens', '未知')}"
                    )
            
            # 统计和打印完整响应
            total_time = time.time() - request_start
            content_chunks = sum(1 for chunk in [True] if full_response)  # 简化计算
            logger.bind(tag=TAG).info(f"函数调用统计 - 总chunk数: {chunk_count}, 总耗时: {total_time:.3f}s, 平均每chunk: {total_time/chunk_count*1000:.1f}ms")
            logger.bind(tag=TAG).info(f"LLM函数调用完整响应: {full_response}")
            if function_calls:
                logger.bind(tag=TAG).info(f"LLM函数调用信息: {function_calls}")

        except Exception as e:
            logger.bind(tag=TAG).error(f"Error in function call streaming: {e}")
            yield f"【OpenAI服务响应异常: {e}】", None
