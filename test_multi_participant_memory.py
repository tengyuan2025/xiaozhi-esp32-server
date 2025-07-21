#!/usr/bin/env python3
"""
测试多参与者记忆生成功能
"""
import requests
import json
import hashlib


def generate_voice_hash(text):
    """为测试生成音色哈希"""
    return hashlib.md5(text.encode()).hexdigest()


def test_multi_participant_memory():
    """测试多参与者对话记忆生成"""
    
    # 模拟一个有两个用户和一个助手的对话
    messages = [
        {
            "role": "user",
            "content": "我是张三，今天天气很好",
            "role_id": None,  # 将由系统自动分配
            "role_name": None,  # 将由系统自动分配
            "voice_hash": generate_voice_hash("user_voice_1")  # 用户1的音色
        },
        {
            "role": "assistant", 
            "content": "你好张三，是的，今天的天气确实很好！",
            "role_id": None,
            "role_name": None,
            "voice_hash": None  # 助手没有音色信息
        },
        {
            "role": "user",
            "content": "我是李四，我也觉得今天适合出去散步",
            "role_id": None,
            "role_name": None, 
            "voice_hash": generate_voice_hash("user_voice_2")  # 用户2的音色
        },
        {
            "role": "assistant",
            "content": "李四你好！确实是散步的好天气，你们可以一起去公园走走",
            "role_id": None,
            "role_name": None,
            "voice_hash": None
        },
        {
            "role": "user", 
            "content": "张三：好主意，我们一起去吧！",
            "role_id": None,
            "role_name": None,
            "voice_hash": generate_voice_hash("user_voice_1")  # 用户1的音色
        }
    ]
    
    # 准备API请求
    payload = {
        "msgs": messages,
        "user_id": "test_device_001",
        "session_id": "multi_participant_test_session_001"
    }
    
    print("正在测试多参与者记忆生成...")
    print(f"对话包含 {len(messages)} 条消息")
    print("参与者音色:")
    unique_voices = set()
    for msg in messages:
        if msg.get("voice_hash"):
            unique_voices.add(msg["voice_hash"])
    print(f"- 用户音色数量: {len(unique_voices)}")
    print(f"- 助手: 1个")
    print(f"预期生成记忆条数: {len(unique_voices) + 1}")  # 用户数量 + 助手
    
    try:
        # 发送请求到mem0 API
        response = requests.post("http://localhost:5001/add", json=payload)
        result = response.json()
        
        print("\n=== API 响应 ===")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if result.get("status") == "success":
            print("\n✅ 多参与者记忆生成测试成功！")
        else:
            print(f"\n❌ 测试失败: {result.get('message', '未知错误')}")
            
    except Exception as e:
        print(f"\n❌ 请求失败: {e}")

def test_query_memories():
    """测试查询多参与者记忆"""
    print("\n=== 测试记忆查询 ===")
    
    # 查询刚才创建的记忆
    query_params = {
        "user_id": "test_device_001_1",  # 查询用户1的记忆
        "session_id": "multi_participant_test_session_001"
    }
    
    try:
        response = requests.get("http://localhost:5001/list", params=query_params)
        result = response.json()
        
        print(f"用户1的记忆查询结果:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 查询助手的记忆
        query_params["user_id"] = "test_device_001_6"  # 假设助手的ID是6
        response = requests.get("http://localhost:5001/list", params=query_params)
        result = response.json()
        
        print(f"\n助手的记忆查询结果:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"查询失败: {e}")


if __name__ == "__main__":
    print("🚀 开始测试多参与者记忆生成功能")
    print("=" * 50)
    
    # 测试记忆生成
    test_multi_participant_memory()
    
    # 测试记忆查询
    test_query_memories()
    
    print("\n" + "=" * 50)
    print("✨ 测试完成！")