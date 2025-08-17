#!/usr/bin/env python3
"""测试本地 mem0 API 接口"""

import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8004"

async def test_mem0_api():
    """测试 mem0 API 的基本功能"""
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30) as client:
        print(f"测试 mem0 API - 基础URL: {BASE_URL}")
        print("=" * 50)
        
        # 1. 测试保存记忆
        print("\n1. 测试保存记忆 (POST /memories)")
        messages = [
            {"role": "user", "content": "我叫小明，今年25岁"},
            {"role": "assistant", "content": "很高兴认识你，小明！25岁正是青春年华。"}
        ]
        
        save_data = {
            "messages": messages,
            "user_id": "test_user_123",
            "metadata": {
                "source": "xiaozhi-esp32",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        try:
            response = await client.post("/v1/memories/", json=save_data)
            print(f"状态码: {response.status_code}")
            print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
            
            if response.status_code == 200:
                print("✅ 保存记忆成功！")
            else:
                print("❌ 保存记忆失败")
        except Exception as e:
            print(f"❌ 保存记忆出错: {type(e).__name__}: {e}")
        
        # 2. 测试搜索记忆
        print("\n\n2. 测试搜索记忆 (POST /search)")
        search_data = {
            "query": "我的名字",
            "user_id": "test_user_123",
            "limit": 10
        }
        
        try:
            response = await client.post("/v1/memories/search", json=search_data)
            print(f"状态码: {response.status_code}")
            result = response.json()
            print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            if response.status_code == 200:
                print("✅ 搜索记忆成功！")
                if "results" in result and result["results"]:
                    print(f"找到 {len(result['results'])} 条相关记忆")
                else:
                    print("未找到相关记忆")
            else:
                print("❌ 搜索记忆失败")
        except Exception as e:
            print(f"❌ 搜索记忆出错: {type(e).__name__}: {e}")
        
        # 3. 测试获取所有记忆
        print("\n\n3. 测试获取所有记忆 (GET /memories)")
        try:
            response = await client.get("/v1/memories/", params={"user_id": "test_user_123"})
            print(f"状态码: {response.status_code}")
            memories = response.json()
            print(f"响应: {json.dumps(memories, ensure_ascii=False, indent=2)}")
            
            if response.status_code == 200:
                print("✅ 获取记忆成功！")
                if isinstance(memories, list):
                    print(f"总共有 {len(memories)} 条记忆")
            else:
                print("❌ 获取记忆失败")
        except Exception as e:
            print(f"❌ 获取记忆出错: {type(e).__name__}: {e}")

async def test_health_check():
    """测试服务是否运行"""
    try:
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=5) as client:
            # 尝试多个端点来检查服务状态
            for endpoint in ["/", "/docs", "/openapi.json"]:
                try:
                    response = await client.get(endpoint)
                    print(f"健康检查 {endpoint} - 状态码: {response.status_code}")
                    if response.status_code in [200, 307, 503]:  # 503 可能是服务启动但有问题
                        print("✅ mem0 服务正在运行")
                        return True
                except:
                    continue
    except Exception as e:
        print(f"❌ 无法连接到 mem0 服务: {type(e).__name__}: {e}")
        print(f"请确保 mem0 服务正在 {BASE_URL} 上运行")
        return False
    return False

if __name__ == "__main__":
    print("开始测试本地 mem0 API...")
    print("请确保 mem0 服务已启动在 http://127.0.0.1:8004")
    print("-" * 50)
    
    # 先检查服务是否运行
    if asyncio.run(test_health_check()):
        # 运行主测试
        asyncio.run(test_mem0_api())
    else:
        print("\n请先启动 mem0 服务:")
        print("cd /Users/yushuangyang/workspace/mem0")
        print("python server/main.py")