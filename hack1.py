#!/usr/bin/env python3
"""
渗透测试实训 - 目录扫描和敏感文件发现
目标：http://47.113.178.182:32820/
目的：发现隐藏的管理页面、备份文件、配置文件等
"""

import requests
import concurrent.futures
from urllib.parse import urljoin
import sys
from typing import List, Set

# 禁用SSL警告
requests.packages.urllib3.disable_warnings()

class DirectoryScanner:
    def __init__(self, base_url: str, timeout: int = 5):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.found_paths = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def get_common_paths(self) -> List[str]:
        """返回常见的敏感路径列表 - 增强版"""
        paths = []

        # ========== 高频CTF路径 ==========
        # Git/SVN泄露（极其常见！）
        vcs_paths = [
            '.git/config', '.git/HEAD', '.git/index', '.git/logs/HEAD',
            '.svn/entries', '.svn/wc.db', '.hg/requires'
        ]

        # Flag相关（CTF必备）
        flag_paths = [
            'flag', 'flag.txt', 'flag.php', 'flag.html', 'flag.zip',
            'fl4g', 'fl4g.txt', 'f1ag.txt', 'FLAG', 'FLAG.txt',
            'key.txt', 'secret.txt', 'password.txt', 'pass.txt',
            'hint.txt', 'readme.txt', 'README.txt'
        ]

        # 备份文件（各种后缀组合）
        backup_bases = ['backup', 'back', 'bak', 'old', 'www', 'web', 'site',
                        'index', 'home', 'main', 'data', 'database', 'db']
        backup_exts = ['.zip', '.tar.gz', '.tar', '.rar', '.7z', '.bak',
                       '.old', '.sql', '.gz', '.tar.bz2']
        backup_paths = []
        for base in backup_bases:
            for ext in backup_exts:
                backup_paths.append(f'{base}{ext}')

        # PHP备份和临时文件
        php_backup = [
            'index.php.bak', 'index.php.old', 'index.php~', 'index.php.swp',
            '.index.php.swp', 'config.php.bak', 'config.php.old',
            'admin.php.bak', 'login.php.bak', 'upload.php.bak'
        ]

        # 管理页面
        admin_paths = [
            'admin', 'admin/', 'admin.php', 'admin.html', 'admin/login',
            'admin/index.php', 'administrator', 'manage', 'manager',
            'backend', 'console', 'control', 'dashboard', 'cms',
            'admin/admin.php', 'admin/index.html', 'login', 'login.php',
            'user/login', 'manage.php', 'system', 'sys'
        ]

        # 配置文件
        config_paths = [
            'config', 'config.php', 'config.inc.php', 'config.json',
            'config.xml', 'config.yml', 'configuration.php', 'settings.php',
            '.env', '.env.local', '.env.production', 'web.config',
            'app.config', 'database.yml', 'db.php', 'conn.php',
            'config/database.php', 'inc/config.php'
        ]

        # 上传目录和文件管理
        upload_paths = [
            'upload', 'uploads', 'upload/', 'uploads/', 'upload.php',
            'file', 'files', 'files/', 'uploadfiles', 'upfile.php',
            'images/', 'img/', 'media/', 'attachments/', 'attachment/',
            'static/upload/', 'public/upload/'
        ]

        # API和接口
        api_paths = [
            'api', 'api/', 'api/v1', 'api/v1/', 'api/v2', 'api/v2/',
            'rest', 'rest/', 'graphql', 'swagger', 'api-docs',
            'api/users', 'api/admin', 'api/config', 'api/user',
            'api/login', 'api/flag'
        ]

        # 测试和调试
        test_paths = [
            'test', 'test/', 'test.php', 'test.html', 'testing',
            'dev', 'dev/', 'development', 'debug', 'debug.php',
            'phpinfo.php', 'info.php', 'probe.php', 'p.php',
            'shell.php', '1.php', 'a.php', 'test1.php'
        ]

        # 敏感目录
        sensitive_dirs = [
            'temp/', 'tmp/', 'logs/', 'log/', 'cache/', 'backup/',
            'backups/', 'include/', 'includes/', 'inc/', 'data/',
            'db/', 'database/', 'sql/', 'mysql/', 'conf/', 'config/',
            'old/', 'bak/', 'www/', 'wwwroot/', 'web/', 'html/'
        ]

        # 信息收集文件
        info_files = [
            'robots.txt', 'sitemap.xml', 'crossdomain.xml',
            '.htaccess', 'web.config', '.user.ini',
            'README.md', 'readme.md', 'CHANGELOG', 'LICENSE',
            'composer.json', 'package.json', 'yarn.lock',
            '.gitignore', '.dockerignore'
        ]

        # 数据库相关
        db_paths = [
            'database.sql', 'db.sql', 'mysql.sql', 'data.sql',
            'backup.sql', '1.sql', 'dump.sql', 'phpmyadmin',
            'phpmyadmin/', 'pma/', 'mysql/', 'adminer.php'
        ]

        # 编辑器临时文件
        editor_temp = [
            '.index.php.swp', '.config.php.swp', '.admin.php.swp',
            'index.php~', 'config.php~', '.index.php.swo'
        ]

        # 常见页面（多种后缀）
        base_pages = ['index', 'home', 'main', 'default', 'login', 'user',
                      'admin', 'manage', 'upload', 'file', 'show', 'view']
        page_exts = ['', '.php', '.html', '.htm', '.txt', '.bak', '.old',
                     '.zip', '.rar', '.jsp', '.asp', '.aspx']
        page_paths = []
        for page in base_pages:
            for ext in page_exts:
                page_paths.append(f'{page}{ext}')

        # 数字文件名（CTF常见）
        number_files = [f'{i}.php' for i in range(10)] + [f'{i}.html' for i in range(10)]
        number_files += [f'{i}.txt' for i in range(10)] + [f'test{i}.php' for i in range(5)]

        # 隐藏文件
        hidden_files = [
            '.git', '.svn', '.htaccess', '.htpasswd', '.bash_history',
            '.mysql_history', '.DS_Store', 'Thumbs.db'
        ]

        # 合并所有路径
        paths.extend(vcs_paths)
        paths.extend(flag_paths)
        paths.extend(backup_paths)
        paths.extend(php_backup)
        paths.extend(admin_paths)
        paths.extend(config_paths)
        paths.extend(upload_paths)
        paths.extend(api_paths)
        paths.extend(test_paths)
        paths.extend(sensitive_dirs)
        paths.extend(info_files)
        paths.extend(db_paths)
        paths.extend(editor_temp)
        paths.extend(page_paths)
        paths.extend(number_files)
        paths.extend(hidden_files)

        # 去重并返回
        return list(set(paths))

    def check_path(self, path: str) -> dict:
        """检查单个路径是否存在"""
        url = urljoin(self.base_url + '/', path)
        try:
            response = self.session.get(
                url,
                timeout=self.timeout,
                allow_redirects=False,
                verify=False
            )

            # 检查响应状态码
            if response.status_code in [200, 201, 204, 301, 302, 307, 308, 401, 403]:
                return {
                    'url': url,
                    'status': response.status_code,
                    'size': len(response.content),
                    'path': path
                }
        except requests.exceptions.Timeout:
            pass
        except requests.exceptions.RequestException:
            pass

        return None

    def scan(self, max_workers: int = 20):
        """执行目录扫描"""
        print(f"[*] 开始扫描目标: {self.base_url}")
        print(f"[*] 使用 {max_workers} 个并发线程")
        print("-" * 70)

        paths = self.get_common_paths()
        print(f"[*] 共 {len(paths)} 个路径待扫描\n")

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.check_path, path): path for path in paths}

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    self.found_paths.append(result)
                    status_icon = self._get_status_icon(result['status'])
                    print(f"{status_icon} [{result['status']}] {result['url']} ({result['size']} bytes)")

        print("\n" + "=" * 70)
        print(f"[+] 扫描完成! 发现 {len(self.found_paths)} 个可访问路径")

        # 按状态码分类显示
        self._print_summary()

    def _get_status_icon(self, status: int) -> str:
        """根据状态码返回图标"""
        if status == 200:
            return "[✓]"
        elif status in [301, 302, 307, 308]:
            return "[→]"
        elif status in [401, 403]:
            return "[!]"
        else:
            return "[?]"

    def _print_summary(self):
        """打印扫描摘要"""
        if not self.found_paths:
            return

        print("\n" + "=" * 70)
        print("发现的路径分类:")
        print("=" * 70)

        # 按状态码分组
        status_groups = {}
        for item in self.found_paths:
            status = item['status']
            if status not in status_groups:
                status_groups[status] = []
            status_groups[status].append(item)

        # 优先显示200状态码
        for status in sorted(status_groups.keys(), key=lambda x: (x != 200, x)):
            print(f"\n[状态码: {status}] ({len(status_groups[status])} 个)")
            for item in status_groups[status]:
                print(f"  • {item['url']}")

        # 高亮可能包含flag的路径
        print("\n" + "=" * 70)
        print("可能包含FLAG的路径:")
        print("=" * 70)
        flag_keywords = ['flag', 'key', 'secret', 'admin', 'backup', 'config']
        potential_flags = [
            item for item in self.found_paths
            if any(keyword in item['path'].lower() for keyword in flag_keywords)
            and item['status'] == 200
        ]

        if potential_flags:
            for item in potential_flags:
                print(f"  ★ {item['url']} (重点关注!)")
        else:
            print("  (未发现明显可疑路径，请手动检查所有200状态码路径)")


def main():
    target_url = "http://47.113.178.182:32820/"

    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║         渗透测试实训 - 目录扫描工具                          ║
    ║         目标：发现隐藏的管理页面和敏感文件                    ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)

    scanner = DirectoryScanner(target_url, timeout=10)
    scanner.scan(max_workers=30)

    print("\n[*] 提示：")
    print("    1. 访问所有状态码为 200 的路径，查看页面内容")
    print("    2. 特别关注包含 'flag' 'admin' 'backup' 'config' 的路径")
    print("    3. 检查页面源代码，flag可能隐藏在HTML注释中")
    print("    4. 尝试访问发现的目录下的 index.html 或 index.php")
    print("    5. 对于403路径，尝试添加不同的扩展名绕过")


if __name__ == "__main__":
    main()
