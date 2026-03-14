#!/usr/bin/env pwsh
# claude-safe.ps1
# 防止 Claude Code 在无 pty/tty 环境下卡住的包装脚本
# 保存到系统 PATH 中的目录，如 C:\Windows\System32\ 或 ~/scripts/

param(
    [Parameter(Position=0)]
    [string]$Task = "",
    
    [Parameter(Position=1)]
    [string]$WorkDir = ".",
    
    [switch]$Interactive,
    [switch]$Print,
    [int]$Timeout = 120
)

$ErrorActionPreference = "Continue"

# 检测是否有 pty/tty
function Test-HasPty {
    # Windows Terminal
    if ($env:WT_SESSION) { return $true }
    # VS Code
    if ($env:TERM_PROGRAM -eq "vscode") { return $true }
    # 常见终端
    if ($env:TERM -match "xterm|screen|tmux") { return $true }
    # SSH
    if ($env:SSH_TTY) { return $true }
    
    return $false
}

# 执行 Claude Code
function Invoke-ClaudeCode {
    param(
        [string]$Cmd,
        [string]$Dir,
        [bool]$IsInteractive,
        [bool]$IsPrint
    )
    
    $originalDir = Get-Location
    
    try {
        if ($Dir -and $Dir -ne ".") {
            if (Test-Path $Dir) {
                Set-Location $Dir
                Write-Host "Working directory: $Dir" -ForegroundColor Cyan
            } else {
                Write-Warning "Directory not found: $Dir, using current directory"
            }
        }
        
        $claudeCmd = "claude"
        
        # 根据模式构建命令
        if ($IsInteractive) {
            # 交互模式
            Write-Host "Running Claude Code in interactive mode..." -ForegroundColor Green
            & $claudeCmd
        }
        elseif ($IsPrint -or $Cmd) {
            # 打印/非交互模式
            Write-Host "Running Claude Code in print mode..." -ForegroundColor Green
            
            if ($Cmd) {
                # 使用 echo 管道确保有输入，防止卡住
                $fullCmd = "echo . | $claudeCmd --print --no-read `"$Cmd`""
            } else {
                $fullCmd = "echo . | $claudeCmd --print --no-read"
            }
            
            # 执行并捕获输出
            $output = Invoke-Expression $fullCmd 2>&1
            $exitCode = $LASTEXITCODE
            
            # 打印输出
            $output | ForEach-Object { Write-Host $_ }
            
            return $exitCode
        }
        else {
            # 默认交互模式
            Write-Host "Running Claude Code in interactive mode..." -ForegroundColor Green
            & $claudeCmd
        }
        
        return $LASTEXITCODE
        
    }
    finally {
        Set-Location $originalDir
    }
}

# 主逻辑
$hasPty = Test-HasPty

Write-Host "=== Claude Safe Runner ===" -ForegroundColor Yellow
Write-Host "PTY Detected: $hasPty" -ForegroundColor $(if ($hasPty) { "Green" } else { "Yellow" })
Write-Host "Task: $Task" -ForegroundColor Cyan
Write-Host "WorkDir: $WorkDir" -ForegroundColor Cyan
Write-Host ""

if ($Interactive) {
    # 强制交互模式
    $exitCode = Invoke-ClaudeCode -Cmd $Task -Dir $WorkDir -IsInteractive $true -IsPrint $false
}
elseif ($Print -or $Task) {
    # 打印/任务模式
    $exitCode = Invoke-ClaudeCode -Cmd $Task -Dir $WorkDir -IsInteractive $false -IsPrint $true
}
else {
    # 无参数，默认交互
    $exitCode = Invoke-ClaudeCode -Cmd "" -Dir $WorkDir -IsInteractive $true -IsPrint $false
}

Write-Host ""
Write-Host "Exit code: $exitCode" -ForegroundColor $(if ($exitCode -eq 0) { "Green" } else { "Red" })

exit $exitCode
