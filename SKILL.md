---
name: openclaw-claude-code
description: 通过 OpenClaw 调用 Claude Code 进行编码任务。适用于需要 Claude Code 编程助手的场景。
---

# OpenClaw 调用 Claude Code 技能

本技能提供通过 OpenClaw 调用 Claude Code 的完整解决方案。

## ⚠️ 重要规则

**与 Claude Code 对话必须使用英文 Prompt！**

虽然用户用中文和你对话，但 Claude Code 需要英文 prompt 才能更好地理解任务。

```javascript
// ❌ 错误
command: "claude -p '创建一个登录页面'"

// ✅ 正确
command: "claude -p 'Create a modern login page with HTML and CSS'"
```

## 核心功能

1. **PTY 安全调用** - 防止无 pty/tty 时卡住
2. **工作目录指定** - 在指定目录运行 Claude Code
3. **后台任务支持** - 长任务后台运行
4. **进度监控** - 实时查看执行状态
5. **项目权限配置** - 自动配置写入权限

## 调用方法

### 1. 使用 claude_code_run.py（推荐）

这是最稳定的调用方式，自动处理 Windows PowerShell 脚本和 PTY 问题：

```javascript
exec({
  command: "python C:\\\\Users\\\\wqq\\\\.openclaw\\\\workspace\\\\scripts\\\\claude_code_run.py \"Your task description in English\"",
  pty: true,
  workdir: "E:\\\\project-directory",
  timeout: 120
})
```

### 2. 直接调用 Claude Code

```javascript
exec({
  command: "claude -p 'Create a hello world app'",
  pty: true,
  workdir: "E:\\project",
  timeout: 60
})
```

### 3. 交互式调用

```javascript
exec({
  command: "python C:\\\\Users\\\\wqq\\\\.openclaw\\\\workspace\\\\scripts\\\\claude_code_run.py -i",
  pty: true,
  workdir: "E:\\project",
  timeout: 300
})
```

## 项目权限配置

**重要：每次在新项目使用 Claude Code 前，必须配置权限！**

### 自动配置方法

在调用 Claude Code 前，自动创建权限配置：

```javascript
// 1. 创建权限配置目录
exec({ command: "mkdir 项目目录/.claude" })

// 2. 创建权限配置文件
write({
  content: '{\n  "permissions": {\n    "allow": ["Write", "Edit", "Read", "Bash"]\n  }\n}',
  path: "项目目录/.claude/settings.json"
})
```

### 手动配置

在项目根目录创建 `.claude/settings.json`：

```json
{
  "permissions": {
    "allow": ["Write", "Edit", "Read", "Bash"]
  }
}
```

## Claude Code Runner 脚本

脚本位置：`C:\Users\wqq\.openclaw\workspace\scripts\claude_code_run.py`

### 功能特性

- ✅ 强制 PTY，防止卡住
- ✅ 自动查找 Claude CLI（支持 Windows PowerShell）
- ✅ 超时控制
- ✅ 实时输出
- ✅ Windows/Linux/Mac 跨平台

### 使用方法

```bash
# 自测
python claude_code_run.py --test

# 执行任务
python claude_code_run.py "Create a login page"

# 指定工作目录
python claude_code_run.py -w E:\project "Fix the bug"

# 交互模式
python claude_code_run.py -i

# 查看帮助
python claude_code_run.py --help
```

## Spec-Kit 工作流（可选）

如果需要使用 spec-kit 进行规范的开发流程：

### 1. 安装 spec-kit

```bash
uvx --from git+https://github.com/github/spec-kit.git specify --help
```

### 2. 初始化项目

```bash
uvx --from git+https://github.com/github/spec-kit.git specify init 项目名 --ai claude --ignore-agent-tools
```

### 3. 使用 Claude Code 的 /speckit 命令

```bash
# 进入项目目录
cd 项目名

# 使用 Claude Code 调用：
# /speckit.specify - 定义需求
# /speckit.plan - 制定计划
# /speckit.tasks - 生成任务
# /speckit.implement - 执行实现
```

## 完整调用流程

### 示例：创建一个新项目

```javascript
// 1. 创建项目目录
exec({ command: "mkdir E:\\new-project" })

// 2. 配置权限
write({
  content: '{"permissions": {"allow": ["Write", "Edit", "Read", "Bash"]}}',
  path: "E:\\new-project\\.claude\\settings.json"
})

// 3. 调用 Claude Code（英文 prompt！）
exec({
  command: "python C:\\\\Users\\\\wqq\\\\.openclaw\\\\workspace\\\\scripts\\\\claude_code_run.py \"Create a modern todo list app with dark theme. Use Chinese text for UI.\"",
  pty: true,
  workdir: "E:\\\\new-project",
  timeout: 120
})
```

## 处理确认提示

Claude Code 首次运行会询问是否信任目录：

```javascript
// 发送确认
process(action='submit', sessionId='xxx', data:'1')
```

## 监控进度

```javascript
// 检查状态
process(action='poll', sessionId='xxx')

// 查看输出
process(action='log', sessionId='xxx', limit: 50)

// 发送输入（确认等）
process(action='submit', sessionId='xxx', data:'1')
```

## 常见问题

### Q: Claude Code 卡住不动

A: 
1. 可能是等待确认，按 `1` 发送确认
2. 使用 `claude_code_run.py` 包装器
3. 添加 `--print` 参数

### Q: 权限被拒绝，文件无法写入

A: 
1. 在项目目录创建 `.claude/settings.json`
2. 配置权限：`{"permissions": {"allow": ["Write", "Edit", "Read", "Bash"]}}`
3. 重新调用 Claude Code

### Q: 输出乱码

A: 确保使用 `pty: true`

## 相关文件

| 文件 | 位置 |
|------|------|
| Claude Code Runner | `C:\Users\wqq\.openclaw\workspace\scripts\claude_code_run.py` |
| Spec-Kit Runner | `C:\Users\wqq\.openclaw\workspace\scripts\spec-kit-run.py` |
| Code Review Agent | `C:\Users\wqq\.claude\agents\code-reviewer.md` |
| Spec Developer Agent | `C:\Users\wqq\.claude\agents\spec-developer.md` |

## 相关文档

- [Claude Code 官方文档](https://code.claude.com/docs)
- [Spec-Kit GitHub](https://github.com/github/spec-kit)
