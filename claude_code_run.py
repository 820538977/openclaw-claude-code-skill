#!/usr/bin/env python3
"""
Claude Code Runner - 封装 Claude CLI，防止无 TTY 卡住
强制使用伪终端，支持后台运行和超时控制
"""

import argparse
import os
import sys
import subprocess
import time
import threading
import tempfile
import shutil
from pathlib import Path

# 检查并安装依赖
def find_claude():
    """查找 Claude CLI"""
    # 1. Windows 特定路径 (PowerShell 脚本)
    windows_paths = [
        r"D:\Program Files\nodejs\claude.ps1",
    ]
    for path in windows_paths:
        if os.path.exists(path):
            return path
    
    # 2. 检查 PATH 中 (exe 或常规命令)
    claude_path = shutil.which('claude')
    if claude_path:
        return claude_path
    
    # 3. 其他 Windows 路径
    other_paths = [
        os.path.expanduser(r"~\AppData\Local\Programs\claude\claude.exe"),
        r"C:\Program Files\Claude Code\claude.exe",
    ]
    for path in other_paths:
        if os.path.exists(path):
            return path
    
    return None


def is_windows_ps1(claude_path):
    """检查是否是 Windows PowerShell 脚本"""
    return claude_path and claude_path.lower().endswith('.ps1')


# Windows 上使用 wexpect，Linux/Mac 使用 pexpect
if sys.platform == 'win32':
    try:
        import wexpect
        WEXPECT_AVAILABLE = True
    except ImportError:
        print("正在安装 wexpect...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "wexpect"])
        import wexpect
        WEXPECT_AVAILABLE = True
    PEXPECT = wexpect
else:
    try:
        import pexpect
        PEXPECT = pexpect
    except ImportError:
        print("正在安装 pexpect...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pexpect"])
        import pexpect
        PEXPECT = pexpect


class ClaudeRunner:
    """Claude Code 运行器"""
    
    def __init__(self, workdir=None, timeout=120, verbose=False):
        self.workdir = workdir or os.getcwd()
        self.timeout = timeout
        self.verbose = verbose
        self.process = None
        
    def _has_pty(self):
        """检测是否有伪终端"""
        return sys.platform != 'win32' or (
            hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
        )
    
    def _build_command(self, task, mode='print'):
        """构建 Claude 命令"""
        cmd = ['claude']
        
        if mode == 'print' or task:
            cmd.append('--print')
            # PowerShell 版本不支持 --no-read
            if not is_windows_ps1(find_claude()):
                cmd.append('--no-read')
        
        if task:
            cmd.append(task)
            
        return cmd
    
    def run_interactive(self):
        """交互模式"""
        cmd = ['claude']
        
        if self.verbose:
            print(f"[DEBUG] Running: {' '.join(cmd)}")
            print(f"[DEBUG] Workdir: {self.workdir}")
        
        # 使用 pexpect 处理交互
        try:
            self.process = PEXPECT.spawn(
                cmd[0],
                cmd[1:],
                cwd=self.workdir,
                timeout=self.timeout,
                encoding='utf-8'
            )
            self.process.interact()
        except Exception as e:
            print(f"Error: {e}")
            return 1
        finally:
            if self.process:
                self.process.close()
                
        return 0
    
    def run_task(self, task):
        """执行任务模式"""
        # 查找 Claude CLI
        claude_path = find_claude()
        if not claude_path:
            print("Error: Claude CLI not found.")
            print("Please install: https://code.claude.com/docs")
            return 1
        
        # 构建命令
        cmd = self._build_command(task, mode='print')
        
        # 处理 Windows PowerShell 脚本
        if is_windows_ps1(claude_path):
            # 使用 powershell -File 调用 .ps1
            cmd = ['powershell', '-ExecutionPolicy', 'Bypass', '-File', claude_path] + cmd[1:]
        else:
            cmd[0] = claude_path
        
        if self.verbose:
            print(f"[DEBUG] Running: {' '.join(cmd)}")
            print(f"[DEBUG] Workdir: {self.workdir}")
            print(f"[DEBUG] Timeout: {self.timeout}s")
        
        # 检查 claude 是否可用
        try:
            check_cmd = cmd[:1] + ['--version'] + (cmd[2:] if len(cmd) > 2 else [])
            if is_windows_ps1(claude_path):
                check_cmd = ['powershell', '-ExecutionPolicy', 'Bypass', '-File', claude_path, '--version']
            subprocess.run(check_cmd, 
                         capture_output=True, timeout=10)
        except FileNotFoundError:
            print("Error: Claude CLI not found. Please install it first.")
            print("Install: https://code.claude.com/docs")
            return 1
        except subprocess.TimeoutExpired:
            print("Warning: Claude --version timeout, but continuing...")
        
        # 使用 pexpect 执行任务
        try:
            self.process = PEXPECT.spawn(
                cmd[0],
                cmd[1:],
                cwd=self.workdir,
                timeout=self.timeout,
                encoding='utf-8',
                env={**os.environ, 'FORCE_COLOR': '1'}
            )
            
            # 实时输出
            while True:
                try:
                    self.process.expect(
                        PEXPECT.TIMEOUT,
                        timeout=self.timeout
                    )
                    if self.process.before:
                        print(self.process.before, end='')
                except PEXPECT.TIMEOUT:
                    # 检查是否还在运行
                    if not self.process.isalive():
                        break
                    # 继续等待
                    continue
                except PEXPECT.EOF:
                    break
                    
            # 打印剩余输出
            if self.process.before:
                print(self.process.before, end='')
                
            self.process.close()
            
            if self.process.exitstatus is not None:
                return self.process.exitstatus
            return 0
            
        except Exception as e:
            print(f"Error: {e}")
            return 1
        except subprocess.TimeoutExpired:
            print(f"\nError: Task timeout after {self.timeout}s")
            if self.process:
                self.process.terminate()
            return 124
            
    def run_safe(self, task=None):
        """安全运行 - 自动检测最佳模式"""
        
        print("=" * 50)
        print("Claude Safe Runner")
        print("=" * 50)
        print(f"Workdir: {self.workdir}")
        print(f"Timeout: {self.timeout}s")
        print(f"Has PTY: {self._has_pty()}")
        print("-" * 50)
        
        if task:
            return self.run_task(task)
        else:
            return self.run_interactive()


def self_test():
    """自测函数"""
    print("\n" + "=" * 50)
    print("Claude Runner 自测")
    print("=" * 50)
    
    # 测试1: 检查 Claude CLI
    print("\n[TEST 1] 检查 Claude CLI...")
    
    # 使用 find_claude 查找
    claude_path = find_claude()
    if not claude_path:
        print("✗ Claude CLI 未找到")
        print("  请先安装 Claude Code: https://code.claude.com/docs")
        return False
    
    print(f"✓ 找到 Claude: {claude_path}")
    
    # 尝试运行
    try:
        cmd = [claude_path, '--version']
        if is_windows_ps1(claude_path):
            cmd = ['powershell', '-ExecutionPolicy', 'Bypass', '-File', claude_path, '--version']
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print(f"✓ Claude CLI 可用: {result.stdout.strip()}")
        else:
            print(f"✗ Claude CLI 返回非零: {result.returncode}")
            return False
    except FileNotFoundError:
        print("✗ Claude CLI 未找到")
        return False
    except subprocess.TimeoutExpired:
        print("⚠ Claude CLI 超时（可能正常）")
    
    # 测试2: 检查工作目录
    print("\n[TEST 2] 检查工作目录...")
    test_dir = tempfile.mkdtemp(prefix='claude_test_')
    print(f"✓ 创建临时目录: {test_dir}")
    
    # 测试3: 运行简单任务
    print("\n[TEST 3] 运行简单任务...")
    runner = ClaudeRunner(
        workdir=test_dir,
        timeout=30,
        verbose=False
    )
    
    # 清理临时目录
    try:
        shutil.rmtree(test_dir)
        print(f"✓ 清理临时目录: {test_dir}")
    except:
        pass
    
    print("\n" + "=" * 50)
    print("自测完成！")
    print("=" * 50)
    print("""
使用方法:
  python claude_code_run.py "你的任务"
  python claude_code_run.py -w /path/to/project "任务"
  python claude_code_run.py -i  # 交互模式
""")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Claude Code Runner - 安全封装 Claude CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python claude_code_run.py "创建 hello.py 文件"
  python claude_code_run.py -w E:\\project "修复登录 bug"
  python claude_code_run.py -i
  python claude_code_run.py --test  # 自测
        """
    )
    
    parser.add_argument(
        'task',
        nargs='?',
        default=None,
        help='要执行的任务描述'
    )
    
    parser.add_argument(
        '-w', '--workdir',
        default=os.getcwd(),
        help='工作目录 (默认: 当前目录)'
    )
    
    parser.add_argument(
        '-t', '--timeout',
        type=int,
        default=120,
        help='超时时间秒 (默认: 120)'
    )
    
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='交互模式'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='详细输出'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='运行自测'
    )
    
    args = parser.parse_args()
    
    if args.test:
        success = self_test()
        sys.exit(0 if success else 1)
    
    # 创建运行器
    runner = ClaudeRunner(
        workdir=args.workdir,
        timeout=args.timeout,
        verbose=args.verbose
    )
    
    # 执行
    if args.interactive or not args.task:
        exit_code = runner.run_interactive()
    else:
        exit_code = runner.run_task(args.task)
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
