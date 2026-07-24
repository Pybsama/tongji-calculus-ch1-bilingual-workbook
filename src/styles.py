from __future__ import annotations

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


NAVY = colors.HexColor("#172A46")
BLUE = colors.HexColor("#3568D4")
TEAL = colors.HexColor("#2A9D8F")
GOLD = colors.HexColor("#E9A23B")
CORAL = colors.HexColor("#E76F51")
PURPLE = colors.HexColor("#7557C7")
INK = colors.HexColor("#1F2937")
MUTED = colors.HexColor("#667085")
PALE_BLUE = colors.HexColor("#EEF4FF")
PALE_TEAL = colors.HexColor("#EAF8F5")
PALE_GOLD = colors.HexColor("#FFF7E8")
PALE_CORAL = colors.HexColor("#FFF0EC")
PALE_PURPLE = colors.HexColor("#F3EFFF")
GRID = colors.HexColor("#D7DCE5")
PAPER = colors.HexColor("#FCFCFD")


SECTION_INFO = {
    1: ("映射与函数", "Mappings and Functions"),
    2: ("数列的极限", "Limits of Sequences"),
    3: ("函数的极限", "Limits of Functions"),
    4: ("无穷小与无穷大", "Infinitesimals and Infinite Quantities"),
    5: ("极限运算法则", "Algebra of Limits"),
    6: ("极限存在准则与两个重要极限", "Existence Criteria and Two Fundamental Limits"),
    7: ("无穷小的比较", "Comparison of Infinitesimals"),
    8: ("连续性与间断点", "Continuity and Discontinuities"),
    9: ("连续函数的运算", "Operations on Continuous Functions"),
    10: ("闭区间上连续函数的性质", "Continuous Functions on Closed Intervals"),
}

DIFFICULTY_LABELS = {
    "basic": ("基础", "Basic", TEAL),
    "standard": ("常规", "Standard", BLUE),
    "advanced": ("进阶", "Advanced", PURPLE),
    "hard": ("困难", "Hard", CORAL),
    "challenge": ("挑战", "Challenge", GOLD),
}

TYPE_LABELS = {
    "single_choice": ("单项选择", "Single choice"),
    "multiple_choice": ("多项选择", "Multiple choice"),
    "true_false": ("判断辨析", "True/false with justification"),
    "fill_blank": ("填空", "Fill in the blank"),
    "calculation": ("计算", "Calculation"),
    "proof": ("证明", "Proof"),
    "comprehensive": ("参数·综合·应用", "Parameter / synthesis / application"),
    "error_diagnosis": ("错解诊断", "Error diagnosis"),
}

TIER_LABELS = {
    "foundation": ("基础篇", "Foundation"),
    "methods": ("方法篇", "Methods"),
    "synthesis": ("综合篇", "Synthesis"),
    "challenge": ("挑战篇", "Challenge"),
}


def register_fonts() -> None:
    fonts = {
        "Workbook": ("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", 0),
        "WorkbookBold": ("/System/Library/Fonts/STHeiti Medium.ttc", 0),
    }
    registered = set(pdfmetrics.getRegisteredFontNames())
    for name, (path, index) in fonts.items():
        if name not in registered:
            pdfmetrics.registerFont(TTFont(name, path, subfontIndex=index))


def build_styles(language: str) -> dict[str, ParagraphStyle]:
    register_fonts()
    sample = getSampleStyleSheet()
    body_size = 10.8 if language == "zh" else 10.4
    leading = 16.8 if language == "zh" else 15.8
    styles = {
        "body": ParagraphStyle(
            "BodyCJK",
            parent=sample["BodyText"],
            fontName="Workbook",
            fontSize=body_size,
            leading=leading,
            textColor=INK,
            wordWrap="CJK",
            spaceAfter=7,
        ),
        "small": ParagraphStyle(
            "SmallCJK",
            parent=sample["BodyText"],
            fontName="Workbook",
            fontSize=8.8,
            leading=12.8,
            textColor=MUTED,
            wordWrap="CJK",
        ),
        "meta": ParagraphStyle(
            "MetaCJK",
            parent=sample["BodyText"],
            fontName="Workbook",
            fontSize=8.7,
            leading=12,
            textColor=MUTED,
            wordWrap="CJK",
        ),
        "h1": ParagraphStyle(
            "H1CJK",
            parent=sample["Heading1"],
            fontName="WorkbookBold",
            fontSize=23,
            leading=30,
            textColor=NAVY,
            wordWrap="CJK",
            spaceBefore=8,
            spaceAfter=14,
        ),
        "h2": ParagraphStyle(
            "H2CJK",
            parent=sample["Heading2"],
            fontName="WorkbookBold",
            fontSize=16,
            leading=22,
            textColor=NAVY,
            wordWrap="CJK",
            spaceBefore=8,
            spaceAfter=9,
        ),
        "question": ParagraphStyle(
            "QuestionTitle",
            parent=sample["Heading2"],
            fontName="WorkbookBold",
            fontSize=15,
            leading=21,
            textColor=NAVY,
            wordWrap="CJK",
            spaceAfter=8,
        ),
        "prompt": ParagraphStyle(
            "PromptCJK",
            parent=sample["BodyText"],
            fontName="Workbook",
            fontSize=12.2 if language == "zh" else 11.7,
            leading=20 if language == "zh" else 18.5,
            textColor=INK,
            wordWrap="CJK",
            spaceAfter=8,
        ),
        "choice": ParagraphStyle(
            "ChoiceCJK",
            parent=sample["BodyText"],
            fontName="Workbook",
            fontSize=10.8,
            leading=16.2,
            leftIndent=8,
            textColor=INK,
            wordWrap="CJK",
            spaceAfter=3,
        ),
        "box_title": ParagraphStyle(
            "BoxTitleCJK",
            parent=sample["BodyText"],
            fontName="WorkbookBold",
            fontSize=10,
            leading=14,
            textColor=NAVY,
            wordWrap="CJK",
            spaceAfter=4,
        ),
        "box_body": ParagraphStyle(
            "BoxBodyCJK",
            parent=sample["BodyText"],
            fontName="Workbook",
            fontSize=9.7 if language == "zh" else 9.3,
            leading=15 if language == "zh" else 14.3,
            textColor=INK,
            wordWrap="CJK",
            spaceAfter=3,
        ),
        "step": ParagraphStyle(
            "StepCJK",
            parent=sample["BodyText"],
            fontName="Workbook",
            fontSize=10.5 if language == "zh" else 10.1,
            leading=16.5 if language == "zh" else 15.5,
            textColor=INK,
            leftIndent=15,
            firstLineIndent=-15,
            wordWrap="CJK",
            spaceAfter=7,
        ),
        "center": ParagraphStyle(
            "CenterCJK",
            parent=sample["BodyText"],
            fontName="Workbook",
            fontSize=10,
            leading=15,
            textColor=INK,
            alignment=TA_CENTER,
            wordWrap="CJK",
        ),
        "table": ParagraphStyle(
            "TableCJK",
            parent=sample["BodyText"],
            fontName="Workbook",
            fontSize=8.4,
            leading=12.2,
            textColor=INK,
            alignment=TA_LEFT,
            wordWrap="CJK",
        ),
    }
    return styles
