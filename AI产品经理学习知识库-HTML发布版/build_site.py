#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
from datetime import date
from pathlib import Path


OUT_DIR = Path(__file__).resolve().parent
SOURCE_DIR = OUT_DIR.parent / "AI产品经理学习知识库"
ARTICLES_DIR = OUT_DIR / "articles"
ASSETS_DIR = OUT_DIR / "assets"
CSS_DIR = ASSETS_DIR / "css"
JS_DIR = ASSETS_DIR / "js"
IMG_DIR = ASSETS_DIR / "img"


SECTION_LABELS = {
    ".": "起步与说明",
    "01-AI产品经理全貌": "01 全貌地图",
    "02-核心知识点详解": "02 核心知识",
    "03-实战项目-AI用户研究洞察助手": "03 实战项目",
    "04-工作模板": "04 工作模板",
    "05-AI Product Owner成长路径": "05 成长路径",
    "06-AI Product Owner作战流程": "06 作战流程",
}


ILLUSTRATION_RULES = [
    (("RAG", "知识库", "召回", "引用"), "rag.svg", "把知识、证据和回答连成可信链路"),
    (("Agent", "Skill", "Gateway", "Loop", "工具调用", "Harness"), "agent-system.svg", "把模型能力装进受控的业务系统"),
    (("评测", "Eval", "质量", "验收", "回归"), "eval.svg", "用样本、指标和回归集守住质量底线"),
    (("安全", "隐私", "治理", "红线", "风险", "信任"), "governance.svg", "在可控边界内释放 AI 的生产力"),
    (("路线", "成长", "能力模型", "90天", "作品集", "转型"), "roadmap.svg", "把学习路径变成可执行的成长阶梯"),
    (("Prompt", "Schema", "契约"), "prompt-schema.svg", "让自然语言和产品系统稳定对接"),
    (("数据", "埋点", "ROI", "商业", "成本", "延迟", "性能"), "metrics.svg", "用数据证明 AI 是否真的创造结果"),
    (("用户研究", "PRD", "MVP", "实战项目", "洞察助手"), "research-assistant.svg", "从真实材料到洞察、机会点和 PRD 草稿"),
    (("模板", "清单", "RACI", "Roadmap", "周报"), "template-kit.svg", "把好方法沉淀成可复用的工作模板"),
]


def ensure_dirs() -> None:
    for path in (ARTICLES_DIR, CSS_DIR, JS_DIR, IMG_DIR):
        path.mkdir(parents=True, exist_ok=True)


def normalize_title(path: Path, text: str) -> str:
    for line in text.splitlines():
        match = re.match(r"^\s*#\s+(.+?)\s*$", line)
        if match:
            return match.group(1).strip()
    return path.stem


def plain_text(markdown: str) -> str:
    text = re.sub(r"```.*?```", " ", markdown, flags=re.S)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[*_>#|`-]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def excerpt(markdown: str, limit: int = 126) -> str:
    for line in markdown.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("```") or stripped.startswith("|"):
            continue
        clean = plain_text(stripped)
        if clean:
            return clean[:limit] + ("..." if len(clean) > limit else "")
    clean = plain_text(markdown)
    return clean[:limit] + ("..." if len(clean) > limit else "")


def reading_time(markdown: str) -> int:
    count = len(re.sub(r"\s+", "", plain_text(markdown)))
    return max(1, round(count / 650))


def inline_markdown(text: str) -> str:
    placeholders: list[str] = []

    def stash(value: str) -> str:
        placeholders.append(value)
        return f"\u0000{len(placeholders) - 1}\u0000"

    text = html.escape(text, quote=False)
    text = re.sub(
        r"`([^`]+)`",
        lambda m: stash(f"<code>{html.escape(m.group(1))}</code>"),
        text,
    )
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(
        r"\[([^\]]+)\]\((https?://[^)]+)\)",
        r'<a href="\2" target="_blank" rel="noreferrer">\1</a>',
        text,
    )
    for idx, value in enumerate(placeholders):
        text = text.replace(f"\u0000{idx}\u0000", value)
    return text


def split_table_row(line: str) -> list[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [cell.strip() for cell in line.split("|")]


def is_table_separator(line: str) -> bool:
    return bool(re.match(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$", line))


def make_heading_id(text: str, used: dict[str, int]) -> str:
    base = re.sub(r"<[^>]+>", "", text)
    base = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "-", base).strip("-").lower()
    if not base:
        base = "section"
    used[base] = used.get(base, 0) + 1
    return base if used[base] == 1 else f"{base}-{used[base]}"


def render_markdown(markdown: str) -> tuple[str, list[dict[str, str]]]:
    lines = markdown.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    headings: list[dict[str, str]] = []
    used_ids: dict[str, int] = {}
    i = 0
    skipped_first_h1 = False

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped.startswith("```"):
            language = stripped[3:].strip()
            code_lines: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1
            code = html.escape("\n".join(code_lines))
            lang_class = f' class="language-{html.escape(language)}"' if language else ""
            out.append(f"<pre><code{lang_class}>{code}</code></pre>")
            continue

        heading = re.match(r"^(#{1,6})\s+(.+?)\s*$", stripped)
        if heading:
            level = len(heading.group(1))
            raw_title = heading.group(2).strip()
            if level == 1 and not skipped_first_h1 and not out:
                skipped_first_h1 = True
                i += 1
                continue
            rendered_title = inline_markdown(raw_title)
            heading_id = make_heading_id(raw_title, used_ids)
            if level <= 3:
                headings.append({"level": str(level), "title": re.sub(r"<[^>]+>", "", rendered_title), "id": heading_id})
            out.append(f'<h{level} id="{heading_id}">{rendered_title}</h{level}>')
            i += 1
            continue

        if stripped in ("---", "***", "___"):
            out.append("<hr>")
            i += 1
            continue

        if i + 1 < len(lines) and "|" in stripped and is_table_separator(lines[i + 1]):
            table_lines = [stripped, lines[i + 1].strip()]
            i += 2
            while i < len(lines) and "|" in lines[i].strip() and lines[i].strip():
                table_lines.append(lines[i].strip())
                i += 1
            headers = split_table_row(table_lines[0])
            body = [split_table_row(row) for row in table_lines[2:]]
            out.append('<div class="table-wrap"><table>')
            out.append("<thead><tr>" + "".join(f"<th>{inline_markdown(cell)}</th>" for cell in headers) + "</tr></thead>")
            out.append("<tbody>")
            for row in body:
                if len(row) < len(headers):
                    row = row + [""] * (len(headers) - len(row))
                out.append("<tr>" + "".join(f"<td>{inline_markdown(cell)}</td>" for cell in row[: len(headers)]) + "</tr>")
            out.append("</tbody></table></div>")
            continue

        if stripped.startswith(">"):
            quote_lines: list[str] = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote_lines.append(lines[i].strip().lstrip(">").strip())
                i += 1
            out.append("<blockquote>" + "".join(f"<p>{inline_markdown(q)}</p>" for q in quote_lines if q) + "</blockquote>")
            continue

        if re.match(r"^\s*[-*+]\s+", line):
            items: list[str] = []
            while i < len(lines) and re.match(r"^\s*[-*+]\s+", lines[i]):
                item = re.sub(r"^\s*[-*+]\s+", "", lines[i]).strip()
                items.append(item)
                i += 1
            out.append("<ul>" + "".join(f"<li>{inline_markdown(item)}</li>" for item in items) + "</ul>")
            continue

        if re.match(r"^\s*\d+\.\s+", line):
            items = []
            while i < len(lines) and re.match(r"^\s*\d+\.\s+", lines[i]):
                item = re.sub(r"^\s*\d+\.\s+", "", lines[i]).strip()
                items.append(item)
                i += 1
            out.append("<ol>" + "".join(f"<li>{inline_markdown(item)}</li>" for item in items) + "</ol>")
            continue

        paragraph: list[str] = []
        while i < len(lines):
            current = lines[i]
            current_stripped = current.strip()
            if (
                not current_stripped
                or current_stripped.startswith("```")
                or re.match(r"^(#{1,6})\s+", current_stripped)
                or (i + 1 < len(lines) and "|" in current_stripped and is_table_separator(lines[i + 1]))
                or current_stripped.startswith(">")
                or re.match(r"^\s*[-*+]\s+", current)
                or re.match(r"^\s*\d+\.\s+", current)
            ):
                break
            paragraph.append(current_stripped)
            i += 1
        out.append("<p>" + inline_markdown(" ".join(paragraph)) + "</p>")

    return "\n".join(out), headings


def collect_docs() -> list[dict[str, object]]:
    docs: list[dict[str, object]] = []
    paths = sorted(SOURCE_DIR.rglob("*.md"), key=lambda p: str(p.relative_to(SOURCE_DIR)))
    for index, path in enumerate(paths, start=1):
        markdown = path.read_text(encoding="utf-8")
        rel = path.relative_to(SOURCE_DIR)
        parent = str(rel.parent)
        section = SECTION_LABELS.get(parent, parent)
        title = normalize_title(path, markdown)
        docs.append(
            {
                "index": index,
                "source_path": rel.as_posix(),
                "path": path,
                "slug": f"doc-{index:03d}.html",
                "title": title,
                "section": section,
                "excerpt": excerpt(markdown),
                "minutes": reading_time(markdown),
                "markdown": markdown,
            }
        )
    return docs


def choose_illustration(doc: dict[str, object]) -> tuple[str, str]:
    haystack = f"{doc['title']} {doc['source_path']}"
    for keywords, filename, caption in ILLUSTRATION_RULES:
        if any(keyword in haystack for keyword in keywords):
            return filename, caption
    return "product-map.svg", "从场景、能力、流程和结果看懂 AI 产品全貌"


def group_docs(docs: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    groups: dict[str, list[dict[str, object]]] = {}
    for doc in docs:
        groups.setdefault(str(doc["section"]), []).append(doc)
    return groups


def nav_html(docs: list[dict[str, object]], current_slug: str | None, prefix: str) -> str:
    groups = group_docs(docs)
    parts: list[str] = []
    for section, items in groups.items():
        parts.append(f'<div class="nav-section"><div class="nav-section-title">{html.escape(section)}</div>')
        for doc in items:
            active = " active" if doc["slug"] == current_slug else ""
            href = f'{prefix}articles/{doc["slug"]}' if prefix == "" else f'{doc["slug"]}'
            if prefix == "../":
                href = doc["slug"]
            parts.append(
                f'<a class="nav-link{active}" href="{href}" data-title="{html.escape(str(doc["title"]).lower())}" '
                f'data-section="{html.escape(str(doc["section"]).lower())}">'
                f'<span>{html.escape(str(doc["title"]))}</span>'
                f'<small>{doc["minutes"]} min</small>'
                f"</a>"
            )
        parts.append("</div>")
    return "\n".join(parts)


def toc_html(headings: list[dict[str, str]]) -> str:
    if not headings:
        return '<p class="toc-empty">这篇文章很短，直接阅读即可。</p>'
    links = []
    for item in headings:
        level_class = "toc-h3" if item["level"] == "3" else "toc-h2"
        links.append(f'<a class="{level_class}" href="#{html.escape(item["id"])}">{html.escape(item["title"])}</a>')
    return "\n".join(links)


def article_template(doc: dict[str, object], docs: list[dict[str, object]], body: str, headings: list[dict[str, str]]) -> str:
    index = int(doc["index"])
    prev_doc = docs[index - 2] if index > 1 else None
    next_doc = docs[index] if index < len(docs) else None
    img, caption = choose_illustration(doc)
    prev_next = []
    if prev_doc:
        prev_next.append(f'<a class="pager-card" href="{prev_doc["slug"]}"><small>上一篇</small><strong>{html.escape(str(prev_doc["title"]))}</strong></a>')
    if next_doc:
        prev_next.append(f'<a class="pager-card next" href="{next_doc["slug"]}"><small>下一篇</small><strong>{html.escape(str(next_doc["title"]))}</strong></a>')
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(str(doc["title"]))} - AI Product Owner 成长知识库</title>
  <meta name="description" content="{html.escape(str(doc["excerpt"]))}">
  <link rel="stylesheet" href="../assets/css/style.css">
</head>
<body class="page-article">
  <div class="progress-bar" id="progressBar"></div>
  <header class="site-header">
    <a class="brand" href="../index.html">
      <span class="brand-mark">APO</span>
      <span>AI Product Owner 成长知识库</span>
    </a>
    <div class="header-actions">
      <button class="ghost-button" data-search-open>搜索</button>
      <button class="icon-button" data-nav-toggle aria-label="打开目录">目录</button>
    </div>
  </header>
  <div class="layout">
    <aside class="sidebar" id="sidebar">
      <div class="sidebar-head">
        <a href="../index.html">知识库首页</a>
        <button class="sidebar-close" data-nav-toggle>关闭</button>
      </div>
      <input class="nav-filter" type="search" placeholder="筛选文章..." data-nav-filter>
      <nav class="side-nav">
        {nav_html(docs, str(doc["slug"]), "../")}
      </nav>
    </aside>
    <main class="article-shell">
      <article class="article">
        <div class="article-kicker">{html.escape(str(doc["section"]))}</div>
        <h1>{html.escape(str(doc["title"]))}</h1>
        <p class="article-lead">{html.escape(str(doc["excerpt"]))}</p>
        <div class="article-meta">
          <span>{doc["minutes"]} 分钟阅读</span>
          <span>源文件：{html.escape(str(doc["source_path"]))}</span>
        </div>
        <figure class="article-visual">
          <img src="../assets/img/{img}" alt="{html.escape(caption)}">
          <figcaption>{html.escape(caption)}</figcaption>
        </figure>
        <div class="article-content">
          {body}
        </div>
        <section class="after-reading">
          <h2>读完可以带走什么</h2>
          <p>把这篇文章转成一个可交付物：一张判断表、一段 PRD 描述、一个评测样本集，或一次可复盘的业务实验。</p>
        </section>
        <nav class="pager">
          {"".join(prev_next)}
        </nav>
      </article>
      <aside class="toc">
        <div class="toc-card">
          <div class="toc-title">本文目录</div>
          {toc_html(headings)}
        </div>
      </aside>
    </main>
  </div>
  <div class="search-modal" data-search-modal aria-hidden="true">
    <div class="search-panel">
      <div class="search-head">
        <input type="search" placeholder="搜索 AI 场景、RAG、Agent、Eval..." data-search-input>
        <button data-search-close>关闭</button>
      </div>
      <div class="search-results" data-search-results></div>
    </div>
  </div>
  <script src="../assets/js/search-index.js"></script>
  <script src="../assets/js/main.js"></script>
</body>
</html>
"""


def index_template(docs: list[dict[str, object]]) -> str:
    groups = group_docs(docs)
    total_minutes = sum(int(doc["minutes"]) for doc in docs)
    cards = []
    for section, items in groups.items():
        first = items[0]
        cards.append(
            f"""<a class="module-card" href="articles/{first["slug"]}">
          <span>{len(items)} 篇</span>
          <h3>{html.escape(section)}</h3>
          <p>{html.escape(str(first["excerpt"]))}</p>
        </a>"""
        )
    recommended_titles = [
        "AI 产品经理全貌地图",
        "AI Product Owner 成长路线",
        "90 天 AI 产品经理学习路线",
        "从 0 到 1 落地 AI 产品",
        "AI 场景判断",
        "Prompt 与 Schema 产品契约",
        "RAG 进阶与产品验收",
        "Agent 产品结构与治理",
        "Skill 能力单元与暴露策略",
        "Gateway 路由与 Agent Loop",
    ]
    recommended = []
    for title in recommended_titles:
        match = next((doc for doc in docs if str(doc["title"]) == title), None)
        if match:
            recommended.append(
                f'<a href="articles/{match["slug"]}"><strong>{html.escape(title)}</strong><span>{html.escape(str(match["section"]))}</span></a>'
            )
    latest = "".join(
        f'<a class="compact-link" href="articles/{doc["slug"]}"><span>{html.escape(str(doc["title"]))}</span><small>{doc["minutes"]} min</small></a>'
        for doc in docs[:12]
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI Product Owner 成长知识库</title>
  <meta name="description" content="面向从交互设计师转型为 AI Product Owner 的公开学习知识库。">
  <link rel="stylesheet" href="assets/css/style.css">
</head>
<body class="page-home">
  <header class="site-header">
    <a class="brand" href="index.html">
      <span class="brand-mark">APO</span>
      <span>AI Product Owner 成长知识库</span>
    </a>
    <div class="header-actions">
      <button class="ghost-button" data-search-open>搜索</button>
      <a class="primary-button" href="articles/{docs[0]["slug"]}">开始阅读</a>
    </div>
  </header>
  <main>
    <section class="hero">
      <div class="hero-copy">
        <div class="eyebrow">公开发布版 · 静态 HTML</div>
        <h1>把 AI 能力放进真实业务流程，并对结果负责。</h1>
        <p>这不是一份术语清单，而是一套 AI Product Owner 的学习与实战系统：从场景判断、Prompt、RAG、Agent，到 Eval、治理、ROI 和作品集。</p>
        <div class="hero-actions">
          <a class="primary-button" href="articles/{docs[0]["slug"]}">进入知识库</a>
          <button class="ghost-button" data-search-open>搜索主题</button>
        </div>
      </div>
      <div class="hero-visual">
        <img src="assets/img/hero-lab.svg" alt="AI Product Owner 知识库结构图">
      </div>
    </section>
    <section class="stats-band">
      <div><strong>{len(docs)}</strong><span>篇文档</span></div>
      <div><strong>{len(groups)}</strong><span>个模块</span></div>
      <div><strong>{total_minutes}</strong><span>分钟系统阅读</span></div>
      <div><strong>100%</strong><span>本地静态资源</span></div>
    </section>
    <section class="section">
      <div class="section-head">
        <h2>学习模块</h2>
        <p>先看全貌，再进入核心知识、实战项目和工作模板。</p>
      </div>
      <div class="module-grid">
        {"".join(cards)}
      </div>
    </section>
    <section class="section split-section">
      <div>
        <div class="section-head">
          <h2>推荐阅读路径</h2>
          <p>适合第一次公开分享给别人时，引导对方顺着主线理解。</p>
        </div>
        <div class="reading-path">
          {"".join(recommended)}
        </div>
      </div>
      <aside class="home-panel">
        <h2>最近目录</h2>
        {latest}
      </aside>
    </section>
  </main>
  <div class="search-modal" data-search-modal aria-hidden="true">
    <div class="search-panel">
      <div class="search-head">
        <input type="search" placeholder="搜索 AI 场景、RAG、Agent、Eval..." data-search-input>
        <button data-search-close>关闭</button>
      </div>
      <div class="search-results" data-search-results></div>
    </div>
  </div>
  <script src="assets/js/search-index.js"></script>
  <script src="assets/js/main.js"></script>
</body>
</html>
"""


def write_css() -> None:
    (CSS_DIR / "style.css").write_text(
        r"""
:root {
  --bg: #f6f7fb;
  --paper: #ffffff;
  --paper-soft: #eef3f7;
  --ink: #17202a;
  --muted: #667085;
  --line: #d8dee8;
  --teal: #0f766e;
  --blue: #2563eb;
  --rose: #e11d48;
  --amber: #d97706;
  --shadow: 0 18px 50px rgba(22, 32, 42, 0.08);
}

* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
  line-height: 1.72;
  letter-spacing: 0;
}
a { color: inherit; text-decoration: none; }
img { max-width: 100%; display: block; }
button, input { font: inherit; }

.progress-bar {
  position: fixed;
  left: 0;
  top: 0;
  z-index: 80;
  height: 3px;
  width: 0%;
  background: linear-gradient(90deg, var(--teal), var(--blue), var(--amber));
}

.site-header {
  position: sticky;
  top: 0;
  z-index: 50;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 14px 24px;
  border-bottom: 1px solid rgba(216, 222, 232, 0.8);
  background: rgba(246, 247, 251, 0.92);
  backdrop-filter: blur(14px);
}
.brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-weight: 800;
  color: #182230;
}
.brand-mark {
  display: inline-grid;
  place-items: center;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  color: white;
  background: #17202a;
  font-size: 12px;
  letter-spacing: 0;
}
.header-actions { display: flex; align-items: center; gap: 10px; }
.primary-button,
.ghost-button,
.icon-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 40px;
  padding: 0 15px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--paper);
  color: var(--ink);
  cursor: pointer;
  white-space: nowrap;
}
.primary-button {
  border-color: #17202a;
  background: #17202a;
  color: white;
  font-weight: 700;
}
.ghost-button:hover,
.icon-button:hover,
.primary-button:hover { transform: translateY(-1px); }
.icon-button { display: none; }

.hero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(340px, 500px);
  gap: 48px;
  align-items: center;
  max-width: 1180px;
  margin: 0 auto;
  padding: 68px 24px 38px;
}
.eyebrow,
.article-kicker {
  display: inline-flex;
  margin-bottom: 14px;
  color: var(--teal);
  font-size: 13px;
  font-weight: 800;
}
.hero h1 {
  margin: 0;
  max-width: 820px;
  font-size: clamp(38px, 6vw, 76px);
  line-height: 1.05;
  letter-spacing: 0;
}
.hero p {
  max-width: 720px;
  margin: 22px 0 0;
  color: #475467;
  font-size: 19px;
}
.hero-actions { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 30px; }
.hero-visual {
  padding: 16px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--paper);
  box-shadow: var(--shadow);
}

.stats-band {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1px;
  max-width: 1180px;
  margin: 24px auto 0;
  padding: 0 24px;
}
.stats-band div {
  min-height: 108px;
  padding: 22px;
  border: 1px solid var(--line);
  background: var(--paper);
}
.stats-band strong { display: block; font-size: 34px; line-height: 1; }
.stats-band span { display: block; margin-top: 8px; color: var(--muted); }

.section {
  max-width: 1180px;
  margin: 0 auto;
  padding: 54px 24px 0;
}
.section-head { margin-bottom: 20px; }
.section-head h2,
.home-panel h2 {
  margin: 0;
  font-size: 28px;
  line-height: 1.2;
}
.section-head p { margin: 8px 0 0; color: var(--muted); }
.module-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}
.module-card,
.home-panel,
.reading-path a {
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--paper);
  box-shadow: 0 10px 28px rgba(22, 32, 42, 0.05);
}
.module-card {
  min-height: 178px;
  padding: 22px;
}
.module-card:hover,
.reading-path a:hover,
.compact-link:hover,
.nav-link:hover,
.pager-card:hover { border-color: #98a2b3; transform: translateY(-1px); }
.module-card span {
  color: var(--amber);
  font-size: 13px;
  font-weight: 800;
}
.module-card h3 { margin: 14px 0 8px; font-size: 21px; line-height: 1.3; }
.module-card p { margin: 0; color: var(--muted); font-size: 14px; }
.split-section {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 340px;
  gap: 20px;
  padding-bottom: 72px;
}
.reading-path { display: grid; gap: 10px; }
.reading-path a {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  padding: 15px 18px;
}
.reading-path span,
.compact-link small { color: var(--muted); font-size: 13px; }
.home-panel { padding: 20px; align-self: start; }
.compact-link {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 11px 0;
  border-bottom: 1px solid var(--line);
}
.compact-link:last-child { border-bottom: 0; }

.layout {
  display: grid;
  grid-template-columns: 300px minmax(0, 1fr);
  min-height: calc(100vh - 69px);
}
.sidebar {
  position: sticky;
  top: 69px;
  height: calc(100vh - 69px);
  overflow: auto;
  padding: 18px;
  border-right: 1px solid var(--line);
  background: #fbfcff;
}
.sidebar-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
  font-weight: 800;
}
.sidebar-close { display: none; }
.nav-filter {
  width: 100%;
  min-height: 40px;
  padding: 0 12px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--paper);
}
.nav-section { margin-top: 20px; }
.nav-section-title {
  margin-bottom: 8px;
  color: var(--muted);
  font-size: 12px;
  font-weight: 900;
}
.nav-link {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 10px;
  align-items: center;
  padding: 10px 11px;
  border: 1px solid transparent;
  border-radius: 8px;
  color: #344054;
  font-size: 14px;
}
.nav-link span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.nav-link small { color: var(--muted); font-size: 11px; }
.nav-link.active {
  border-color: rgba(15, 118, 110, 0.28);
  background: rgba(15, 118, 110, 0.08);
  color: #0f766e;
  font-weight: 800;
}

.article-shell {
  display: grid;
  grid-template-columns: minmax(0, 780px) 250px;
  gap: 34px;
  max-width: 1140px;
  width: 100%;
  margin: 0 auto;
  padding: 44px 28px 80px;
}
.article {
  min-width: 0;
  padding: 36px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--paper);
  box-shadow: var(--shadow);
}
.article h1 {
  margin: 0;
  font-size: clamp(32px, 5vw, 50px);
  line-height: 1.15;
  letter-spacing: 0;
}
.article-lead {
  margin: 18px 0 0;
  color: #475467;
  font-size: 18px;
}
.article-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 18px;
  color: var(--muted);
  font-size: 13px;
}
.article-meta span {
  padding: 5px 9px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--paper-soft);
}
.article-visual {
  margin: 28px 0 34px;
  padding: 14px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #f8fafc;
}
.article-visual figcaption {
  margin-top: 9px;
  color: var(--muted);
  font-size: 13px;
  text-align: center;
}
.article-content h1,
.article-content h2,
.article-content h3,
.article-content h4 {
  scroll-margin-top: 90px;
  line-height: 1.28;
  letter-spacing: 0;
}
.article-content h1 { margin: 38px 0 16px; font-size: 34px; }
.article-content h2 {
  margin: 42px 0 14px;
  padding-top: 20px;
  border-top: 1px solid var(--line);
  font-size: 28px;
}
.article-content h3 { margin: 28px 0 12px; font-size: 21px; }
.article-content p { margin: 14px 0; }
.article-content ul,
.article-content ol { padding-left: 1.25rem; margin: 14px 0; }
.article-content li { margin: 7px 0; }
.article-content strong { color: #101828; }
.article-content code {
  padding: 2px 5px;
  border-radius: 5px;
  background: #edf2f7;
  color: #9f1239;
  font-size: 0.9em;
}
pre {
  position: relative;
  overflow: auto;
  margin: 20px 0;
  padding: 18px;
  border-radius: 8px;
  background: #101828;
  color: #f8fafc;
}
pre code {
  padding: 0;
  background: transparent;
  color: inherit;
  font-size: 14px;
}
.copy-code {
  position: absolute;
  right: 10px;
  top: 10px;
  min-height: 30px;
  padding: 0 9px;
  border: 1px solid rgba(255,255,255,0.22);
  border-radius: 6px;
  background: rgba(255,255,255,0.08);
  color: white;
  cursor: pointer;
}
blockquote {
  margin: 22px 0;
  padding: 16px 18px;
  border-left: 4px solid var(--teal);
  background: rgba(15, 118, 110, 0.08);
  border-radius: 8px;
}
.table-wrap {
  overflow: auto;
  margin: 20px 0;
  border: 1px solid var(--line);
  border-radius: 8px;
}
table {
  width: 100%;
  border-collapse: collapse;
  min-width: 620px;
  background: white;
}
th, td {
  padding: 12px 14px;
  border-bottom: 1px solid var(--line);
  text-align: left;
  vertical-align: top;
}
th {
  background: #eef3f7;
  color: #344054;
  font-size: 13px;
}
tr:last-child td { border-bottom: 0; }

.after-reading {
  margin-top: 46px;
  padding: 22px;
  border: 1px solid rgba(37, 99, 235, 0.22);
  border-radius: 8px;
  background: rgba(37, 99, 235, 0.06);
}
.after-reading h2 { margin: 0 0 8px; font-size: 22px; }
.after-reading p { margin: 0; color: #475467; }
.pager {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-top: 24px;
}
.pager-card {
  min-height: 86px;
  padding: 14px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fbfcff;
}
.pager-card small { display: block; color: var(--muted); }
.pager-card strong { display: block; margin-top: 5px; line-height: 1.35; }
.pager-card.next { text-align: right; }

.toc {
  position: sticky;
  top: 94px;
  height: fit-content;
}
.toc-card {
  padding: 16px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: rgba(255,255,255,0.78);
}
.toc-title {
  margin-bottom: 10px;
  font-weight: 900;
}
.toc a {
  display: block;
  padding: 6px 0;
  color: var(--muted);
  font-size: 13px;
  line-height: 1.35;
}
.toc a:hover,
.toc a.active { color: var(--teal); font-weight: 800; }
.toc-h3 { padding-left: 12px !important; }
.toc-empty { color: var(--muted); font-size: 13px; }

.search-modal {
  position: fixed;
  inset: 0;
  z-index: 90;
  display: none;
  padding: 8vh 18px;
  background: rgba(16, 24, 40, 0.42);
}
.search-modal.open { display: block; }
.search-panel {
  max-width: 760px;
  margin: 0 auto;
  overflow: hidden;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--paper);
  box-shadow: var(--shadow);
}
.search-head {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 10px;
  padding: 14px;
  border-bottom: 1px solid var(--line);
}
.search-head input {
  min-height: 44px;
  padding: 0 12px;
  border: 1px solid var(--line);
  border-radius: 8px;
}
.search-head button {
  min-height: 44px;
  padding: 0 14px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #17202a;
  color: white;
  cursor: pointer;
}
.search-results { max-height: 62vh; overflow: auto; padding: 10px; }
.search-result {
  display: block;
  padding: 14px;
  border-radius: 8px;
}
.search-result:hover { background: #eef3f7; }
.search-result strong { display: block; }
.search-result span { color: var(--muted); font-size: 13px; }
.search-result p { margin: 6px 0 0; color: #475467; font-size: 14px; }

@media (max-width: 1120px) {
  .article-shell { grid-template-columns: minmax(0, 1fr); }
  .toc { display: none; }
}
@media (max-width: 900px) {
  .hero { grid-template-columns: 1fr; padding-top: 44px; }
  .stats-band { grid-template-columns: repeat(2, 1fr); }
  .module-grid { grid-template-columns: 1fr; }
  .split-section { grid-template-columns: 1fr; }
  .layout { grid-template-columns: 1fr; }
  .sidebar {
    position: fixed;
    inset: 0 auto 0 0;
    z-index: 70;
    width: min(86vw, 340px);
    height: 100vh;
    transform: translateX(-105%);
    transition: transform 0.2s ease;
    top: 0;
  }
  .sidebar.open { transform: translateX(0); }
  .sidebar-close { display: inline-flex; border: 0; background: transparent; color: var(--muted); }
  .icon-button { display: inline-flex; }
  .article-shell { padding: 22px 14px 60px; }
  .article { padding: 24px 18px; }
}
@media (max-width: 620px) {
  .site-header { padding: 12px 14px; }
  .brand span:last-child { display: none; }
  .hero h1 { font-size: 40px; }
  .hero p { font-size: 16px; }
  .stats-band { grid-template-columns: 1fr; }
  .pager { grid-template-columns: 1fr; }
  .pager-card.next { text-align: left; }
  .reading-path a { display: block; }
  .reading-path span { display: block; margin-top: 5px; }
}
""".strip()
        + "\n",
        encoding="utf-8",
    )


def write_js(docs: list[dict[str, object]]) -> None:
    search_index = [
        {
            "title": doc["title"],
            "section": doc["section"],
            "excerpt": doc["excerpt"],
            "url": ("articles/" + str(doc["slug"])),
            "articleUrl": str(doc["slug"]),
            "text": plain_text(str(doc["markdown"]))[:2400],
        }
        for doc in docs
    ]
    (JS_DIR / "search-index.js").write_text(
        "window.SEARCH_INDEX = " + json.dumps(search_index, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )
    (JS_DIR / "main.js").write_text(
        r"""
(function () {
  const modal = document.querySelector('[data-search-modal]');
  const searchInput = document.querySelector('[data-search-input]');
  const searchResults = document.querySelector('[data-search-results]');
  const isArticle = document.body.classList.contains('page-article');

  function resultUrl(item) {
    return isArticle ? item.articleUrl : item.url;
  }

  function renderResults(query) {
    if (!searchResults) return;
    const q = query.trim().toLowerCase();
    const data = window.SEARCH_INDEX || [];
    const results = q
      ? data.filter((item) => [item.title, item.section, item.excerpt, item.text].join(' ').toLowerCase().includes(q)).slice(0, 12)
      : data.slice(0, 8);
    searchResults.innerHTML = results.map((item) => `
      <a class="search-result" href="${resultUrl(item)}">
        <strong>${item.title}</strong>
        <span>${item.section}</span>
        <p>${item.excerpt}</p>
      </a>
    `).join('') || '<div class="search-result"><strong>没有找到结果</strong><p>换一个关键词试试，比如 RAG、Agent、Eval、治理。</p></div>';
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
    const value = max > 0 ? (window.scrollY / max) * 100 : 0;
    progress.style.width = `${Math.min(100, Math.max(0, value))}%`;
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
      document.querySelectorAll('.nav-link').forEach((link) => {
        const haystack = `${link.dataset.title || ''} ${link.dataset.section || ''}`;
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

  const tocLinks = Array.from(document.querySelectorAll('.toc a'));
  const headings = tocLinks.map((link) => document.querySelector(link.getAttribute('href'))).filter(Boolean);
  if ('IntersectionObserver' in window && headings.length) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          tocLinks.forEach((link) => link.classList.toggle('active', link.getAttribute('href') === `#${entry.target.id}`));
        }
      });
    }, { rootMargin: '-20% 0px -70% 0px', threshold: 0.01 });
    headings.forEach((heading) => observer.observe(heading));
  }
})();
""".strip()
        + "\n",
        encoding="utf-8",
    )


def svg_shell(title: str, subtitle: str, body: str, w: int = 960, h: int = 540) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{html.escape(title)}">
  <defs>
    <linearGradient id="panel" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0" stop-color="#ffffff"/>
      <stop offset="1" stop-color="#eef3f7"/>
    </linearGradient>
    <filter id="shadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="18" stdDeviation="18" flood-color="#17202a" flood-opacity="0.12"/>
    </filter>
  </defs>
  <rect width="{w}" height="{h}" fill="#f6f7fb"/>
  <rect x="34" y="34" width="{w-68}" height="{h-68}" rx="8" fill="url(#panel)" stroke="#d8dee8" filter="url(#shadow)"/>
  <text x="68" y="86" font-family="Arial, 'PingFang SC', sans-serif" font-size="28" font-weight="800" fill="#17202a">{html.escape(title)}</text>
  <text x="68" y="122" font-family="Arial, 'PingFang SC', sans-serif" font-size="16" fill="#667085">{html.escape(subtitle)}</text>
  {body}
</svg>
"""


def write_illustrations() -> None:
    illustrations = {
        "hero-lab.svg": svg_shell(
            "AI Product Owner Knowledge System",
            "Scenario · Harness · Eval · Governance · Outcome",
            """
  <g font-family="Arial, 'PingFang SC', sans-serif">
    <rect x="78" y="170" width="190" height="94" rx="8" fill="#0f766e" opacity="0.92"/>
    <text x="102" y="207" font-size="18" font-weight="800" fill="#fff">场景判断</text>
    <text x="102" y="235" font-size="13" fill="#d9f5f0">边界 · 价值 · 风险</text>
    <rect x="324" y="170" width="190" height="94" rx="8" fill="#2563eb" opacity="0.92"/>
    <text x="348" y="207" font-size="18" font-weight="800" fill="#fff">能力编排</text>
    <text x="348" y="235" font-size="13" fill="#dbeafe">Prompt · RAG · Agent</text>
    <rect x="570" y="170" width="190" height="94" rx="8" fill="#d97706" opacity="0.94"/>
    <text x="594" y="207" font-size="18" font-weight="800" fill="#fff">质量闭环</text>
    <text x="594" y="235" font-size="13" fill="#fff7ed">Eval · Trace · Review</text>
    <path d="M270 217 H318" stroke="#98a2b3" stroke-width="4"/>
    <path d="M516 217 H564" stroke="#98a2b3" stroke-width="4"/>
    <rect x="184" y="326" width="470" height="78" rx="8" fill="#17202a"/>
    <text x="224" y="358" font-size="18" font-weight="800" fill="#fff">AI Product Owner</text>
    <text x="224" y="386" font-size="14" fill="#cbd5e1">对业务结果、质量、安全和协作负责</text>
    <path d="M420 264 V318" stroke="#98a2b3" stroke-width="4"/>
  </g>
""",
        ),
        "product-map.svg": svg_shell(
            "AI 产品全貌",
            "从业务问题到可运行系统",
            """
  <g font-family="Arial, 'PingFang SC', sans-serif">
    <rect x="92" y="178" width="160" height="72" rx="8" fill="#e0f2fe" stroke="#2563eb"/>
    <text x="122" y="222" font-size="18" font-weight="800" fill="#17202a">业务场景</text>
    <rect x="312" y="178" width="160" height="72" rx="8" fill="#dcfce7" stroke="#0f766e"/>
    <text x="342" y="222" font-size="18" font-weight="800" fill="#17202a">AI 能力</text>
    <rect x="532" y="178" width="160" height="72" rx="8" fill="#fff7ed" stroke="#d97706"/>
    <text x="562" y="222" font-size="18" font-weight="800" fill="#17202a">产品流程</text>
    <rect x="312" y="322" width="160" height="72" rx="8" fill="#ffe4e6" stroke="#e11d48"/>
    <text x="342" y="366" font-size="18" font-weight="800" fill="#17202a">业务结果</text>
    <path d="M252 214 H312 M472 214 H532 M612 250 C612 330 472 358 472 358 M312 358 C220 350 172 292 172 250" fill="none" stroke="#98a2b3" stroke-width="4"/>
  </g>
""",
        ),
        "rag.svg": svg_shell(
            "RAG 可信链路",
            "召回、引用、拒答和验收共同决定质量下限",
            """
  <g font-family="Arial, 'PingFang SC', sans-serif">
    <rect x="84" y="182" width="150" height="78" rx="8" fill="#dbeafe" stroke="#2563eb"/>
    <text x="116" y="226" font-size="18" font-weight="800" fill="#17202a">用户问题</text>
    <rect x="302" y="150" width="170" height="70" rx="8" fill="#ecfeff" stroke="#0f766e"/>
    <text x="340" y="191" font-size="17" font-weight="800" fill="#17202a">检索召回</text>
    <rect x="302" y="252" width="170" height="70" rx="8" fill="#fff7ed" stroke="#d97706"/>
    <text x="340" y="293" font-size="17" font-weight="800" fill="#17202a">证据引用</text>
    <rect x="548" y="182" width="170" height="78" rx="8" fill="#dcfce7" stroke="#0f766e"/>
    <text x="588" y="226" font-size="18" font-weight="800" fill="#17202a">可信回答</text>
    <rect x="548" y="334" width="170" height="58" rx="8" fill="#ffe4e6" stroke="#e11d48"/>
    <text x="595" y="369" font-size="16" font-weight="800" fill="#17202a">拒答/澄清</text>
    <path d="M234 221 H302 M472 185 C515 185 515 221 548 221 M472 287 C520 287 520 241 548 241 M633 260 V334" fill="none" stroke="#98a2b3" stroke-width="4"/>
  </g>
""",
        ),
        "agent-system.svg": svg_shell(
            "Agent 受控系统",
            "模型负责推理，Harness 负责边界、工具和审计",
            """
  <g font-family="Arial, 'PingFang SC', sans-serif">
    <rect x="102" y="156" width="610" height="248" rx="8" fill="#f8fafc" stroke="#d8dee8"/>
    <rect x="132" y="200" width="140" height="70" rx="8" fill="#dbeafe" stroke="#2563eb"/>
    <text x="168" y="241" font-size="17" font-weight="800" fill="#17202a">模型</text>
    <rect x="330" y="200" width="140" height="70" rx="8" fill="#dcfce7" stroke="#0f766e"/>
    <text x="360" y="241" font-size="17" font-weight="800" fill="#17202a">Gateway</text>
    <rect x="528" y="200" width="140" height="70" rx="8" fill="#fff7ed" stroke="#d97706"/>
    <text x="568" y="241" font-size="17" font-weight="800" fill="#17202a">Tools</text>
    <rect x="232" y="318" width="336" height="54" rx="8" fill="#17202a"/>
    <text x="318" y="352" font-size="16" font-weight="800" fill="#fff">Trace · Policy · Human Review</text>
    <path d="M272 235 H330 M470 235 H528 M598 270 V318 M202 270 V318" fill="none" stroke="#98a2b3" stroke-width="4"/>
  </g>
""",
        ),
        "eval.svg": svg_shell(
            "Eval 质量系统",
            "样本集、评分维度、回归集和线上反馈组成闭环",
            """
  <g font-family="Arial, 'PingFang SC', sans-serif">
    <rect x="108" y="172" width="160" height="74" rx="8" fill="#eef2ff" stroke="#2563eb"/>
    <text x="146" y="216" font-size="18" font-weight="800" fill="#17202a">样本集</text>
    <rect x="326" y="172" width="160" height="74" rx="8" fill="#dcfce7" stroke="#0f766e"/>
    <text x="360" y="216" font-size="18" font-weight="800" fill="#17202a">评分器</text>
    <rect x="544" y="172" width="160" height="74" rx="8" fill="#fff7ed" stroke="#d97706"/>
    <text x="578" y="216" font-size="18" font-weight="800" fill="#17202a">质量门</text>
    <rect x="326" y="328" width="160" height="74" rx="8" fill="#ffe4e6" stroke="#e11d48"/>
    <text x="360" y="372" font-size="18" font-weight="800" fill="#17202a">回归集</text>
    <path d="M268 209 H326 M486 209 H544 M624 246 C610 318 486 365 486 365 M326 365 C224 350 188 280 188 246" fill="none" stroke="#98a2b3" stroke-width="4"/>
  </g>
""",
        ),
        "governance.svg": svg_shell(
            "治理与信任",
            "权限、红线、审计和人工确认让 AI 可控上线",
            """
  <g font-family="Arial, 'PingFang SC', sans-serif">
    <path d="M402 150 L606 226 V306 C606 374 512 414 402 430 C292 414 198 374 198 306 V226 Z" fill="#ecfeff" stroke="#0f766e" stroke-width="3"/>
    <text x="340" y="255" font-size="22" font-weight="800" fill="#17202a">可信边界</text>
    <text x="310" y="294" font-size="15" fill="#475467">Permission · Audit · Review</text>
    <rect x="106" y="190" width="128" height="56" rx="8" fill="#dbeafe" stroke="#2563eb"/>
    <text x="142" y="225" font-size="15" font-weight="800" fill="#17202a">权限</text>
    <rect x="570" y="190" width="128" height="56" rx="8" fill="#fff7ed" stroke="#d97706"/>
    <text x="606" y="225" font-size="15" font-weight="800" fill="#17202a">红线</text>
    <rect x="106" y="340" width="128" height="56" rx="8" fill="#ffe4e6" stroke="#e11d48"/>
    <text x="142" y="375" font-size="15" font-weight="800" fill="#17202a">审计</text>
    <rect x="570" y="340" width="128" height="56" rx="8" fill="#dcfce7" stroke="#0f766e"/>
    <text x="596" y="375" font-size="15" font-weight="800" fill="#17202a">人工确认</text>
  </g>
""",
        ),
        "roadmap.svg": svg_shell(
            "成长路线",
            "从会解释，到能交付，再到能制定标准",
            """
  <g font-family="Arial, 'PingFang SC', sans-serif">
    <path d="M118 378 C220 286 294 328 388 246 S580 178 700 134" fill="none" stroke="#17202a" stroke-width="6"/>
    <rect x="92" y="342" width="150" height="68" rx="8" fill="#dbeafe" stroke="#2563eb"/>
    <text x="126" y="382" font-size="16" font-weight="800" fill="#17202a">Feature PM</text>
    <rect x="300" y="250" width="170" height="68" rx="8" fill="#dcfce7" stroke="#0f766e"/>
    <text x="330" y="290" font-size="16" font-weight="800" fill="#17202a">Workflow PM</text>
    <rect x="514" y="164" width="170" height="68" rx="8" fill="#fff7ed" stroke="#d97706"/>
    <text x="548" y="204" font-size="16" font-weight="800" fill="#17202a">AI Owner</text>
    <rect x="578" y="324" width="150" height="58" rx="8" fill="#ffe4e6" stroke="#e11d48"/>
    <text x="610" y="359" font-size="15" font-weight="800" fill="#17202a">作品集</text>
  </g>
""",
        ),
        "prompt-schema.svg": svg_shell(
            "Prompt + Schema",
            "把不稳定的自然语言输出变成产品可消费的结构",
            """
  <g font-family="Arial, 'PingFang SC', sans-serif">
    <rect x="90" y="176" width="250" height="184" rx="8" fill="#f8fafc" stroke="#d8dee8"/>
    <text x="120" y="222" font-size="20" font-weight="800" fill="#17202a">Prompt</text>
    <text x="120" y="258" font-size="14" fill="#667085">角色 · 任务 · 规则 · 示例</text>
    <rect x="466" y="176" width="250" height="184" rx="8" fill="#17202a"/>
    <text x="496" y="222" font-size="20" font-weight="800" fill="#fff">Schema</text>
    <text x="496" y="258" font-size="14" fill="#cbd5e1">{ field, type, constraint }</text>
    <path d="M340 268 H466" stroke="#98a2b3" stroke-width="5"/>
    <path d="M444 248 L466 268 L444 288" fill="none" stroke="#98a2b3" stroke-width="5"/>
  </g>
""",
        ),
        "metrics.svg": svg_shell(
            "业务指标闭环",
            "成本、延迟、采纳率和 ROI 一起决定产品是否值得上线",
            """
  <g font-family="Arial, 'PingFang SC', sans-serif">
    <rect x="112" y="334" width="90" height="70" rx="8" fill="#dbeafe" stroke="#2563eb"/>
    <rect x="254" y="286" width="90" height="118" rx="8" fill="#dcfce7" stroke="#0f766e"/>
    <rect x="396" y="226" width="90" height="178" rx="8" fill="#fff7ed" stroke="#d97706"/>
    <rect x="538" y="172" width="90" height="232" rx="8" fill="#ffe4e6" stroke="#e11d48"/>
    <text x="118" y="430" font-size="14" fill="#475467">成本</text>
    <text x="260" y="430" font-size="14" fill="#475467">延迟</text>
    <text x="392" y="430" font-size="14" fill="#475467">采纳率</text>
    <text x="548" y="430" font-size="14" fill="#475467">ROI</text>
    <path d="M110 404 H680" stroke="#98a2b3" stroke-width="3"/>
  </g>
""",
        ),
        "research-assistant.svg": svg_shell(
            "AI 用户研究洞察助手",
            "从访谈材料到洞察卡片、机会点和 PRD 初稿",
            """
  <g font-family="Arial, 'PingFang SC', sans-serif">
    <rect x="94" y="178" width="150" height="88" rx="8" fill="#dbeafe" stroke="#2563eb"/>
    <text x="126" y="228" font-size="17" font-weight="800" fill="#17202a">访谈材料</text>
    <rect x="306" y="178" width="150" height="88" rx="8" fill="#dcfce7" stroke="#0f766e"/>
    <text x="338" y="228" font-size="17" font-weight="800" fill="#17202a">洞察卡片</text>
    <rect x="518" y="178" width="150" height="88" rx="8" fill="#fff7ed" stroke="#d97706"/>
    <text x="552" y="228" font-size="17" font-weight="800" fill="#17202a">机会点</text>
    <rect x="306" y="330" width="150" height="74" rx="8" fill="#17202a"/>
    <text x="350" y="374" font-size="17" font-weight="800" fill="#fff">PRD</text>
    <path d="M244 222 H306 M456 222 H518 M593 266 C572 342 456 367 456 367" fill="none" stroke="#98a2b3" stroke-width="4"/>
  </g>
""",
        ),
        "template-kit.svg": svg_shell(
            "工作模板包",
            "把 PRD、评测、风险、Roadmap 和复盘统一成可复用资产",
            """
  <g font-family="Arial, 'PingFang SC', sans-serif">
    <rect x="130" y="156" width="146" height="190" rx="8" fill="#dbeafe" stroke="#2563eb"/>
    <rect x="318" y="184" width="146" height="190" rx="8" fill="#dcfce7" stroke="#0f766e"/>
    <rect x="506" y="132" width="146" height="190" rx="8" fill="#fff7ed" stroke="#d97706"/>
    <text x="166" y="238" font-size="18" font-weight="800" fill="#17202a">PRD</text>
    <text x="356" y="266" font-size="18" font-weight="800" fill="#17202a">Eval</text>
    <text x="538" y="214" font-size="18" font-weight="800" fill="#17202a">Risk</text>
    <rect x="184" y="394" width="410" height="42" rx="8" fill="#17202a"/>
    <text x="300" y="421" font-size="15" font-weight="800" fill="#fff">Reusable Product Operating System</text>
  </g>
""",
        ),
    }
    for filename, content in illustrations.items():
        (IMG_DIR / filename).write_text(content, encoding="utf-8")


def write_readme() -> None:
    (OUT_DIR / "README_发布说明.md").write_text(
        """# AI 产品经理学习知识库 HTML 发布版

打开 `index.html` 即可浏览，不需要后端服务，也不依赖外网资源。

## 文件结构

- `index.html`：知识库首页
- `articles/`：每篇 Markdown 转换后的文章页
- `assets/css/style.css`：站点样式
- `assets/js/`：搜索、目录、阅读进度和代码复制
- `assets/img/`：本地插图资源
- `build_site.py`：重新生成站点的脚本

## 重新生成

如果你继续修改 `AI产品经理学习知识库/` 里的 Markdown，可以在当前文件夹运行：

```bash
python3 build_site.py
```

脚本会重新读取源 Markdown，并覆盖生成 HTML、CSS、JS 和本地插图。
""",
        encoding="utf-8",
    )


def build() -> None:
    ensure_dirs()
    docs = collect_docs()
    for doc in docs:
        body, headings = render_markdown(str(doc["markdown"]))
        (ARTICLES_DIR / str(doc["slug"])).write_text(article_template(doc, docs, body, headings), encoding="utf-8")
    (OUT_DIR / "index.html").write_text(index_template(docs), encoding="utf-8")
    write_css()
    write_js(docs)
    write_illustrations()
    write_readme()
    summary = {
        "generated_at": date.today().isoformat(),
        "source": str(SOURCE_DIR),
        "documents": len(docs),
        "articles_dir": str(ARTICLES_DIR),
    }
    (OUT_DIR / "build-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Generated {len(docs)} documents into {OUT_DIR}")


if __name__ == "__main__":
    build()
