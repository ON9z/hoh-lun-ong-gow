#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""发布前泄漏扫描：**工作区 + 全历史 blob + 所有提交信息**。

## 为什么必须有它（准则 11 的下半句）
> **「工作区干净」≠「仓库干净」** —— `git show <旧提交>:<file>` 任何人也取得到。

## 而且提交信息是**一等泄漏面**，最容易漏
本仓库自己就踩过：提交信息里写了私有项目的**名字**和一个**绝对路径**，
而当时的工作区里**一个字都没有**。⇒ **介质不止文件**。

## 用法
    python tools/leak_scan.py                    # 扫本仓库
    python tools/leak_scan.py --repo <path>
    python tools/leak_scan.py --patterns <file>  # 追加私有词表（**该文件必须 gitignore**）

退出码：有命中 ⇒ 1；干净 ⇒ 0。

## ⚠ 私有词表为什么外置
本文件是**公开**的。把它做成「把私有项目名写进来」，**扫描器本身就成了泄漏源**。
⇒ 内置的只有**通用的**凭据/路径/邮箱/IP 形状；
   私有词表从 `--patterns` 指定的文件读，**那个文件在 .gitignore 里**。
"""
from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys

# 内置：通用形状（不含任何私有名称 —— 见上）
BUILTIN = {
    "凭据样式": r"(sk-[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|"
              r"-----BEGIN [A-Z ]*PRIVATE KEY-----|"
              r"(api[_-]?key|apikey|secret|password|passwd|token|passphrase)"
              r"\s*[:=]\s*[\"']?[A-Za-z0-9/+=_\-]{12,})",
    "绝对家目录": r"([A-Za-z]:[\\/]{1,2}Users[\\/][A-Za-z0-9._\-]+|"
              r"/home/[A-Za-z0-9._\-]+/|/Users/[A-Za-z0-9._\-]+/)",
    "邮箱": r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}",
    "内网地址": r"(\b10\.\d+\.\d+\.\d+\b|\b192\.168\.\d+\.\d+\b|"
             r"\b172\.(1[6-9]|2\d|3[01])\.\d+\.\d+\b)",
}

# 已知的**合成样本**：命中里含这些子串 ⇒ 判为喂靶用的假样本，不计入问题。
# ⚠ 每一条都必须是**一眼就是假的**（RFC 2606 保留域 / 占位符），否则是在给真泄漏开后门。
SYNTHETIC = ("abcdefghijklmnop", "someone", "example.invalid", "C:\\Users\\x")


def sh(repo: str, *a: str) -> str:
    r = subprocess.run(["git", "-C", repo, *a], capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    return r.stdout


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(pathlib.Path(__file__).resolve().parent.parent))
    ap.add_argument("--patterns", default=".leak-patterns.txt",
                    help="追加私有词表（每行一条正则；该文件必须 gitignore）")
    args = ap.parse_args()
    repo = args.repo

    pats = dict(BUILTIN)
    pf = pathlib.Path(repo) / args.patterns
    if pf.exists():
        # ⚠ 先自证：私有词表**不能被 git 跟踪**，否则它就是新的泄漏源
        tracked = sh(repo, "ls-files", "--error-unmatch", args.patterns).strip()
        if tracked:
            print(f"[!!] {args.patterns} 被 git 跟踪了 —— 它就是新的泄漏源。先 gitignore 它。")
            return 1
        for i, line in enumerate(pf.read_text(encoding="utf-8").splitlines(), 1):
            line = line.strip()
            if line and not line.startswith("#"):
                pats[f"私有词表:{args.patterns}:{i}"] = line
    else:
        print(f"[i] 未找到 {args.patterns} —— 只跑内置的通用形状。")

    findings: dict[str, list[tuple[str, str]]] = {k: [] for k in pats}

    def scan(label: str, text: str) -> None:
        for cat, pat in pats.items():
            try:
                for m in re.finditer(pat, text):
                    ctx = text[max(0, m.start() - 30):m.end() + 30].replace("\n", " ")
                    findings[cat].append((label, ctx))

            except re.error as e:
                findings[cat].append((label, f"<正则错误 {e}>"))

    # 1. 工作区
    # ⚠ 必须**跳过词表文件自己** —— 它逐行写着那些私有词，扫它会得到一地自命中，
    #   把真正的命中淹掉（第一版就是这个毛病，39 处里大半是我自己）。
    _skip = {args.patterns, str(pf.name)}
    for p in pathlib.Path(repo).rglob("*"):
        if ".git" in p.parts or "__pycache__" in p.parts or not p.is_file():
            continue
        if str(p.relative_to(repo)) in _skip:
            continue
        try:
            scan(f"工作区:{p.relative_to(repo)}", p.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            pass

    # 2. **全历史** blob（不只 HEAD）
    n_blob = 0
    for line in sh(repo, "rev-list", "--objects", "--all").splitlines():
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            continue
        sha, name = parts
        if sh(repo, "cat-file", "-t", sha).strip() != "blob":
            continue
        n_blob += 1
        scan(f"历史blob:{name}", sh(repo, "cat-file", "-p", sha))

    # 3. **提交信息**（一等泄漏面）
    scan("提交信息", sh(repo, "log", "--all", "--format=%H%n%B"))
    n_commit = len(sh(repo, "rev-list", "--all").splitlines())

    print(f"扫描范围：blob {n_blob} · 提交 {n_commit} · 工作区全量\n")
    real = fake = 0
    for cat, hits in findings.items():
        if not hits:
            print(f"[OK ] {cat}")
            continue
        synth = [h for h in hits if any(s in h[1] for s in SYNTHETIC)]
        bad = [h for h in hits if not any(s in h[1] for s in SYNTHETIC)]
        real += len(bad)
        fake += len(synth)
        print(f"[{'!! ' if bad else 'i  '}] {cat}：**{len(bad)} 处**"
              + (f"（另 {len(synth)} 处为已知合成样本，不计）" if synth else ""))
        for label, ctx in bad[:10]:
            print(f"        {label}  …{ctx}…")
        if len(bad) > 10:
            print(f"        …（共 {len(bad)} 处，只列前 10）")

    print(f"\n真实命中 = {real}（合成样本 {fake} 处已排除）")
    return 1 if real else 0


if __name__ == "__main__":
    sys.exit(main())
