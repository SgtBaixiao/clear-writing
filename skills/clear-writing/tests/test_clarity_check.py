#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regression tests for the clear-writing clarity checker."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "clarity_check.py"


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )


class TestClarityCheck(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory(prefix="clear-writing-")
        self.addCleanup(self.tempdir.cleanup)
        self.root = Path(self.tempdir.name)

    def write(self, name: str, content: str) -> Path:
        path = self.root / name
        path.write_text(content, encoding="utf-8")
        return path

    def test_default_is_advisory(self) -> None:
        path = self.write("half.md", "这是一段中文,带半角逗号。\n")
        result = run(str(path))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("半角标点", result.stdout)

    def test_strict_fails_only_half_width_punctuation(self) -> None:
        path = self.write("half.md", "这是一段中文,带半角逗号。\n")
        result = run("--strict", str(path))
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("半角标点", result.stdout)

    def test_strict_does_not_fail_advisory_findings(self) -> None:
        path = self.write("meta.md", "这种说法值得深思。\n")
        result = run("--strict", str(path))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("空泛元话语", result.stdout)

    def test_positive_findings(self) -> None:
        cases = {
            "verb": ("万能动词", "我们进行了分析，并实现了提升。\n"),
            "meta": ("空泛元话语", "这种说法值得深思，也引人深思。\n"),
            "heading": ("机械编号标题", "## 一、背景\n"),
            "sentence": ("长句无气口", "这是" + "很长" * 60 + "的一句话。\n"),
            "paragraph": ("长段落", "这是" + "内容" * 220 + "。\n"),
            "opening": (
                "连续相同开头",
                "通过引入缓存，系统变快了。通过优化索引，查询变快了。通过增加机器，容量变大了。\n",
            ),
            "contrast": ("对比翻案结构", "这不是简单的升级，而是一次范式重构。\n"),
            "disclaimer": (
                "免责尾巴",
                "以上仅依据你提供的材料，未做额外核验。\n",
            ),
        }
        for check, (label, content) in cases.items():
            with self.subTest(check=check):
                path = self.write(check + ".md", content)
                result = run("--checks", check, str(path))
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn(label, result.stdout, result.stdout)

    def test_code_urls_and_comments_are_masked(self) -> None:
        path = self.write(
            "protected.md",
            "正文提一句配置：`foo,bar;baz` 必须写成这样。\n"
            "```\n"
            "x = a, b; c.d = 1.5\n"
            "url = \"https://example.com/a,b;c\"\n"
            "```\n"
            "参考 https://foo.com/x,y 和 [点这里](https://bar.com/p,q)。\n"
            "<!-- 注释里的中文,也不该被扫到。 -->\n",
        )
        result = run("--checks", "half", str(path))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("(clean)", result.stdout)

    def test_numbers_and_english_are_not_half_width_findings(self) -> None:
        path = self.write(
            "numbers.md",
            "圆周率约 3.14，千分位写 1,000，版本 v1.2，比例 92.65%。\n"
            "从 3 秒降到 0.8 秒。调用 API 完成鉴权，再写回结果。\n",
        )
        result = run("--checks", "half", str(path))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("(clean)", result.stdout)

    def test_formal_text_and_numbered_steps_are_not_literal_failures(self) -> None:
        path = self.write(
            "formal.md",
            "## 背景\n"
            "本方案经评审通过，将在生产环境分三个阶段实施：准备、切换、观察。\n"
            "1. 打开设置。\n"
            "2. 选择网络。\n"
            "3. 保存配置。\n"
            "——以上为正式通知，请遵照执行。\n",
        )
        result = run("--strict", str(path))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("[机械编号标题·建议]", result.stdout)

    def test_long_technical_sentence_can_be_clean(self) -> None:
        path = self.write(
            "technical.md",
            "这是一个" + "技术" * 35 + "的句子，读起来仍然清楚。\n",
        )
        result = run("--checks", "sentence", str(path))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("(clean)", result.stdout)

    def test_english_citation_does_not_trigger_half_width_check(self) -> None:
        path = self.write(
            "citation.md",
            "参见 “The Science of Scientific Writing”, *American Scientist*。\n"
            "接口名称写作 `API`, 但这里在行内代码中。\n",
        )
        result = run("--checks", "half", str(path))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("(clean)", result.stdout)

    def test_closing_chinese_quote_then_half_comma_is_flagged(self) -> None:
        path = self.write("closing.md", "他说「明白」,转身就走。\n")
        result = run("--checks", "half", str(path))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("半角标点", result.stdout)

    def test_frontmatter_is_ignored(self) -> None:
        path = self.write(
            "frontmatter.md",
            "---\n"
            "name: demo\n"
            "description: 中文,描述\n"
            "---\n"
            "正文正常。\n",
        )
        result = run("--checks", "half", str(path))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("(clean)", result.stdout)

    def test_unclosed_fence_is_an_input_error(self) -> None:
        path = self.write(
            "unclosed.md",
            "正常一句中文。\n"
            "```\n"
            "这句后面藏着,半角逗号。\n",
        )
        result = run(str(path))
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("围栏", result.stdout)

    def test_unclosed_html_comment_is_an_input_error(self) -> None:
        path = self.write("comment.md", "正常一句。\n<!-- 没有闭合\n")
        result = run(str(path))
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("HTML 注释", result.stdout)

    def test_json_output_has_counts_and_exit_code(self) -> None:
        path = self.write("json.md", "中文,正文。\n")
        result = run("--json", "--checks", "half", str(path))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["summary"]["half"], 1)
        self.assertEqual(payload["total"], 1)
        self.assertEqual(payload["exit_code"], 0)
        self.assertEqual(payload["files"][0]["issues"][0]["check"], "half")

    def test_quiet_omits_source_lines(self) -> None:
        path = self.write("quiet.md", "中文,正文。\n")
        result = run("--quiet", str(path))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("半角标点", result.stdout)
        self.assertNotIn("原文：", result.stdout)

    def test_missing_file_exits_two(self) -> None:
        result = run(str(self.root / "missing.md"))
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("读取失败", result.stdout)

    def test_unknown_check_exits_two(self) -> None:
        path = self.write("clean.md", "正文。\n")
        result = run("--checks", "not-a-check", str(path))
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("未知检查项", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
