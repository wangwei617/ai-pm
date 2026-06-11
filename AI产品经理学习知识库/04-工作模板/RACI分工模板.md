# RACI 分工模板

RACI 用于明确 AI 产品落地中每个角色的责任。

- R = Responsible，负责执行。
- A = Accountable，最终负责。
- C = Consulted，被咨询。
- I = Informed，被告知。

## 1. 项目角色

| 角色 | 姓名/团队 | 主要职责 |
| --- | --- | --- |
| AI Product Owner |  | 业务结果和产品决策 |
| 业务方 |  | 场景、目标、验收 |
| 算法/AI 工程 |  | 模型、Prompt、RAG、Agent |
| 后端工程 |  | API、权限、数据、日志 |
| 前端工程 |  | 界面和交互实现 |
| 设计 |  | 体验、信任触点、异常流 |
| 数据分析 |  | 指标、看板、评测数据 |
| 安全/法务 |  | 风险、合规、红线 |
| 运营 |  | 试点、培训、反馈回流 |

## 2. RACI 表

| 工作项 | Product Owner | 业务 | 算法 | 工程 | 设计 | 数据 | 安全/法务 | 运营 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 场景选择 | A | R | C | C | C | C | C | I |
| AI PRD | A/R | C | C | C | C | C | C | I |
| Prompt/Schema | A | C | R | C | C | C | I | I |
| RAG 方案 | A | C | R | R | I | C | C | I |
| Agent 工具调用 | A | C | R | R | C | I | C | I |
| 交互原型 | A | C | C | C | R | I | C | I |
| Eval case | A | C | R | C | C | R | C | I |
| 红线清单 | A | C | C | C | C | I | R | I |
| 灰度上线 | A | R | C | R | C | C | C | R |
| 质量周报 | A/R | I | C | C | I | R | I | I |
| 复盘 | A/R | C | C | C | C | C | C | C |

## 3. 决策机制

说明：

- 谁能决定上线。
- 谁能决定回滚。
- 谁能决定模型变更。
- 谁能决定红线豁免。
- 事故时谁是第一负责人。

