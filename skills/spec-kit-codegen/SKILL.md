---
name: spec-kit-codegen
description: 通过 OpenClaw 调用 Claude Code + Spec-Kit 实现规范化的代码生成工作流。适用于从需求到完整实现的自动化开发场景。
metadata:
  {
    "openclaw":
      {
        "requires": 
          { 
            "bins": ["claude"], 
            "python": true 
          },
        "install":
          [
            {
              "id": "claude-code",
              "kind": "cli",
              "command": "claude --version",
              "label": "Claude Code CLI",
            },
          ],
      },
  }
---

# Spec-Kit + Claude Code 完整工作流

本技能提供从需求描述到完整代码实现的自动化开发流程。

## 核心概念

```
用户需求 → SPEC.md → Claude Code → 完整实现 → 验证
```

## ⚠️ 关键规则

1. **与 Claude Code 对话必须使用英文 Prompt**
2. **先创建 SPEC.md，再调用 Claude Code**
3. **使用 PTY 模式防止输出乱码**
4. **项目目录必须配置权限**

---

## 完整工作流程

### Step 1: 准备项目目录

```javascript
// 创建项目目录
exec({ command: "mkdir E:\\\\project-directory" })

// 配置 Claude Code 权限
write({
  content: '{\n  "permissions": {\n    "allow": ["Write", "Edit", "Read", "Bash", "Glob", "Grep", "Task"]\n  }\n}',
  path: "E:\\\\project-directory\\\\.claude\\\\settings.json"
})
```

### Step 2: 生成 SPEC.md

有两种方式：

#### 方式 A: 使用 spec-kit-run.py（推荐）

```javascript
exec({
  command: 'python C:\\\\Users\\\\wqq\\\\.openclaw\\\\workspace\\\\scripts\\\\spec-kit-run.py "微信小程序电商应用，包含登录、注册、首页、商品列表、商品详情、购物车、结算、搜索、会员中心共9个页面，采用高端大气、简约、现代深色主题设计" -o "E:\\\\汪青青\\\\my-test" -n my-test',
  timeout: 60
})
```

#### 方式 B: 手动创建 SPEC.md

```javascript
write({
  content: `# Project Specification

## 1. Project Overview
**Project Name:** my-test
**Type:** WeChat Mini Program
**Core Functionality:** 电商小程序

## 2. UI/UX Specification
- 主题: 深色现代风格 (#0f0f23, #1a1a2e)
- 主色: #667eea (渐变紫蓝)
- 圆角: 12-28rpx

## 3. Pages
- pages/login/login - 登录页
- pages/register/register - 注册页
- pages/home/home - 首页
- pages/product-list/product-list - 商品列表
- pages/product-detail/product-detail - 商品详情
- pages/cart/cart - 购物车
- pages/checkout/checkout - 结算
- pages/search/search - 搜索
- pages/member/member - 会员中心

## 4. Acceptance Criteria
- [ ] 所有页面可正常编译
- [ ] 页面跳转正常
- [ ] TabBar 配置正确
`,
  path: "E:\\\\project-directory\\\\SPEC.md"
})
```

### Step 3: 调用 Claude Code 实现

```javascript
exec({
  command: 'cd "E:\\\\project-directory"; claude "Read SPEC.md and implement all pages. Create: 1) app.json with tabBar, 2) app.wxss with global styles, 3) All page files (js/json/wxml/wxss). Follow the dark theme spec with #667eea primary color."',
  pty: true,
  timeout: 180
})
```

### Step 4: 处理确认提示

Claude Code 会询问是否信任目录：

```javascript
// 发送确认 "1"
process({ action: 'submit', sessionId: 'xxx', data: '1' })
```

### Step 5: 检查和补充缺失文件

实现后检查文件完整性：

```javascript
exec({
  command: 'python -c "import os; files = [\\"pages/cart/cart.js\\", \\"images/home.png\\"]; [print(f + \\" EXISTS\\") if os.path.exists(r\\"E:\\\\project\\\\\\" + f) else print(f + \\" MISSING\\\") for f in files]"',
  timeout: 30
})
```

---

## 常用模板

### 微信小程序项目模板

```javascript
// 1. 创建项目
exec({ command: 'mkdir "E:\\\\微信小程序\\\\my-app"' })

// 2. 写权限配置
write({ path: "E:\\\\微信小程序\\\\my-app\\\\.claude\\\\settings.json", content: '{"permissions":{"allow":["Write","Edit","Read","Bash","Glob"]}}' })

// 3. 生成 SPEC.md
exec({
  command: 'python C:\\\\Users\\\\wqq\\\\.openclaw\\\\workspace\\\\scripts\\\\spec-kit-run.py "微信小程序电商项目" -o "E:\\\\微信小程序\\\\my-app" -n my-app',
  timeout: 30
})

// 4. Claude Code 实现
exec({
  command: 'claude -p "Implement WeChat mini-program according to SPEC.md. Create app.json, app.js, app.wxss, and all pages with dark theme."',
  pty: true,
  workdir: "E:\\\\微信小程序\\\\my-app",
  timeout: 180
})
```

### Web 前端项目模板

```javascript
exec({
  command: 'python C:\\\\Users\\\\wqq\\\\.openclaw\\\\workspace\\\\scripts\\\\spec-kit-run.py "Modern todo list app with dark theme" -o "E:\\\\projects\\\\todo-app" -n todo-app',
  timeout: 30
})

exec({
  command: 'claude -p "Read SPEC.md and create index.html, style.css, script.js with modern dark UI."',
  pty: true,
  workdir: "E:\\\\projects\\\\todo-app",
  timeout: 120
})
```

---

## 最佳实践

### 1. 清晰的需求描述

```javascript
// ❌ 模糊
command: 'claude "创建小程序"'

// ✅ 清晰
command: 'claude "Create a WeChat mini-program e-commerce app with: 1) Login/Register pages, 2) Home with product grid, 3) Product detail page, 4) Shopping cart, 5) Dark theme with #0f0f23 background and #667eea accent"'
```

### 2. 分步实现复杂项目

```javascript
// 第一步：创建基础结构
exec({
  command: 'claude "Create project structure: app.json, app.js, app.wxss, and all page directories"',
  pty: true,
  workdir: "E:\\\\project",
  timeout: 60
})

// 第二步：实现页面逻辑
exec({
  command: 'claude "Implement all page.js files with business logic"',
  pty: true,
  workdir: "E:\\\\project",
  timeout: 120
})

// 第三步：实现样式
exec({
  command: 'claude "Create modern dark theme styles for all pages. Use #0f0f23 bg, #667eea primary, glassmorphism effects"',
  pty: true,
  workdir: "E:\\\\project",
  timeout: 120
})
```

### 3. 错误处理和验证

```javascript
// 检查实现完整性
exec({
  command: 'python -c "
import os
base = r\\"E:\\\\project\\"
required = [
    \\"app.json\\", \\"app.js\\", \\"app.wxss\\",
    \\"pages/home/home.js\\", \\"pages/home/home.wxml\\",
    \\"pages/cart/cart.js\\", \\"pages/cart/cart.wxml\\"
]
missing = [f for f in required if not os.path.exists(base + f)]
if missing:
    print(\\"MISSING:\\", missing)
else:
    print(\\"ALL FILES EXIST\\")
"',
  timeout: 10
})
```

---

## 常见问题

### Q: Claude Code 输出乱码

A: 确保使用 `pty: true` 参数

### Q: 文件缺失

A: 
1. 手动创建缺失文件
2. 重新调用 Claude Code 并明确指定

### Q: 样式不符合预期

A: 
1. 更新 SPEC.md 中的样式规范
2. 重新调用 Claude Code

### Q: Claude Code 进程卡住

A:
```javascript
// 检查进程状态
process({ action: 'poll', sessionId: 'xxx' })

// 发送确认
process({ action: 'submit', sessionId: 'xxx', data: '1' })

// 终止卡住的进程
process({ action: 'kill', sessionId: 'xxx' })
```

---

## 相关文件

| 文件 | 位置 |
|------|------|
| Spec-Kit Runner | `C:\Users\wqq\.openclaw\workspace\scripts\spec-kit-run.py` |
| Claude Code Runner | `C:\Users\wqq\.openclaw\workspace\scripts\claude_code_run.py` |
| 示例项目 | `E:\汪青青\my-test` |

---

## 工作流示意

```
┌─────────────────────────────────────────────────────────────┐
│                    完整工作流程                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 用户需求                                                │
│     "微信小程序电商应用"                                     │
│           ↓                                                 │
│  2. spec-kit-run.py                                        │
│     生成 SPEC.md                                            │
│           ↓                                                 │
│  3. Claude Code (PTY)                                       │
│     读取 SPEC.md                                            │
│     生成所有代码文件                                          │
│           ↓                                                 │
│  4. 检查完整性                                              │
│     补充缺失文件                                             │
│           ↓                                                 │
│  5. 验证                                                    │
│     编译/运行测试                                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```
