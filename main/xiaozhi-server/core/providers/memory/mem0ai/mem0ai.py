import traceback

from ..base import MemoryProviderBase, logger
from mem0 import MemoryClient
from core.utils.util import check_model_key

TAG = __name__


class MemoryProvider(MemoryProviderBase):
    def __init__(self, config, summary_memory=None):
        super().__init__(config)
        self.api_key = config.get("api_key", "")
        self.api_version = config.get("api_version", "v1.1")
        
        logger.bind(tag=TAG).info(f"初始化Mem0ai - API密钥: {'已配置' if self.api_key else '未配置'}, 版本: {self.api_version}")
        
        model_key_msg = check_model_key("Mem0ai", self.api_key)
        if model_key_msg:
            logger.bind(tag=TAG).error(f"Mem0ai密钥检查失败: {model_key_msg}")
            self.use_mem0 = False
            return
        else:
            self.use_mem0 = True
            logger.bind(tag=TAG).info("Mem0ai密钥检查通过")

        try:
            logger.bind(tag=TAG).info("正在连接到Mem0ai服务...")
            self.client = MemoryClient(api_key=self.api_key)
            logger.bind(tag=TAG).info("成功连接到 Mem0ai 服务")
        except Exception as e:
            logger.bind(tag=TAG).error(f"连接到 Mem0ai 服务时发生错误: {str(e)}")
            logger.bind(tag=TAG).error(f"详细错误: {traceback.format_exc()}")
            self.use_mem0 = False

    async def save_memory(self, msgs):
        if not self.use_mem0:
            logger.bind(tag=TAG).info("Mem0ai未启用，跳过记忆保存")
            return None
        if len(msgs) < 2:
            logger.bind(tag=TAG).info(f"消息数量不足（{len(msgs)} < 2），跳过记忆保存")
            return None

        try:
            # Format the content as a message list for mem0
            messages = [
                {"role": message.role, "content": message.content}
                for message in msgs
                if message.role != "system"
            ]
            logger.bind(tag=TAG).info(f"开始保存记忆到Mem0ai - 用户ID: {self.role_id}, 消息数量: {len(messages)}")
            logger.bind(tag=TAG).debug(f"发送到Mem0ai的消息: {messages}")
            
            result = self.client.add(
                messages, user_id=self.role_id, output_format=self.api_version
            )
            logger.bind(tag=TAG).info(f"Mem0ai记忆保存成功: {result}")
            return result
        except Exception as e:
            logger.bind(tag=TAG).error(f"保存记忆到Mem0ai失败: {str(e)}")
            logger.bind(tag=TAG).error(f"详细错误信息: {traceback.format_exc()}")
            return None

    async def query_memory(self, query: str) -> str:
        if not self.use_mem0:
            logger.bind(tag=TAG).debug("Mem0ai未启用，返回空记忆")
            return ""
        try:
            logger.bind(tag=TAG).info(f"开始查询Mem0ai记忆 - 用户ID: {self.role_id}, 查询: {query}")
            
            results = self.client.search(
                query, user_id=self.role_id, output_format=self.api_version
            )
            
            logger.bind(tag=TAG).debug(f"Mem0ai查询原始结果: {results}")
            
            if not results or "results" not in results:
                logger.bind(tag=TAG).info("Mem0ai查询无结果")
                return ""

            # Format each memory entry with its update time up to minutes
            memories = []
            for entry in results["results"]:
                timestamp = entry.get("updated_at", "")
                if timestamp:
                    try:
                        # Parse and reformat the timestamp
                        dt = timestamp.split(".")[0]  # Remove milliseconds
                        formatted_time = dt.replace("T", " ")
                    except:
                        formatted_time = timestamp
                memory = entry.get("memory", "")
                if timestamp and memory:
                    # Store tuple of (timestamp, formatted_string) for sorting
                    memories.append((timestamp, f"[{formatted_time}] {memory}"))

            # Sort by timestamp in descending order (newest first)
            memories.sort(key=lambda x: x[0], reverse=True)

            # Extract only the formatted strings
            memories_str = "\n".join(f"- {memory[1]}" for memory in memories)
            logger.bind(tag=TAG).info(f"Mem0ai查询成功，返回{len(memories)}条记忆")
            logger.bind(tag=TAG).debug(f"查询结果: {memories_str}")
            return memories_str
        except Exception as e:
            logger.bind(tag=TAG).error(f"查询Mem0ai记忆失败: {str(e)}")
            logger.bind(tag=TAG).error(f"详细错误信息: {traceback.format_exc()}")
            return ""
