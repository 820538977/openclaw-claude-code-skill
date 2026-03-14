# OpenClaw Claude Code Skill

通过 OpenClaw 调用 Claude Code 进行编码任务的完整解决方案。

## 功能特性

- ✅ PTY 安全调用 - 防止无 pty/tty 时卡住
- ✅ 项目权限自动配置
- ✅ Windows/Linux/Mac 跨平台
- ✅ Spec-Kit 工作流支持
- ✅ 进度监控

## 快速开始

### 1. 调用 Claude Code

```javascript
exec({
  command: "python C:\\\\Users\\\\wqq\\\\.openclaw\\\\workspace\\\\scripts\\\\claude_code_run.py \"Your task in English\"",
  pty: true,
  workdir: "E:\\\\project-directory",
  timeout: 120
})
```

### 2. 配置项目权限

在项目目录创建 `.claude/settings.json`：

```json
{
  "permissions": {
    "allow": ["Write", "Edit", "Read", "Bash"]
  }
}
```

## 文件说明

| 文件 | 说明 |
|------|------|
| SKILL.md | 完整技能文档 |
| claude_code_run.py | Claude Code Runner 脚本 |

## 重要规则

**与 Claude Code 对话必须使用英文 Prompt！**

```javascript
// ✅ 正确
command: "claude -p 'Create a modern login page'"

// ❌ 错误
command: "claude -p '创建一个登录页面'"
```

## 相关文档

- [Claude Code 官方文档](https://code.claude.com/docs)
- [Spec-Kit GitHub](https://github.com/github/spec-kit)
