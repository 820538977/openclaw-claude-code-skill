# 记忆库

## 编程约定（2026-03-15）

**尽量全程使用 Claude Code 进行编程任务**
- 用户要求尽量全程使用 Claude Code
- 简单修补、检查操作除外

## OpenClaw 调用 Claude Code 编码

### 方法

在 Windows 环境下，通过 OpenClaw 调用 Claude Code 进行编码任务：

```javascript
exec({
  command: "python claude_code_run.py '你的任务描述'",
  pty: true,
  workdir: "项目目录",
  timeout: 120
})
```

### 关键经验

1. **必须使用 pty:true**
   - Claude Code 是交互式终端应用，需要 PTY 才能正常工作
   - 没有 PTY 会导致输出损坏或程序挂起
   - Windows Terminal 原生支持 ConPTY

2. **使用英文 Prompt**
   - 用户用中文和我对话
   - 但和 Claude Code 对话必须使用英文
   - 这样 Claude Code 能更好地理解任务

3. **工作目录 (workdir)**
   - 使用 workdir 参数指定项目目录
   - Claude Code 会在该目录下创建文件

4. **交互确认**
   - Claude Code 会询问是否信任该目录 → 发送 "1" 确认
   - 创建/修改文件时会请求确认 → 发送 "1" 确认
   - 使用 `process(action='submit', sessionId='xxx', data:'1')` 确认

5. **监控进度**
   - 使用 `process(action='poll', sessionId='xxx')` 检查状态
   - 使用 `process(action='log', sessionId='xxx')` 查看输出

6. **Windows PowerShell 语法**
   - 多命令用分号 `;` 分隔，不要用 `&&`
   - 例如：`cd "E:\path"; claude "task"`

### 应用场景

- 创建新项目、后端 API
- 修改前端页面添加功能
- 代码重构和调试
- 任何需要编码助手的任务

---

## Spec-Kit 工作流配置

### 文件位置

| 文件 | 路径 |
|------|------|
| spec-kit-run.py | `C:\Users\wqq\.openclaw\workspace\scripts\spec-kit-run.py` |
| spec-developer.md | `C:\Users\wqq\.claude\agents\spec-developer.md` |

### 使用方法

1. **生成 SPEC.md**
```bash
python C:\Users\wqq\.openclaw\workspace\scripts\spec-kit-run.py "项目描述" -o "项目目录" -n "项目名"
```

2. **使用 spec-developer subagent**
```
Use the spec-developer subagent to create a todo app
```

### 工作流

1. 运行 spec-kit-run.py 生成 SPEC.md
2. Claude Code 读取 SPEC.md
3. 生成 index.html, style.css, script.js
4. 验证实现

---

*更新于 2026-03-15*
