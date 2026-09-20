#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CN <-> TW 反引号集合一致检查 —— **S->T 对代码 span 是恒等变换**。

## 它为什么能存在（与 `docs/03` §5.2 的关系）

`docs/03` §5.2 的结论是「机器能验形状，验不了内容对不对」——
**那说的是 CN <-> EN**：同一句话两种语言，措辞必然不同，任何锚点都到不了 0（实测 2 报 1 中）。

**CN <-> TW 不是那个情形。** 简转繁对 **代码 span / 路径 / 标识符** 应当是**恒等变换**：
`install/core.py`、`--teams=always`、`docs/01-...md` 在两段里必须**逐字节相同**。

⇒ 判据 `set(CN 反引号 span) == set(TW 反引号 span)` —— **零例外、零假阳性**。
⇒ **这是 §5.2 那条边界的一个真实例外**，而且是**可机器验**的那一侧。
   （§5.2 说"内容验不了"时，没区分"跨语系"与"同语系换字形"；本条补上这个区分。）

## ⛔ 不能拿它查 CN <-> EN

实测 2026-09-21：EN 段 26 个 span vs CN 段 25 个，差的正是三个 `docs/*.en.md` 链接 ——
英文段**有意**链去英文文档 ⇒ 那是**正当差异**，不是漂移。
**用它查 CN<->EN 会全是假阳性**，而假阳性守卫比没有守卫更坏（会训练出忽略）。

## 用法

    python tools/check_lang_backticks.py                  # 默认比 zh-cn vs zh-tw
    python tools/check_lang_backticks.py --pair zh-cn zh-tw
    python tools/check_lang_backticks.py --selftest       # 喂靶：证明它真的会红

退出码：有不一致 ⇒ 1；一致 ⇒ 0。

## ⚠️ 接线状态

**本文件目前是独立脚本，还没有接进 `install/core.py selfcheck [3]`。**
按本仓库准则 09：**独立脚本 = 零消费者 = 死代码。**
需要那一行接线（`core.py` 是别人的文件，故未代为修改）。
"""
from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

for _s in ("stdout", "stderr"):
    try:
        getattr(sys, _s).reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def _load_core():
    """复用 `install/core.py` 的锚点正则 —— **禁止手抄**（准则：单一事实源）。"""
    spec = importlib.util.spec_from_file_location("alg_core", ROOT / "install" / "core.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sections(text: str, anchor_re) -> dict[str, str]:
    """按 `<a id="...">` 把整份文档切成语段。与 `core.readme_lang_sections` 同源。"""
    parts = anchor_re.split(text)
    return {parts[i]: parts[i + 1] for i in range(1, len(parts) - 1, 2)}


def spans(body: str) -> set[str]:
    """行内代码 span 的集合。**剔除围栏代码块**（那是另一种介质，另有判据）。"""
    no_fence = re.sub(r"```.*?```", "", body, flags=re.S)
    return set(re.findall(r"`([^`\n]+)`", no_fence))


def problems(a_name: str, a_body: str, b_name: str, b_body: str) -> list[str]:
    sa, sb = spans(a_body), spans(b_body)
    out: list[str] = []
    only_a, only_b = sorted(sa - sb), sorted(sb - sa)
    if only_a:
        out.append(f"只在 {a_name} 段出现的 span（{len(only_a)} 个）：{only_a}")
    if only_b:
        out.append(f"只在 {b_name} 段出现的 span（{len(only_b)} 个）：{only_b}")
    return out


# ────────────────────────────────────────────────────────────── 喂靶（准则 10）
_GOOD = """\
<a id="a"></a>
prose with `install/core.py` and `--teams=always`
<a id="b"></a>
prose with `install/core.py` and `--teams=always`
"""

_BAD = """\
<a id="a"></a>
prose with `install/core.py` and `--teams=always`
<a id="b"></a>
prose with `install/core.py` and `--teams=ALWAYS`
"""

_BAD_MISSING = """\
<a id="a"></a>
prose with `install/core.py` and `--teams=always`
<a id="b"></a>
prose with only `install/core.py`
"""

_CJK_IN_CODE = """\
<a id="a"></a>
keep it as `判据：` exactly
<a id="b"></a>
oops it became `判據：`
"""


def selftest(anchor_re) -> int:
    """**拿已知好坏样本喂一遍** —— 一个从不红的检查与没有检查不可区分。"""
    cases = [
        ("对偶齐全 ⇒ 不报", _GOOD, False),
        ("繁中段改坏一个 span（大小写）⇒ 报", _BAD, True),
        ("繁中段少了一个 span ⇒ 报", _BAD_MISSING, True),
        ("**机器令牌被转成繁体 ⇒ 报**（这条最要命）", _CJK_IN_CODE, True),
    ]
    bad = 0
    for name, text, want_red in cases:
        sec = sections(text, anchor_re)
        got = problems("a", sec["a"], "b", sec["b"])
        is_red = bool(got)
        ok = is_red == want_red
        print(f"    {'[OK]' if ok else '[!!]'} 喂靶：{name}")
        if not ok:
            bad += 1
            print(f"         期望 {'报' if want_red else '不报'}，实际 {'报' if is_red else '不报'}")
    return bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--readme", default=str(ROOT / "README.md"))
    ap.add_argument("--pair", nargs=2, default=["zh-cn", "zh-tw"])
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    core = _load_core()
    anchor_re = core.README_ANCHOR

    if a.selftest:
        print("[喂靶] 本检查在已知坏样本上会不会红：")
        bad = selftest(anchor_re)
        print(f"\n结果：{'[!!] ' + str(bad) + ' 个喂靶未按预期' if bad else '[OK] 全部按预期'}")
        return 1 if bad else 0

    p = Path(a.readme)
    if not p.exists():
        print(f"[!!] 找不到 {p}")
        return 1
    sec = sections(p.read_text(encoding="utf-8"), anchor_re)
    na, nb = a.pair
    for n in (na, nb):
        if n not in sec:
            print(f"[!!] 找不到语段 `<a id=\"{n}\">`（现有：{sorted(sec)}）")
            return 1

    print(f"比对：{na}  vs  {nb}   （{p.name}）")
    print(f"  span 数：{na}={len(spans(sec[na]))}  {nb}={len(spans(sec[nb]))}")
    got = problems(na, sec[na], nb, sec[nb])
    if got:
        print(f"[!!] 不一致 {len(got)} 处：")
        for g in got:
            print(f"         · {g}")
        print("     ⇐ 简转繁对代码 span 应当是恒等变换；不同 ⇒ 有一侧被改坏了")
        return 1
    print("[OK] 两段反引号集合完全相等")
    return 0


if __name__ == "__main__":
    sys.exit(main())
