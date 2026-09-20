#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""L2 提交钩子的**喂靶测试** —— 拿已知坏样本证明它真的会拦。

## 为什么必须有它（准则 10：机制要能自证）
一个**从未红过**的钩子与没有钩子不可区分 —— 而它更坏，因为它**买走注意力**。
本文件给每个检查项一个"应该被拦"的样本和一个"不应该被拦"的样本。

## ⚠ 我第一版用 shell 测，harness 自己坏了三处（记下来，因为它正是本仓库在讲的东西）
1. **`rc` 取错了**：`cmd | grep ... ; echo rc=$?` 取到的是 **`grep` 的退出码**（准则 07）。
2. **被拦下的提交会把文件留在暂存区** ⇒ 下一个用例看到**累加**的暂存内容 ⇒ 用例之间互相污染。
   修法：**每个用例一个全新仓库**。
3. **`printf` 转义**：`C:\\Users\\x` 被 shell 解释 ⇒ 样本根本不是我想测的那个。
⇒ **"喂靶的 harness 自己也要校准"** —— 否则你测的是 harness，不是被测物。

## 运行
    python tests/test_precommit_hook.py        # 无需 pytest；退出码 0=全过
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
HOOK_SRC = HERE.parent / "hooks" / "pre-commit"


def _git(cwd: Path, *args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    e = dict(os.environ)
    if env:
        e.update(env)
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True,
                          text=True, encoding="utf-8", errors="replace", env=e)


def _fresh_repo(tmp: Path) -> Path:
    """**每个用例一个全新仓库** —— 否则被拦下的提交会把文件留在暂存区，污染下一个用例。"""
    d = tmp / f"r{len(list(tmp.iterdir()))}"
    d.mkdir(parents=True)
    _git(d, "init", "-q")
    _git(d, "config", "user.email", "t@example.invalid")
    _git(d, "config", "user.name", "t")
    hooks = d / ".git" / "hooks"
    hooks.mkdir(parents=True, exist_ok=True)
    shutil.copy2(HOOK_SRC, hooks / "pre-commit")
    os.chmod(hooks / "pre-commit", 0o755)
    return d


def _commit(repo: Path, files: dict[str, str], env: dict | None = None):
    for name, content in files.items():
        p = repo / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    _git(repo, "add", "-A")
    r = _git(repo, "commit", "-m", "t", env=env)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


# ── 应被拦下的（blocked）────────────────────────────────────────────────────
BLOCK_CASES = [
    ("凭据样式：sk- 前缀", {"a.txt": "token=sk-abcdefghijklmnopqrstuvwx\n"}),
    ("凭据样式：api_key=", {"a.txt": 'api_key = "abcdefghijklmnop1234"\n'}),
    ("凭据样式：私钥头", {"a.txt": "-----BEGIN RSA PRIVATE KEY-----\nMIIE\n"}),
    ("绝对家目录路径：Windows", {"a.txt": "see C:\\Users\\someone\\proj\\f.py\n"}),
    ("绝对家目录路径：POSIX", {"a.txt": "see /home/someone/proj/f.py\n"}),
    ("标记不成对", {"a.md": "# t\n<!-- agent-lessons:BEGIN v1.0.0 -->\nx\n"}),
]

# ── 不该被拦下的（must pass）────────────────────────────────────────────────
PASS_CASES = [
    ("干净内容", {"a.txt": "hello\n"}),
    ("行内 allow 豁免", {"a.txt": "see C:\\Users\\someone\\f.py <!-- agent-lessons:allow -->\n"}),
    ("中文内容（编码不该误伤）", {"a.md": "# 标题\n\n正文，含中文与标点。\n"}),
    ("成对的标记块", {"a.md": "# t\n<!-- agent-lessons:BEGIN v1.0.0 -->\nx\n<!-- agent-lessons:END -->\n"}),
    ("文档里谈论凭据（有 allow）", {"a.md": "例如 `api_key = \"...\"` 长这样 <!-- agent-lessons:allow -->\n"}),
]


def main() -> int:
    if not HOOK_SRC.exists():
        print(f"找不到 {HOOK_SRC}")
        return 2
    tmp = Path(tempfile.mkdtemp(prefix="al-hooktest-"))
    bad = 0
    try:
        print("== 应被拦下 ==")
        for name, files in BLOCK_CASES:
            rc, out = _commit(_fresh_repo(tmp), files)
            ok = rc != 0
            bad += 0 if ok else 1
            print(f"  {'[OK]' if ok else '[!!]'} {name}   rc={rc}")

        print("== 不该被拦下 ==")
        for name, files in PASS_CASES:
            rc, out = _commit(_fresh_repo(tmp), files)
            ok = rc == 0
            bad += 0 if ok else 1
            print(f"  {'[OK]' if ok else '[!!]'} {name}   rc={rc}")
            if not ok:
                print("      " + out.strip().splitlines()[-1][:120] if out.strip() else "")

        print("== 逃生口 ==")
        repo = _fresh_repo(tmp)
        rc, _ = _commit(repo, {"a.txt": "see C:\\Users\\someone\\f.py\n"},
                        env={"AGENT_LESSONS_STRICT": "0"})
        print(f"  {'[OK]' if rc == 0 else '[!!]'} STRICT=0 只警告不拦   rc={rc}")
        bad += 0 if rc == 0 else 1

        repo = _fresh_repo(tmp)
        for n, c in [("a.txt", "see C:\\Users\\someone\\f.py\n")]:
            (repo / n).write_text(c, encoding="utf-8")
        _git(repo, "add", "-A")
        rc, _ = _git(repo, "commit", "-m", "t", "--no-verify").returncode, ""
        print(f"  {'[OK]' if rc == 0 else '[!!]'} --no-verify 可绕过   rc={rc}")
        bad += 0 if rc == 0 else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"\n结果：{'[OK] 全部符合预期' if bad == 0 else f'[!!] {bad} 项不符'}")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
