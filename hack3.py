#!/usr/bin/env python3
"""
暴力扫描 - 更多文件名和扩展名组合
"""

import requests
import concurrent.futures

requests.packages.urllib3.disable_warnings()

target = "http://47.113.178.182:32820/"
session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0'})

# flag的各种变体
flag_names = [
    'flag', 'Flag', 'FLAG', 'fl4g', 'f1ag', 'flAg', 'FLag',
    'key', 'secret', 'password', 'pass', 'hint', 'readme',
    'flag_', '_flag', 'flag1', 'flag2', 'myflag', 'theflag',
    'flagfile', 'flaghere', 'getflag'
]

# 更多扩展名
extensions = [
    '', '.txt', '.php', '.html', '.htm', '.zip', '.rar',
    '.bak', '.old', '.swp', '~', '.backup', '.data',
    '.log', '.sql', '.db', '.json', '.xml', '.conf',
    '.inc', '.ini', '.md', '.doc', '.pdf'
]

# 目录+flag组合
directories = ['', 'admin/', 'backup/', 'config/', 'api/', 'uploads/', 'test/', 'dev/', 'tmp/', 'temp/']

paths = []

# 生成所有组合
for dir in directories:
    for name in flag_names:
        for ext in extensions:
            paths.append(f'{dir}{name}{ext}')

# 添加一些特殊路径
special = [
    'robots.txt', 'sitemap.xml', '.git/config', '.git/HEAD',
    'index.php.bak', 'index.html.bak', 'www.zip', 'backup.zip',
    '1.txt', '2.txt', 'test.txt', 'info.txt'
]
paths.extend(special)
paths = list(set(paths))

print(f"[*] 暴力扫描模式")
print(f"[*] 生成路径: {len(paths)} 个")
print(f"[*] 开始扫描...\n")

found = []

def check(path):
    url = target + path
    try:
        r = session.get(url, timeout=5, allow_redirects=False, verify=False)
        if r.status_code == 200:
            return {'url': url, 'size': len(r.content), 'path': path, 'content': r.text[:200]}
    except:
        pass
    return None

with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
    futures = {executor.submit(check, path): path for path in paths}

    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        if result:
            found.append(result)
            print(f"[✓] {result['url']} ({result['size']} bytes)")
            if 'flag' in result['path'].lower():
                print(f"    ⚠️  POTENTIAL FLAG FILE!")
                print(f"    预览: {result['content'][:100]}...")

print(f"\n[+] 找到 {len(found)} 个文件")

if found:
    print("\n[重点] 发现的文件:")
    for item in found:
        print(f"  • {item['url']}")
