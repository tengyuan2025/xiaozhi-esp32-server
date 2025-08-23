import traceback
import requests
from typing import Optional, List, Dict
from ..base import MemoryProviderBase, logger

TAG = __name__


class MemoryProvider(MemoryProviderBase):
    def __init__(self, config, summary_memory=None):
        super().__init__(config)
        self.base_url = config.get("base_url", "http://192.168.1.105:9000")
        self.api_key = config.get("api_key", "")
        self.timeout = config.get("timeout", 30)
        
        logger.bind(tag=TAG).info(f"初始化本地Mem0服务 - 地址: {self.base_url}")
        
        # 创建 requests session，禁用代理
        self.session = requests.Session()
        self.session.proxies = {
            'http': None,
            'https': None,
            'HTTP': None,
            'HTTPS': None
        }
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}" if self.api_key else "",
            "Content-Type": "application/json"
        })
        
        self.use_mem0 = True

    async def save_memory(self, msgs):
        if not self.use_mem0:
            logger.bind(tag=TAG).info("本地Mem0服务未启用，跳过记忆保存")
            return None
        if len(msgs) < 2:
            logger.bind(tag=TAG).info(f"消息数量不足（{len(msgs)} < 2），跳过记忆保存")
            return None

        try:
            # 格式化消息为 mem0 格式
            messages = [
                {"role": message.role, "content": message.content}
                for message in msgs
                if message.role != "system"
            ]
            
            logger.bind(tag=TAG).info(f"开始保存记忆到本地Mem0服务 - 用户ID: {self.role_id}, 消息数量: {len(messages)}")
            
            # 将消息转换为文本格式，适配deepseek_web_service的API
            text_content = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
            
            # 调用本地 mem0 服务的 add 接口
            url = f"{self.base_url}/api/memories"
            response = self.session.post(
                url,
                json={
                    "text": text_content,
                    "user_id": self.role_id
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            logger.bind(tag=TAG).info(f"本地Mem0服务记忆保存成功: {result}")
            return result
        except Exception as e:
            logger.bind(tag=TAG).error(f"保存记忆到本地Mem0服务失败: {str(e)}")
            logger.bind(tag=TAG).error(f"详细错误信息: {traceback.format_exc()}")
            return None

    async def query_memory(self, query: str) -> str:
        if not self.use_mem0:
            logger.bind(tag=TAG).debug("本地Mem0服务未启用，返回空记忆")
            return ""
        try:
            logger.bind(tag=TAG).info(f"开始查询本地Mem0服务记忆 - 用户ID: {self.role_id}, 查询: {query}")
            
            # 调用本地 mem0 服务的 search 接口
            url = f"{self.base_url}/api/search"
            response = self.session.post(
                url,
                json={
                    "query": query,
                    "user_id": self.role_id,
                    "limit": 10
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            
            results = response.json()
            logger.bind(tag=TAG).debug(f"本地Mem0服务查询原始结果: {results}")
            
            # 兼容deepseek_web_service的返回格式
            memories_data = []
            if "memories" in results:
                memories_data = results["memories"]
            elif "results" in results:
                memories_data = results["results"]
            elif isinstance(results, list):
                memories_data = results
            
            if not memories_data:
                logger.bind(tag=TAG).info("本地Mem0服务查询无结果")
                return ""

            # 格式化记忆条目
            memories = []
            for entry in memories_data:
                # 兼容不同的字段名
                content = entry.get("memory", entry.get("content", entry.get("text", str(entry))))
                timestamp = entry.get("updated_at", entry.get("created_at", ""))
                # relevance_score 是相关度分数
                score = entry.get("relevance_score", 0.0)
                
                if content:
                    if timestamp:
                        try:
                            # 解析和重新格式化时间戳
                            dt = timestamp.split(".")[0]  # 移除毫秒
                            formatted_time = dt.replace("T", " ")
                            memory_text = f"[{formatted_time}] {content}"
                        except:
                            memory_text = f"[{timestamp}] {content}"
                    else:
                        memory_text = content
                    
                    # 包含相关度得分信息
                    if score > 0:
                        memory_text += f" (相关度: {score:.1f})"
                    
                    memories.append((timestamp or "0", memory_text))

            # 按时间戳降序排序（最新的在前）
            memories.sort(key=lambda x: x[0], reverse=True)

            # 提取格式化的字符串
            memories_str = "\n".join(f"- {memory[1]}" for memory in memories)
            logger.bind(tag=TAG).info(f"本地Mem0服务查询成功，返回{len(memories)}条记忆")
            logger.bind(tag=TAG).debug(f"查询结果: {memories_str}")
            return memories_str
        except Exception as e:
            logger.bind(tag=TAG).error(f"查询本地Mem0服务记忆失败: {str(e)}")
            logger.bind(tag=TAG).error(f"详细错误信息: {traceback.format_exc()}")
            return ""

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.session.close()