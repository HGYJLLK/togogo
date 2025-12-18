#!/usr/bin/env python3
"""
针对性二次扫描 - 基于首页线索
目标目录: /admin, /api, /backup, /config, /uploads
"""

import requests
import concurrent.futures
from urllib.parse import urljoin

requests.packages.urllib3.disable_warnings()

target = "http://47.113.178.182:32820/"
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

# 基于首页提示的目标目录
base_dirs = ['admin', 'api', 'backup', 'config', 'uploads', 'upload', 'test', 'dev']

# 每个目录下可能的文件
files = [
    'index.html', 'index.php', 'index.htm',
    'flag.txt', 'flag.php', 'flag.html', 'flag',
    'main.php', 'home.php', 'login.php',
    'config.php', 'settings.php',
    'info.php', 'phpinfo.php',
    'data.txt', 'secret.txt', 'key.txt',
    'readme.txt', 'README.txt',
    'backup.zip', 'backup.sql', 'db.sql',
    'test.php', 'admin.php'
]

# 生成完整路径列表
paths = []

# 1. 直接访问目录
for dir in base_dirs:
    paths.append(dir)
    paths.append(dir + '/')

# 2. 目录下的文件
for dir in base_dirs:
    for file in files:
        paths.append(f'{dir}/{file}')

# 3. 一些特殊路径
special_paths = [
    'flag.txt', 'flag.php', 'flag.html', 'flag',
    'fl4g.txt', 'f1ag.txt', 'key.txt',
    'robots.txt', 'sitemap.xml',
    '.git/config', '.git/HEAD',
    'index.php.bak', 'config.php.bak',
    'www.zip', 'backup.zip', 'web.zip',
    'test.php', '1.php', 'shell.php',
    'phpinfo.php', 'info.php'
]

paths.extend(special_paths)
paths = list(set(paths))  # 去重

print(f"[*] 开始二次针对性扫描")
print(f"[*] 目标: {target}")
print(f"[*] 扫描路径数: {len(paths)}")
print("-" * 70)

found = []

def check(path):
    url = urljoin(target, path)
    try:
        r = session.get(url, timeout=5, allow_redirects=False, verify=False)
        if r.status_code in [200, 201, 301, 302, 401, 403]:
            return {
                'url': url,
                'status': r.status_code,
                'size': len(r.content),
                'path': path
            }
    except:
        pass
    return None

with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
    futures = {executor.submit(check, path): path for path in paths}

    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        if result:
            found.append(result)
            icon = "[✓]" if result['status'] == 200 else "[!]"
            print(f"{icon} [{result['status']}] {result['url']} ({result['size']} bytes)")

print("\n" + "=" * 70)
print(f"[+] 发现 {len(found)} 个路径")

# 重点显示200状态码
status_200 = [x for x in found if x['status'] == 200]
if status_200:
    print("\n[重点关注] 状态码200的路径:")
    for item in status_200:
        print(f"  ★ {item['url']}")
        # 如果包含flag关键词，特别标注
        if 'flag' in item['path'].lower():
            print(f"     ⚠️  可能包含FLAG!")
