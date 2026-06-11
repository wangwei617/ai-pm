# yuanbao.md 内容合并清单

本文记录 `yuanbao.md` 中已合并到知识库的内容，方便后续追溯。

## 1. 已新增为独立专题

### AI 基础常识与能力边界

来源内容：

- 模型不等于算法。
- 训练、微调、推理。
- 参数与超参数。
- 监督、无监督、强化学习。
- 泛化与过拟合。
- 不确定性。
- LLM 擅长、不擅长、不适合的任务。

合并到：

- `02-核心知识点详解/13-AI基础常识与能力边界.md`

### Fine-tuning 与领域适配

来源内容：

- 什么时候考虑微调。
- Prompt + RAG 能否先解决。
- 微调不是万能按钮。
- 数据量、标注成本、回归风险、维护成本。

合并到：

- `02-核心知识点详解/14-Fine-tuning与领域适配.md`

### Prompt 与 Schema 产品契约

来源内容：

- Prompt 是模型行为的软约束界面。
- System Prompt、Context、User Input 三层拼装。
- Schema 是模型输出的接口契约。
- JSON 结构化输出与前端渲染关系。
- Prompt + Schema 在产品链路中的位置。

合并到：

- `02-核心知识点详解/15-Prompt与Schema产品契约.md`

### RAG 进阶与产品验收

来源内容：

- RAG 离线建库和在线问答。
- 文档清洗、Chunk、Embedding、向量库。
- 查询改写、混合检索、Rerank、上下文压缩。
- Naive RAG、Advanced RAG、Modular RAG、Agentic RAG、GraphRAG、Multi-Modal RAG。
- RAG 产品验收清单。

合并到：

- `02-核心知识点详解/16-RAG进阶与产品验收.md`

### 数据飞轮与反馈闭环

来源内容：

- 标注体系。
- 黄金集。
- 用户反馈回流。
- Eval as Product。
- 红队测试、对抗 case、A/B、分层发布。

合并到：

- `02-核心知识点详解/17-数据飞轮与反馈闭环.md`

## 2. 已增强到原有文档

### AI 产品经理全貌地图

增强内容：

- AI PM 的核心原则：做决策与取舍，不是写训练脚本。
- AI PM 多管的新轴线：不确定性、数据/知识、模型行为、安全红线、质量回归。
- AI 应用层、数据/知识层、模型层三层工作范围。
- 能力说明书、Prompt/Eval diff、红线清单等交付件。

### Prompt 工程与工作流设计

增强内容：

- Prompt 是软约束界面。
- System Prompt、Context、User Input 三层结构。
- 输出 Schema 和版本化管理。

### RAG 与知识库

增强内容：

- 过滤、重排、混合检索、元数据过滤。
- 检索质检和 RAG 验收清单。
- 不只看最终答案，也要看召回 chunk。

### AI 评测体系

增强内容：

- 在线指标、体验信号、Schema 合规率、人工二审通过率。
- 红队测试、对抗 case、Eval as Product。
- Prompt、模型、RAG 改动后都要回归。

### 成本、延迟与性能

增强内容：

- 200ms、800ms、2s、长任务对应不同 UX。
- 云端 API、私有化、端侧小模型的部署形态权衡。

### 工作模板

增强内容：

- AI PRD 模板增加输入契约、输出 Schema、红线清单、失败降级。
- Prompt 模板增加三层拼装、Output Schema、Eval diff。
- RAG 模板增加 chunk 参数、混合检索、检索质检。
- 评测模板增加 Eval Case Sheet 和 Eval Diff。

## 3. 已新增为工作模板

- `04-工作模板/能力说明书模板.md`
- `04-工作模板/红线清单模板.md`

## 4. 暂未直接合并的内容

`yuanbao.md` 中提到的一些外部学习资料和工具书清单暂未直接合并为推荐书单，因为资料有效性和版本可能变化。后续如果要做「学习资源库」，建议单独整理，并优先核对官方文档和最新资料。

## 5. 第二次补充内容已合并

### 交互设计师转 AI 产品经理行动指南

来源内容：

- UX-trained AI PM 的三件事：看出 AI 体验风险、把体验判断翻译成业务约束、让交付物形成固定位置。
- UX 能力到 AI PM 能力的映射：信息架构、用户心智、组件化、异常流、信息层级。
- 五个抓手：可信度设计、AI 链路全景图、失败路径 PRD 化、Eval 最小闭环、语言转换。
- 90 天身份转化路线。

合并到：

- `01-AI产品经理全貌/04-交互设计师转AI产品经理行动指南.md`
- `README.md`
- `01-AI产品经理全貌/02-90天学习路线.md`

### RAG Top-K 召回与拒答/澄清

来源内容：

- RAG 检索是帮模型找参考资料。
- 召回 Top-K chunk 的通俗解释。
- 没召回着的两种情况：资料库没有、资料有但没匹配上。
- 相关度阈值、最少召回块数、低置信不生成。
- 拒答不是失败，是保护体验。
- 澄清用于拯救模糊意图。

合并到：

- `02-核心知识点详解/05-RAG与知识库.md`
- `02-核心知识点详解/16-RAG进阶与产品验收.md`
- `04-工作模板/RAG方案模板.md`

### 新增工作模板

新增：

- `04-工作模板/AI链路全景图模板.md`
- `04-工作模板/信任触点清单模板.md`

## 6. Agent 产品结构内容已合并

来源内容：

- Agent 是在循环里运行的 LLM。
- Agent 的本质是工具、循环、停止条件和权限边界。
- Agent 的五个构件：LLM、Tools、Context/Memory、Controller/Harness、Trace。
- Agent 不等于多轮聊天。
- PM 验收 Agent 的 6 个硬问题：白名单、确认、停止条件、权限、工具异常、Trace。
- 没有工具白名单、停止条件、确认机制的 Agent 是事故预演。

合并到：

- `02-核心知识点详解/18-Agent产品结构与治理.md`
- `02-核心知识点详解/06-Agent与工具调用.md`
- `04-工作模板/Agent方案模板.md`
- `04-工作模板/Agent上线验收清单.md`
- `05-AI Product Owner成长路径/02-AI Product Owner能力模型.md`

## 7. Skill 能力单元内容已合并

来源内容：

- Skill 是系统级可调用能力单元。
- Skill 更像车载附件功能，不是发动机。
- Agent 是调度者，Skill 是动词的实现体。
- 用户直接用 Skill 是通过按钮、指令、表单等受控入口。
- 哪些 Skill 可以直通暴露，哪些必须经过 Agent/Workflow，哪些必须锁死。
- 能直通的 Skill 必须低风险、可校验、无副作用或可撤销。

合并到：

- `02-核心知识点详解/19-Skill能力单元与暴露策略.md`
- `02-核心知识点详解/18-Agent产品结构与治理.md`
- `04-工作模板/Agent方案模板.md`
- `04-工作模板/AI风险分级模板.md`
- `04-工作模板/Skill盘点与暴露策略模板.md`
- `05-AI Product Owner成长路径/02-AI Product Owner能力模型.md`

## 8. Gateway 路由与 Agent Loop 内容已合并

来源内容：

- 路由是入口层对用户意图和业务链路的确定性决策。
- 不要把路由写死在 Prompt 里。
- Gateway 负责入口统一、意图识别、风险判断、权限判断、链路选择和 Harness 加载。
- 路由结果包括 RAG、Safe Skill、Agent、拒绝或人工审核。
- Loop 是 Agent 的回合制执行，不是搜索。
- Loop 在环境操作型产品里表现为目录探测、读取、执行、验证、交付等 Step。
- Harness 必须定义 max_steps、max_time、no_progress、security_stop、user_stop 等停止条件。

合并到：

- `02-核心知识点详解/20-Gateway路由与Agent Loop.md`
- `04-工作模板/AI链路全景图模板.md`
- `04-工作模板/Agent方案模板.md`
- `AI Product Owner版本升级说明.md`
