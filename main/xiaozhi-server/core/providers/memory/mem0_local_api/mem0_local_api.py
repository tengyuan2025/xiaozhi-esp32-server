import traceback
import httpx
from typing import Optional, List, Dict
from ..base import MemoryProviderBase, logger

TAG = __name__


class MemoryProvider(MemoryProviderBase):
    def __init__(self, config, summary_memory=None):
        super().__init__(config)
        self.base_url = config.get("base_url", "http://localhost:8004")
        self.api_key = config.get("api_key", "")
        self.timeout = config.get("timeout", 30)
        
        logger.bind(tag=TAG).info(f"初始化本地Mem0服务 - 地址: {self.base_url}")
        
        # 创建 HTTP 客户端
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}" if self.api_key else "",
                "Content-Type": "application/json"
            },
            timeout=self.timeout
        )
        
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
            
            # 调用本地 mem0 服务的 add 接口
            response = await self.client.post(
                "/v1/memories",
                json={
                    "messages": messages,
                    "user_id": self.role_id,
                    "metadata": {
                        "source": "xiaozhi-esp32"
                    }
                }
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
            response = await self.client.post(
                "/v1/memories/search",
                json={
                    "query": query,
                    "user_id": self.role_id,
                    "limit": 10
                }
            )
            response.raise_for_status()
            
            results = response.json()
            logger.bind(tag=TAG).debug(f"本地Mem0服务查询原始结果: {results}")
            
            if not results or "results" not in results:
                logger.bind(tag=TAG).info("本地Mem0服务查询无结果")
                return ""

            # 格式化记忆条目
            memories = []
            for entry in results["results"]:
                timestamp = entry.get("updated_at", "")
                if timestamp:
                    try:
                        # 解析和重新格式化时间戳
                        dt = timestamp.split(".")[0]  # 移除毫秒
                        formatted_time = dt.replace("T", " ")
                    except:
                        formatted_time = timestamp
                memory = entry.get("memory", "")
                if timestamp and memory:
                    memories.append((timestamp, f"[{formatted_time}] {memory}"))

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
        await self.client.aclose()