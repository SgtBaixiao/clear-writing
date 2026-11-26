#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Surface-level writing checks for the clear-writing skill.

The script is deliberately conservative. It reports possible problems; it does
not rewrite text, score "AI-ness", or decide whether a sentence is good.

Default behaviour is advisory: findings do not change the exit code. ``--strict``
only makes half-width punctuation inside Chinese prose a failure. Malformed
input, such as an unclosed code fence or HTML comment, exits with code 2.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


CHECK_ORDER = (
    "half",
    "verb",
    "meta",
    "heading",
    "sentence",
    "paragraph",
    "opening",
    "contrast",
    "disclaimer",
)

CHECK_LABELS = {
    "half": "半角标点",
    "verb": "万能动词",
    "meta": "空泛元话语",
    "heading": "机械编号标题",
    "sentence": "长句无气口",
    "paragraph": "长段落",
    "opening": "连续相同开头",
    "contrast": "对比翻案结构",
    "disclaimer": "免责尾巴",
}

CHECK_KINDS = {
    "half": "字面",
    "verb": "建议",
    "meta": "建议",
    "heading": "建议",
    "sentence": "建议",
    "paragraph": "建议",
    "opening": "建议",
    "contrast": "建议",
    "disclaimer": "建议",
}

CJK = r"\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff"
CJK_RE = re.compile(r"[" + CJK + r"]")

# Include closing Chinese punctuation so a half-width comma after a quote or
# bracket is still treated as punctuation embedded in Chinese prose.
CJK_OR_CLOSE = (
    r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff"
    r"\u300d\u300f\u300b\u3011\u3015\u201d\u2019\uff09\uff3d]"
)

RE_HALF = re.compile(
    CJK_OR_CLOSE + r"[,;:?!]"
    + r"|" + CJK_OR_CLOSE + r"\.(?![0-9])"
)

RE_HEADING = re.compile(
    r"^#{1,6}[ \t]*("
    r"[一二三四五六七八九十百]+[、.．]"
    r"|[（(][一二三四五六七八九十0-9]+[）)]"
    r"|第[一二三四五六七八九十0-9]+[章节部分步条个方面维度]"
    r"|[0-9]+(?:[.．][0-9]+)*[、.．)）]"
    r"|[一二三四五六七八九十]+[步条个方面维度]"
    r")"
)

RE_META = re.compile(
    r"值得注意的是|值得关注的是|值得深思|引人深思|发人深省|令人深思"
    r"|不禁让人|不禁要问|不难发现|众所周知|综上所述|由此可见"
    r"|总的来说|总体而言|需要指出的是|值得玩味"
    r"|毫无疑问|显而易见|可以看到|可以看出"
)

RE_CONTRAST = re.compile(
    r"不是[^，。；\n]{1,40}[，,](?:而)?是[^，。；\n]{1,40}"
    r"|并非[^，。；\n]{1,40}[，,](?:而)?是[^，。；\n]{1,40}"
    r"|这不是[^，。；\n]{1,40}"
    r"|不在[^，。；\n]{1,20}[，,]?而(?:在|是)"
    r"|(?:看似|表面上)[^，。；\n]{1,40}[，,]?实则"
    r"|你以为[^，。；\n]{1,40}[，,]?其实"
    r"|真正[^，。；\n]{1,30}的是"
    r"|不只是[^，。；\n]{1,30}[，,]?更是"
)

RE_DISCLAIMER = re.compile(
    r"(?:以上|上述)[^。！？\n]{0,20}(?:仅|只)(?:依据|根据|基于)"
    r"|(?:以上|上述)[^。！？\n]{0,20}按(?:你|您)的"
    r"|未(?:做|经过?)?(?:额外|进一步|实际)?的?(?:核验|核实|核查|查证)(?!的)"
    r"|(?:无法|没法|没有|尚未|还没)(?:核验|核实|查证)(?!的)"
)

GENERIC_MODIFIERS = (
    r"(?:全面|深入|系统|持续|进一步|有效|相关|必要|重要|充分|积极|有力"
    r"|扎实|稳妥|严格|认真|科学|合理|有序|稳步|大力|切实|显著|明显"
    r"|大幅|整体|综合|重点|专项|集中|统一)"
)

ACTION_NOUNS = (
    r"(?:分析|研究|评估|验证|确认|处理|优化|提升|改善|改进|建设|管理"
    r"|维护|支持|保障|贡献|决定|反应|响应|覆盖|增长|发展|落地|总结"
    r"|汇报|沟通|协同|协作|服务|体验|质量|效率|成本|安全|稳定|可靠性"
    r"|可用性|性能|容量|弹性|扩展性|可观测性)"
)

OUTCOME_NOUNS = (
    r"(?:提升|改善|改进|增长|发展|突破|跨越|升级|优化|覆盖|落地|闭环"
    r"|能力|水平|机制|体系|流程|方案|效果|价值|意义|作用|目标|指标"
    r"|路径|方式|方法|策略|模式|标准|规范|要求|成果|经验|做法|举措"
    r"|安排|部署|计划|质量|效率|成本|安全|稳定|可靠性|可用性|性能"
    r"|容量|弹性|扩展性|可观测性)"
)

TAIL = r"(?=[，。；：、！？\s]|$)"

VERB_PATTERNS = tuple(
    re.compile(pattern)
    for pattern in (
        r"(?:进行|作出|做出|开展|予以|加以|给予|实施)"
        r"(?:了|着|过)?"
        + GENERIC_MODIFIERS
        + r"?(?:的)?"
        + ACTION_NOUNS
        + r"(?:工作|任务|活动|措施|方案|机制|体系|流程|能力|水平|效果|价值"
          r"|意义|作用|目标|指标|路径|方式|方法|策略|模式|标准|规范|要求"
          r"|成果|经验|做法|举措|安排|部署|计划)?"
        + TAIL,
        r"(?:实现|完成|取得|形成|构建|打造|推动|推进|促进|赋能|助力)"
        r"(?:了|着|过)?"
        + GENERIC_MODIFIERS
        + r"?(?:的)?"
        + OUTCOME_NOUNS
        + TAIL,
        r"(?:作出|做出|给出|形成|产生)"
        r"(?:了|着|过)?"
        r"(?:重要|积极|应有|突出|更大|新的?|正确|明确|最终)?"
        r"(?:贡献|决定|反应|响应|判断|评价|结论|安排|部署|承诺|回答|选择)"
        + TAIL,
        r"对[^，。；\n]{1,24}(?:进行|开展|实施|予以|加以)"
        r"(?:了)?"
        + GENERIC_MODIFIERS
        + r"?(?:的)?"
        + ACTION_NOUNS
        + TAIL,
    )
)

COMMON_OPENINGS = {
    "通过",
    "为了",
    "随着",
    "基于",
    "使用",
    "需要",
    "可以",
    "我们",
    "本文",
    "本方案",
    "该方案",
    "在",
    "对",
    "从",
    "当",
    "如果",
    "由于",
    "因为",
    "因此",
    "此外",
    "同时",
    "另外",
}

ENUMERATION_OPENINGS = {
    "第一",
    "第二",
    "第三",
    "第四",
    "第五",
    "其一",
    "其二",
    "其三",
    "首先",
    "其次",
    "最后",
    "一是",
    "二是",
    "三是",
}

REPORTING_OPENINGS = {
    "原文说",
    "原文写",
    "原文是",
    "例如",
    "比如",
    "举例",
}

HALF_TO_FULL = {
    ",": "，",
    ";": "；",
    ":": "：",
    "?": "？",
    "!": "！",
    ".": "。",
}


class ScanError(Exception):
    """Input that would make the scan unreliable."""


@dataclass(frozen=True)
class Issue:
    check: str
    line: int
    column: int
    text: str
    detail: str
    display: str = ""

    def as_dict(self) -> dict:
        return {
            "check": self.check,
            "label": CHECK_LABELS[self.check],
            "kind": CHECK_KINDS[self.check],
            "line": self.line,
            "column": self.column,
            "text": self.text,
            "detail": self.detail,
        }


@dataclass(frozen=True)
class Unit:
    kind: str
    line: int
    text: str


def blank_preserving_newlines(value: str) -> str:
    """Replace visible characters with spaces, keeping line numbers stable."""
    return "".join("\n" if char == "\n" else " " for char in value)


def mask_fenced_blocks(text: str) -> str:
    """Blank fenced code blocks and reject an unclosed fence.

    A malformed fence would hide the rest of the document from the scanner, so
    it is an input error rather than a silent skip.
    """
    lines = text.splitlines(keepends=True)
    output = []
    in_fence = False
    fence_char = ""
    fence_length = 0
    open_line = 0

    for line_number, raw in enumerate(lines, 1):
        line_without_ending = raw.rstrip("\r\n")
        match = re.match(r"^[ \t]{0,3}(`{3,}|~{3,})(.*)$", line_without_ending)
        if match:
            marker = match.group(1)
            remainder = match.group(2)
            if not in_fence:
                in_fence = True
                fence_char = marker[0]
                fence_length = len(marker)
                open_line = line_number
                output.append(blank_preserving_newlines(raw))
                continue
            if (
                marker[0] == fence_char
                and len(marker) >= fence_length
                and not remainder.strip()
            ):
                in_fence = False
                fence_char = ""
                fence_length = 0
                output.append(blank_preserving_newlines(raw))
                continue

        if in_fence:
            output.append(blank_preserving_newlines(raw))
        else:
            output.append(raw)

    if in_fence:
        raise ScanError(
            "第 %d 行起出现未闭合的代码围栏（%s）。"
            "继续扫描会把后文误当代码跳过，请先闭合围栏。"
            % (open_line, fence_char * max(fence_length, 3))
        )
    return "".join(output)


def mask_html_comments(text: str) -> str:
    """Blank HTML comments and reject an unclosed comment."""
    text = re.sub(
        r"<!--.*?-->",
        lambda match: blank_preserving_newlines(match.group()),
        text,
        flags=re.DOTALL,
    )
    if "<!--" in text:
        raise ScanError("存在未闭合的 HTML 注释（<!-- 没有对应的 -->）。")
    return text


def mask_frontmatter(text: str) -> str:
    """Blank a leading YAML frontmatter block without changing line numbers."""
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---", 4)
    if end == -1:
        return text
    end += len("\n---")
    return blank_preserving_newlines(text[:end]) + text[end:]


def mask_inline_markup(line: str) -> str:
    """Blank code spans, links, URLs, e-mail addresses, and HTML tags."""
    masked = re.sub(
        r"(!?\[[^\]\n]*\]\()([^)\n]*)(\))",
        lambda match: match.group(1)
        + blank_preserving_newlines(match.group(2))
        + match.group(3),
        line,
    )
    masked = re.sub(
        r"^(\s*\[[^\]]+\]:\s*)(\S+)(.*)$",
        lambda match: match.group(1)
        + blank_preserving_newlines(match.group(2))
        + match.group(3),
        masked,
    )
    masked = re.sub(
        r"(?i)(?:https?://|ftp://|www\.)[^\s<>()\"']+",
        lambda match: blank_preserving_newlines(match.group()),
        masked,
    )
    masked = re.sub(
        r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        lambda match: blank_preserving_newlines(match.group()),
        masked,
    )
    masked = re.sub(
        r"</?[A-Za-z][^>\n]*>",
        lambda match: blank_preserving_newlines(match.group()),
        masked,
    )
    masked = re.sub(
        r"(`+)(.+?)\1",
        lambda match: blank_preserving_newlines(match.group()),
        masked,
    )
    return masked


def half_match_is_chinese_prose(line: str, match: re.Match) -> bool:
    """Reject half punctuation after an English quotation or bracket.

    ``”`` and ``）`` are in the CJK context set because they commonly end
    Chinese prose. But an English title followed by a half-width comma is a
    legitimate citation style, not Chinese punctuation. Inspect the content
    inside the closing mark before deciding.
    """
    start = match.start()
    if start <= 0:
        return False
    previous = line[start]
    if CJK_RE.fullmatch(previous):
        return True

    pairs = {
        "”": "“",
        "’": "‘",
        "）": "（",
        "》": "《",
        "」": "「",
        "』": "『",
        "〕": "〔",
        "］": "［",
    }
    opener = pairs.get(previous)
    if not opener:
        return False
    opener_at = line.rfind(opener, max(0, start - 160), start)
    if opener_at == -1:
        return False
    return bool(CJK_RE.search(line[opener_at + 1 : start]))


def count_cjk(text: str) -> int:
    return len(CJK_RE.findall(text))


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[。！？!?；;])\s*", text)
    return [part.strip() for part in parts if part.strip()]


def split_breaths(sentence: str) -> list[str]:
    return [part for part in re.split(r"[，,、；;：:。！？!?\n]+", sentence) if part.strip()]


def is_block_start(line: str) -> bool:
    stripped = line.lstrip()
    if not stripped:
        return True
    if re.match(r"^#{1,6}[ \t]*", stripped):
        return True
    if re.match(r"^(?:[-+*]|\d+[.)])\s+", stripped):
        return True
    if stripped.startswith(("|", ">")):
        return True
    if re.match(r"^(?:-{3,}|\*{3,}|_{3,})\s*$", stripped):
        return True
    return False


def build_units(masked_lines: Sequence[str]) -> list[Unit]:
    units: list[Unit] = []
    current: list[str] = []
    current_line = 0

    def flush() -> None:
        nonlocal current, current_line
        if current:
            units.append(Unit("prose", current_line, " ".join(current)))
            current = []
            current_line = 0

    for line_number, line in enumerate(masked_lines, 1):
        if not line.strip():
            flush()
            continue
        if is_block_start(line):
            flush()
            stripped = line.strip()
            if re.match(r"^#{1,6}[ \t]*", stripped):
                kind = "heading"
            elif re.match(r"^(?:[-+*]|\d+[.)])\s+", stripped):
                kind = "list"
            elif stripped.startswith("|"):
                kind = "table"
            elif stripped.startswith(">"):
                kind = "quote"
            else:
                kind = "other"
            units.append(Unit(kind, line_number, stripped))
            continue
        if not current:
            current_line = line_number
        current.append(line.strip())

    flush()
    return units


def merge_matches(patterns: Iterable[re.Pattern], text: str) -> list[re.Match]:
    raw = []
    for pattern in patterns:
        raw.extend(pattern.finditer(text))
    raw.sort(key=lambda match: (match.start(), -(match.end() - match.start())))
    selected: list[re.Match] = []
    for match in raw:
        if any(
            not (match.end() <= chosen.start() or match.start() >= chosen.end())
            for chosen in selected
        ):
            continue
        selected.append(match)
    return selected


def snippet(text: str, limit: int = 96) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    if len(compact) <= limit:
        return compact
    return compact[: limit - 1] + "…"


def add_issue(
    issues: list[Issue],
    seen: set[tuple[str, int, int, str]],
    check: str,
    line: int,
    column: int,
    text: str,
    detail: str,
    display: str = "",
) -> None:
    key = (check, line, column, text)
    if key in seen:
        return
    seen.add(key)
    issues.append(Issue(check, line, column, snippet(text), detail, display))


def scan_units(
    units: Sequence[Unit],
    checks: set[str],
    max_sentence: int,
    max_breath: int,
    max_paragraph: int,
    issues: list[Issue],
    seen: set[tuple[str, int, int, str]],
) -> None:
    for unit in units:
        if unit.kind in {"heading", "table"}:
            continue

        sentences = split_sentences(unit.text)
        if "sentence" in checks:
            for sentence in sentences:
                cjk_count = count_cjk(sentence)
                breaths = split_breaths(sentence)
                longest_breath = max((count_cjk(part) for part in breaths), default=0)
                if cjk_count >= max_sentence and longest_breath >= max_breath:
                    add_issue(
                        issues,
                        seen,
                        "sentence",
                        unit.line,
                        1,
                        sentence,
                        "整句 %d 个汉字，最长气口 %d 个汉字；先判断是否需要补停顿，不要机械拆短。"
                        % (cjk_count, longest_breath),
                    )

        if "paragraph" in checks and unit.kind in {"prose", "quote"}:
            cjk_count = count_cjk(unit.text)
            if cjk_count >= max_paragraph:
                add_issue(
                    issues,
                    seen,
                    "paragraph",
                    unit.line,
                    1,
                    unit.text,
                    "段落约 %d 个汉字、%d 句；确认是否混入了多个中心，或能否拆成更清楚的层次。"
                    % (cjk_count, len(sentences)),
                )

        if "opening" in checks and len(sentences) >= 3:
            index = 0
            while index < len(sentences) - 2:
                run_end = index + 1
                while run_end < len(sentences) and same_opening(
                    sentences[index], sentences[run_end]
                ):
                    run_end += 1
                if run_end - index >= 3:
                    prefix = opening_prefix(sentences[index])
                    add_issue(
                        issues,
                        seen,
                        "opening",
                        unit.line,
                        1,
                        " ".join(sentences[index:run_end]),
                        "连续 %d 句都以“%s”开头；确认这是必要的排比，还是句式惯性。"
                        % (run_end - index, prefix),
                    )
                    index = run_end
                else:
                    index += 1


def opening_prefix(sentence: str) -> str:
    cleaned = re.sub(r"^[\s>#*+\-\d.、）)]+", "", sentence)
    return cleaned[:4]


def same_opening(left: str, right: str) -> bool:
    left_prefix = opening_prefix(left)
    right_prefix = opening_prefix(right)
    if len(left_prefix) < 2 or len(right_prefix) < 2:
        return False
    left_two = left_prefix[:2]
    right_two = right_prefix[:2]
    if left_two in ENUMERATION_OPENINGS or right_two in ENUMERATION_OPENINGS:
        return False
    if left_prefix in REPORTING_OPENINGS or right_prefix in REPORTING_OPENINGS:
        return False
    if len(left_prefix) >= 4 and len(right_prefix) >= 4 and left_prefix == right_prefix:
        return True
    return left_two == right_two and left_two in COMMON_OPENINGS


def scan_masked_text(
    original_lines: Sequence[str],
    masked_lines: Sequence[str],
    checks: set[str],
    max_sentence: int,
    max_breath: int,
    max_paragraph: int,
) -> list[Issue]:
    issues: list[Issue] = []
    seen: set[tuple[str, int, int, str]] = set()

    for line_number, masked in enumerate(masked_lines, 1):
        display = original_lines[line_number - 1] if line_number <= len(original_lines) else ""

        if "half" in checks:
            for match in RE_HALF.finditer(masked):
                if not half_match_is_chinese_prose(masked, match):
                    continue
                punct = match.group()[-1]
                add_issue(
                    issues,
                    seen,
                    "half",
                    line_number,
                    match.start() + 1,
                    match.group(),
                    "中文正文中的半角“%s”，建议改为“%s”。"
                    % (punct, HALF_TO_FULL.get(punct, punct)),
                    display,
                )

        if "verb" in checks:
            for match in merge_matches(VERB_PATTERNS, masked):
                add_issue(
                    issues,
                    seen,
                    "verb",
                    line_number,
                    match.start() + 1,
                    match.group(),
                    "万能动词加抽象名词；先找真正的动作，再决定是否保留这个说法。",
                    display,
                )

        if "meta" in checks:
            for match in RE_META.finditer(masked):
                add_issue(
                    issues,
                    seen,
                    "meta",
                    line_number,
                    match.start() + 1,
                    match.group(),
                    "空泛元话语；删掉，或改成有材料支撑的具体判断。",
                    display,
                )

        if "heading" in checks and RE_HEADING.match(masked):
            add_issue(
                issues,
                seen,
                "heading",
                line_number,
                1,
                masked.strip(),
                "机械编号标题；确认读者是否需要这个编号，操作步骤和法规条款可以保留。",
                display,
            )

        if "contrast" in checks:
            for match in RE_CONTRAST.finditer(masked):
                add_issue(
                    issues,
                    seen,
                    "contrast",
                    line_number,
                    match.start() + 1,
                    match.group(),
                    "对比或翻案结构；确认它在推进判断，而不是制造语气。",
                    display,
                )

        if "disclaimer" in checks:
            for match in RE_DISCLAIMER.finditer(masked):
                add_issue(
                    issues,
                    seen,
                    "disclaimer",
                    line_number,
                    match.start() + 1,
                    match.group(),
                    "正文里的免责或未核实尾巴；原文要求保留时照留，自己加的提醒放到正文外。",
                    display,
                )

    scan_units(
        build_units(masked_lines),
        checks,
        max_sentence,
        max_breath,
        max_paragraph,
        issues,
        seen,
    )
    return issues


def scan_text(
    text: str,
    checks: set[str],
    max_sentence: int,
    max_breath: int,
    max_paragraph: int,
) -> list[Issue]:
    original_lines = text.split("\n")
    masked_text = mask_frontmatter(text)
    masked_text = mask_fenced_blocks(masked_text)
    masked_text = mask_html_comments(masked_text)
    masked_lines = [mask_inline_markup(line) for line in masked_text.split("\n")]
    return scan_masked_text(
        original_lines,
        masked_lines,
        checks,
        max_sentence,
        max_breath,
        max_paragraph,
    )


def parse_checks(value: str) -> tuple[str, ...]:
    if value.strip().lower() == "all":
        return CHECK_ORDER
    requested = [item.strip() for item in value.split(",") if item.strip()]
    unknown = [item for item in requested if item not in CHECK_ORDER]
    if unknown:
        raise ValueError("未知检查项：%s；可选：%s" % (", ".join(unknown), ",".join(CHECK_ORDER)))
    if not requested:
        raise ValueError("--checks 不能为空")
    return tuple(item for item in CHECK_ORDER if item in requested)


def format_human(
    results: Sequence[tuple[str, Sequence[Issue], str | None]],
    checks: Sequence[str],
    strict: bool,
    quiet: bool,
) -> str:
    lines: list[str] = []
    totals = {check: 0 for check in checks}
    error_count = 0

    for path, issues, error in results:
        lines.append("=== %s ===" % path)
        if error:
            lines.append("  [!] %s" % error)
            error_count += 1
            continue
        if not issues:
            lines.append("    (clean)")
            continue
        for issue in issues:
            totals[issue.check] += 1
        if quiet:
            counts = {}
            for issue in issues:
                counts[issue.check] = counts.get(issue.check, 0) + 1
            detail = "，".join(
                "%s %d" % (CHECK_LABELS[check], counts[check])
                for check in checks
                if check in counts
            )
            lines.append("    %d 处（%s）" % (len(issues), detail))
            continue
        for issue in issues:
            lines.append(
                "  [%s·%s] L%d:%d %s"
                % (
                    CHECK_LABELS[issue.check],
                    CHECK_KINDS[issue.check],
                    issue.line,
                    issue.column,
                    issue.text,
                )
            )
            lines.append("      %s" % issue.detail)
            if issue.display and issue.display.strip() != issue.text:
                lines.append("      原文：%s" % snippet(issue.display, 120))

    lines.append("---- 摘要 ----")
    for check in checks:
        lines.append("  %-12s %d 处" % (CHECK_LABELS[check], totals[check]))
    total = sum(totals.values())
    lines.append(
        "  合计 %d 处；模式=%s；%s"
        % (
            total,
            "提示",
            "--strict 时仅“半角标点”命中会让退出码为 1"
            if strict
            else "默认不因提示改变退出码",
        )
    )
    if error_count:
        lines.append("  输入错误 %d 个文件，退出码 2" % error_count)
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "clear-writing 的字面与结构提示扫描器。"
            "它不改稿、不打 AI 分；默认只报告，--strict 只让中文正文中的半角标点失败。"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("files", nargs="+", help="要检查的 Markdown 或纯文本文件")
    parser.add_argument(
        "--checks",
        default=",".join(CHECK_ORDER),
        help="逗号分隔的检查项；all 表示全部。可选：%s" % ",".join(CHECK_ORDER),
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="仅把中文正文中的半角标点作为失败条件；其他项仍只提示",
    )
    parser.add_argument("--quiet", action="store_true", help="只输出每个文件的命中摘要")
    parser.add_argument("--json", action="store_true", help="输出机器可读的 JSON")
    parser.add_argument(
        "--max-sentence",
        type=int,
        default=100,
        help="长句提示阈值：整句汉字数（默认 100）",
    )
    parser.add_argument(
        "--max-breath",
        type=int,
        default=28,
        help="长句提示阈值：最长无停顿气口汉字数（默认 28）",
    )
    parser.add_argument(
        "--max-paragraph",
        type=int,
        default=400,
        help="长段提示阈值：段落汉字数（默认 400）",
    )
    args = parser.parse_args(argv)

    try:
        checks = parse_checks(args.checks)
    except ValueError as error:
        parser.error(str(error))

    if args.max_sentence < 1 or args.max_breath < 1 or args.max_paragraph < 1:
        parser.error("阈值必须是正整数")

    results: list[tuple[str, list[Issue], str | None]] = []
    for path_string in args.files:
        path = Path(path_string)
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as error:
            results.append((path_string, [], "读取失败：%s" % error))
            continue
        try:
            issues = scan_text(
                text,
                set(checks),
                args.max_sentence,
                args.max_breath,
                args.max_paragraph,
            )
        except ScanError as error:
            results.append((path_string, [], str(error)))
            continue
        results.append((path_string, issues, None))

    error_count = sum(1 for _, _, error in results if error)
    half_count = sum(
        1
        for _, issues, error in results
        if not error
        for issue in issues
        if issue.check == "half"
    )
    exit_code = 2 if error_count else (1 if args.strict and half_count else 0)

    if args.json:
        payload = {
            "checks": list(checks),
            "strict": args.strict,
            "files": [
                {
                    "path": path,
                    "error": error,
                    "issues": [issue.as_dict() for issue in issues],
                }
                for path, issues, error in results
            ],
            "summary": {
                check: sum(
                    1
                    for _, issues, error in results
                    if not error
                    for issue in issues
                    if issue.check == check
                )
                for check in checks
            },
            "total": sum(
                1
                for _, issues, error in results
                if not error
                for _ in issues
            ),
            "errors": error_count,
            "exit_code": exit_code,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(format_human(results, checks, args.strict, args.quiet))

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
