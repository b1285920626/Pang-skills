---
name: pang-opencode-ctrl
description: 使用opencode-cli操作opencode.用此技能管理会话,选择模型,切换代理.协调 opencode的编码工作
---

## Core rule
openclaw不编码.全部规划,编码和问题分析交给opencode完成

---

## 1. 启动/检查 opencode serve

运行 `python3 scripts/check-and-up.py`：
- 返回 `true` → 已运行，继续
- 返回 `false` → 启动失败，向用户报告全部返回内容

---

## 2. 派发任务

### 命令模板

```bash
cd <项目根目录> && opencode run --attach http://localhost:4096 \
  --dir <项目根目录> \
  -f <附件> \
  --title "<项目>_<类型>_<发起人>" \
  '<任务描述>'
```

### 参数说明

| 参数 | 必填 | 说明 |
|------|------|------|
| `--dir` | ✅ | session 归属的项目根目录。**缺了这个 → session 挂到 daemon 默认项目下，`session list` 查不到，agent 在错误目录找文件。** 不确定用哪个目录时问用户。 |
| `--title` | ✅ | 格式 `<项目>_<类型>_<发起人>`，如 `PhostBook_方案_Clovette`。用于识别 session，必须和任务内容对应。 |
| `-f` | 按需 | 附件文件路径，相对于项目根目录 |
| `--agent` | 按需 | 见下方 agent 选择 |
| `-m` | 按需 | 模型选择 |
| 任务描述 | ✅ | 最后一个参数，完整的任务描述 |

### ⚠️ 禁止重复发任务

发任务前先查 session list，看是否有同名 title 的 session：
- 有 → 等它完成，不重发
- 没有 → 正常发送

---

## 3. 验证任务状态

> ⚠️ **关键理解：`opencode run` CLI 进程退出 ≠ session 失败。**
> Session 由 daemon（`opencode serve`）独立管理，CLI 只是观察者。
> CLI 退出了（无论什么信号），session 仍在后台继续运行。

### 前置判断：要不要验？

| 执行方式 | 能直接看结果？ | 需要验证流程？ |
|---------|:------------:|:-------------:|
| 前台执行（等待 CLI 输出返回） | ✅ 直接在 stdout 看结果 | ❌ 不需要 |
| exec timeout / SIGKILL / 中断 | ❌ 没拿到完整结果 | ✅ 需要走验证流程 |
| background 启动后隔段时间来查 | ❌ 进程早结束了 | ✅ 需要走验证流程 |

**简单来说：如果这次执行成功看到了完整返回（含完成确认），就跳过验证。其他情况全都要走验证流程。**

### 标准验证流程

#### 步骤 1：获取 session ID

```bash
cd <项目根目录> && opencode session list -n 5
```

找到刚发的 session（匹配 title），记下 Session ID。
如果 session 没出现 → 从上级目录也查一次，检查 `--dir` 是否设对。

#### 步骤 2：用 poll_session.py 等待完成

```bash
python3 scripts/poll_session.py <session_id>
```

脚本会每隔 5 秒轮询 OpenCode REST API，等待 assistant 回复完成后输出结果。

#### 步骤 3：判断结果

| 输出情况 | 判断 |
|---------|------|
| 输出了 agent 回复文本 | ✅ session 正常完成 |
| 输出了文件变更（diff） | ✅ 任务执行成功 |
| 输出了 Error / Failed | ❌ 任务执行出错 |
| 脚本报 404 | ❌ session ID 不存在 |
| 脚本报连接错误 | ❌ opencode serve 可能挂了 |

---

## 4. 会话管理

### 查 session

```bash
opencode session list -n 10
```

`session list` 是目录相关的，只显示当前项目下的 session。
如果查不到，换上级目录重试。

### 重命名 session

```bash
python3 scripts/rename-session.py <session_id> <新名称>
```

### 复用规则

- 同一类型的任务用同一个 session
- 类型区分：前端 / 后端 / 测试 / 方案 等
- 用户未明确要求时，除非当前项目不存在同类型的 session，否则不应该用新 session

---

## 5. Agent 选择

opencode 安装了 oh-my-openagent 插件，有以下主力 agent：

| Agent | 角色 | 适用场景 |
|-------|------|---------|
| **Sisyphus** | 主要编排者（默认） | 简单问题、小型改动 |
| **Prometheus** | 规划者 | 复杂问题、大型改动——先出计划 |
| **Atlas** | 执行者 | Prometheus 出计划后执行 |

使用 `opencode run` 时通过 `--agent` 选择。

### 计划模式（多功能 / 多模块任务）

1. 用 Prometheus 制定详细计划
   - 要求每次提问尽可能提出当前全部问题，由 openclaw 向用户确认
   - 计划必须有详细步骤，保存到 `plan.md`
2. 计划完成 → 用户确认 → 切换 Atlas，发送 `/start-work` 执行

### 直接构建模式（单功能 / 简单任务）

1. 任务交给 Sisyphus
2. 让它尽可能提出全部问题，由 openclaw 向用户确认
3. 确认后给出方案，向用户确认
4. 确认后让 Sisyphus 开始工作

---

## 6. 模型选择

可以通过 `opencode models` 查询完整列表。常用模型：

1. **免费模型**
   - `opencode/big-pickle`
   - `opencode/deepseek-v4-flash-free`
   - `opencode/mimo-v2.5-free`

2. **opencode-go 订阅模型**
   - `opencode-go/deepseek-v4-flash`
   - `opencode-go/deepseek-v4-pro`
   - `opencode-go/glm-5.1`
   - `opencode-go/kimi-k2.6`

3. **DeepSeek 官方 API**
   - `deepseek/deepseek-v4-flash`
   - `deepseek/deepseek-v4-pro`

---

## 7. 常见陷阱（排查指引）

| 症状 | 可能原因 | 怎么做 |
|------|---------|-------|
| `session list` 查不到新 session | `--dir` 漏了或指向了错误路径 | 从上级目录查，检查 `--dir` 参数 |
| CLI 退出（SIGKILL/SIGTERM） | process timeout 或 pkill | session 仍在跑，走验证流程（第 3 节） |
| 文件没写入预期路径 | session 归属了错误项目 root | 从 `~` 或上级目录查 session list 确认归属 |
| Agent 一直在探索找文件 | `--dir` 不对，在错误 root 下找文件 | 停掉当前 session，修正 `--dir` 重发 |
| 重复出现多个同名 session | 多次重发造成的 | 清理多余的，只保留最新的那个 |
| `nc -X` SSH 代理连接不上 | `nc` 的 SOCKS 代理与 SSH 不兼容 | 改用 HTTP 代理或 `socat` 做 ProxyCommand |