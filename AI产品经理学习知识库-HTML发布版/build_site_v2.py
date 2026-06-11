#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
import shutil
from collections import defaultdict
from datetime import date
from pathlib import Path

import build_site as base


OUT_DIR = Path(__file__).resolve().parent
ARTICLES_DIR = OUT_DIR / "articles"
MODULES_DIR = OUT_DIR / "modules"
ASSETS_DIR = OUT_DIR / "assets"
CSS_DIR = ASSETS_DIR / "css"
JS_DIR = ASSETS_DIR / "js"
IMG_DIR = ASSETS_DIR / "img"


MODULES = [
    {
        "slug": "start",
        "title": "入门与总览",
        "short": "先知道这套知识库怎么读",
        "source_sections": {"起步与说明", "01 全貌地图"},
        "color": "teal",
        "promise": "帮读者建立 AI Product Owner 的整体坐标，知道自己要补什么、先读什么、最后要交付什么。",
    },
    {
        "slug": "core",
        "title": "核心知识",
        "short": "从场景、Prompt、RAG 到 Agent",
        "source_sections": {"02 核心知识"},
        "color": "blue",
        "promise": "把 AI 产品里最容易混淆的概念，翻译成产品经理能写进 PRD 和评审会的话。",
    },
    {
        "slug": "project",
        "title": "实战项目",
        "short": "用一个用户研究助手串起方法",
        "source_sections": {"03 实战项目"},
        "color": "amber",
        "promise": "通过完整项目，把输入、链路、界面、评测、上线和复盘连成一个可展示的作品。",
    },
    {
        "slug": "templates",
        "title": "工作模板",
        "short": "直接拿去写 PRD、评测和复盘",
        "source_sections": {"04 工作模板"},
        "color": "rose",
        "promise": "把抽象方法沉淀成工作表、清单和评审材料，降低真正落地时的空转成本。",
    },
    {
        "slug": "growth",
        "title": "成长与作战",
        "short": "从能力模型到作品集和落地流程",
        "source_sections": {"05 成长路径", "06 作战流程"},
        "color": "violet",
        "promise": "帮助读者把学习成果包装成可证明的能力，并形成从 0 到 1 推动 AI 产品的节奏。",
    },
]

COLOR = {
    "teal": {
        "badge": "bg-teal-50 text-teal-700 ring-teal-200",
        "soft": "bg-teal-50",
        "solid": "bg-teal-600",
        "border": "border-teal-200",
        "text": "text-teal-700",
    },
    "blue": {
        "badge": "bg-blue-50 text-blue-700 ring-blue-200",
        "soft": "bg-blue-50",
        "solid": "bg-blue-600",
        "border": "border-blue-200",
        "text": "text-blue-700",
    },
    "amber": {
        "badge": "bg-amber-50 text-amber-700 ring-amber-200",
        "soft": "bg-amber-50",
        "solid": "bg-amber-500",
        "border": "border-amber-200",
        "text": "text-amber-700",
    },
    "rose": {
        "badge": "bg-rose-50 text-rose-700 ring-rose-200",
        "soft": "bg-rose-50",
        "solid": "bg-rose-600",
        "border": "border-rose-200",
        "text": "text-rose-700",
    },
    "violet": {
        "badge": "bg-violet-50 text-violet-700 ring-violet-200",
        "soft": "bg-violet-50",
        "solid": "bg-violet-600",
        "border": "border-violet-200",
        "text": "text-violet-700",
    },
}


PATHS = [
    {
        "title": "转岗快速路径",
        "desc": "适合交互设计师、传统 PM，先建立定位，再补核心概念，最后形成作品集。",
        "titles": [
            "阅读指南与写作标准",
            "AI 产品经理全貌地图",
            "交互设计师转 AI 产品经理行动指南",
            "90 天 AI Product Owner 学习路线",
            "AI Product Owner 作品集标准",
        ],
    },
    {
        "title": "项目落地路径",
        "desc": "适合已经有一个 AI 项目在手的人，直接从场景边界、链路、评测和上线推进。",
        "titles": [
            "从 0 到 1 落地 AI 产品",
            "AI 场景判断",
            "Prompt 与 Schema 产品契约",
            "RAG 进阶与产品验收",
            "AI 评测体系",
            "AI 安全、隐私与治理",
        ],
    },
    {
        "title": "Agent 系统路径",
        "desc": "适合想理解下一代 AI 产品结构的人，重点看 Agent、Skill、Gateway 和治理。",
        "titles": [
            "Agent 与工具调用",
            "Agent 产品结构与治理",
            "Skill 能力单元与暴露策略",
            "Gateway 路由与 Agent Loop",
            "Agent 方案模板",
            "Agent 上线验收清单",
        ],
    },
]


PROFILE_RULES = [
    (
        ("场景判断", "适配性判断"),
        {
            "name": "AI 场景判断",
            "analogy": "场景判断像开工前的地质勘探：不是问能不能挖，而是先看这块地值不值得挖、会不会塌、塌了谁承担。",
            "case": "比如“自动总结用户反馈”适合 AI，因为文本密集、人工耗时、结果可复核；但“自动批准高额退款”就要谨慎，因为失败代价高、责任边界重。",
            "mistakes": ["只因为技术能做就立项", "没有定义失败代价和人工兜底", "把低频、低价值、强责任场景硬塞给 AI"],
            "deliverables": ["AI 场景边界卡", "适配性判断表", "失败代价说明", "人工兜底方案", "MVP 验证假设"],
            "exercise": "选 3 个候选 AI 场景，用“高频/价值/可复核/失败代价/数据可得性”给它们打分。",
        },
    ),
    (
        ("交互设计", "信任设计", "AI UX"),
        {
            "name": "AI 交互与信任体验",
            "analogy": "AI 交互设计不是给聊天框换皮，而是设计人和不确定系统如何协作：什么时候让 AI 做，什么时候让用户看，什么时候必须停。",
            "case": "洞察助手生成结论时，界面不只展示“结论”，还要展示证据、置信度、编辑入口、采纳/拒绝反馈和重新生成，用户才敢把它用于决策。",
            "mistakes": ["把 AI 输出当确定答案展示", "没有引用、撤销、编辑和反馈入口", "让用户通过反复改 Prompt 来弥补产品设计缺失"],
            "deliverables": ["AI 输出组件规范", "信任触点清单", "异常状态设计", "反馈入口设计", "人工确认流程"],
            "exercise": "找一个 AI 输出页面，标出用户在阅读、怀疑、修改、采纳、纠错时分别需要什么控件。",
        },
    ),
    (
        ("大语言模型", "LLM", "模型基础", "能力边界"),
        {
            "name": "模型能力与边界",
            "analogy": "LLM 像一个语言和模式识别能力很强的实习生：会总结、改写、归类，但不天然知道事实、权限和业务责任。",
            "case": "让模型总结会议纪要通常可行；让它直接判断合同风险并自动发给客户，就需要知识来源、法务审核和责任边界。",
            "mistakes": ["把模型输出当事实", "用大模型解决确定性规则问题", "不知道失败来自模型、知识、Prompt 还是产品流程"],
            "deliverables": ["模型能力边界说明", "适用/不适用场景表", "失败归因表", "降级策略", "人工审核规则"],
            "exercise": "把一个 AI 功能的失败原因分成：模型理解错、知识缺失、指令不清、权限限制、用户输入差。",
        },
    ),
    (
        ("RAG", "召回", "Top-K", "GraphRAG"),
        {
            "name": "RAG 与知识系统",
            "analogy": "可以把它理解成给模型配一个会翻资料的研究助理：先找证据，再组织回答，证据不够就别硬答。",
            "case": "例如 HR 制度助手回答“年假怎么折算”。真正的产品重点不是让模型说得顺，而是确认它查到了正确制度版本、权限允许展示，并且引用能支撑结论。",
            "mistakes": ["只看答案像不像，不看引用是否支撑结论", "把召回失败当成模型不聪明", "没有拒答和澄清机制，导致用户越问越不信"],
            "deliverables": ["知识库切分策略", "Top-K 质量门", "引用展示规范", "拒答/澄清文案", "RAG 验收样本集"],
            "exercise": "拿你公司的一份制度或 FAQ，设计 10 个真实问题，并标注每个问题应该引用哪一段材料。",
        },
    ),
    (
        ("Agent", "Skill", "Gateway", "Loop", "工具调用", "Harness"),
        {
            "name": "Agent 与能力编排",
            "analogy": "Agent 不是更会聊天的人，而是一个在受控循环里做事的调度员：想一步、调工具、看结果、再决定下一步。",
            "case": "客服改地址场景里，Agent 不能直接“想改就改”。它应该先查订单、判断状态、生成改动预览、让用户确认，再调用改地址工具并留下 Trace。",
            "mistakes": ["把高风险工具直接暴露给模型", "只设计 happy path，没有超时、失败和人工接管", "把路由、权限和审计都写进 Prompt"],
            "deliverables": ["工具白名单", "Skill 登记表", "Agent Loop 流程图", "Gateway 路由规则", "审计与人工确认策略"],
            "exercise": "选一个你熟悉的业务动作，拆成 5 个 Skill，并给每个 Skill 标注风险等级和是否需要人工确认。",
        },
    ),
    (
        ("评测", "Eval", "质量", "验收", "回归"),
        {
            "name": "Eval 与质量闭环",
            "analogy": "Eval 像 AI 产品的体检表。不是上线前测一次，而是每次改 Prompt、换模型、加知识都要重新量一遍。",
            "case": "用户研究洞察助手不能只展示几个好样例。你需要准备覆盖清晰访谈、含糊表达、噪声文本和敏感信息的样本集，看它是否稳定提取、引用和拒答。",
            "mistakes": ["用 3 个顺眼样例替代评测集", "只评准确率，不评可用性、风险和成本", "上线后没有回归集，效果退化也不知道"],
            "deliverables": ["Eval case 集", "评分 Rubric", "质量门槛", "回归测试记录", "线上反馈回流表"],
            "exercise": "为当前文章主题设计 20 条评测样本，至少包含 5 条边界样本和 3 条应该拒答的样本。",
        },
    ),
    (
        ("安全", "隐私", "治理", "红线", "风险", "信任"),
        {
            "name": "安全、信任与治理",
            "analogy": "治理不是给产品踩刹车，而是给 AI 划车道：哪些能自动跑，哪些要降速，哪些必须人来开。",
            "case": "企业知识库助手面对薪酬、绩效、合同等内容时，最重要的不是“回答得完整”，而是先确认用户是否有权限、是否涉及敏感信息、是否需要转人工。",
            "mistakes": ["上线前才想安全问题", "没有风险分级，所有场景都一个策略", "缺少日志和审计，出问题无法复盘"],
            "deliverables": ["风险分级表", "红线清单", "权限矩阵", "信任触点清单", "审计日志字段"],
            "exercise": "把一个 AI 功能拆成 L1/L2/L3 三类风险，并分别写出自动化、人审和禁止输出策略。",
        },
    ),
    (
        ("路线", "成长", "能力模型", "90 天", "作品集", "转型", "Product Owner"),
        {
            "name": "成长路径与作品集",
            "analogy": "转型不是补一堆名词，而是攒一组能证明你会落地的证据：图、表、样本、复盘和业务结果。",
            "case": "从交互设计师转 AI Product Owner，优势不是懂模型参数，而是能把不确定输出设计成可复核、可编辑、可回滚、可评测的产品体验。",
            "mistakes": ["把学习路线写成工具清单", "作品集只展示界面，不展示评测和结果", "只说参与项目，不说自己负责的判断和取舍"],
            "deliverables": ["能力自评表", "90 天路线图", "作品集结构", "项目复盘页", "面试讲述脚本"],
            "exercise": "选一个你做过的项目，用“业务问题-为什么用 AI-链路设计-评测-结果”重写成一页作品集。",
        },
    ),
    (
        ("Prompt", "Schema", "契约"),
        {
            "name": "Prompt 与结构化输出",
            "analogy": "Prompt 像给模型的任务说明，Schema 像产品系统的收货标准。没有 Schema，AI 输出再漂亮也很难进入流程。",
            "case": "让 AI 提取用户痛点时，不能只要求“总结一下”。你要规定字段、类型、证据、置信度和失败处理，这样后续页面、筛选和评测才能接住。",
            "mistakes": ["把 Prompt 当咒语，不写输入输出边界", "没有示例和反例，导致模型风格漂移", "输出格式不稳定，工程只能被迫做脏解析"],
            "deliverables": ["Prompt 说明书", "Output Schema", "Few-shot 示例", "失败处理规则", "Prompt 版本记录"],
            "exercise": "把一个开放式任务改写成结构化 Schema，并写出至少 2 个合格输出样例和 1 个拒答样例。",
        },
    ),
    (
        ("数据", "埋点", "ROI", "商业", "成本", "延迟", "性能", "飞轮"),
        {
            "name": "指标、成本与业务结果",
            "analogy": "AI 产品不是只看“生成得好不好”，还要看它是否省时间、少返工、能规模化，并且成本别把收益吃掉。",
            "case": "一个客服摘要功能如果能把单次处理时间从 8 分钟降到 5 分钟，但幻觉导致返工增加，最终 ROI 可能并不好看。",
            "mistakes": ["只汇报调用量，不汇报采纳率和节省时间", "忽略 token、延迟和人工复核成本", "没有反馈闭环，数据只用于看板不用于改进"],
            "deliverables": ["指标树", "埋点方案", "成本估算表", "ROI 复盘", "数据飞轮设计"],
            "exercise": "为一个 AI 功能写出 3 个业务指标、3 个质量指标、2 个成本指标，并说明谁每周看这些数。",
        },
    ),
    (
        ("用户研究", "PRD", "MVP", "洞察助手", "旅程", "项目"),
        {
            "name": "实战项目落地",
            "analogy": "一个好实战项目像一条小生产线：材料进来、AI 处理、人来校验、结果沉淀，下一次会更好。",
            "case": "AI 用户研究洞察助手的核心不是“自动总结访谈”，而是把证据、痛点、机会点和 PRD 草稿连起来，让产品决策少一点拍脑袋。",
            "mistakes": ["MVP 做得太大，一开始就想覆盖所有研究材料", "只做生成，不设计采纳、修改和纠错回流", "没有质量门槛，洞察看起来对但无法证明"],
            "deliverables": ["用户旅程图", "MVP PRD", "Prompt 工作流", "评测方案", "Owner 级落地计划"],
            "exercise": "拿 3 段真实用户反馈，手动标注痛点、证据和机会点，再对比 AI 输出差在哪。",
        },
    ),
    (
        ("模板", "清单", "RACI", "Roadmap", "周报", "方案"),
        {
            "name": "工作模板与交付物",
            "analogy": "模板不是填空题，而是把好判断固定下来，让团队每次讨论都站在同一张桌面上。",
            "case": "AI PRD 模板如果只写功能列表，就会漏掉模型失败、人工确认、评测门槛、权限边界和上线监控这些真正决定成败的部分。",
            "mistakes": ["模板字段很多，但没有决策用途", "只写目标，不写验收口径", "没有责任人，评审后没人推进"],
            "deliverables": ["可复制模板", "评审检查清单", "RACI 分工", "上线检查表", "复盘表"],
            "exercise": "把模板里的每个字段标注为“评审用、研发用、运营用、治理用”，删掉没有用途的字段。",
        },
    ),
]

DEFAULT_PROFILE = {
    "name": "AI 产品通用方法",
    "analogy": "把 AI 产品想成一条业务流水线：不是模型单点表现好就够了，而是输入、处理、校验、展示和反馈都要接上。",
    "case": "同一个模型放在不同产品里，效果可能天差地别。差别往往不在模型，而在场景边界、输入质量、流程设计、评测和治理。",
    "mistakes": ["只讲 AI 能力，不讲业务结果", "只看演示效果，不看异常和失败", "缺少可交付物，读完不知道下一步做什么"],
    "deliverables": ["场景边界说明", "链路全景图", "验收问题", "风险清单", "复盘记录"],
    "exercise": "读完后用 5 句话复述本文：它解决什么问题、为什么重要、怎么落地、怎么验收、常见坑是什么。",
}


def ensure_dirs() -> None:
    for path in (ARTICLES_DIR, MODULES_DIR, CSS_DIR, JS_DIR, IMG_DIR):
        path.mkdir(parents=True, exist_ok=True)


def clean_generated_dirs() -> None:
    for path in (ARTICLES_DIR, MODULES_DIR):
        if path.exists():
            shutil.rmtree(path)
    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
    MODULES_DIR.mkdir(parents=True, exist_ok=True)


def module_for_doc(doc: dict[str, object]) -> dict[str, str]:
    section = str(doc["section"])
    for module in MODULES:
        if section in module["source_sections"]:
            return module
    return MODULES[0]


def docs_by_module(docs: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for doc in docs:
        groups[module_for_doc(doc)["slug"]].append(doc)
    return groups


def profile_for_doc(doc: dict[str, object]) -> dict[str, object]:
    title = str(doc["title"])
    source = str(doc["source_path"])
    title_source = f"{title} {source}"
    if any(key in title_source for key in ["场景判断", "适配性判断"]):
        return next(profile for keywords, profile in PROFILE_RULES if "场景判断" in keywords)
    if any(key in title_source for key in ["交互设计", "信任触点", "AI UX"]):
        return next(profile for keywords, profile in PROFILE_RULES if "交互设计" in keywords)
    if any(key in title_source for key in ["大语言模型", "LLM", "基础常识", "能力边界"]):
        return next(profile for keywords, profile in PROFILE_RULES if "大语言模型" in keywords)
    if any(key in title_source for key in ["Prompt", "Schema"]):
        return next(profile for keywords, profile in PROFILE_RULES if "Prompt" in keywords)
    if any(key in title_source for key in ["Agent", "Skill", "Gateway", "Loop", "工具调用", "Harness"]):
        return next(profile for keywords, profile in PROFILE_RULES if "Agent" in keywords)
    if any(key in title_source for key in ["RAG", "知识库", "召回", "Top-K"]):
        return next(profile for keywords, profile in PROFILE_RULES if "RAG" in keywords)
    if any(key in title_source for key in ["评测", "Eval", "质量", "验收", "回归"]):
        return next(profile for keywords, profile in PROFILE_RULES if "评测" in keywords)
    if any(key in title_source for key in ["安全", "隐私", "治理", "红线", "风险", "信任"]):
        return next(profile for keywords, profile in PROFILE_RULES if "安全" in keywords)
    if any(key in title_source for key in ["路线", "成长", "能力模型", "90 天", "90天", "作品集", "转型", "Product Owner"]):
        return next(profile for keywords, profile in PROFILE_RULES if "路线" in keywords)
    if any(key in title_source for key in ["数据", "埋点", "ROI", "商业", "成本", "延迟", "性能", "飞轮"]):
        return next(profile for keywords, profile in PROFILE_RULES if "数据" in keywords)
    if any(key in title_source for key in ["用户研究", "PRD", "MVP", "洞察助手", "旅程", "项目"]):
        return next(profile for keywords, profile in PROFILE_RULES if "用户研究" in keywords)
    if any(key in title_source for key in ["模板", "清单", "RACI", "Roadmap", "周报", "方案"]):
        return next(profile for keywords, profile in PROFILE_RULES if "模板" in keywords)

    haystack = f"{title_source} {base.plain_text(str(doc['markdown']))[:700]}"
    for keywords, profile in PROFILE_RULES:
        if any(keyword in haystack for keyword in keywords):
            return profile
    return DEFAULT_PROFILE


def word_count(doc: dict[str, object]) -> int:
    return len(re.sub(r"\s+", "", base.plain_text(str(doc["markdown"]))))


def difficulty(doc: dict[str, object]) -> str:
    title = str(doc["title"])
    text = f"{title} {doc['source_path']}"
    if any(key in text for key in ["Gateway", "Loop", "Agent 产品结构", "RAG 进阶", "Schema", "Fine-tuning"]):
        return "进阶"
    if any(key in text for key in ["模板", "清单", "PRD", "方案", "周报"]):
        return "实战"
    return "基础"


def tailwind_head(title: str, description: str, css_prefix: str) -> str:
    return f"""<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(description)}">
  <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
  <link rel="stylesheet" href="{css_prefix}assets/css/style.css">
</head>"""


def brand(prefix: str) -> str:
    return f"""<a class="flex items-center gap-3 font-black tracking-tight text-slate-950" href="{prefix}index.html">
  <span class="grid h-9 w-9 place-items-center rounded-lg bg-slate-950 text-xs font-black text-white">APO</span>
  <span class="hidden sm:inline">AI Product Owner 成长知识库</span>
</a>"""


def header(prefix: str, article: bool = False) -> str:
    module_href = f"{prefix}modules/start.html"
    return f"""<header class="sticky top-0 z-50 border-b border-slate-200/80 bg-white/90 backdrop-blur-xl">
  <div class="mx-auto flex h-16 max-w-[1440px] items-center justify-between gap-4 px-4 sm:px-6">
    {brand(prefix)}
    <nav class="hidden items-center gap-1 md:flex">
      <a class="rounded-lg px-3 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-100 hover:text-slate-950" href="{prefix}index.html#paths">阅读路径</a>
      <a class="rounded-lg px-3 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-100 hover:text-slate-950" href="{module_href}">模块</a>
      <button class="rounded-lg px-3 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-100 hover:text-slate-950" data-search-open>搜索</button>
    </nav>
    <div class="flex items-center gap-2">
      <button class="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-bold text-slate-700 shadow-sm hover:bg-slate-50" data-search-open>搜索</button>
      <button class="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-bold text-slate-700 shadow-sm hover:bg-slate-50 lg:hidden" data-nav-toggle>{'目录' if article else '模块'}</button>
    </div>
  </div>
</header>"""


def search_modal(prefix: str) -> str:
    return f"""<div class="fixed inset-0 z-[90] hidden bg-slate-950/40 p-4 pt-[8vh]" data-search-modal aria-hidden="true">
  <div class="mx-auto max-w-3xl overflow-hidden rounded-xl border border-slate-200 bg-white shadow-2xl">
    <div class="flex gap-3 border-b border-slate-200 p-3">
      <input class="min-h-12 flex-1 rounded-lg border border-slate-200 px-4 text-base outline-none focus:border-teal-500 focus:ring-4 focus:ring-teal-500/10" type="search" placeholder="搜索 RAG、Agent、Eval、治理、作品集..." data-search-input>
      <button class="rounded-lg bg-slate-950 px-4 text-sm font-bold text-white" data-search-close>关闭</button>
    </div>
    <div class="max-h-[62vh] overflow-auto p-2" data-search-results></div>
  </div>
</div>"""


def nav_sidebar(docs: list[dict[str, object]], current_slug: str | None, prefix: str) -> str:
    grouped = docs_by_module(docs)
    chunks = []
    for module in MODULES:
        items = grouped.get(module["slug"], [])
        if not items:
            continue
        color = COLOR[module["color"]]
        module_href = f"{prefix}modules/{module['slug']}.html"
        chunks.append(
            f"""<section class="mb-5">
  <a class="mb-2 flex items-center justify-between rounded-lg px-2 py-1.5 text-xs font-black uppercase tracking-wide {color['text']} hover:bg-slate-100" href="{module_href}">
    <span>{html.escape(module['title'])}</span><span>{len(items)}</span>
  </a>"""
        )
        for i, doc in enumerate(items, 1):
            active = doc["slug"] == current_slug
            cls = "bg-slate-950 text-white shadow-sm" if active else "text-slate-600 hover:bg-slate-100 hover:text-slate-950"
            chunks.append(
                f"""<a class="group mb-1 grid grid-cols-[1.5rem_minmax(0,1fr)_auto] items-center gap-2 rounded-lg px-2 py-2 text-sm {cls}" href="{prefix}articles/{doc['slug']}" data-title="{html.escape(str(doc['title']).lower())}" data-module="{html.escape(module['title'].lower())}">
  <span class="text-xs opacity-60">{i:02d}</span>
  <span class="truncate">{html.escape(str(doc['title']))}</span>
  <span class="text-[11px] opacity-60">{doc['minutes']}m</span>
</a>"""
            )
        chunks.append("</section>")
    return "\n".join(chunks)


def html_list(items: list[str], kind: str = "ul") -> str:
    tag = "ol" if kind == "ol" else "ul"
    return f"<{tag}>" + "".join(f"<li>{html.escape(item)}</li>" for item in items) + f"</{tag}>"


def content_enhancement(doc: dict[str, object], module: dict[str, str]) -> tuple[str, str]:
    profile = profile_for_doc(doc)
    title = str(doc["title"])
    source = str(doc["source_path"])
    deliverables = profile["deliverables"][:]
    if "模板" in title or "清单" in title:
        deliverables = ["可直接复制的模板结构", "字段使用说明", "评审时的检查问题", "交付后的维护责任人"]
    if "路线" in title or "成长" in title:
        deliverables = ["阶段目标", "能力缺口清单", "每周练习任务", "作品集证据"]
    outcomes = [
        f"能用一句话解释「{title}」为什么值得学。",
        f"能把本文内容转成一个真实工作中的交付物，而不是只停留在概念理解。",
        f"能识别这个主题最常见的翻车点，并在 PRD 或评审中提前补上。",
    ]
    guide = f"""<section class="not-prose my-8 rounded-xl border border-slate-200 bg-slate-50 p-5">
  <div class="mb-4 flex flex-wrap items-center gap-2">
    <span class="rounded-full px-3 py-1 text-xs font-black ring-1 {COLOR[module['color']]['badge']}">本篇导读</span>
    <span class="text-sm font-semibold text-slate-500">{html.escape(profile['name'])}</span>
  </div>
  <div class="grid gap-3 md:grid-cols-3">
    <div class="rounded-lg border border-slate-200 bg-white p-4">
      <div class="text-sm font-black text-slate-950">你会看懂</div>
      <p class="mt-2 text-sm text-slate-600">{html.escape(outcomes[0])}</p>
    </div>
    <div class="rounded-lg border border-slate-200 bg-white p-4">
      <div class="text-sm font-black text-slate-950">你会拿走</div>
      <p class="mt-2 text-sm text-slate-600">{html.escape(deliverables[0])}、{html.escape(deliverables[1])}。</p>
    </div>
    <div class="rounded-lg border border-slate-200 bg-white p-4">
      <div class="text-sm font-black text-slate-950">你要避免</div>
      <p class="mt-2 text-sm text-slate-600">{html.escape(profile['mistakes'][0])}。</p>
    </div>
  </div>
</section>"""
    supplement = f"""<section class="not-prose mt-12 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
  <div class="mb-5">
    <span class="rounded-full px-3 py-1 text-xs font-black ring-1 {COLOR[module['color']]['badge']}">实战化补充</span>
    <h2 class="mt-4 text-2xl font-black tracking-tight text-slate-950">把「{html.escape(title)}」用到真实工作里</h2>
    <p class="mt-2 text-slate-600">这一段不是补术语，而是帮你把文章从“读懂”推进到“能用”。公开分享时，读者最需要的通常不是更多概念，而是知道下一步该怎么做。</p>
  </div>
  <div class="grid gap-4 lg:grid-cols-2">
    <div class="rounded-lg bg-slate-50 p-4">
      <h3 class="text-base font-black text-slate-950">轻松理解</h3>
      <p class="mt-2 text-sm leading-7 text-slate-600">{html.escape(profile['analogy'])}</p>
    </div>
    <div class="rounded-lg bg-slate-50 p-4">
      <h3 class="text-base font-black text-slate-950">业务小案例</h3>
      <p class="mt-2 text-sm leading-7 text-slate-600">{html.escape(profile['case'])}</p>
    </div>
    <div class="rounded-lg bg-slate-50 p-4">
      <h3 class="text-base font-black text-slate-950">常见翻车点</h3>
      <ul class="mt-2 space-y-2 text-sm leading-7 text-slate-600">
        {''.join(f'<li class="flex gap-2"><span class="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-rose-500"></span><span>{html.escape(item)}</span></li>' for item in profile['mistakes'])}
      </ul>
    </div>
    <div class="rounded-lg bg-slate-50 p-4">
      <h3 class="text-base font-black text-slate-950">建议沉淀的交付物</h3>
      <ul class="mt-2 space-y-2 text-sm leading-7 text-slate-600">
        {''.join(f'<li class="flex gap-2"><span class="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-teal-500"></span><span>{html.escape(item)}</span></li>' for item in deliverables)}
      </ul>
    </div>
  </div>
  <div class="mt-4 rounded-lg border border-dashed border-slate-300 bg-white p-4">
    <h3 class="text-base font-black text-slate-950">读完马上做</h3>
    <p class="mt-2 text-sm leading-7 text-slate-600">{html.escape(profile['exercise'])}</p>
  </div>
  <div class="mt-4 rounded-lg bg-slate-950 p-4 text-white">
    <div class="text-xs font-black uppercase text-slate-400">一句可复述总结</div>
    <p class="mt-2 text-base font-semibold leading-7">学习「{html.escape(title)}」的重点，不是背定义，而是把它变成可判断、可设计、可验收、可复盘的产品工作。</p>
  </div>
  <p class="mt-4 text-xs text-slate-400">增强来源：{html.escape(source)} · 主题识别：{html.escape(profile['name'])}</p>
</section>"""
    return guide, supplement


def toc_html(headings: list[dict[str, str]]) -> str:
    if not headings:
        return '<p class="text-sm text-slate-500">这篇文章结构很短，可以直接阅读。</p>'
    return "".join(
        f'<a class="block rounded-md px-2 py-1.5 text-sm leading-5 text-slate-500 hover:bg-slate-100 hover:text-slate-950 {"pl-5" if h["level"] == "3" else "font-semibold"}" href="#{html.escape(h["id"])}">{html.escape(h["title"])}</a>'
        for h in headings[:28]
    )


def article_template(doc: dict[str, object], docs: list[dict[str, object]], groups: dict[str, list[dict[str, object]]], body: str, headings: list[dict[str, str]]) -> str:
    module = module_for_doc(doc)
    module_docs = groups[module["slug"]]
    module_index = module_docs.index(doc) + 1
    overall_index = docs.index(doc) + 1
    prev_doc = docs[overall_index - 2] if overall_index > 1 else None
    next_doc = docs[overall_index] if overall_index < len(docs) else None
    img, caption = base.choose_illustration(doc)
    guide, supplement = content_enhancement(doc, module)
    color = COLOR[module["color"]]
    pager = []
    if prev_doc:
        pager.append(f'<a class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm hover:border-slate-300" href="{prev_doc["slug"]}"><span class="text-xs font-bold text-slate-400">上一篇</span><strong class="mt-1 block text-slate-950">{html.escape(str(prev_doc["title"]))}</strong></a>')
    if next_doc:
        pager.append(f'<a class="rounded-xl border border-slate-200 bg-white p-4 text-right shadow-sm hover:border-slate-300" href="{next_doc["slug"]}"><span class="text-xs font-bold text-slate-400">下一篇</span><strong class="mt-1 block text-slate-950">{html.escape(str(next_doc["title"]))}</strong></a>')

    return f"""<!doctype html>
<html lang="zh-CN" class="scroll-smooth">
{tailwind_head(str(doc['title']) + ' - AI Product Owner 成长知识库', str(doc['excerpt']), '../')}
<body class="bg-slate-50 text-slate-900 antialiased">
  <div class="fixed left-0 top-0 z-[80] h-1 bg-gradient-to-r from-teal-500 via-blue-500 to-amber-400" id="progressBar"></div>
  {header('../', article=True)}
  <div class="mx-auto grid max-w-[1440px] grid-cols-1 lg:grid-cols-[320px_minmax(0,1fr)]">
    <aside class="fixed inset-y-0 left-0 z-[70] w-[86vw] max-w-sm -translate-x-full overflow-y-auto border-r border-slate-200 bg-white p-4 shadow-2xl transition-transform lg:sticky lg:top-16 lg:h-[calc(100vh-4rem)] lg:w-auto lg:max-w-none lg:translate-x-0 lg:shadow-none" id="sidebar">
      <div class="mb-4 flex items-center justify-between lg:hidden">
        <strong>文章目录</strong>
        <button class="rounded-lg border border-slate-200 px-3 py-1 text-sm font-bold" data-nav-toggle>关闭</button>
      </div>
      <input class="mb-4 h-10 w-full rounded-lg border border-slate-200 px-3 text-sm outline-none focus:border-teal-500 focus:ring-4 focus:ring-teal-500/10" type="search" placeholder="筛选文章..." data-nav-filter>
      {nav_sidebar(docs, str(doc['slug']), '../')}
    </aside>
    <main class="grid min-w-0 grid-cols-1 gap-6 px-4 py-6 xl:grid-cols-[minmax(0,820px)_280px] xl:px-8">
      <article class="min-w-0 rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:p-8">
        <nav class="mb-5 flex flex-wrap items-center gap-2 text-sm text-slate-500">
          <a class="font-bold hover:text-slate-950" href="../index.html">首页</a>
          <span>/</span>
          <a class="font-bold hover:text-slate-950" href="../modules/{module['slug']}.html">{html.escape(module['title'])}</a>
          <span>/</span>
          <span>第 {module_index} 篇</span>
        </nav>
        <div class="mb-4 flex flex-wrap items-center gap-2">
          <span class="rounded-full px-3 py-1 text-xs font-black ring-1 {color['badge']}">{html.escape(module['title'])}</span>
          <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-600">{difficulty(doc)}</span>
          <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-600">{doc['minutes']} 分钟阅读</span>
        </div>
        <h1 class="max-w-3xl text-4xl font-black leading-tight tracking-tight text-slate-950 sm:text-5xl">{html.escape(str(doc['title']))}</h1>
        <p class="mt-5 max-w-3xl text-lg leading-8 text-slate-600">{html.escape(str(doc['excerpt']))}</p>
        <div class="mt-6 grid gap-3 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600 sm:grid-cols-3">
          <div><span class="block text-xs font-black uppercase text-slate-400">当前位置</span><strong class="mt-1 block text-slate-950">{html.escape(module['title'])} · {module_index}/{len(module_docs)}</strong></div>
          <div><span class="block text-xs font-black uppercase text-slate-400">全库进度</span><strong class="mt-1 block text-slate-950">{overall_index}/{len(docs)} 篇</strong></div>
          <div><span class="block text-xs font-black uppercase text-slate-400">源文件</span><strong class="mt-1 block truncate text-slate-950">{html.escape(str(doc['source_path']))}</strong></div>
        </div>
        <figure class="my-8 overflow-hidden rounded-xl border border-slate-200 bg-slate-50 p-3">
          <img class="w-full rounded-lg" src="../assets/img/{img}" alt="{html.escape(caption)}">
          <figcaption class="mt-3 text-center text-sm text-slate-500">{html.escape(caption)}</figcaption>
        </figure>
        {guide}
        <div class="article-content">
          {body}
        </div>
        {supplement}
        <nav class="mt-6 grid gap-3 sm:grid-cols-2">
          {''.join(pager)}
        </nav>
      </article>
      <aside class="hidden xl:block">
        <div class="sticky top-24 space-y-4">
          <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <div class="mb-3 text-sm font-black text-slate-950">本文目录</div>
            {toc_html(headings)}
          </div>
          <div class="rounded-xl border {color['border']} {color['soft']} p-4">
            <div class="text-sm font-black text-slate-950">模块目标</div>
            <p class="mt-2 text-sm leading-6 text-slate-600">{html.escape(module['promise'])}</p>
          </div>
        </div>
      </aside>
    </main>
  </div>
  {search_modal('../')}
  <script src="../assets/js/search-index.js"></script>
  <script src="../assets/js/main.js"></script>
</body>
</html>"""


def doc_link(doc: dict[str, object], prefix: str = "") -> str:
    return f"{prefix}articles/{doc['slug']}"


def path_cards(docs: list[dict[str, object]]) -> str:
    by_title = {str(doc["title"]): doc for doc in docs}
    cards = []
    for path in PATHS:
        items = []
        for title in path["titles"]:
            doc = by_title.get(title)
            if doc:
                items.append(
                    f"""<a class="group flex items-center justify-between gap-4 rounded-lg border border-slate-200 bg-white p-3 hover:border-slate-300 hover:bg-slate-50" href="{doc_link(doc)}">
  <span class="font-bold text-slate-800 group-hover:text-slate-950">{html.escape(title)}</span>
  <span class="text-xs font-bold text-slate-400">{doc['minutes']}m</span>
</a>"""
                )
        cards.append(
            f"""<section class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
  <h3 class="text-xl font-black tracking-tight text-slate-950">{html.escape(path['title'])}</h3>
  <p class="mt-2 text-sm leading-6 text-slate-600">{html.escape(path['desc'])}</p>
  <div class="mt-4 space-y-2">{''.join(items)}</div>
</section>"""
        )
    return "".join(cards)


def index_template(docs: list[dict[str, object]], groups: dict[str, list[dict[str, object]]]) -> str:
    total_minutes = sum(int(doc["minutes"]) for doc in docs)
    total_words = sum(word_count(doc) for doc in docs)
    module_cards = []
    for module in MODULES:
        items = groups.get(module["slug"], [])
        if not items:
            continue
        color = COLOR[module["color"]]
        module_cards.append(
            f"""<a class="group rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-md" href="modules/{module['slug']}.html">
  <div class="mb-4 flex items-center justify-between">
    <span class="rounded-full px-3 py-1 text-xs font-black ring-1 {color['badge']}">{len(items)} 篇</span>
    <span class="text-slate-300 transition group-hover:text-slate-500">→</span>
  </div>
  <h3 class="text-xl font-black tracking-tight text-slate-950">{html.escape(module['title'])}</h3>
  <p class="mt-2 text-sm leading-6 text-slate-600">{html.escape(module['short'])}</p>
  <p class="mt-4 text-sm leading-6 text-slate-500">{html.escape(module['promise'])}</p>
</a>"""
        )
    return f"""<!doctype html>
<html lang="zh-CN" class="scroll-smooth">
{tailwind_head('AI Product Owner 成长知识库', '面向 AI 产品经理与 AI Product Owner 的公开学习知识库。', '')}
<body class="bg-slate-50 text-slate-900 antialiased">
  {header('')}
  <main>
    <section class="mx-auto grid max-w-[1180px] gap-10 px-4 py-14 sm:px-6 lg:grid-cols-[minmax(0,1fr)_420px] lg:py-20">
      <div>
        <div class="mb-5 inline-flex rounded-full bg-teal-50 px-3 py-1 text-sm font-black text-teal-700 ring-1 ring-teal-200">公开发布版 · Tailwind v4</div>
        <h1 class="max-w-4xl text-5xl font-black leading-[1.05] tracking-tight text-slate-950 sm:text-6xl lg:text-7xl">把 AI 能力放进真实业务流程，并对结果负责。</h1>
        <p class="mt-6 max-w-2xl text-lg leading-8 text-slate-600">这套知识库不是术语堆叠，而是一条从场景判断、能力编排、质量评测到治理复盘的学习路径。你可以按路径学习，也可以直接进入某个模块解决手头问题。</p>
        <div class="mt-8 flex flex-wrap gap-3">
          <a class="rounded-lg bg-slate-950 px-5 py-3 text-sm font-black text-white shadow-sm hover:bg-slate-800" href="modules/start.html">按模块阅读</a>
          <a class="rounded-lg border border-slate-200 bg-white px-5 py-3 text-sm font-black text-slate-800 shadow-sm hover:bg-slate-50" href="#paths">选择阅读路径</a>
          <button class="rounded-lg border border-slate-200 bg-white px-5 py-3 text-sm font-black text-slate-800 shadow-sm hover:bg-slate-50" data-search-open>搜索主题</button>
        </div>
      </div>
      <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-xl">
        <img class="rounded-lg" src="assets/img/hero-lab.svg" alt="AI Product Owner 知识库结构图">
        <div class="mt-4 grid grid-cols-2 gap-3">
          <div class="rounded-lg bg-slate-50 p-4"><strong class="block text-2xl font-black text-slate-950">{len(docs)}</strong><span class="text-sm text-slate-500">篇文章</span></div>
          <div class="rounded-lg bg-slate-50 p-4"><strong class="block text-2xl font-black text-slate-950">{len(MODULES)}</strong><span class="text-sm text-slate-500">个模块</span></div>
          <div class="rounded-lg bg-slate-50 p-4"><strong class="block text-2xl font-black text-slate-950">{total_minutes}</strong><span class="text-sm text-slate-500">分钟阅读</span></div>
          <div class="rounded-lg bg-slate-50 p-4"><strong class="block text-2xl font-black text-slate-950">{total_words//1000}k</strong><span class="text-sm text-slate-500">字内容</span></div>
        </div>
      </div>
    </section>
    <section class="border-y border-slate-200 bg-white">
      <div class="mx-auto grid max-w-[1180px] gap-4 px-4 py-6 sm:grid-cols-2 sm:px-6 lg:grid-cols-4">
        <div><span class="text-xs font-black uppercase text-slate-400">第一步</span><p class="mt-1 font-bold text-slate-900">先确定自己在哪条学习路径</p></div>
        <div><span class="text-xs font-black uppercase text-slate-400">第二步</span><p class="mt-1 font-bold text-slate-900">进入模块，按顺序读关键文章</p></div>
        <div><span class="text-xs font-black uppercase text-slate-400">第三步</span><p class="mt-1 font-bold text-slate-900">把文章转成模板或项目交付物</p></div>
        <div><span class="text-xs font-black uppercase text-slate-400">第四步</span><p class="mt-1 font-bold text-slate-900">用 Eval、治理和复盘证明结果</p></div>
      </div>
    </section>
    <section class="mx-auto max-w-[1180px] px-4 py-14 sm:px-6" id="paths">
      <div class="mb-6">
        <h2 class="text-3xl font-black tracking-tight text-slate-950">先选一条阅读路径</h2>
        <p class="mt-2 text-slate-600">不要从目录里迷路。根据你现在的目标，直接进入最有用的路线。</p>
      </div>
      <div class="grid gap-4 lg:grid-cols-3">{path_cards(docs)}</div>
    </section>
    <section class="mx-auto max-w-[1180px] px-4 pb-16 sm:px-6">
      <div class="mb-6">
        <h2 class="text-3xl font-black tracking-tight text-slate-950">知识库模块</h2>
        <p class="mt-2 text-slate-600">每个模块都有自己的目标、文章顺序和可交付物。</p>
      </div>
      <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">{''.join(module_cards)}</div>
    </section>
  </main>
  {search_modal('')}
  <script src="assets/js/search-index.js"></script>
  <script src="assets/js/main.js"></script>
</body>
</html>"""


def module_template(module: dict[str, str], docs: list[dict[str, object]], module_docs: list[dict[str, object]], groups: dict[str, list[dict[str, object]]]) -> str:
    color = COLOR[module["color"]]
    doc_cards = []
    for i, doc in enumerate(module_docs, 1):
        profile = profile_for_doc(doc)
        doc_cards.append(
            f"""<a class="group rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-md" href="../articles/{doc['slug']}">
  <div class="flex items-center justify-between gap-3">
    <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-black text-slate-600">第 {i:02d} 篇</span>
    <span class="text-xs font-bold text-slate-400">{doc['minutes']}m · {difficulty(doc)}</span>
  </div>
  <h3 class="mt-4 text-xl font-black leading-snug tracking-tight text-slate-950">{html.escape(str(doc['title']))}</h3>
  <p class="mt-2 line-clamp-3 text-sm leading-6 text-slate-600">{html.escape(str(doc['excerpt']))}</p>
  <div class="mt-4 rounded-lg bg-slate-50 p-3 text-sm leading-6 text-slate-500">
    <strong class="text-slate-800">读完拿走：</strong>{html.escape(profile['deliverables'][0])}
  </div>
</a>"""
        )
    return f"""<!doctype html>
<html lang="zh-CN" class="scroll-smooth">
{tailwind_head(module['title'] + ' - AI Product Owner 成长知识库', module['promise'], '../')}
<body class="bg-slate-50 text-slate-900 antialiased">
  {header('../')}
  <main class="mx-auto max-w-[1180px] px-4 py-10 sm:px-6">
    <nav class="mb-6 flex flex-wrap items-center gap-2 text-sm text-slate-500">
      <a class="font-bold hover:text-slate-950" href="../index.html">首页</a>
      <span>/</span>
      <span>{html.escape(module['title'])}</span>
    </nav>
    <section class="grid gap-8 lg:grid-cols-[minmax(0,1fr)_340px]">
      <div>
        <span class="rounded-full px-3 py-1 text-xs font-black ring-1 {color['badge']}">{len(module_docs)} 篇文章</span>
        <h1 class="mt-5 text-5xl font-black leading-tight tracking-tight text-slate-950">{html.escape(module['title'])}</h1>
        <p class="mt-4 max-w-3xl text-lg leading-8 text-slate-600">{html.escape(module['promise'])}</p>
      </div>
      <aside class="rounded-xl border {color['border']} {color['soft']} p-5">
        <h2 class="text-lg font-black text-slate-950">这个模块怎么读</h2>
        <ol class="mt-3 space-y-2 text-sm leading-6 text-slate-600">
          <li>1. 先读前两篇，建立判断框架。</li>
          <li>2. 遇到概念时直接做一张表或一页图。</li>
          <li>3. 最后把内容落到你的项目或作品集。</li>
        </ol>
      </aside>
    </section>
    <section class="mt-10 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      {''.join(doc_cards)}
    </section>
  </main>
  {search_modal('../')}
  <script src="../assets/js/search-index.js"></script>
  <script src="../assets/js/main.js"></script>
</body>
</html>"""


def write_css() -> None:
    (CSS_DIR / "style.css").write_text(
        r"""
html { scroll-behavior: smooth; }
body { letter-spacing: 0; }
.article-content {
  color: #334155;
  font-size: 17px;
  line-height: 1.9;
}
.article-content h1,
.article-content h2,
.article-content h3,
.article-content h4 {
  color: #020617;
  letter-spacing: 0;
  scroll-margin-top: 96px;
}
.article-content h2 {
  margin-top: 2.6rem;
  padding-top: 1.4rem;
  border-top: 1px solid #e2e8f0;
  font-size: 1.72rem;
  line-height: 1.25;
  font-weight: 900;
}
.article-content h3 {
  margin-top: 1.9rem;
  font-size: 1.22rem;
  line-height: 1.35;
  font-weight: 900;
}
.article-content p { margin: 1rem 0; }
.article-content ul,
.article-content ol {
  margin: 1rem 0;
  padding-left: 1.35rem;
}
.article-content li { margin: .4rem 0; }
.article-content strong { color: #0f172a; font-weight: 850; }
.article-content a { color: #0f766e; text-decoration: underline; text-underline-offset: 3px; }
.article-content code {
  border-radius: .4rem;
  background: #f1f5f9;
  padding: .12rem .35rem;
  color: #be123c;
  font-size: .9em;
}
.article-content pre {
  position: relative;
  overflow: auto;
  margin: 1.2rem 0;
  border-radius: .75rem;
  background: #0f172a;
  padding: 1.1rem;
  color: #f8fafc;
  line-height: 1.7;
}
.article-content pre code {
  background: transparent;
  color: inherit;
  padding: 0;
}
.copy-code {
  position: absolute;
  right: .65rem;
  top: .65rem;
  border: 1px solid rgba(255,255,255,.22);
  border-radius: .45rem;
  background: rgba(255,255,255,.1);
  color: white;
  padding: .25rem .55rem;
  font-size: 12px;
  font-weight: 800;
}
.article-content blockquote {
  margin: 1.3rem 0;
  border-left: 4px solid #0f766e;
  border-radius: .75rem;
  background: #f0fdfa;
  padding: .9rem 1.1rem;
  color: #115e59;
}
.table-wrap {
  overflow: auto;
  margin: 1.2rem 0;
  border: 1px solid #e2e8f0;
  border-radius: .75rem;
}
.article-content table {
  width: 100%;
  min-width: 680px;
  border-collapse: collapse;
  background: white;
}
.article-content th,
.article-content td {
  border-bottom: 1px solid #e2e8f0;
  padding: .8rem .9rem;
  text-align: left;
  vertical-align: top;
}
.article-content th {
  background: #f8fafc;
  color: #475569;
  font-size: .82rem;
  font-weight: 900;
}
.article-content tr:last-child td { border-bottom: 0; }
[data-search-modal].open { display: block; }
#sidebar.open { transform: translateX(0); }
""".strip()
        + "\n",
        encoding="utf-8",
    )


def write_js(docs: list[dict[str, object]]) -> None:
    search_index = [
        {
            "title": doc["title"],
            "section": module_for_doc(doc)["title"],
            "excerpt": doc["excerpt"],
            "url": "articles/" + str(doc["slug"]),
            "articleUrl": str(doc["slug"]),
            "moduleUrl": "../articles/" + str(doc["slug"]),
            "text": base.plain_text(str(doc["markdown"]))[:2600],
        }
        for doc in docs
    ]
    (JS_DIR / "search-index.js").write_text("window.SEARCH_INDEX = " + json.dumps(search_index, ensure_ascii=False) + ";\n", encoding="utf-8")
    (JS_DIR / "main.js").write_text(
        r"""
(function () {
  const modal = document.querySelector('[data-search-modal]');
  const searchInput = document.querySelector('[data-search-input]');
  const searchResults = document.querySelector('[data-search-results]');
  const inArticle = document.body.querySelector('article') && location.pathname.includes('/articles/');
  const inModule = location.pathname.includes('/modules/');

  function urlFor(item) {
    if (inArticle) return item.articleUrl;
    if (inModule) return item.moduleUrl;
    return item.url;
  }

  function renderResults(query) {
    if (!searchResults) return;
    const q = query.trim().toLowerCase();
    const data = window.SEARCH_INDEX || [];
    const results = q
      ? data.filter((item) => [item.title, item.section, item.excerpt, item.text].join(' ').toLowerCase().includes(q)).slice(0, 14)
      : data.slice(0, 10);
    searchResults.innerHTML = results.map((item) => `
      <a class="block rounded-lg p-4 hover:bg-slate-50" href="${urlFor(item)}">
        <div class="flex items-center justify-between gap-3">
          <strong class="text-slate-950">${item.title}</strong>
          <span class="shrink-0 rounded-full bg-slate-100 px-2 py-1 text-xs font-bold text-slate-500">${item.section}</span>
        </div>
        <p class="mt-2 text-sm leading-6 text-slate-600">${item.excerpt}</p>
      </a>
    `).join('') || '<div class="p-4 text-sm text-slate-500">没搜到，换个关键词试试。</div>';
  }

  function openSearch() {
    if (!modal) return;
    modal.classList.add('open');
    modal.setAttribute('aria-hidden', 'false');
    renderResults('');
    setTimeout(() => searchInput && searchInput.focus(), 20);
  }
  function closeSearch() {
    if (!modal) return;
    modal.classList.remove('open');
    modal.setAttribute('aria-hidden', 'true');
  }
  document.querySelectorAll('[data-search-open]').forEach((button) => button.addEventListener('click', openSearch));
  document.querySelectorAll('[data-search-close]').forEach((button) => button.addEventListener('click', closeSearch));
  if (searchInput) searchInput.addEventListener('input', (event) => renderResults(event.target.value));
  if (modal) modal.addEventListener('click', (event) => { if (event.target === modal) closeSearch(); });
  document.addEventListener('keydown', (event) => {
    if (event.key === '/' && !event.metaKey && !event.ctrlKey && document.activeElement.tagName !== 'INPUT') {
      event.preventDefault();
      openSearch();
    }
    if (event.key === 'Escape') closeSearch();
  });

  const progress = document.getElementById('progressBar');
  function updateProgress() {
    if (!progress) return;
    const max = document.documentElement.scrollHeight - window.innerHeight;
    progress.style.width = `${Math.min(100, Math.max(0, max > 0 ? (window.scrollY / max) * 100 : 0))}%`;
  }
  window.addEventListener('scroll', updateProgress, { passive: true });
  updateProgress();

  document.querySelectorAll('pre').forEach((pre) => {
    const button = document.createElement('button');
    button.className = 'copy-code';
    button.type = 'button';
    button.textContent = '复制';
    button.addEventListener('click', async () => {
      const code = pre.innerText.replace(/^复制\s*/, '');
      try {
        await navigator.clipboard.writeText(code);
        button.textContent = '已复制';
        setTimeout(() => { button.textContent = '复制'; }, 1200);
      } catch (error) {
        button.textContent = '手动复制';
      }
    });
    pre.appendChild(button);
  });

  const navFilter = document.querySelector('[data-nav-filter]');
  if (navFilter) {
    navFilter.addEventListener('input', (event) => {
      const q = event.target.value.trim().toLowerCase();
      document.querySelectorAll('[data-title]').forEach((link) => {
        const haystack = `${link.dataset.title || ''} ${link.dataset.module || ''}`;
        link.style.display = haystack.includes(q) ? '' : 'none';
      });
    });
  }

  document.querySelectorAll('[data-nav-toggle]').forEach((button) => {
    button.addEventListener('click', () => {
      const sidebar = document.getElementById('sidebar');
      if (sidebar) sidebar.classList.toggle('open');
    });
  });
})();
""".strip()
        + "\n",
        encoding="utf-8",
    )


def write_readme() -> None:
    (OUT_DIR / "README_发布说明.md").write_text(
        """# AI 产品经理学习知识库 HTML 发布版

打开 `index.html` 即可浏览。

## v2 更新

- 使用 Tailwind CSS v4 浏览器版本作为公开样式底座。
- 新增 `modules/` 模块页，让用户先按学习路径和模块进入，而不是直接掉进长目录。
- 每篇文章增加主题化导读、业务案例、常见误区、交付物和练习，不改动源 Markdown。
- 保留站内搜索、文章目录、阅读进度、代码复制和本地 SVG 插图。

## 重新生成

如果你继续修改 `AI产品经理学习知识库/` 里的 Markdown，可以在当前文件夹运行：

```bash
python3 build_site_v2.py
```

> 说明：Tailwind 官方浏览器 CDN 适合快速预览和轻量发布。如果要做正式高流量站点，建议后续把 Tailwind 编译成静态 CSS。
""",
        encoding="utf-8",
    )


def build() -> None:
    ensure_dirs()
    clean_generated_dirs()
    docs = base.collect_docs()
    groups = docs_by_module(docs)
    base.write_illustrations()
    for doc in docs:
        body, headings = base.render_markdown(str(doc["markdown"]))
        (ARTICLES_DIR / str(doc["slug"])).write_text(article_template(doc, docs, groups, body, headings), encoding="utf-8")
    for module in MODULES:
        module_docs = groups.get(module["slug"], [])
        if module_docs:
            (MODULES_DIR / f"{module['slug']}.html").write_text(module_template(module, docs, module_docs, groups), encoding="utf-8")
    (OUT_DIR / "index.html").write_text(index_template(docs, groups), encoding="utf-8")
    write_css()
    write_js(docs)
    write_readme()
    summary = {
        "generated_at": date.today().isoformat(),
        "version": "tailwind-v2",
        "documents": len(docs),
        "modules": len(MODULES),
        "articles_dir": str(ARTICLES_DIR),
    }
    (OUT_DIR / "build-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Generated v2 site: {len(docs)} documents, {len(MODULES)} modules -> {OUT_DIR}")


if __name__ == "__main__":
    build()
