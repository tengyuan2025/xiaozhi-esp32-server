#!/usr/bin/env python3
"""
测试音色角色管理器
"""
import sys
import os

# 添加项目路径
sys.path.append('/Users/yushuangyang/workspace/xiaozhi-esp32-server/main/xiaozhi-server')

from core.utils.role_manager import VoiceRoleManager
from core.utils.dialogue import Message


def test_voice_role_manager():
    """测试音色角色管理器"""
    print("🔧 测试音色角色管理器...")
    
    # 创建角色管理器
    role_manager = VoiceRoleManager()
    
    # 创建测试消息
    messages = [
        Message(role="user", content="我是张三，今天天气很好", voice_hash="voice_hash_user1"),
        Message(role="assistant", content="你好张三，是的，今天的天气确实很好！"),
        Message(role="user", content="我是李四，我也觉得今天适合出去散步", voice_hash="voice_hash_user2"),
        Message(role="assistant", content="李四你好！确实是散步的好天气"),
        Message(role="user", content="张三：好主意，我们一起去吧！", voice_hash="voice_hash_user1"),
    ]
    
    print(f"原始消息数量: {len(messages)}")
    
    # 为消息分配角色信息
    enhanced_messages = role_manager.assign_roles_to_messages(messages)
    
    print("\n=== 增强后的消息 ===")
    for i, msg in enumerate(enhanced_messages):
        print(f"消息 {i+1}:")
        print(f"  角色: {msg.role}")
        print(f"  内容: {msg.content}")
        print(f"  角色ID: {getattr(msg, 'role_id', None)}")
        print(f"  角色名称: {getattr(msg, 'role_name', None)}")
        print(f"  音色哈希: {getattr(msg, 'voice_hash', None)}")
        print()
    
    # 获取参与者信息
    participants = role_manager.get_participants_from_messages(enhanced_messages)
    
    print("=== 对话参与者 ===")
    for participant_id, participant_info in participants.items():
        print(f"参与者ID: {participant_id}")
        print(f"角色名称: {participant_info['role_name']}")
        print(f"音色哈希: {participant_info['voice_hash']}")
        print()
    
    print(f"总参与者数量: {len(participants)}")
    print("✅ 音色角色管理器测试完成！")
    
    # 关闭连接
    role_manager.close()
    
    return participants, enhanced_messages


if __name__ == "__main__":
    try:
        participants, messages = test_voice_role_manager()
        print(f"\n🎯 预期结果: 为 {len(participants)} 个参与者生成记忆")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()