#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""agent-lessons 安装器核心 —— **跨 agent / 幂等 / 可逆 / 可运维**。

## 设计要点（每条都对应一条本文档自身主张的机制）

1. **单一事实源 + 派生，禁止手抄**（= 机制一）
   注入块**不是**写死在这个文件里的常量，而是从 `guidelines/*.md` **运行时派生**的。
   ⇒ 改一条准则 ⇒ 所有已安装的 agent 下次同步时自动跟着变。

2. **默认只读（dry-run）**，写要显式 `--apply`
   它要改的是**别人的 agent 配置文件**（可能含用户自己的内容）。
   ⇒ 先看要写什么，再决定写不写。

3. **带标记的块 + 绝不覆盖用户内容**（= 可逆）
   写入形如：
       <!-- agent-lessons:BEGIN v1 -->  ...  <!-- agent-lessons:END -->
   `--uninstall` 只删这两行之间的内容，**其余一字不动**。

4. **幂等**：重复安装不会产生第二份块；旧版块会被**原地替换**。

5. **可运维**：`status`（装了什么/什么版本/内容是否漂移）、`sync`（重新派生并更新）、
   `uninstall`、`selfcheck`（安装器自己的自检）。

## 用法
    python core.py status                 # 看当前装了哪些、是否与 guidelines 一致
    python core.py install --agent claude # 默认 dry-run，打印将要写入的内容
    python core.py install --agent claude --apply
    python core.py install --agent generic --target /path/to/project --apply
    python core.py sync    --apply        # guidelines 改了之后，把已装的块更新一遍
    python core.py uninstall --agent claude --apply
    python core.py selfcheck
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import os
import platform
import re
import shutil
import sys
from pathlib import Path

VERSION = "1.0.0"
# ⚠ 2026-09-20 修：原为 `\s*$`。在 `re.M` 下 `\s` **会吃掉行尾换行** ⇒ 匹配区间越过 `\n`
#   ⇒ 替换后**少一个换行** ⇒ 第二次安装仍判「有变化」⇒ **不幂等**（每次 sync 都重写文件）。
#   `selfcheck` 没抓到这个（它当时没有幂等用例）—— 已补。
#   ⇒ 改用 `[ \t]*$`：只吃行内空白，不吃换行。
BEGIN_RE = re.compile(r"^[ \t]*<!--\s*agent-lessons:BEGIN[^>]*-->[ \t]*$", re.M)
END_RE = re.compile(r"^[ \t]*<!--\s*agent-lessons:END\s*-->[ \t]*$", re.M)
BEGIN = f"<!-- agent-lessons:BEGIN v{VERSION} -->"
END = "<!-- agent-lessons:END -->"

# ── agent teams 策略：**三值，安装时由用户定** ─────────────────────────────
# ⚠ 2026-09-21 加。要求：**一开始就决定**「默认打开 / 每次询问 / 永不打开」，
#   而不是让 agent 每次自己猜 —— 「猜」正是本仓库记的那些事故的温床。
# ⚠ 为什么让 **BEGIN 标记行**携带它，而不是另建一个配置文件：
#   ① `nl=1` 已经用同一手法把状态写在标记行上了（见 `apply_block` 的注释），有先例；
#   ② 另建文件 = 多一个要 gitignore、要迁移、要向用户解释的东西
#      —— 本项目对「基建过剩」有实伤记录，能不加就不加；
#   ③ `BEGIN_RE` 本来就是 `[^>]*`，多一个属性不影响解析。
# ⚠ 而 `BEGIN` 常量**保持原样、不参数化** —— selfcheck 的喂靶直接引用它（`f"头\n{BEGIN}\nX\n"`），
#   改它会连带改坏测试。**这是「改之前先 grep 三种位置」的实例。**
TEAMS_POLICIES = ("always", "ask", "never")
TEAMS_DEFAULT = "ask"


def begin_line(teams: str = TEAMS_DEFAULT) -> str:
    return f"<!-- agent-lessons:BEGIN v{VERSION} teams={teams} -->"


def teams_of(text: str) -> str:
    """从**已存在的** BEGIN 行读回策略；读不到或非法 ⇒ 取默认。

    ⚠ 为什么不报错：用户的块可能是更早版本装的（那时没有 teams 属性）。
       **升级路径必须无损** —— 读到就沿用，读不到就取默认，绝不让升级失败。
    """
    m = re.search(r"agent-lessons:BEGIN[^>]*?\bteams=(\w+)", text)
    return m.group(1) if m and m.group(1) in TEAMS_POLICIES else TEAMS_DEFAULT


def teams_line(teams: str, lang: str = "zh") -> str:
    if lang == "en":
        body = {"always": "spawn subagents/teammates freely when it helps",
                "ask": "**ask the user first** before spawning subagents/teammates",
                "never": "do not spawn subagents/teammates"}[teams]
        return (f"- **[teams] agent teams: {teams}** -- {body}. "
                f"(Change with `--teams=...`.)")
    body = {"always": "需要并行时**直接开**分身/队员",
            "ask": "需要并行时**先问用户**再开分身/队员",
            "never": "**不开**分身/队员，全部自己做"}[teams]
    return f"- **[teams] agent teams：{teams}** —— {body}。（改：`--teams=...` 重装）"


# ⚠ 2026-09-20 修（真机自测发现）：默认 Windows 控制台是 GBK，而本文件原先在输出里用了
#   emoji 勾叉（U+2705 / U+274C）⇒ `UnicodeEncodeError: 'gbk' codec can't encode ...`
#   ⇒ **安装器在绝大多数 Windows 用户那里直接崩**（本项目记忆里早有 "stdout GBK" 这一条）。
#   修法两件一起：
#     (a) 这里把 stdout/stderr 强制 UTF-8 且 `errors="replace"`（绝不因编码崩）；
#     (b) **面向用户的输出改用 ASCII 标记** `[OK]` / `[!!]` —— 即使 reconfigure 失败也不会崩。
#   ⚠ 注：改这段时我用了全局字符串替换，**把注释里的原文也一起换了**，导致注释一度在说反话
#     （"用了 [OK] 会崩"）。凡批量替换，**必须回头读一遍被改到的注释**。
for _s in ("stdout", "stderr"):
    try:
        getattr(sys, _s).reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
GUIDELINES = ROOT / "guidelines"
DOCS = ROOT / "docs"


def doc_parity_problems(docs: Path) -> list[str]:
    """中/英文档的**结构对偶**检查：`XX.md` 与 `XX.en.md` 的 `##`/`###` 数必须相等。

    ⚠ 为什么要有它：`AGENTS.md` 里只写了「改文档要和它的对偶语言版本一起改」——
      **那是一句话，不是机制。** 2026-09-20 我给 `03` 加了一节 `###`，
      英文版是**靠我当场记得**才同步的。下次换个 agent、或者我自己隔一天，
      就会静默漂移：中文有 8 节、英文有 7 节，**而没有任何东西会发现**。

    ⇒ 判据取「**类别**」不取「字面」：比的是标题的层级与数量，
      不是措辞 —— 两种语言的措辞本来就该不同。
    """
    if not docs.is_dir():
        return [f"docs 目录不存在：{docs}"]

    def shape(p: Path) -> tuple[int, int, int]:
        t = p.read_text(encoding="utf-8")
        # ⚠ 第三项（分隔线）是**补的**，因为第一版只数 ##/### 时**漏掉了真事**：
        #   我在中文版里留了**连续两条 `---`**，英文版只有一条 ——
        #   中英不对称，而守卫报"一致"。**判据的宽度决定了它能看见什么。**
        #   判据取 `^---$`（行首行尾），不会误伤表格分隔行 `|---|---|`。
        return (len(re.findall(r"^## ", t, re.M)),
                len(re.findall(r"^### ", t, re.M)),
                len(re.findall(r"^---\s*$", t, re.M)))

    out: list[str] = []
    for f in sorted(docs.glob("*.md")):
        if f.name.endswith(".en.md"):
            continue
        en = docs / (f.name[:-3] + ".en.md")
        if not en.exists():
            out.append(f"{f.name}：缺英文对偶（{en.name}）")
            continue
        a, b = shape(f), shape(en)
        if a != b:
            out.append(f"{f.name} vs {en.name}：结构不一致 "
                       f"（zh ##/###/---={a[0]}/{a[1]}/{a[2]}，"
                       f"en={b[0]}/{b[1]}/{b[2]}）")
    # ⚠ 反向也查：孤立的 `.en.md`（有英文没中文）同样是漂移，且更容易漏。
    #   ⚠ 2026-09-20 实测踩坑：`.en.md` 是 **6** 个字符，我第一版写 `[:-7]`（多砍一个）
    #     ⇒ 真目录 3 个**完全正常**的文件被判成"缺中文对偶"。
    #     **假阳性守卫比没有守卫更坏**：它会让人去创建本不该存在的文件。
    #     抓到它的不是 review，是同一段里那句 `喂靶：对偶齐全 ⇒ 不报`。
    for f in sorted(docs.glob("*.en.md")):
        zh = docs / (f.name[:-6] + ".md")
        if not zh.exists():
            out.append(f"{f.name}：缺中文对偶（{zh.name}）")
    return out


# ────────────────────────────────────────────────────────────── 派生注入块
def guidelines_dir(lang: str = "zh") -> Path:
    """语言的准则目录。英文在 `guidelines/en/` 下，文件名与中文版**同名**。

    ⚠ 2026-09-20 修（**由翻译队员发现，不是我自己发现的**）：
      本函数原先**不存在** —— `load_guidelines()` 直接 `GLOB("*.md")`（**非递归**）。
      ⇒ 把英文准则放进 `guidelines/en/` 之后，**它们对安装器完全不可见**：
          磁盘上 24 个文件 · `load_guidelines()` 只回 12 · 英文被读到 **0**
      ⇒ 而 `selfcheck` **仍然是绿的**（它查的是那 12 个中文文件）。
      **⇒ 这正是准则 09/10 落在"验证方式"本身：一个"通过"，证明的是别的文件。**
      ⇒ 凡"新增一个目录"的改动，先问：**谁会读到它？**（读者是不是非递归的？）
    """
    return GUIDELINES / "en" if lang == "en" else GUIDELINES


def load_guidelines(lang: str = "zh") -> list[tuple[str, str, str]]:
    """从 `guidelines[/en]/*.md` 派生 [(编号, 标题, 判据行)]。

    文件约定：首行 `# <标题>`；正文里**第一条以「判据：」开头的行**就是它的判据。
    **没有判据的文件会被 `selfcheck` 报出来** —— 一条没有可执行判据的"准则"是废话。
    ⚠ `判据：` 是**机器接口**，两种语言都不译（译了会让所有条目变成"缺判据行"）。
    """
    out: list[tuple[str, str, str]] = []
    gdir = guidelines_dir(lang)
    if not gdir.is_dir():
        return out
    for f in sorted(gdir.glob("*.md")):
        text = f.read_text(encoding="utf-8")
        title = ""
        for ln in text.splitlines():
            if ln.startswith("# "):
                title = ln[2:].strip()
                break
        # ⚠ 2026-09-20 修（**吃自己的狗粮时发现的**）：原实现只取**第一条**以「判据：」开头的行
        #   ⇒ **多行判据会被静默截断**，而截断后的块**看起来是完整的** —— 正是本仓库准则 06/07
        #   反复讲的「静默丢弃 + 自信总数」。
        #   实例：准则 11 的判据写成两行，装出来的块只有前半句「…（对外发布 / 写生产数据 /
        #   改权限与配置），」—— 一句没有谓语的句子。
        #   ⇒ 现在**续行一并收**：判据行之后，直到空行 / 标题 / 列表项 / 表格行为止。
        crit_lines: list[str] = []
        for ln in text.splitlines():
            s = ln.strip().lstrip("-* ").strip()
            if not crit_lines and s.startswith("判据："):
                crit_lines.append(s[len("判据："):].strip())
                continue
            if crit_lines:
                if (not s) or s[0] in "#|>" or s.startswith(("- ", "* ")):
                    break
                crit_lines.append(s)
        crit = " ".join(crit_lines).strip()
        stem = f.stem
        num = stem.split("-", 1)[0] if "-" in stem else stem
        out.append((num, title or stem, crit))
    return out


def render_block(lang: str = "zh", teams: str = TEAMS_DEFAULT) -> str:
    """渲染注入块。**必须由 `load_guidelines(lang)` 派生，不得写死。**"""
    if teams not in TEAMS_POLICIES:
        teams = TEAMS_DEFAULT
    items = load_guidelines(lang)
    if lang == "en":
        head = [
            begin_line(teams),
            f"# Engineering guidelines (agent-lessons v{VERSION})",
            "",
            "Derived from `guidelines/*.md`. Do not edit by hand — run `install/core.py sync`.",
            "",
        ]
    else:
        head = [
            begin_line(teams),
            f"# 工程准则（agent-lessons v{VERSION}）",
            "",
            "以下由 `guidelines/*.md` **派生**（请勿手改本块；改准则后跑 `install/core.py sync`）。",
            "",
        ]
    body = []
    for num, title, crit in items:
        body.append(f"- **[{num}] {title}**")
        if crit:
            # ⚠ `判据：` **两种语言都不译** —— 它是机器接口（load_guidelines 靠它抽取）。
            body.append(f"  - 判据：{crit}")
        else:
            body.append("  - ⚠ （该准则缺少「判据：」行 —— 不可执行）"
                        if lang != "en" else
                        "  - [!!] This guideline has no `判据：` line -- not actionable")
    # ⚠ 2026-09-20 修：tail 原为**硬编码中文**，两种语言共用 ⇒ 英文块末尾会突然出现一句中文。
    #   （自测发现：英文块里 13 处中文, 除 `判据：` 外还有这一句。）
    tail = ["", teams_line(teams, lang), "",
            ("See `docs/` for the full write-up." if lang == "en"
             else "完整说明见仓库 `docs/`。"), END]
    return "\n".join(head + body + tail) + "\n"


# ────────────────────────────────────────────────────────────── 目标解析
def resolve_target(agent: str, target: str | None) -> Path | None:
    """返回要写入的文件路径。`generic` 需要一个显式目录。"""
    home = Path.home()
    if agent == "claude":
        return Path(os.environ.get("CLAUDE_CONFIG_DIR", home / ".claude")) / "CLAUDE.md"
    if agent == "codex":
        return Path(os.environ.get("CODEX_HOME", home / ".codex")) / "AGENTS.md"
    if agent == "cursor":
        return (Path(target) if target else Path.cwd()) / "AGENTS.md"
    if agent == "generic":
        return (Path(target) if target else Path.cwd()) / "AGENTS.md"
    return None


def supported_agents() -> list[str]:
    return ["claude", "codex", "cursor", "generic"]


# ────────────────────────────────────────────────────────────── L2：git 提交钩子
HOOK_SRC_REL = "hooks/pre-commit"
HOOK_MARK = "agent-lessons pre-commit hook"   # 归属标记：只删/改「带这个标记的」文件


def _git_dir(target: Path) -> Path | None:
    """向上找 `.git`（兼容 `.git` 是文件的情况：worktree / submodule）。"""
    cur = target.resolve()
    for d in [cur, *cur.parents]:
        g = d / ".git"
        if g.is_dir():
            return g
        if g.is_file():                       # worktree: `gitdir: <path>`
            try:
                line = g.read_text(encoding="utf-8", errors="replace").strip()
                if line.startswith("gitdir:"):
                    p = Path(line.split(":", 1)[1].strip())
                    return p if p.is_absolute() else (d / p).resolve()
            except Exception:
                return None
    return None


def git_hook_install(target: Path, apply: bool) -> int:
    gd = _git_dir(target)
    if gd is None:
        print(f"  [--] git 钩子 (L2)：{target} 不是 git 仓库 ⇒ **这一层装不上**（如实报告，不假装成功）")
        return 0
    dst = gd / "hooks" / "pre-commit"
    src = ROOT / HOOK_SRC_REL
    if not src.exists():
        print(f"  [!!] 找不到 {src} ⇒ 跳过")
        return 1
    ours = dst.exists() and HOOK_MARK in dst.read_text(encoding="utf-8", errors="replace")
    if dst.exists() and not ours:
        # ⚠ **绝不覆盖别人的钩子** —— 那可能是有人的自定义逻辑，覆盖掉是静默破坏。
        #   本工具替用户做的决定到此为止：报出来，让人自己合并。
        print(f"  [!!] git 钩子 (L2)：{dst} 已存在且**不是本工具装的** ⇒ **拒绝覆盖**")
        print("       请自行合并，或先移走它。（本工具不替你做这个决定）")
        return 1
    verb = "更新" if ours else "安装"
    print(f"  [{'OK' if apply else '--'}] git 钩子 (L2)：将{verb} {dst}")
    if not apply:
        return 0
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    try:
        os.chmod(dst, 0o755)
    except Exception:
        print("       ⚠ 无法设置可执行位（Windows 上通常无妨；若 git 不执行它，见 README）")
    print(f"  [OK] git 钩子已{verb}")
    return 0


def git_hook_uninstall(target: Path, apply: bool) -> int:
    gd = _git_dir(target)
    if gd is None:
        return 0
    dst = gd / "hooks" / "pre-commit"
    if not dst.exists():
        return 0
    if HOOK_MARK not in dst.read_text(encoding="utf-8", errors="replace"):
        print(f"  [--] git 钩子 (L2)：{dst} 不是本工具装的 ⇒ 不动它")
        return 0
    print(f"  [{'OK' if apply else '--'}] git 钩子 (L2)：将删除 {dst}")
    if apply:
        dst.unlink()
        print("  [OK] git 钩子已删除")
    return 0


# ────────────────────────────────────────────────────────────── 块操作（纯函数，可测）
def find_block(text: str) -> tuple[int, int] | None:
    """返回 (start, end) 字符区间；没有块 ⇒ None。多处 ⇒ 抛错（防止我们写坏过文件）。"""
    starts = [m.start() for m in BEGIN_RE.finditer(text)]
    ends = [m.end() for m in END_RE.finditer(text)]
    if len(starts) != len(ends):
        raise ValueError(f"标记不成对：BEGIN×{len(starts)} / END×{len(ends)} —— 拒绝改动，请人工检查")
    if not starts:
        return None
    if len(starts) > 1:
        raise ValueError(f"发现 {len(starts)} 个块 —— 拒绝改动（本工具只应有一个块）")
    if ends[0] < starts[0]:
        raise ValueError("END 出现在 BEGIN 之前 —— 拒绝改动")
    return starts[0], ends[0]


NL_TAG = "nl=1"


def apply_block(text: str, block: str) -> str:
    """插入或**原地替换**块。**不修改用户文件里已有的任何字符。**

    ⚠ 精确可逆的难点（2026-09-20 自测发现）：当用户文件**不以换行结尾**时，
    为了让块从新的一行开始，必须补一个换行；而这个补的换行与"用户自己的换行"
    **在块前看起来完全一样** ⇒ 卸载时无法靠局部判断区分。
    **⇒ 让标记自己携带这个信息**：补过就把 `nl=1` 写进 BEGIN 行，
    `remove_block` 读它、把那个换行一并删掉 ⇒ **装卸互为精确逆运算**。
    """
    span = find_block(text)
    if span is None:
        added = bool(text) and not text.endswith("\n")
        blk = block
        if added:
            # 把 nl=1 塞进 BEGIN 行（在 ` -->` 之前）
            blk = re.sub(r"(<!--\s*agent-lessons:BEGIN[^>]*?)(\s*-->)",
                         r"\1 " + NL_TAG + r"\2", block, count=1)
        return text + ("\n" if added else "") + ("\n" if text else "") + blk
    # ⚠ 替换分支**必须保住已有的 nl=1 标记** —— 否则第二次安装会把标记丢掉：
    #   标记没了 ⇒ 幂等失败（文本变了），且卸载时无法知道该不该删那个换行。
    #   （自测发现：这一版之前的替换分支正是这样把标记弄丢的。）
    keep_nl = NL_TAG in text[span[0]: span[0] + 200]
    blk = block
    if keep_nl and NL_TAG not in blk:
        blk = re.sub(r"(<!--\s*agent-lessons:BEGIN[^>]*?)(\s*-->)",
                     r"\1 " + NL_TAG + r"\2", block, count=1)
    return text[: span[0]] + blk.rstrip("\n") + text[span[1]:]


def remove_block(text: str) -> str:
    """只删块本身，**外加安装时插入的那一个分隔空行**（若它确实在）—— 其余一字不动。

    ⚠ 2026-09-20 修：原实现尾部有 `re.sub(r"\\n{3,}", "\\n\\n", out)` ——
      **它会动用户自己的空行**（用户原有 3 个空行会被压成 2 个）。
      「卸载后用户内容一字不动」是本工具的承诺 ⇒ 改成**只精确删掉自己加的那一个 `\\n`**。
    """
    span = find_block(text)
    if span is None:
        return text
    start, end = span
    # 块自己的两个换行（分隔空行 + 结尾换行）可以删；用户内容里的换行不动。
    if start >= 2 and text[start - 1] == "\n" and text[start - 2] == "\n":
        start -= 1
    if text[end:end + 1] == "\n":
        end += 1
    out = text[:start] + text[end:]
    # 安装时若给用户原文补过换行（标记里写着 nl=1）⇒ 这里把它删掉 ⇒ 精确还原
    if NL_TAG in text[span[0]: span[0] + 200] and out.endswith("\n") and not out.endswith("\n\n"):
        out = out[:-1]
    return out


# ────────────────────────────────────────────────────────────── 命令
def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""


def _diff(old: str, new: str, name: str) -> str:
    d = list(difflib.unified_diff(old.splitlines(True), new.splitlines(True),
                                 fromfile=f"a/{name}", tofile=f"b/{name}"))
    return "".join(d) if d else "(无变化)"


def _write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, p)


def cmd_install(a) -> int:
    tgt = resolve_target(a.agent, a.target)
    if tgt is None:
        print(f"未知 agent：{a.agent}（支持：{', '.join(supported_agents())}）")
        return 2
    # ⚠ 顺序要紧：**必须先读旧文件**，才能沿用里面已有的 teams 策略。
    #   否则「重装但不带 --teams」会把用户上次的选择悄悄重置成默认 ——
    #   那是「升级路径有损」，与 `teams_of` 的注释是同一条判据。
    old = _read(tgt)
    _teams = getattr(a, "teams", None) or teams_of(old)
    block = render_block(a.lang, _teams)
    try:
        new = apply_block(old, block)
    except ValueError as e:
        print(f"[!!] {tgt}\n   {e}")
        return 2
    changed = new != old
    print(f"目标 : {tgt}")
    print(f"内容 : {len(load_guidelines())} 条准则 · 块 {len(block.splitlines())} 行 · "
          f"{'将改变文件' if changed else '无变化（已是最新）'}")
    if a.verbose or not a.apply:
        print("-" * 70)
        print(_diff(old, new, str(tgt)))
        print("-" * 70)
    # ── L2：git 提交钩子（**跨 agent 的兜底层**）──
    # 它装到 `.git/hooks/`（**本地、不进版本库、可逆**），所以默认就装。
    rc_hook = 0
    if not a.no_git_hook:
        proj = Path(a.target) if a.target else Path.cwd()
        print("-" * 70)
        print("L2 git 提交钩子（不依赖宿主，任何 agent 写的代码都要过这道门）：")
        rc_hook = git_hook_install(proj, a.apply)
    if not a.apply:
        print("（dry-run：未写任何东西。加 --apply 才会写）")
        return rc_hook
    if changed:
        _write(tgt, new)
        print(f"[OK] L1 已写入 {tgt}")
    if rc_hook == 0:
        print("卸载：`core.py uninstall --agent " + a.agent + " --apply`")
    return rc_hook


def cmd_uninstall(a) -> int:
    tgt = resolve_target(a.agent, a.target)
    if tgt is None or not tgt.exists():
        print(f"目标不存在：{tgt}")
        return 2
    old = _read(tgt)
    try:
        new = remove_block(old)
    except ValueError as e:
        print(f"[!!] {e}")
        return 2
    print(f"目标 : {tgt}\n结果 : {'将删除块' if new != old else '未发现块（无事可做）'}")
    rc_hook = 0
    if not a.no_git_hook:
        proj = Path(a.target) if a.target else Path.cwd()
        print("-" * 70)
        rc_hook = git_hook_uninstall(proj, a.apply)
    if not a.apply:
        print("（dry-run：未写。加 --apply 才会写）")
        return rc_hook
    if new != old:
        _write(tgt, new)
        print("[OK] 已卸载（用户原有内容未动）")
    return rc_hook


def cmd_status(a) -> int:
    items = load_guidelines()
    print(f"agent-lessons v{VERSION}")
    print(f"准则 : {len(items)} 条（来自 {GUIDELINES}）")
    for num, title, crit in items:
        flag = "" if crit else "  ⚠ 缺「判据：」行"
        print(f"       [{num}] {title}{flag}")
    _en = load_guidelines("en")
    print(f"       English：{len(_en)} 条（来自 {guidelines_dir('en')}）"
          if _en else f"       English：**缺失**（{guidelines_dir('en')} 不存在或为空）")
    print("-" * 60)
    block = render_block("zh")
    for agent in supported_agents():
        tgt = resolve_target(agent, a.target if agent in ("generic", "cursor") else None)
        if tgt is None:
            continue
        if not tgt.exists():
            print(f"  {agent:<9} {tgt}  —— 文件不存在（未安装）")
            continue
        try:
            span = find_block(_read(tgt))
        except ValueError as e:
            print(f"  {agent:<9} {tgt}  [!!] {e}")
            continue
        if span is None:
            print(f"  {agent:<9} {tgt}  —— 无块（未安装）")
            continue
        cur = _read(tgt)[span[0]: span[1]]
        same = cur.strip() == block.strip()
        print(f"  {agent:<9} {tgt}  —— [OK] 已装{'（与 guidelines 一致）' if same else '（⚠ 与 guidelines 不一致，跑 sync）'}")
    return 0


def _redact(p: Path | str) -> str:
    """把家目录前缀换成 `~` —— **路径本身就可能带用户名**，这是最容易漏的泄漏面。"""
    s = str(p)
    for home in {str(Path.home()), os.path.expanduser("~")}:
        if home and s.startswith(home):
            s = "~" + s[len(home):]
            break
    return s.replace("\\", "/")


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def cmd_report(a) -> int:
    """生成**可直接贴到 issue 的诊断包**：**只含结构，不含内容**。

    ## 这条命令的设计约束（比它能做什么更重要）
    用户报告问题时，最容易的做法是"把你的配置文件贴上来" —— **那是错的**：
    那个文件里可能有**别人的私密内容**（提示词、内部路径、项目信息）。

    ⇒ 规则：
      ✅ 带：版本 / 系统 / Python 版本 / **装了哪几层** / 目标的**路径**（家目录已替换为 `~`）
            / 块**是否存在** / 块的**长度与哈希**（判断"是否与发布版一致"）/ 各层自检结果
      ⛔ 不带：文件的**任何内容** / 环境变量的**值** / 用户名 / 主机名 / 项目文件清单

    ⇒ 判据：**如果一个字段会让第三方推断出「这个人是谁 / 在做什么项目」，它就不该进这个包。**
    """
    print(f"# agent-lessons diagnostic report")
    print()
    print(f"- version: {VERSION}")
    print(f"- os: {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"- python: {platform.python_version()}")
    print(f"- guidelines: zh={len(load_guidelines('zh'))} en={len(load_guidelines('en'))} "
          f"parity={'ok' if {n for n,_,_ in load_guidelines('zh')} == {n for n,_,_ in load_guidelines('en')} else 'MISMATCH'}")
    print()
    print("## layers per agent")
    for agent in supported_agents():
        tgt = resolve_target(agent, a.target if agent in ("generic", "cursor") else None)
        if tgt is None:
            continue
        row = [f"- **{agent}**"]
        row.append(f"  - target: `{_redact(tgt)}`")
        row.append(f"  - file exists: {tgt.exists()}")
        if tgt.exists():
            try:
                span = find_block(_read(tgt))
            except ValueError as e:
                row.append(f"  - block: **BROKEN** ({e})")
            else:
                if span is None:
                    row.append("  - block: absent")
                else:
                    cur = _read(tgt)[span[0]: span[1]]
                    # ⚠ 必须用**块里实际记的策略**去比对。用默认值比 ⇒ 用户选了 `never`
                    #   而块本身是对的，这里照样报 matches-source=False
                    #   —— **一个纯由我这次改动引入的假阳性**。
                    same = cur.strip() == render_block("zh", teams_of(cur)).strip()
                    row.append(f"  - block: present, {len(cur)} chars, sha256={_sha(cur)}, "
                               f"matches-source={same}")
        print("\n".join(row))
    print()
    print("## L2 git commit hook")
    proj = Path(a.target) if a.target else Path.cwd()
    gd = _git_dir(proj)
    if gd is None:
        print(f"- repo: none (scanned from `{_redact(proj)}`)")
    else:
        dst = gd / "hooks" / "pre-commit"
        ours = dst.exists() and HOOK_MARK in dst.read_text(encoding="utf-8", errors="replace")
        src = ROOT / HOOK_SRC_REL
        print(f"- hook: exists={dst.exists()} ours={ours}")
        if dst.exists() and src.exists():
            same = dst.read_text(encoding="utf-8", errors="replace") == src.read_text(encoding="utf-8")
            print(f"- hook matches shipped source: {same}")
    print()
    print("## selfcheck (summary)")
    print("- (run `install/core.py selfcheck` locally; paste only the summary lines if it fails)")
    print()
    print("---")
    print("This bundle contains **no file contents, no environment values, and no "
          "username/hostname** — only structure. Paths have the home directory replaced by `~`.")
    return 0


def cmd_sync(a) -> int:
    return cmd_install(argparse.Namespace(agent=a.agent, target=a.target, lang=a.lang,
                                          apply=a.apply, verbose=a.verbose,
                                          teams=getattr(a, "teams", None),
                                          no_git_hook=getattr(a, "no_git_hook", False)))


def cmd_selfcheck(a) -> int:
    """安装器**自检** —— 它是机制的一部分，所以它自己也要被验。"""
    bad = 0
    items = load_guidelines()
    print(f"[1] guidelines：{len(items)} 条")
    if not items:
        print("    [!!] 一条都没有 —— 检查目录", GUIDELINES)
        bad += 1
    for num, title, crit in items:
        if not crit:
            print(f"    [!!] [{num}] {title} —— 缺「判据：」行（不可执行）")
            bad += 1

    # ⚠ 2026-09-20 加（**由翻译队员指出**）：**必须两种语言都查**。
    #   只查一个目录 ⇒ 另一种语言的准则**重演同一个"零消费者"**：
    #   一个英文文件写漏了 `判据：`，**没有任何东西会发现**。
    #   ⚠ 而且再加一条**它没提的**：两种语言的**条目集合必须一致** ——
    #   否则一边加了准则、另一边没加，**两份块会静默漂移**（准则 09 的另一种形态）。
    for lang, label in (("zh", "中文"), ("en", "English")):
        g = guidelines_dir(lang)
        lst = load_guidelines(lang)
        miss = [t for _, t, c in lst if not c]
        n_bad = len(miss)
        if not g.is_dir():
            print(f"    [--] {label} 准则目录不存在：{g}（**该语言的 L1 块无从派生**）")
            continue
        print(f"    {'[OK]' if (lst and not n_bad) else '[!!]'} {label}：{len(lst)} 条"
              + (f"，其中 {n_bad} 条缺「判据：」" if n_bad else ""))
        if not lst:
            bad += 1
        bad += n_bad
    _zh = {n for n, _, _ in load_guidelines("zh")}
    _en = {n for n, _, _ in load_guidelines("en")}
    if _zh != _en:
        print(f"    [!!] **两种语言的条目集合不一致** —— "
              f"只在中文: {sorted(_zh - _en)}；只在英文: {sorted(_en - _zh)}")
        print("         ⇒ 两份注入块会**静默漂移**。补上缺的那边，或删掉多的那边。")
        bad += 1
    else:
        print(f"    [OK] 中/英 条目集合一致（{len(_zh)} 条）")
    # ⚠ 判据解析：**多行判据必须完整收下** —— 吃狗粮时发现准则 11 被截成半句。
    #   判据 = 「多行判据的续行被收全」
    import tempfile as _tf
    _d = Path(_tf.mkdtemp())
    _g = _d / "guidelines"; _g.mkdir()
    (_g / "99-x.md").write_text(
        "# 多行判据\n\n判据：第一段，\n第二段收尾。\n\n尾注。\n", encoding="utf-8")
    _save = GUIDELINES
    globals()["GUIDELINES"] = _g
    try:
        _c = load_guidelines()
        _ok = bool(_c) and _c[0][2] == "第一段， 第二段收尾。"
    finally:
        globals()["GUIDELINES"] = _save
    print(f"    {'[OK]' if _ok else '[!!]'} 多行判据：续行被收全（不得截成半句）")
    if not _ok:
        bad += 1

    print("[2] 块操作（纯函数，用合成样本喂靶）")
    # ⚠ 喂靶的"替换块"**必须是真实的块形状（含标记）** ——
    #   我第一版传的是字面量 "BLOCK2\n"（不含标记），却断言"正好一个 BEGIN" ⇒ 恒 FAIL。
    #   **那是测试写错，不是生产错**（生产行为逐项核过：原地替换、用户内容保留）。
    BLK1 = f"<!-- agent-lessons:BEGIN v0 -->\n旧\n{END}\n"
    BLK2 = f"<!-- agent-lessons:BEGIN v1 -->\n新\n{END}\n"
    cases = [
        ("空文件 → 插入", "", lambda t: apply_block(t, BLK1),
         lambda r: r.count("agent-lessons:BEGIN") == 1),
        ("已有块 → 原地替换（不新增第二块）", f"用户内容\n{BLK1}尾\n",
         lambda t: apply_block(t, BLK2),
         lambda r: (r.count("agent-lessons:BEGIN") == 1 and "新" in r and "旧" not in r
                    and "用户内容" in r and "尾" in r)),
        ("卸载 → 只删块，用户内容保留", f"头\n{BLK1}尾\n",
         remove_block, lambda r: "旧" not in r and "头" in r and "尾" in r),
        ("标记不成对 → 必须拒绝", f"头\n{BEGIN}\nX\n",
         lambda t: find_block(t), lambda r: False),   # 期望抛错
        # ⚠ 幂等：**这条本该拦住"正则吃掉换行"那个 bug** —— 加它是因为当时没有这条例。
        ("幂等：同内容二次安装 ⇒ 逐字节不变", f"用户内容\n{BLK1}尾\n",
         lambda t: apply_block(apply_block(t, BLK2), BLK2),
         lambda r: r == apply_block(f"用户内容\n{BLK1}尾\n", BLK2)),
        # ⚠ 边角形态（自测中真的踩过）：
        #   · **无尾换行**：安装必须补一个换行，而它与"用户自己的换行"在块前**无法区分**
        #     ⇒ 靠把 `nl=1` 写进 BEGIN 行来记住；替换分支还必须**保住**这个标记。
        #   · **CRLF**：用户的 `\r\n` 不能被改写。
        ("边角：原文无尾换行 ⇒ 仍须精确还原", "用户原有内容",
         lambda t: remove_block(apply_block(apply_block(t, BLK1), BLK1)),
         lambda r: r == "用户原有内容"),
        ("边角：CRLF 原文 ⇒ 仍须精确还原", "a\r\nb\r\n",
         lambda t: remove_block(apply_block(apply_block(t, BLK1), BLK1)),
         lambda r: r == "a\r\nb\r\n"),
        ("安装 → 卸载 ⇒ 还原用户原文（不残留分隔空行）", "用户内容\n",
         lambda t: remove_block(apply_block(t, BLK1)),
         lambda r: r == "用户内容\n"),
    ]
    for name, src, fn, ok in cases:
        try:
            res = fn(src)
            good = ok(res)
        except ValueError:
            good = "拒绝" in name
        print(f"    {'[OK]' if good else '[!!]'} {name}")
        if not good:
            bad += 1
    print("[2.5] agent teams 策略（三值，且升级无损）")
    # ⚠ 准则 10：每条都要有一个**已知会失败**的方向，否则恒真。
    _t_ok = {
        "三种取值都能往返": all(teams_of(begin_line(t) + "\n") == t for t in TEAMS_POLICIES),
        "非法取值被拒（不是照抄）": teams_of("<!-- agent-lessons:BEGIN v1 teams=乱写 -->") == TEAMS_DEFAULT,
        "老块（无 teams 属性）⇒ 取默认（**升级无损**）":
            teams_of("<!-- agent-lessons:BEGIN v1.0.0 -->") == TEAMS_DEFAULT,
        "三种取值的块**互不相同**（改策略要真的改内容）":
            len({render_block("zh", t) for t in TEAMS_POLICIES}) == len(TEAMS_POLICIES),
        "策略只写进 BEGIN 行**和**正文各一处":
            all(render_block("zh", t).count(f"teams={t}") == 1 for t in TEAMS_POLICIES),
    }
    for name, good in _t_ok.items():
        print(f"    {'[OK]' if good else '[!!]'} {name}")
        if not good:
            bad += 1

    print("[3] 中/英文档结构对偶（docs/）")
    # ⚠ 准则 10：**新守卫必须拿已知坏样本喂一遍**，证明它真的会红。
    #   ⇒ 用合成目录喂三种坏形状，而不是只跑真目录然后宣称"通过"。
    _dtmp = Path(_tf.mkdtemp()) / "docs"; _dtmp.mkdir()
    (_dtmp / "ok.md").write_text("## A\n### A1\n## B\n", encoding="utf-8")
    (_dtmp / "ok.en.md").write_text("## A\n### A1\n## B\n", encoding="utf-8")
    (_dtmp / "drift.md").write_text("## A\n### A1\n## B\n", encoding="utf-8")     # 有 ###
    (_dtmp / "drift.en.md").write_text("## A\n## B\n", encoding="utf-8")          # 少了 ###
    (_dtmp / "orphan.en.md").write_text("## A\n", encoding="utf-8")               # 无中文对偶
    (_dtmp / "nopair.md").write_text("## A\n", encoding="utf-8")                  # 无英文对偶
    # ⚠ 这一条是**为我自己犯过的错**加的：中文版里留了连续两条 `---`，英文版一条，
    #   而第一版守卫只数 ##/### ⇒ 报"一致"。**喂靶要覆盖我真正犯过的那个形状。**
    (_dtmp / "sep.md").write_text("## A\n\n---\n\n---\n\n## B\n", encoding="utf-8")
    (_dtmp / "sep.en.md").write_text("## A\n\n---\n\n## B\n", encoding="utf-8")
    _drift_ok = {
        "对偶齐全 ⇒ 不报": not [p for p in doc_parity_problems(_dtmp) if "ok" in p],
        "只有分隔线数不同 ⇒ 报": bool([p for p in doc_parity_problems(_dtmp) if "sep" in p]),
        "层级数漂移 ⇒ 报": bool([p for p in doc_parity_problems(_dtmp) if "drift" in p]),
        "孤立英文 ⇒ 报": bool([p for p in doc_parity_problems(_dtmp) if "orphan" in p]),
        "缺英文对偶 ⇒ 报": bool([p for p in doc_parity_problems(_dtmp) if "nopair" in p]),
    }
    for name, good in _drift_ok.items():
        print(f"    {'[OK]' if good else '[!!]'} 喂靶：{name}")
        if not good:
            bad += 1

    _real = doc_parity_problems(DOCS)
    print(f"    {'[OK]' if not _real else '[!!]'} 真目录 docs/："
          + ("中英结构一致" if not _real else f"{len(_real)} 处漂移"))
    for p in _real:
        print(f"         · {p}")
    bad += len(_real)

    print("[4] L2 已装钩子 与 源文件 是否一致")
    # ⚠ 2026-09-20 加，因为**我当场踩了**：改了 hooks/pre-commit、测试全绿
    #   （喂靶测的是**源文件**），但 `.git/hooks/pre-commit` 还是**旧副本** ⇒
    #   新加的那行「成功也留痕」**在现场一次都没跑过**。这又是准则 09（接线 ≠ 生效）。
    #   ⚠ 而且 `report` **早就会报这一条**（`hook matches shipped source: False`）——
    #     **问题是 report 要人主动去跑**。⇒ 搬进 selfcheck，让它每次提交都查。
    #     判据：**「机制存在」不等于「机制会跑到」**，这一条本身就是它自己的例证。
    _src = ROOT / "hooks" / "pre-commit"
    _inst = ROOT / ".git" / "hooks" / "pre-commit"
    if not (_src.exists() and _inst.exists()):
        print(f"    [--] 跳过（源存在={_src.exists()}，已装副本存在={_inst.exists()}）")
    else:
        def _norm(p: Path) -> bytes:
            return p.read_bytes().replace(b"\r\n", b"\n")
        if _norm(_src) == _norm(_inst):
            print("    [OK] 已装钩子与 hooks/pre-commit 逐字节一致")
        else:
            print("    [!!] **已装钩子与源不一致** —— 你改了 hooks/ 但没重新安装，"
                  "新逻辑在现场从未跑过")
            # ⚠ 修复命令**故意不写 `install --apply`**：那会同时写用户的 agent 配置
            #   （`~/.claude/CLAUDE.md` 之类），**改用户配置属于要人点头的一类**。
            #   这里只需要换一个文件，就给最小动作。
            print("         ⇒ 修（只换钩子，不动任何配置）：")
            print("             cp hooks/pre-commit .git/hooks/pre-commit && "
                  "chmod +x .git/hooks/pre-commit")
            print("           （或 `install/core.py install --apply`，"
                  "但它会**同时改写你的 agent 配置**）")
            bad += 1

    print(f"\n结果：{'[OK] 全部通过' if bad == 0 else f'[!!] {bad} 项有问题'}")
    return 0 if bad == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="agent-lessons installer")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p):
        p.add_argument("--agent", default="claude", choices=supported_agents())
        p.add_argument("--target", default=None,
                       help="装到哪个项目目录（L1 的 AGENTS.md 与 L2 的 git 钩子都以它为根；默认当前目录）")
        p.add_argument("--lang", default="zh", choices=["zh", "en"])
        # ⚠ `default=None`（不是 TEAMS_DEFAULT）—— 让「没给」与「给了 ask」**可区分**：
        #   没给 ⇒ 沿用它已有的选择（升级无损）；给了 ⇒ 就用给的。
        p.add_argument("--teams", default=None, choices=list(TEAMS_POLICIES),
                       help="agent teams 策略：always（需要就自己开）/ ask（每次先问你）/ "
                            "never（不开）。不给则沿用已有设置，首次安装取 ask。")
        p.add_argument("--apply", action="store_true", help="真的写（默认 dry-run）")
        p.add_argument("--verbose", action="store_true")
        p.add_argument("--no-git-hook", action="store_true",
                       help="不装 L2（git 提交钩子）。默认**装** —— 它是唯一"
                            "「不依赖宿主、又真的能说不」的一层，也是跨 agent 的兜底")

    for name in ("install", "sync", "uninstall"):
        common(sub.add_parser(name))
    common(sub.add_parser("status"))
    common(sub.add_parser("report"))     # 诊断包：**只含结构，不含内容**（供贴 issue）
    sub.add_parser("selfcheck")

    a = ap.parse_args()
    return {"install": cmd_install, "sync": cmd_sync, "uninstall": cmd_uninstall,
            "status": cmd_status, "selfcheck": cmd_selfcheck,
            "report": cmd_report}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
