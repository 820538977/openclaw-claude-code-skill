---
name: openclaw-claude-code
description: 通过 OpenClaw 调用 Claude Code 进行编码任务。适用于需要 Claude Code 编程助手的场景。
---

# OpenClaw 调用 Claude Code 技能

本技能提供通过 OpenClaw 调用 Claude Code 的完整解决方案。

## 核心功能

1. **PTY 安全调用** - 防止无 pty/tty 时卡住
2. **工作目录指定** - 在指定目录运行 Claude Code
3. **后台任务支持** - 长任务后台运行
4. **进度监控** - 实时查看执行状态

## 调用方法

### 1. 快速调用（一次性任务）

```javascript
exec({
  command: "claude -p '你的任务描述'",
  pty: true,
  workdir: "项目目录路径",
  timeout: 120
})
```

### 2. 交互式调用

```javascript
exec({
  command: "claude",
  pty: true,
  workdir: "项目目录路径",
  timeout: 300
})
```

### 3. 使用 claude-safe 包装器（推荐）

使用 `claude-safe` 命令，防止 pty 问题卡住：

```javascript
exec({
  command: "claude-safe '你的任务' --workdir 项目目录",
  pty: true,
  timeout: 120
})
```

## Claude-Safe 包装器

已创建 Python 版本，更稳定可靠。

### 安装

```bash
# 复制到用户脚本目录
mkdir -p ~/scripts
cp scripts/claude_code_run.py ~/scripts/

# 添加到 PATH (可选)
```

### 使用方法

```bash
# 自测
python claude_code_run.py --test

# 执行任务
python claude_code_run.py "创建一个 hello.py"
python claude_code_run.py -w E:\project "修复登录 bug"

# 交互模式
python claude_code_run.py -i
```

### OpenClaw 中调用

```javascript
exec({
  command: "python C:\\\\Users\\\\wqq\\\\.openclaw\\\\workspace\\\\scripts\\\\claude_code_run.py \"你的任务\"",
  pty: true,
  workdir: "E:\\\\project",
  timeout: 120
})
```

```powershell
# claude-safe.ps1
param(
    [Parameter(Position=0)]
    [string]$Task,
    
    [Parameter(Position=1)]
    [string]$WorkDir = "."
)

# 设置错误处理
$ErrorActionPreference = "Stop"

# 如果没有传递任务，进入交互模式
if (-not $Task) {
    claude
    exit $LASTEXITCODE
}

# 检查是否有 pty/tty
$hasPty = $false
if ($env:TERM_PROGRAM -eq "vscode" -or $env:WT_SESSION -or $env:TERM -eq "xterm-256color") {
    $hasPty = $true
}

# 执行 Claude Code
if ($hasPty) {
    # 有 pty，使用交互模式
    claude -p $Task
} else {
    # 无 pty，使用 --print 模式 + 确保非交互
    claude --print --no-read $Task 2>&1
}

exit $LASTEXITCODE
```

### 更安全的版本（带超时和重试）

```powershell
# claude-safe.ps1
param(
    [Parameter(Position=0)]
    [string]$Task,
    
    [Parameter(Position=1)]
    [string]$WorkDir = ".",
    
    [int]$Timeout = 120,
    [int]$Retries = 2
)

function Invoke-SafeClaude {
    param($cmd, $dir, $maxRetries)
    
    $attempt = 0
    $lastError = $null
    
    while ($attempt -lt $maxRetries) {
        $attempt++
        
        try {
            Push-Location $dir
            
            # 尝试使用不同模式
            $result = & cmd /c "echo . | claude -p `"$cmd`"" 2>&1
            
            if ($LASTEXITCODE -eq 0 -or $result -notmatch "hang|stuck|timeout") {
                Pop-Location
                return $result
            }
            
            # 如果失败，尝试备用模式
            Write-Host "[Attempt $attempt] Retrying with alternative mode..."
            $result = & cmd /c "claude --print --no-read `"$cmd`"" 2>&1
            
            Pop-Location
            
            if ($LASTEXITCODE -eq 0) {
                return $result
            }
            
            $lastError = $result
            
        } catch {
            $lastError = $_.Exception.Message
            Pop-Location
            Start-Sleep -Seconds 2
        }
    }
    
    throw "Claude Code failed after $maxRetries attempts. Last error: $lastError"
}

# 主逻辑
if (-not $Task) {
    claude
} else {
    Invoke-SafeClaude -cmd $Task -dir $WorkDir -maxRetries $Retries
}
```

## 最佳实践

### 1. 始终使用 pty:true

```javascript
exec({
  command: "claude -p '修复登录 bug'",
  pty: true,  // 必须！
  workdir: "E:\\project",
  timeout: 60
})
```

### 2. 处理确认提示

Claude Code 首次运行会询问是否信任目录，需要发送确认：

```javascript
// 首次确认
process(action='submit', sessionId='xxx', data:'1')

// 文件修改确认
process(action='submit', sessionId='xxx', data:'1')
```

### 3. 监控进度

```javascript
// 检查状态
process(action='poll', sessionId='xxx')

// 查看输出
process(action='log', sessionId='xxx', limit: 50)

// 发送输入
process(action='submit', sessionId='xxx', data:'y')
```

### 4. 常用 CLI 参数

| 参数 | 说明 |
|------|------|
| `-p, --print` | 非交互模式，执行完任务后退出 |
| `-m, --model` | 指定模型 (opus/sonnet/haiku) |
| `--no-read` | 禁用文件读取（仅命令行模式） |
| `--continue` | 继续上一个会话 |
| `--add-dir` | 添加额外目录到上下文 |

### 5. 权限模式

在 OpenClaw 中无法交互切换权限模式。如果需要无提示执行：

```bash
# 使用 --print 模式会自动跳过大部分确认
claude -p "你的任务" --print
```

## 常见问题

### Q: Claude Code 卡住不动

A: 
1. 可能是等待确认，按 `1` 发送确认
2. 使用 `claude-safe` 包装器
3. 添加 `--print` 参数

### Q: 权限被拒绝

A: OpenClaw 的 exec 默认在 sandbox 模式运行，某些命令可能需要 `elevated: true`

### Q: 输出乱码

A: 确保使用 `pty: true`，Claude Code 需要终端才能正确输出

## 使用示例

### 示例 1: 创建一个新文件

```javascript
exec({
  command: "claude -p '在当前目录创建 README.md，内容包括项目名称、简介和安装步骤'",
  pty: true,
  workdir: "E:\\project",
  timeout: 30
})
```

### 示例 2: 后台运行长任务

```javascript
exec({
  command: "claude -p '重构 auth 模块，添加单元测试'",
  pty: true,
  workdir: "E:\\project",
  background: true,
  timeout: 600
})
// 返回 sessionId 用于监控
```

### 示例 3: 代码审查

```javascript
exec({
  command: "claude -p 'Review this PR: git diff origin/main'",
  pty: true,
  workdir: "E:\\project",
  timeout: 120
})
```

## 相关文档

- [Claude Code 官方文档](https://code.claude.com/docs)
- [CLI 参考](/en/cli-reference)
- [Sub-agents](/en/sub-agents)
- [Skills](/en/skills)
