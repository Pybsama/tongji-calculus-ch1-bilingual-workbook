from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
from typing import Callable, Iterable
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from src.styles import (
    BLUE,
    CORAL,
    DIFFICULTY_LABELS,
    GOLD,
    GRID,
    INK,
    MUTED,
    NAVY,
    PALE_BLUE,
    PALE_CORAL,
    PALE_GOLD,
    PALE_PURPLE,
    PALE_TEAL,
    PAPER,
    PURPLE,
    SECTION_INFO,
    TEAL,
    TIER_LABELS,
    TYPE_LABELS,
    build_styles,
    register_fonts,
)


EXERCISE_SIZE = (264 * mm, 198 * mm)
SOLUTION_SIZE = (198 * mm, 264 * mm)


def _braced_argument(text: str, start: int) -> tuple[str, int] | None:
    if start >= len(text) or text[start] != "{":
        return None
    depth = 0
    for index in range(start, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1 : index], index + 1
    return None


def _replace_one_argument(
    text: str,
    command: str,
    formatter: Callable[[str], str],
) -> str:
    cursor = 0
    while True:
        index = text.find(command, cursor)
        if index < 0:
            return text
        argument = _braced_argument(text, index + len(command))
        if argument is None:
            cursor = index + len(command)
            continue
        inner, end = argument
        replacement = formatter(_normalize_math_markup(inner))
        text = text[:index] + replacement + text[end:]
        cursor = index + len(replacement)


def _replace_fraction(text: str) -> str:
    cursor = 0
    command = r"\frac"
    while True:
        index = text.find(command, cursor)
        if index < 0:
            return text
        numerator = _braced_argument(text, index + len(command))
        if numerator is None:
            cursor = index + len(command)
            continue
        numerator_text, after_numerator = numerator
        denominator = _braced_argument(text, after_numerator)
        if denominator is None:
            cursor = after_numerator
            continue
        denominator_text, end = denominator
        replacement = (
            f"({_normalize_math_markup(numerator_text)})/"
            f"({_normalize_math_markup(denominator_text)})"
        )
        text = text[:index] + replacement + text[end:]
        cursor = index + len(replacement)


def _normalize_math_markup(value: str) -> str:
    text = value.replace("$", "")
    text = _replace_fraction(text)
    text = _replace_one_argument(text, r"\sqrt", lambda inner: f"√({inner})")
    text = _replace_one_argument(text, r"\mathbb", lambda inner: {"R": "ℝ", "Q": "ℚ", "N": "ℕ", "Z": "ℤ"}.get(inner, inner))
    text = _replace_one_argument(text, r"\widetilde", lambda inner: f"{inner}̃")
    text = _replace_one_argument(text, r"\underline", lambda inner: "________" if not inner or "qquad" in inner else inner)
    blackboard = {"R": "ℝ", "Q": "ℚ", "N": "ℕ", "Z": "ℤ"}
    text = re.sub(
        r"\\mathbb\s*([RQNZ])",
        lambda match: blackboard[match.group(1)],
        text,
    )
    text = re.sub(r"\\widetilde\s*([A-Za-z])", lambda match: f"{match.group(1)}̃", text)
    replacements = {
        r"\Rightarrow": "⇒",
        r"\varepsilon": "ε",
        r"\epsilon": "ε",
        r"\infty": "∞",
        r"\delta": "δ",
        r"\alpha": "α",
        r"\xi": "ξ",
        r"\mu": "μ",
        r"\pi": "π",
        r"\sqrt": "√",
        r"\sin": "sin",
        r"\cos": "cos",
        r"\ln": "ln",
        r"\lim": "lim",
        r"\min": "min",
        r"\to": "→",
        r"\le": "≤",
        r"\ge": "≥",
        r"\ne": "≠",
        r"\in": "∈",
        r"\cap": "∩",
        r"\pm": "±",
        r"\cdot": "·",
        r"\equiv": "≡",
        r"\qquad": "    ",
        r"\displaystyle": "",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    text = re.sub(r"_\{([^{}]+)\}", r"_(\1)", text)
    text = re.sub(r"\^\{([^{}]+)\}", r"^(\1)", text)
    text = text.replace(r"\{", "{").replace(r"\}", "}")
    text = text.replace(r"\ ", " ")
    text = re.sub(r"\\([A-Za-z]+)", r"\1", text)
    return text


def _safe(value: object) -> str:
    return escape(_normalize_math_markup(str(value))).replace("\n", "<br/>")


def _lang(item: dict, language: str) -> dict:
    return item[language]


def _section_name(number: int, language: str) -> str:
    return SECTION_INFO[number][0 if language == "zh" else 1]


def _difficulty(item: dict, language: str) -> tuple[str, colors.Color]:
    zh, en, color = DIFFICULTY_LABELS[item["difficulty"]]
    return (zh if language == "zh" else en, color)


def _type_name(item: dict, language: str) -> str:
    zh, en = TYPE_LABELS[item["type"]]
    return zh if language == "zh" else en


def _tier_name(tier: str, language: str) -> str:
    zh, en = TIER_LABELS[tier]
    return zh if language == "zh" else en


class DottedWorkspace(Flowable):
    def __init__(self, width: float, height: float, language: str):
        super().__init__()
        self.width = width
        self.height = height
        self.language = language

    def wrap(self, avail_width: float, avail_height: float) -> tuple[float, float]:
        return min(self.width, avail_width), min(self.height, avail_height)

    def draw(self) -> None:
        canvas = self.canv
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#E3E7EE"))
        canvas.setLineWidth(0.7)
        canvas.roundRect(0, 0, self.width, self.height, 5 * mm, stroke=1, fill=0)
        canvas.setFillColor(GRID)
        step = 8 * mm
        radius = 0.38
        x = step
        while x < self.width - step / 2:
            y = step
            while y < self.height - step / 2:
                canvas.circle(x, y, radius, stroke=0, fill=1)
                y += step
            x += step
        canvas.setFont("Workbook", 7.5)
        canvas.setFillColor(colors.HexColor("#A4ACB9"))
        label = "答题区 · 可继续加页" if self.language == "zh" else "WORKSPACE · add pages as needed"
        canvas.drawRightString(self.width - 4 * mm, self.height - 5 * mm, label)
        canvas.restoreState()


class CoverPanel(Flowable):
    def __init__(self, width: float, height: float, language: str, kind: str):
        super().__init__()
        self.width = width
        self.height = height
        self.language = language
        self.kind = kind

    def wrap(self, avail_width: float, avail_height: float) -> tuple[float, float]:
        return min(self.width, avail_width), min(self.height, avail_height)

    def draw(self) -> None:
        c = self.canv
        w, h = self.width, self.height
        c.saveState()
        c.setFillColor(NAVY)
        c.roundRect(0, 0, w, h, 8 * mm, stroke=0, fill=1)
        c.setFillColor(BLUE)
        c.circle(w * 0.86, h * 0.78, 29 * mm, stroke=0, fill=1)
        c.setFillColor(TEAL)
        c.circle(w * 0.82, h * 0.72, 15 * mm, stroke=0, fill=1)
        c.setStrokeColor(colors.Color(1, 1, 1, alpha=0.14))
        c.setLineWidth(1.2)
        for offset in range(0, 9):
            y = 18 * mm + offset * 12 * mm
            c.line(w * 0.55, y, w - 12 * mm, y + 18 * mm)

        c.setFillColor(colors.white)
        c.setFont("Workbook", 10)
        kicker = (
            "同济大学《高等数学》第七版 · 第一章"
            if self.language == "zh"
            else "TONGJI CALCULUS, 7TH EDITION · CHAPTER 1"
        )
        c.drawString(14 * mm, h - 20 * mm, kicker)

        c.setFont("WorkbookBold", 25 if self.language == "zh" else 22)
        if self.language == "zh":
            lines = ["函数与极限", "分层训练习题册"] if self.kind == "exercises" else ["函数与极限", "超详细解析"]
        else:
            lines = ["FUNCTIONS & LIMITS", "EXERCISE WORKBOOK"] if self.kind == "exercises" else [
                "FUNCTIONS & LIMITS",
                "DETAILED SOLUTIONS",
            ]
        y = h - 53 * mm
        for line in lines:
            c.drawString(14 * mm, y, line)
            y -= 13 * mm

        c.setFont("Workbook", 11)
        subtitle = (
            "100 道原创与教材经典方法变式 · 从基础到挑战"
            if self.language == "zh"
            else "100 original and textbook-method adaptations · basic to challenge"
        )
        c.drawString(14 * mm, y - 5 * mm, subtitle)
        c.setFillColor(colors.HexColor("#D7E3FF"))
        c.setFont("Workbook", 9)
        note = (
            "Goodnotes 4:3 优化版 · 2026"
            if self.language == "zh"
            else "Goodnotes-optimized 4:3 edition · 2026"
        )
        c.drawString(14 * mm, 16 * mm, note)
        c.restoreState()


class WorkbookDocTemplate(BaseDocTemplate):
    def __init__(
        self,
        filename: str,
        *,
        page_size: tuple[float, float],
        language: str,
        kind: str,
        title: str,
    ):
        self.language = language
        self.kind = kind
        self.running_title = title
        margin_x = 14 * mm
        margin_top = 17 * mm
        margin_bottom = 13 * mm
        super().__init__(
            filename,
            pagesize=page_size,
            leftMargin=margin_x,
            rightMargin=margin_x,
            topMargin=margin_top,
            bottomMargin=margin_bottom,
            title=title,
            author="Independent Study Workbook Project",
            subject="Tongji Calculus Chapter 1 bilingual exercises and solutions",
        )
        frame = Frame(
            self.leftMargin,
            self.bottomMargin,
            self.width,
            self.height,
            id="main",
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
        )
        self.addPageTemplates(PageTemplate(id="default", frames=[frame], onPage=self._decorate_page))

    def _decorate_page(self, canvas, doc) -> None:
        canvas.saveState()
        canvas.setFillColor(PAPER)
        canvas.rect(0, 0, doc.pagesize[0], doc.pagesize[1], stroke=0, fill=1)
        if doc.page > 1:
            canvas.setStrokeColor(colors.HexColor("#E4E8EF"))
            canvas.setLineWidth(0.7)
            canvas.line(doc.leftMargin, doc.pagesize[1] - 11 * mm, doc.pagesize[0] - doc.rightMargin, doc.pagesize[1] - 11 * mm)
            canvas.setFillColor(MUTED)
            canvas.setFont("Workbook", 7.8)
            canvas.drawString(doc.leftMargin, doc.pagesize[1] - 8.3 * mm, self.running_title)
            canvas.drawRightString(doc.pagesize[0] - doc.rightMargin, 7.2 * mm, f"{doc.page}")
        canvas.restoreState()

    def afterFlowable(self, flowable: Flowable) -> None:
        bookmark = getattr(flowable, "_bookmark_name", None)
        outline = getattr(flowable, "_outline_text", None)
        level = getattr(flowable, "_outline_level", 0)
        if bookmark and outline:
            self.canv.bookmarkPage(bookmark)
            self.canv.addOutlineEntry(outline, bookmark, level=level, closed=False)


def _bookmark_paragraph(text: str, style, name: str, outline: str, level: int = 0) -> Paragraph:
    paragraph = Paragraph(text, style)
    paragraph._bookmark_name = name
    paragraph._outline_text = outline
    paragraph._outline_level = level
    return paragraph


def _cover_story(styles: dict, width: float, language: str, kind: str) -> list[Flowable]:
    height = 156 * mm if kind == "exercises" else 194 * mm
    if language == "zh":
        disclaimer = "独立编写学习资料。非同济大学或高等教育出版社官方出版物。"
    else:
        disclaimer = "Independently authored study material. Not an official publication of Tongji University or Higher Education Press."
    return [
        Spacer(1, 7 * mm),
        CoverPanel(width, height, language, kind),
        Spacer(1, 7 * mm),
        Paragraph(_safe(disclaimer), styles["small"]),
        PageBreak(),
    ]


def _summary_table(items: list[dict], language: str, styles: dict, width: float) -> Table:
    if language == "zh":
        labels = ["题目", "章节", "难度层级", "题型"]
        values = [
            "100 道",
            "10 节全覆盖",
            "基础 → 挑战",
            "8 类混合",
        ]
    else:
        labels = ["Questions", "Sections", "Progression", "Formats"]
        values = ["100", "All 10 sections", "Basic → challenge", "8 mixed formats"]
    data = []
    for label, value in zip(labels, values):
        data.append(
            [
                Paragraph(f"<b>{_safe(value)}</b><br/><font color='#667085'>{_safe(label)}</font>", styles["center"])
            ]
        )
    table = Table([data], colWidths=[width / 4] * 4)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PALE_BLUE),
                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#D6E2FA")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D6E2FA")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ]
        )
    )
    return table


def _coverage_table(items: list[dict], language: str, styles: dict, width: float) -> Table:
    counts = Counter(item["section"] for item in items)
    if language == "zh":
        data = [["节次", "主题", "题数", "关键覆盖"]]
        keywords = {
            1: "定义域、复合、反函数、性质",
            2: "ε-N、性质、子列、递推",
            3: "单侧极限、ε-δ、性质",
            4: "无穷小/无穷大、倒数关系",
            5: "分解、通分、有理化、参数",
            6: "夹逼、单调有界、两个重要极限",
            7: "阶、等价代换、相消陷阱",
            8: "连续、参数、间断分类",
            9: "连续运算、复合与初等函数",
            10: "最值、零点、介值、一致连续",
        }
    else:
        data = [["Sec.", "Topic", "Items", "Key coverage"]]
        keywords = {
            1: "domains, composition, inverses, properties",
            2: "epsilon-N, properties, subsequences, recursion",
            3: "one-sided limits, epsilon-delta, properties",
            4: "infinitesimals, infinity, reciprocals",
            5: "factoring, rationalization, parameters",
            6: "squeeze, monotone-bounded, two limits",
            7: "orders, equivalents, cancellation traps",
            8: "continuity, parameters, classification",
            9: "operations, composition, elementary functions",
            10: "extrema, zeros, IVT, uniform continuity",
        }
    for section in range(1, 11):
        data.append([str(section), _section_name(section, language), str(counts[section]), keywords[section]])
    rendered = [[Paragraph(f"<b>{_safe(cell)}</b>" if row_index == 0 else _safe(cell), styles["table"]) for cell in row] for row_index, row in enumerate(data)]
    table = Table(rendered, colWidths=[width * 0.08, width * 0.28, width * 0.09, width * 0.55], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F9FC")]),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#D9DEE8")),
                ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#E2E6ED")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def _front_matter(items: list[dict], language: str, styles: dict, width: float, kind: str) -> list[Flowable]:
    if language == "zh":
        heading = "使用说明"
        body = (
            "建议先按“基础篇 → 方法篇 → 综合篇 → 挑战篇”完成。每题右上角给出难度、题型与建议用时。"
            "第一次作答不要查解析；订正时在解析册中记录“错因”，隔 48 小时再做一次。"
        )
        classic = "“教材经典方法变式”表示保留教材代表性方法，但题目结构、参数或问法已经重新设计。"
        scope = "范围说明：只使用第一章知识，不调用导数、洛必达法则、泰勒公式或幂级数。"
        coverage_heading = "知识覆盖矩阵"
    else:
        heading = "How to use this set"
        body = (
            "Work through Foundation, Methods, Synthesis, and Challenge in that order. "
            "Each question shows its difficulty, format, and suggested time. Attempt it before opening the solution book; "
            "record the cause of each error and retry after 48 hours."
        )
        classic = (
            "“Textbook-method adaptation” means the representative method is retained while the structure, parameters, "
            "or task have been independently redesigned."
        )
        scope = (
            "Scope: Chapter 1 tools only. Derivatives, L'Hopital's rule, Taylor expansions, and power series are not used."
        )
        coverage_heading = "Coverage matrix"
    return [
        _bookmark_paragraph(_safe(heading), styles["h1"], "front-matter", heading, 0),
        _summary_table(items, language, styles, width),
        Spacer(1, 8 * mm),
        Paragraph(_safe(body), styles["body"]),
        Paragraph(_safe(classic), styles["body"]),
        Paragraph(_safe(scope), styles["body"]),
        Spacer(1, 5 * mm),
        Paragraph(_safe(coverage_heading), styles["h2"]),
        _coverage_table(items, language, styles, width),
        PageBreak(),
    ]


def _meta_table(item: dict, language: str, styles: dict, width: float) -> Table:
    diff_label, diff_color = _difficulty(item, language)
    type_label = _type_name(item, language)
    section_label = f"§{item['section']} · {_section_name(item['section'], language)}"
    time_label = f"{item['minutes']} 分钟" if language == "zh" else f"{item['minutes']} min"
    classic = (
        "教材经典方法变式"
        if language == "zh"
        else "Textbook-method adaptation"
    )
    cells = [
        (section_label, PALE_BLUE, NAVY),
        (diff_label, colors.Color(diff_color.red, diff_color.green, diff_color.blue, alpha=0.12), diff_color),
        (type_label, PALE_PURPLE, PURPLE),
        (time_label, PALE_GOLD, GOLD),
    ]
    if item["classic_method"]:
        cells.append((classic, PALE_TEAL, TEAL))
    rendered = [
        Paragraph(f"<font color='{text.hexval()}'><b>{_safe(label)}</b></font>", styles["meta"])
        for label, _, text in cells
    ]
    table = Table([rendered], colWidths=[width / len(cells)] * len(cells))
    commands = [
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#D8DEE9")),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D8DEE9")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    for index, (_, background, _) in enumerate(cells):
        commands.append(("BACKGROUND", (index, 0), (index, 0), background))
    table.setStyle(TableStyle(commands))
    return table


def _exercise_item(item: dict, language: str, styles: dict, width: float) -> list[Flowable]:
    localized = _lang(item, language)
    title = f"{item['id']} · {localized['title']}"
    question = _bookmark_paragraph(
        _safe(title),
        styles["question"],
        item["id"],
        title,
        1,
    )
    content: list[Flowable] = [
        _meta_table(item, language, styles, width),
        Spacer(1, 5 * mm),
        question,
        Paragraph(_safe(localized["prompt"]), styles["prompt"]),
    ]
    for index, choice in enumerate(localized.get("choices", [])):
        label = chr(ord("A") + index)
        content.append(Paragraph(f"<b>{label}.</b> {_safe(choice)}", styles["choice"]))
    content.append(Spacer(1, 3 * mm))
    heights = {"S": 68 * mm, "M": 86 * mm, "L": 101 * mm, "XL": 111 * mm}
    content.append(DottedWorkspace(width, heights[item["space"]], language))
    return [KeepTogether(content)]


def _box(
    title: str,
    body: str | Iterable[str],
    *,
    styles: dict,
    width: float,
    background: colors.Color,
    accent: colors.Color,
) -> Table:
    if isinstance(body, str):
        lines = [body]
    else:
        lines = list(body)
    paragraphs: list[Flowable] = [
        Paragraph(f"<font color='{accent.hexval()}'><b>{_safe(title)}</b></font>", styles["box_title"])
    ]
    for line in lines:
        paragraphs.append(Paragraph(_safe(line), styles["box_body"]))
    table = Table([[paragraphs]], colWidths=[width])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), background),
                ("BOX", (0, 0), (-1, -1), 0.7, accent),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    return table


def _solution_item(item: dict, language: str, styles: dict, width: float) -> list[Flowable]:
    localized = _lang(item, language)
    solution = localized["solution"]
    title = f"{item['id']} · {localized['title']}"
    if language == "zh":
        labels = {
            "question": "题目回顾",
            "answer": "结论先行",
            "knowledge": "本题知识点",
            "analysis": "审题与方法选择",
            "steps": "逐步推导",
            "pitfalls": "易错点",
            "verification": "检验与核对",
            "takeaway": "方法总结",
            "extension": "变式提示",
        }
    else:
        labels = {
            "question": "Question",
            "answer": "Answer first",
            "knowledge": "Knowledge points",
            "analysis": "Reading the problem and choosing a method",
            "steps": "Step-by-step derivation",
            "pitfalls": "Common pitfalls",
            "verification": "Verification",
            "takeaway": "Method summary",
            "extension": "Extension prompt",
        }
    story: list[Flowable] = [
        _meta_table(item, language, styles, width),
        Spacer(1, 5 * mm),
        _bookmark_paragraph(_safe(title), styles["question"], f"S-{item['id']}", title, 1),
        _box(
            labels["question"],
            localized["prompt"],
            styles=styles,
            width=width,
            background=PALE_BLUE,
            accent=BLUE,
        ),
        Spacer(1, 4 * mm),
        _box(
            labels["answer"],
            localized["answer"],
            styles=styles,
            width=width,
            background=PALE_GOLD,
            accent=GOLD,
        ),
        Spacer(1, 4 * mm),
        _box(
            labels["knowledge"],
            [f"• {item_text}" for item_text in solution["knowledge"]],
            styles=styles,
            width=width,
            background=PALE_TEAL,
            accent=TEAL,
        ),
        Spacer(1, 4 * mm),
        _box(
            labels["analysis"],
            solution["analysis"],
            styles=styles,
            width=width,
            background=colors.HexColor("#F7F9FC"),
            accent=NAVY,
        ),
        Spacer(1, 5 * mm),
        Paragraph(_safe(labels["steps"]), styles["h2"]),
    ]
    for index, step in enumerate(solution["steps"], start=1):
        step_label = f"第 {index} 步" if language == "zh" else f"Step {index}"
        story.append(Paragraph(f"<b>{_safe(step_label)}.</b> {_safe(step)}", styles["step"]))
    story.extend(
        [
            Spacer(1, 2 * mm),
            _box(
                labels["pitfalls"],
                [f"• {item_text}" for item_text in solution["pitfalls"]],
                styles=styles,
                width=width,
                background=PALE_CORAL,
                accent=CORAL,
            ),
            Spacer(1, 4 * mm),
            _box(
                labels["verification"],
                solution["verification"],
                styles=styles,
                width=width,
                background=PALE_BLUE,
                accent=BLUE,
            ),
            Spacer(1, 4 * mm),
            _box(
                labels["takeaway"],
                solution["takeaway"],
                styles=styles,
                width=width,
                background=PALE_PURPLE,
                accent=PURPLE,
            ),
        ]
    )
    if solution.get("extension"):
        story.extend(
            [
                Spacer(1, 4 * mm),
                _box(
                    labels["extension"],
                    solution["extension"],
                    styles=styles,
                    width=width,
                    background=PALE_GOLD,
                    accent=GOLD,
                ),
            ]
        )
    return story


def _assessment(items: list[dict], language: str, styles: dict, width: float) -> list[Flowable]:
    if language == "zh":
        heading = "训练价值、局限与二刷路线"
        strengths_title = "这套题的优点"
        strengths = [
            "十节完整覆盖，并用知识点标签建立可回查索引。",
            "概念、计算、证明、参数、反例和错解诊断并重，能暴露“会算但不懂条件”的问题。",
            "难题仍严格使用第一章工具，能训练夹逼、等价代换边界和连续性定理的真正理解。",
            "中英文题号与数学内容一一对应，可同时积累微积分英语表达。",
        ]
        limits_title = "需要知道的局限"
        limits = [
            "100 题无法穷尽所有代数变形；遇到薄弱类型仍需追加同类专项训练。",
            "教材内容均为经典方法变式，不是教材原题的逐字复刻。",
            "难度标记具有一定主观性；高中代数基础不同，实际耗时会明显不同。",
            "一致连续性属于星号选学内容；若课堂未讲，可暂时跳过对应选做题。",
            "为守住第一章边界，本套题不展示后续章节中更快捷的洛必达或泰勒方法。",
        ]
        route_title = "建议二刷路线"
        route = [
            "第一遍：按难度顺序限时完成，只标记信心等级，不查答案。",
            "订正：在解析册中写下错因，区分概念、代数、方法选择和书写不严谨。",
            "48 小时后：只重做错题及其前后相邻题，要求不用提示独立复现。",
            "一周后：按知识点索引交叉抽题，重点回练极限定义、相消型等价无穷小和连续性定理条件。",
        ]
    else:
        heading = "Training value, limitations, and second-pass route"
        strengths_title = "Strengths"
        strengths = [
            "All ten sections are covered and indexed by knowledge point.",
            "Conceptual, computational, proof, parameter, counterexample, and error-diagnosis tasks expose more than routine algebra.",
            "Even the hard questions stay within Chapter 1 tools and train the real boundaries of squeeze arguments, equivalent infinitesimals, and continuity theorems.",
            "Chinese and English identifiers and mathematics match one-to-one, supporting calculus vocabulary development.",
        ]
        limits_title = "Limitations"
        limits = [
            "One hundred questions cannot exhaust every algebraic transformation; weak categories may need extra drills.",
            "Textbook material is represented by independently rewritten method adaptations, not verbatim textbook questions.",
            "Difficulty is partly subjective and depends on prior algebra preparation.",
            "Uniform continuity is starred enrichment; skip those optional items if your course omits it.",
            "To respect the Chapter 1 boundary, later shortcuts such as L'Hopital's rule and Taylor expansions are not shown.",
        ]
        route_title = "Recommended second pass"
        route = [
            "First pass: work under time limits, record confidence, and do not open the solutions.",
            "Correction: classify each error as conceptual, algebraic, method-selection, or rigor/communication.",
            "After 48 hours: redo wrong items and their neighbors without prompts.",
            "After one week: sample by knowledge tag, emphasizing limit definitions, cancellation in equivalent infinitesimals, and theorem hypotheses.",
        ]
    return [
        PageBreak(),
        _bookmark_paragraph(_safe(heading), styles["h1"], "assessment", heading, 0),
        _box(strengths_title, [f"• {text}" for text in strengths], styles=styles, width=width, background=PALE_TEAL, accent=TEAL),
        Spacer(1, 6 * mm),
        _box(limits_title, [f"• {text}" for text in limits], styles=styles, width=width, background=PALE_CORAL, accent=CORAL),
        Spacer(1, 6 * mm),
        _box(route_title, [f"{index}. {text}" for index, text in enumerate(route, start=1)], styles=styles, width=width, background=PALE_BLUE, accent=BLUE),
    ]


def _build(
    items: list[dict],
    language: str,
    output_path: Path,
    kind: str,
) -> None:
    register_fonts()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if kind == "exercises":
        page_size = EXERCISE_SIZE
        title = "同济高数第一章·习题册" if language == "zh" else "Tongji Calculus Chapter 1 · Exercises"
    else:
        page_size = SOLUTION_SIZE
        title = "同济高数第一章·超详细解析" if language == "zh" else "Tongji Calculus Chapter 1 · Detailed Solutions"
    styles = build_styles(language)
    doc = WorkbookDocTemplate(
        str(output_path),
        page_size=page_size,
        language=language,
        kind=kind,
        title=title,
    )
    story: list[Flowable] = []
    story.extend(_cover_story(styles, doc.width, language, kind))
    story.extend(_front_matter(items, language, styles, doc.width, kind))

    last_tier: str | None = None
    first_item = True
    for item in items:
        if not first_item:
            story.append(PageBreak())
        if item["tier"] != last_tier:
            tier_heading = _tier_name(item["tier"], language)
            story.append(
                _bookmark_paragraph(
                    _safe(tier_heading),
                    styles["h1"],
                    f"tier-{item['tier']}",
                    tier_heading,
                    0,
                )
            )
            tier_note = (
                "请先独立完成，再对照解析。"
                if language == "zh"
                else "Attempt independently before consulting the solutions."
            )
            story.append(Paragraph(_safe(tier_note), styles["body"]))
            story.append(PageBreak())
            last_tier = item["tier"]

        if kind == "exercises":
            story.extend(_exercise_item(item, language, styles, doc.width))
        else:
            story.extend(_solution_item(item, language, styles, doc.width))
        first_item = False
    story.extend(_assessment(items, language, styles, doc.width))
    doc.build(story)


def build_exercises(items: list[dict], language: str, output_path: Path) -> None:
    _build(items, language, output_path, "exercises")


def build_solutions(items: list[dict], language: str, output_path: Path) -> None:
    _build(items, language, output_path, "solutions")
