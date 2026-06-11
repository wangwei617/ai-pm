# Gateway 路由与 Agent Loop

## 0. 一句话抓住本质

路由决定请求走哪条路，Loop 决定进入 Agent 后怎么一步步执行。

路由是调度中心，Loop 是行程本身。

## 1. 这两个概念是什么

Gateway 路由解决的是：

```text
用户这个请求应该走哪条业务链路？
```

Agent Loop 解决的是：

```text
进入 Agent 后，每一步如何执行、观察、再决策，以及什么时候停止？
```

一个在入口层，一个在执行层。

## 2. 路由是什么

路由是对用户输入做的第一个关键决策：识别用户核心意图，并决定由哪条业务链路服务。

用户输入可能来自：

- 聊天消息。
- CLI。
- Webhook/API。
- 定时任务。
- 表单。
- 按钮。

路由层要判断：

- 这是知识查询吗？
- 这是安全的只读操作吗？
- 这是写操作吗？
- 这是复杂多步任务吗？
- 这个请求风险等级是什么？
- 用户是否有权限？

## 2.1 用汽车比喻讲明白

用户可以从不同入口叫车：

- 聊天：师傅，去机场。
- App：设置目的地后点出发。
- 定时任务：每天 7 点去公司。

Gateway 就是调度中心。

它不会把用户原话直接扔给司机，让司机自己猜今天该开快递车、救火车还是越野车。

它会先判断任务类型、风险和权限，再决定派哪条业务链路。

## 3. 常见路由结果

| 路由结果 | 对应链路 | 特点 |
| --- | --- | --- |
| 知识/查询意图 | RAG 链路 | 只读，检索 + 生成 |
| 只读操作意图 | Safe Skill 链路 | 调安全工具，直接返回 |
| 写操作/复杂任务 | Agent 链路 | 多步执行，预览、确认、审计 |
| 高风险/越权 | 拒绝或人工审核 | 不进入模型自由执行 |

示例：

```text
用户问：产假怎么请？
→ 路由到 RAG 链路

用户点：查订单状态
→ 路由到 Safe Skill 链路

用户说：帮我改收货地址并通知客户
→ 路由到 Agent 链路，需要预览、确认、审计
```

## 4. 为什么不要把路由写死在 Prompt 里

新手常见错误是在 System Prompt 里写：

```text
如果用户问知识，就查资料库；
如果用户要操作订单，就调用工具。
```

这很危险。

### 不可靠

LLM 是概率模型，可能把「改地址」误判成「查地址」。

### 不安全

用户可能通过提示词注入误导模型，让它走错链路或调用危险工具。

### 难维护

每次新增功能、新工具、新风险规则，都要改 Prompt。一改 Prompt，其他能力也可能漂移。

正确做法：

```text
把路由从模型推理责任中剥离出来，变成 Gateway 中由产品代码控制的确定性逻辑。
```

LLM 可以辅助意图识别，但最终路由决策应该由 Gateway 和策略规则裁决。

## 4.1 反例：让模型自己路由的翻车点

错误做法：

```text
System Prompt：如果用户要查资料就走 RAG，如果用户要操作系统就调用工具。
```

翻车点：

- 用户说「看看当前地址」，模型误以为可以改地址。
- 用户通过提示注入诱导模型调用危险工具。
- 新增一个工具后，旧 Prompt 的行为发生漂移。
- 高风险请求没有经过权限和风险判断。

路由不是聊天策略，而是产品安全逻辑。

## 5. Gateway 应该做什么

Gateway 是入口层和调度中心。

它负责：

- 统一接收不同入口的请求。
- 做输入清洗。
- 识别意图。
- 判断风险等级。
- 判断权限。
- 选择业务链路。
- 加载对应 Harness。
- 拦截越权和高风险请求。

示例：环境操作型产品

```text
用户输入：把 /var/log 目录打包发给我。
```

Gateway 判断：

- 涉及文件操作。
- 涉及网络发送。
- 涉及敏感目录。
- 属于高风险组合。

路由结果：

- 普通用户：拒绝。
- 管理员：进入受限 Agent 链路，加载高安全 Harness。

高安全 Harness 可能包括：

- 工具白名单：file_read、tar/zip 受限命令、secure_send。
- 禁止访问非授权目录。
- 每一步需要确认。
- 全量 Trace。

## 6. 路由决策表

PM 应该在 PRD 中定义路由决策表。

| 入口来源 | 意图特征 | 识别出的工具需求 | 风险等级 | 路由决策 |
| --- | --- | --- | --- | --- |
| 聊天消息 | 查看、列出、搜索 | file_read、browser 只读 | 低 | Safe Skill |
| 聊天消息 | 分析、统计、合并 | bash、python | 中 | Agent，低资源沙箱 |
| CLI 命令 | scp、wget、sudo | network、bash 高危命令 | 高 | 高安全 Agent，人工审核 |
| 定时任务 | 固定脚本任务 | 预设工具集 | 中/低 | 受限 Agent，执行完发报告 |

这张表是产品逻辑的宪法，不应该散落在 Prompt 里。

## 7. Loop 是什么

Agent 语境里的 Loop，不是代码里的 for/while 本身，而是回合制执行：

```text
模型输出一个动作
→ 系统执行动作
→ 把结果拿回来喂给模型
→ 模型根据新信息继续决定下一步
→ 直到完成或停止
```

每一轮叫一个 Step。

伪代码：

```text
repeat until should_stop:
  next = llm.think(context)
  if next is answer:
    return render(next)
  if next is tool_call:
    obs = run_tool_safely(next)
    context.append(obs)
```

常见说法：

- ReAct。
- Tool-use loop。
- Agent loop。
- Reasoning-Action loop。

本质都是：

```text
想 → 做 → 看 → 再想
```

## 8. Loop 不是搜索

Loop 不等于 RAG，不等于搜索工具。

搜索只是可能被调用的一种工具。

在环境操作型产品里，工具可能是：

- bash。
- 文件读写。
- 浏览器操作。
- 代码执行。
- 系统命令。

所以 Loop 更准确的说法是：

```text
执行回合 / Execution Steps
```

不是「搜索轮次」。

## 9. Manus-like 产品里的 Loop 示例

用户任务：

```text
帮我把这个目录下所有 CSV 合并成一份，并统计每列空值率。
```

执行回合：

```text
Step 1: 查看目录
→ bash: ls /workspace/
→ 观察：file1.csv file2.csv file3.csv

Step 2: 读取文件头
→ file_read: head(file1.csv)
→ 观察：col_a,col_b,col_c

Step 3: 写合并脚本并运行
→ python_run: merge.py
→ 观察：done / error / stdout

Step 4: 验证产物
→ file_read: head(out.csv)

Step 5: 返回结果
```

这就是 Agent Loop：不是搜索，而是干活时的步骤链条。

## 9.1 允许的动作序列模板

对于环境操作型 Agent，不要让模型随便发明流程，可以给它预设可接受的动作序列。

例如 CSV 处理任务：

```text
目录探测 → 读取样本 → 生成执行计划 → 用户确认高风险步骤 → 执行脚本 → 验证产物 → 交付结果
```

动作序列表：

| Step 类型 | 允许工具 | 目标 | 风险控制 |
| --- | --- | --- | --- |
| 目录探测 | `ls`、file_list | 了解文件结构 | 只允许 workspace |
| 读取样本 | file_read | 判断格式 | 限制读取大小 |
| 生成计划 | LLM | 给出执行方案 | 高风险命令需确认 |
| 执行脚本 | python_run/bash 受限命令 | 处理文件 | 沙箱、超时、禁止危险命令 |
| 验证产物 | file_read/stat | 检查结果 | 只读 |
| 交付结果 | final_answer/file_export | 返回摘要和文件 | 记录 Trace |

## 10. Loop 为什么必须被 Harness 管住

如果放任模型想继续就继续，可能出现：

- 无限循环。
- API 账单爆炸。
- 重复调用工具。
- 越权访问。
- 执行危险命令。
- 被工具返回内容注入。

Harness 必须定义停止条件。

常见停止条件：

| 停止条件 | 说明 |
| --- | --- |
| max_steps | 最多执行几步 |
| max_time | 总时长上限 |
| max_cost | 单次任务成本上限 |
| no_progress | 连续 N 步无新增信息 |
| security_stop | 命中禁止模式立即停止 |
| user_stop | 用户中止任务 |
| completion | 达到完成状态 |

## 11. 安全停止示例

环境操作型产品必须特别关注：

- 逃出 workspace。
- 访问 private IP。
- 调用 `sudo`。
- 执行 `rm -rf`。
- 上传敏感文件。
- 下载未知脚本。
- 连接未授权网络。

这些情况应触发 security_stop，而不是继续交给模型解释。

## 12. PRD 里应该写什么

至少写清：

- 入口来源。
- 路由决策表。
- 意图识别方式。
- 风险等级。
- 路由结果。
- 加载哪个 Harness。
- Agent 最大步数。
- 单步和总任务超时。
- no_progress 判断。
- security_stop 条件。
- 用户中止方式。
- Trace 字段。

## 12.1 PRD 可粘贴写法

```text
系统在 Gateway 层完成路由决策，不依赖模型在 Prompt 中自行选择链路。
Gateway 根据入口、意图、工具需求、权限和风险等级，将请求路由到 RAG、Safe Skill、Agent、拒绝或人工审核。
进入 Agent 链路后，执行过程按 Step 运行，并受 max_steps、max_time、no_progress、security_stop 和 user_stop 约束。
```

路由决策表：

| 入口 | 意图 | 工具需求 | 风险 | 路由 | Harness |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |

Loop 控制表：

| 控制项 | 规则 | 触发后 |
| --- | --- | --- |
| max_steps |  | 停止并总结 |
| max_time |  | 停止并提示 |
| no_progress |  | 停止/转人工 |
| security_stop |  | 立即停止并审计 |
| user_stop |  | 中断任务 |

## 13. 人话总结

路由是入口层的调度中心。

它决定用户请求走 RAG、Safe Skill、Agent、拒绝还是人工审核。

不要把路由写死在 Prompt 里，因为路由是安全和业务决策，必须由 Gateway 可靠执行。

Loop 是 Agent 的回合制执行。

模型每步选择一个工具执行，把结果拿回来，再决定下一步。Harness 决定它能不能继续走。

## 14. 一句可复述总结

路由不能靠 Prompt 猜，必须由 Gateway 决定；Loop 不能让模型无限跑，必须由 Harness 刹车。
