import traceback
import os
from ..base import MemoryProviderBase, logger
from core.utils.util import check_model_key
import requests
import time  # 放在函数内部避免全局污染

TAG = __name__


class MemoryProvider(MemoryProviderBase):
    def __init__(self, config, summary_memory=None):
        super().__init__(config)
        self.use_mem0 = True


    async def save_memory(self, msgs, session_id=None):
        if not self.use_mem0:
            return None
        if len(msgs) < 2:
            return None

        try:
            from core.utils.role_manager import VoiceRoleManager
            
            # 初始化角色管理器
            role_manager = VoiceRoleManager()
            
            # 为消息分配角色信息
            enhanced_msgs = role_manager.assign_roles_to_messages(msgs)
            
            # 获取对话中的所有参与者
            participants = role_manager.get_participants_from_messages(enhanced_msgs)
            
            print(f"对话参与者: {participants}")
            print(f"开始生成 {len(participants)} 个参与者的总结记忆...")
            
            # 首先清除该session中现有的记忆，避免重复
            if session_id:
                try:
                    clear_payload = {"session_id": session_id}
                    clear_resp = requests.delete("http://localhost:5001/clear_session", json=clear_payload)
                    print(f"清除session {session_id} 的旧记忆: {clear_resp.status_code}")
                except Exception as e:
                    print(f"清除旧记忆失败: {e}")
            
            # 构建完整的对话上下文，用于智能事实提取
            full_conversation_context = []
            for message in enhanced_msgs:
                if message.role != "system":
                    role_info = participants.get(getattr(message, 'role_id', None), {})
                    role_name = role_info.get('role_name', '未知')
                    full_conversation_context.append(f"{role_name}: {message.content}")
            
            complete_conversation = "\n".join(full_conversation_context)
            print(f"完整对话上下文构建完成，共{len(full_conversation_context)}条消息")
            
            # 为每个参与者生成基于完整对话上下文的记忆
            results = []
            for participant_id, participant_info in participants.items():
                # 收集该参与者的发言（用于统计）
                participant_messages = []
                for message in enhanced_msgs:
                    if message.role != "system" and getattr(message, 'role_id', None) == participant_id:
                        participant_messages.append(message.content)
                
                # 如果该参与者有发言，则基于完整对话生成记忆
                if participant_messages:
                    # 创建上下文感知的消息，包含完整对话和目标参与者信息
                    context_aware_message = {
                        "role": "user", 
                        "content": f"以下是完整对话内容：\n{complete_conversation}\n\n请基于上述完整对话，提取与参与者 {participant_info['role_name']} 相关的事实信息。注意：\n1. 问答关系：如果{participant_info['role_name']}回答了问题，将答案作为{participant_info['role_name']}的事实\n2. 如果{participant_info['role_name']}提出的问题没有得到回答，不记录该问题\n3. 跳过无意义的打招呼和客套话\n4. 专注于客观、可验证的事实信息"
                    }
                    
                    # 使用mem0标准接口进行上下文感知的事实提取
                    payload = {
                        "msgs": [context_aware_message],
                        "user_id": self.role_id,  # 保持原始设备ID
                        "session_id": session_id,
                        "role_id": participant_id,
                        "role_name": participant_info['role_name']
                    }
                    
                    # 添加音色信息
                    if participant_info.get('voice_hash'):
                        payload["voice_hash"] = participant_info['voice_hash']
                    
                    print(f"为参与者 {participant_info['role_name']} (ID: {participant_id}) 基于完整对话上下文生成事实记忆")
                    print(f"参与者发言数: {len(participant_messages)}")
                    print(f"对话总轮次: {len(full_conversation_context)}")
                    
                    resp = requests.post("http://localhost:5001/add", json=payload)
                    participant_result = resp.json()
                    participant_result['participant'] = participant_info
                    participant_result['context_messages'] = len(full_conversation_context)
                    participant_result['participant_messages'] = len(participant_messages)
                    results.append(participant_result)
            
            # 关闭角色管理器连接
            role_manager.close()
            
            print(f"✅ 成功为 {len(participants)} 个参与者生成总结记忆")
            return {
                "total_participants": len(participants),
                "memories_created": len(results),
                "participants": list(participants.values()),
                "results": results
            }
            
        except Exception as e:
            logger.bind(tag=TAG).error(f"保存记忆失败: {str(e)}")
            return None
    
    def _generate_participant_summary(self, combined_content, role_name):
        """为参与者生成总结内容"""
        # 简单的关键词提取和合并逻辑
        # 可以根据需要增强这个函数，例如使用NLP技术
        
        # 基本的重复内容去除和关键信息提取
        sentences = combined_content.split('。')
        key_info = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 3:
                # 简单去重：避免相似内容
                is_duplicate = False
                for existing in key_info:
                    if len(set(sentence) & set(existing)) / len(set(sentence)) > 0.7:
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    key_info.append(sentence)
        
        # 合并关键信息
        if len(key_info) <= 1:
            return combined_content
        else:
            return "，".join(key_info[:3])  # 最多保留3个关键点

    async def query_memory(self, query: str) -> str:
        if not self.use_mem0:
            return ""
        try:
            params = {
                "query": query,
                "user_id": self.role_id
            }
            start_time = time.time()
            resp = requests.get("http://localhost:5001/search", params=params)
            elapsed = time.time() - start_time
            print(f"Memory search请求耗时: {elapsed:.3f}秒, {params}")
            result = resp.json()
            if not result or "results" not in result:
                return ""

            memories = []
            for entry in result["results"].get("results", []):
                timestamp = entry.get("updated_at", "")
                if timestamp:
                    try:
                        dt = timestamp.split(".")[0]
                        formatted_time = dt.replace("T", " ")
                    except:
                        formatted_time = timestamp
                memory = entry.get("memory", "")
                if timestamp and memory:
                    memories.append((timestamp, f"[{formatted_time}] {memory}"))

            memories.sort(key=lambda x: x[0], reverse=True)
            memories_str = "\n".join(f"- {memory[1]}" for memory in memories)
            logger.bind(tag=TAG).debug(f"Query results: {memories_str}")
            return memories_str
        except Exception as e:
            logger.bind(tag=TAG).error(f"查询记忆失败: {str(e)}")
            return ""