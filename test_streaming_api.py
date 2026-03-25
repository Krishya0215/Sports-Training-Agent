#!/usr/bin/env python3
"""
测试流式API的脚本
用于验证思考过程和答案的流式输出是否正常
"""
import asyncio
import json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def test_streaming_api():
    """测试流式API"""
    url = "http://localhost:8000/api/query"
    
    # 创建session支持重试机制
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["POST"],
        backoff_factor=1
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    
    # 测试问题
    question = "我今天应该进行什么样的训练？"
    
    print(f"发送问题: {question}")
    print("=" * 60)
    
    try:
        response = session.post(
            url,
            json={"question": question, "use_multi_agent": False},
            stream=True,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"错误: HTTP {response.status_code}")
            print(response.text)
            return
        
        print("开始接收流式数据...")
        print("-" * 60)
        
        thinking_content = ""
        answer_content = ""
        current_section = None
        
        for line in response.iter_lines():
            if not line:
                continue
            
            if isinstance(line, bytes):
                line = line.decode('utf-8')
            
            if line.startswith('data: '):
                try:
                    data = json.loads(line[6:])
                    
                    if 'error' in data:
                        print(f"❌ 错误: {data['error']}")
                        return
                    
                    msg_type = data.get('type', 'answer')
                    content = data.get('content', '')
                    done = data.get('done', False)
                    
                    if msg_type == 'thinking':
                        if current_section != 'thinking':
                            print("\n🧠 思考过程:")
                            current_section = 'thinking'
                        thinking_content += content
                        print(content, end='', flush=True)
                    elif msg_type == 'answer':
                        if current_section != 'answer':
                            print("\n\n💡 答案:")
                            current_section = 'answer'
                        answer_content += content
                        print(content, end='', flush=True)
                    
                    if done:
                        print(f"\n\n[{msg_type.upper()} 完成]")
                
                except json.JSONDecodeError as e:
                    print(f"JSON解析错误: {e}")
                    print(f"行内容: {line}")
        
        print("\n" + "=" * 60)
        print("流式数据接收完成！")
        print(f"\n思考过程字数: {len(thinking_content)}")
        print(f"答案字数: {len(answer_content)}")
        
    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("开始测试流式API...")
    print(f"请确保后端API服务器运行在 http://localhost:8000")
    print()
    test_streaming_api()
