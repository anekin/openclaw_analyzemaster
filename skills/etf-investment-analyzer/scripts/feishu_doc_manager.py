#!/usr/bin/env python3
"""
Feishu Document Manager - 创建并移动飞书文档到指定文件夹
"""
import subprocess
import json
import re
import sys
from datetime import datetime


def create_feishu_doc(title: str, content: str) -> str:
    """Create Feishu document using openclaw CLI"""
    print(f"📄 创建飞书文档: {title}")
    
    # Build the command
    cmd = ['openclaw', 'tools', 'feishu_doc', 'create', '--title', title, '--content', content]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = result.stdout + result.stderr
        
        # Parse document token from output
        # Look for patterns like: "document_id": "xxx" or document_id: xxx
        patterns = [
            r'"document_id"[:\s]*"([a-zA-Z0-9_-]+)"',
            r'"doc_token"[:\s]*"([a-zA-Z0-9_-]+)"',
            r'document[_-]?id[:\s]*([a-zA-Z0-9_-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                return match.group(1)
        
        print(f"⚠️ 无法解析文档ID")
        print(f"输出: {output[:500]}")
        return None
        
    except Exception as e:
        print(f"❌ 创建文档失败: {e}")
        return None


def move_feishu_doc(file_token: str, folder_token: str) -> bool:
    """Move Feishu document to target folder using openclaw CLI"""
    print(f"📁 移动文档到目标文件夹...")
    
    cmd = ['openclaw', 'tools', 'feishu_drive', 'move', 
           '--file-token', file_token, 
           '--folder-token', folder_token]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"✅ 文档移动成功")
            return True
        else:
            print(f"⚠️ 移动文档失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 移动文档失败: {e}")
        return False


def main():
    """Main entry point for testing"""
    if len(sys.argv) < 2:
        print("Usage: python3 feishu_doc_manager.py <action> [args]")
        print("Actions: create, move, create-and-move")
        return
    
    action = sys.argv[1]
    
    if action == "create-and-move":
        # Test: Create a doc and move it
        today = datetime.now().strftime('%Y-%m-%d')
        title = f"ETF交易日报-{today}"
        content = f"# {title}\n\n测试内容 - {datetime.now().strftime('%H:%M')}"
        folder_token = "YeEEfZ0f1lvroGdQnCGc6EMvn4b"
        
        doc_token = create_feishu_doc(title, content)
        if doc_token:
            print(f"✅ 文档创建成功: {doc_token}")
            print(f"🔗 链接: https://feishu.cn/docx/{doc_token}")
            
            if move_feishu_doc(doc_token, folder_token):
                print(f"✅ 完整流程完成!")
            else:
                print(f"⚠️ 文档已创建但未移动到目标文件夹")
        else:
            print(f"❌ 文档创建失败")


if __name__ == '__main__':
    main()
