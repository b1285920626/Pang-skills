---
name: pang-opencode-ctrl
description: 使用opencode-cli操作opencode.用此技能管理会话,选择模型,切换代理.协调 opencode的编码工作
---
## Core rule
openclaw不编码.全部规划,编码和问题分析交给opencode完成

## 使用方式
1. 使用`python3 scripts/check-and-up.py`检查或启动opencode,失败会返回false,此时则向用户报告全部返回内容
2. 使用`opencode run --attach http://localhost:4096 --dir <项目根目录> [任务具体内容]`派发任务, ⚠️`--dir <项目根目录>` 必填, 不确定应该是哪个目录时必须询问用户, 其他参数:
	1. `-f`附加到消息的文件
	2. 复用session时, 使用`-s <session_id>`指定session
	3. 当需要使用新session时, 使用`--title`命令给新session命名. 命名为`<项目名>_<类型>_<发起人名>`,例如"PhostBook_后端_Clovette"
	4. `--agent`选择代理
	5. `-m`选择模型
3. 派发任务命令使用必须使用 background 模式启动, 如果意外中断可以使用`python3 scripts/poll_session.py <session_id>`查询是否已完成
4. 使用新session时,任务执行完成/中断后及时查询session列表, 根据名称找到对应session id并记录

## session管理
1. 使用`opencode session list -n 10`命令查询session列表可获取session id, `-n` 参数限制返回条数
2. 使用如下命令修改session名称`python3 scripts/rename-session.py <session_id> <newname>`
3. 复用已存在的session,同一类型的任务使用同一个session,不同类型的不能混用,类型如: 前端/后端/测试 
4. 用户未明确要求时,除非当前项目不存在同类型的session,否则不应该使用新session

## agent 选择
opencode 安装了oh-my-openagent插件,有以下主力 agent, 使用`opencode run`命令时可通过`--agent`进行选择:
- Sisyphus: 主要编排者(默认) . 简单问题,小型改动交给它处理
- Prometheus: 规划者. 复杂问题,大型改动由它进行规划
- Atlas:执行者,Prometheus做好计划后交由它进行执行

### 计划模式
当需要构建,修改,重构涉及多个功能,接口,甚至是多模块时, 步骤如下:
1. 使用Prometheus制定详细计划
	- 要求Prometheus每次提问尽可能提出当前全部问题,然后由openclaw向用户一一确认
	- 计划必须有详细步骤,并保存到plan.md中
2. 计划完成后切换至Atlas, 发送`/start-work`开始执行计划

### 直接构建模式
当需要构建,修改,重构单个功能,接口,或者编写简单脚本等相对简单的工作时:
1. 将任务交给Sisyphus,并询问任务是否有模糊,互相冲突等问题,让它尽可能提出当前全部问题,然后由openclaw向用户确认
2. 要求澄清问题后给出方案并向用户确认是否正确
3. 确认后要求Sisyphus开始工作

## 模型选择
当前全部可用模型列表可以通过`opencode models`命令查询,以下是常用模型
1. 免费模型
	opencode/big-pickle
	opencode/deepseek-v4-flash-free
	opencode/mimo-v2.5-free
2. opencode-go订阅模型
	opencode-go/deepseek-v4-flash
	opencode-go/deepseek-v4-pro
	opencode-go/glm-5.1
	opencode-go/kimi-k2.6
3. deepseek官方api
	deepseek/deepseek-v4-flash
	deepseek/deepseek-v4-pro