from __future__ import annotations

from collections import Counter
import os
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any

from src.labels import (
    DIFFICULTY_LABELS,
    SECTION_INFO,
    TIER_LABELS,
    TYPE_LABELS,
)

TECTONIC_BUNDLE = "https://relay.fullyjustified.net/default_bundle_v33.tar"
TECTONIC_VERSION = "0.16.9"
SOURCE_DATE_EPOCH = "1711929600"


_PROSE_ESCAPE = {
    "\\": r"\textbackslash{}",
    "{": r"\{",
    "}": r"\}",
    "#": r"\#",
    "$": r"\$",
    "%": r"\%",
    "&": r"\&",
    "_": r"\_",
    "^": r"\textasciicircum{}",
    "~": r"\textasciitilde{}",
}


def _escape_prose(value: str) -> str:
    return "".join(_PROSE_ESCAPE.get(char, char) for char in value).replace(
        "\n", r"\\"
    )


def latex_text(value: str) -> str:
    """Convert mixed prose and `$...$` source into safe XeLaTeX markup."""

    pieces = value.split("$")
    if len(pieces) % 2 == 0:
        raise ValueError(f"unbalanced LaTeX delimiters: {value!r}")
    output: list[str] = []
    for index, piece in enumerate(pieces):
        if index % 2 == 0:
            output.append(_escape_prose(piece))
        else:
            output.append(rf"\({piece}\)")
    return "".join(output)


_BOOKMARK_COMMANDS = {
    "Delta": "Δ",
    "alpha": "α",
    "beta": "β",
    "delta": "δ",
    "epsilon": "ε",
    "infty": "∞",
    "lambda": "λ",
    "mu": "μ",
    "pi": "π",
    "theta": "θ",
    "to": "→",
    "varepsilon": "ε",
}


def _bookmark_math(value: str) -> str:
    previous = None
    while previous != value:
        previous = value
        value = re.sub(
            r"\\frac\{([^{}]*)\}\{([^{}]*)\}",
            lambda match: f"{match.group(1)}/{match.group(2)}",
            value,
        )
        value = re.sub(r"\\(?:text|mathrm)\{([^{}]*)\}", r"\1", value)
    value = re.sub(
        r"\\([A-Za-z]+)",
        lambda match: _BOOKMARK_COMMANDS.get(match.group(1), match.group(1)),
        value,
    )
    value = value.replace(r"\{", "{").replace(r"\}", "}")
    value = value.replace("{", "").replace("}", "")
    return re.sub(r"\s+", " ", value).strip()


def bookmark_text(value: str) -> str:
    """Return plain Unicode text suitable for a PDF bookmark."""

    pieces = value.split("$")
    if len(pieces) % 2 == 0:
        raise ValueError(f"unbalanced LaTeX delimiters: {value!r}")
    return "".join(
        piece if index % 2 == 0 else _bookmark_math(piece)
        for index, piece in enumerate(pieces)
    )


CHAPTER_TITLES = {
    1: {
        "zh": ("函数与极限", "第一章"),
        "en": ("Functions and Limits", "Chapter 1"),
    },
    2: {
        "zh": ("导数与微分", "第二章"),
        "en": ("Derivatives and Differentials", "Chapter 2"),
    },
}

_DIFFICULTY_COLORS = {
    "basic": "Teal",
    "standard": "Blue",
    "advanced": "Purple",
    "hard": "Coral",
    "challenge": "Gold",
}

_WORKSPACE_HEIGHTS = {"S": 55, "M": 66, "L": 79, "XL": 92}

_LINEAGE_LABELS = {
    "zh": {
        "open_text_adaptation": "开放教材方法改写",
        "classic_method_variant": "经典方法变式",
        "original_synthesis": "原创综合 / 诊断",
    },
    "en": {
        "open_text_adaptation": "Open-text method adaptation",
        "classic_method_variant": "Classic-method variant",
        "original_synthesis": "Original synthesis / diagnosis",
    },
}


def _localized_label(
    mapping: dict[str, tuple[Any, ...]], key: str, language: str
) -> str:
    value = mapping[key]
    return str(value[0 if language == "zh" else 1])


def _tex_list(values: list[str], *, numbered: bool = False) -> str:
    environment = "enumerate" if numbered else "itemize"
    options = (
        r"[leftmargin=6mm,label=\textbf{\arabic*.},itemsep=2.3mm,topsep=1.5mm]"
        if numbered
        else r"[leftmargin=5mm,itemsep=1.4mm,topsep=1mm]"
    )
    items = "\n".join(r"\item " + latex_text(value) for value in values)
    return rf"\begin{{{environment}}}{options}" + "\n" + items + "\n" + rf"\end{{{environment}}}"


def _document_preamble(
    *, language: str, kind: str, chapter: int, pdf_title: str
) -> str:
    exercise = kind == "exercises"
    paper = (
        "paperwidth=264mm,paperheight=198mm,top=8mm,bottom=8mm,left=12mm,right=12mm,"
        "includeheadfoot,headheight=5mm,headsep=3mm,footskip=6mm"
        if exercise
        else "paperwidth=198mm,paperheight=264mm,top=10mm,bottom=10mm,left=13mm,right=13mm,"
        "includeheadfoot,headheight=5mm,headsep=3mm,footskip=6mm"
    )
    body_size = "11pt" if language == "zh" else "10pt"
    line_spread = "1.30" if language == "zh" else "1.24"
    running_title = CHAPTER_TITLES[chapter][language][0]
    footer_note = "LaTeX 数学排版" if language == "zh" else "Typeset with LaTeX"
    locale = (
        r'\XeTeXlinebreaklocale "zh"' + "\n" + r"\XeTeXlinebreakskip = 0pt plus 1pt"
        if language == "zh"
        else ""
    )
    return rf"""
\documentclass[{body_size}]{{article}}
\usepackage[{paper}]{{geometry}}
\usepackage{{fontspec}}
\usepackage{{xeCJK}}
\usepackage{{amsmath,amssymb,mathtools}}
\usepackage{{unicode-math}}
\usepackage{{xcolor}}
\usepackage{{fancyhdr}}
\usepackage{{enumitem}}
\usepackage{{array,tabularx,booktabs}}
\usepackage{{needspace}}
\usepackage{{hyperref}}
\usepackage{{bookmark}}
\usepackage{{ragged2e}}
\usepackage{{lastpage}}
\setmainfont{{texgyreheros-regular.otf}}[
  BoldFont=texgyreheros-bold.otf,
  ItalicFont=texgyreheros-italic.otf,
  BoldItalicFont=texgyreheros-bolditalic.otf,
  Scale=MatchLowercase
]
\setsansfont{{texgyreheros-regular.otf}}[
  BoldFont=texgyreheros-bold.otf,
  ItalicFont=texgyreheros-italic.otf,
  BoldItalicFont=texgyreheros-bolditalic.otf,
  Scale=MatchLowercase
]
\setCJKmainfont{{FandolSong-Regular.otf}}[BoldFont=FandolSong-Bold.otf]
\setCJKsansfont{{FandolHei-Regular.otf}}[BoldFont=FandolHei-Bold.otf]
\setmathfont{{STIXTwoMath-Regular.otf}}
{locale}
\linespread{{{line_spread}}}
\setlength{{\parindent}}{{0pt}}
\setlength{{\parskip}}{{2.2mm}}
\setlength{{\emergencystretch}}{{2em}}
\definecolor{{Navy}}{{HTML}}{{172A46}}
\definecolor{{Blue}}{{HTML}}{{3568D4}}
\definecolor{{Teal}}{{HTML}}{{2A9D8F}}
\definecolor{{Gold}}{{HTML}}{{E9A23B}}
\definecolor{{Coral}}{{HTML}}{{E76F51}}
\definecolor{{Purple}}{{HTML}}{{7557C7}}
\definecolor{{Ink}}{{HTML}}{{1F2937}}
\definecolor{{Muted}}{{HTML}}{{667085}}
\definecolor{{Grid}}{{HTML}}{{D7DCE5}}
\definecolor{{PaleBlue}}{{HTML}}{{EEF4FF}}
\definecolor{{PaleTeal}}{{HTML}}{{EAF8F5}}
\definecolor{{PaleGold}}{{HTML}}{{FFF7E8}}
\definecolor{{PaleCoral}}{{HTML}}{{FFF0EC}}
\definecolor{{PalePurple}}{{HTML}}{{F3EFFF}}
\color{{Ink}}
\hypersetup{{
  unicode=true,
  pdftitle={{{_escape_prose(pdf_title)}}},
  pdfauthor={{Independent study workbook contributors}},
  pdfsubject={{Tongji Calculus 7th edition scope; LaTeX-typeset study workbook}},
  colorlinks=true,
  linkcolor=Blue,
  urlcolor=Blue,
  bookmarksopen=true
}}
\pagestyle{{fancy}}
\fancyhf{{}}
\renewcommand{{\headrulewidth}}{{0.3pt}}
\renewcommand{{\footrulewidth}}{{0pt}}
\fancyhead[L]{{\small\color{{Muted}} {_escape_prose(running_title)}}}
\fancyhead[R]{{\small\color{{Muted}} {_escape_prose(footer_note)}}}
\fancyfoot[C]{{\small\color{{Muted}} \thepage\ /\ \pageref*{{LastPage}}}}
\newcommand{{\badge}}[2]{{\begingroup\setlength{{\fboxsep}}{{1.6mm}}\colorbox{{#1}}{{\color{{white}}\sffamily\bfseries\small #2}}\endgroup}}
\newcommand{{\softbadge}}[1]{{\begingroup\setlength{{\fboxsep}}{{1.4mm}}\colorbox{{PaleBlue}}{{\color{{Navy}}\sffamily\bfseries\small #1}}\endgroup}}
\newcommand{{\boxheading}}[2]{{%
  \par\needspace{{4\baselineskip}}\vspace{{1.1mm}}%
  \noindent\begingroup\setlength{{\fboxsep}}{{2mm}}%
  \colorbox{{#1}}{{\parbox{{\dimexpr\linewidth-2\fboxsep\relax}}{{\sffamily\bfseries\color{{Navy}} #2}}}}%
  \endgroup\par\nobreak\vspace{{1.1mm}}%
}}
\newcommand{{\dotrow}}{{\noindent\leaders\hbox to 8mm{{\hss\textcolor{{Grid}}{{\tiny$\bullet$}}\hss}}\hfill\kern0pt\par\vspace{{6.2mm}}}}
\begin{{document}}
"""


def _cover(*, language: str, kind: str, chapter: int) -> str:
    topic, chapter_label = CHAPTER_TITLES[chapter][language]
    if language == "zh":
        document_kind = "分层训练习题册" if kind == "exercises" else "超详细解析"
        kicker = f"同济大学《高等数学》第七版 · {chapter_label}"
        subtitle = "100 道经典方法变式与高质量综合训练"
        note = "全部数学公式由 XeTeX / LaTeX 编译 · Goodnotes 4:3 优化"
    else:
        document_kind = "Exercise Workbook" if kind == "exercises" else "Detailed Solutions"
        kicker = f"Tongji Calculus, 7th Edition · {chapter_label}"
        subtitle = "100 classic-method adaptations and high-quality synthesis problems"
        note = "All mathematics compiled by XeTeX / LaTeX · 4:3 study edition"
    return rf"""
\thispagestyle{{empty}}
\pagecolor{{Navy}}\color{{white}}
\vspace*{{14mm}}
{{\sffamily\bfseries\large {_escape_prose(kicker)}}}
\vspace{{22mm}}

{{\sffamily\bfseries\fontsize{{30}}{{36}}\selectfont {_escape_prose(topic)}\par}}
\vspace{{5mm}}
{{\sffamily\bfseries\fontsize{{22}}{{28}}\selectfont {_escape_prose(document_kind)}\par}}
\vspace{{12mm}}
{{\large {_escape_prose(subtitle)}\par}}
\vfill
{{\color{{white!80}}\rule{{\linewidth}}{{0.8pt}}\par}}
\vspace{{4mm}}
{{\small {_escape_prose(note)}\par}}
\clearpage
\nopagecolor\color{{Ink}}
"""


def _front_matter(items: list[dict[str, Any]], *, language: str, kind: str, chapter: int) -> str:
    if language == "zh":
        title = "使用说明与训练结构"
        intro = (
            "本资料按由易到难组织，题号 Q001--Q100 在中英文版、习题册与解析册中完全一致。"
            "公式均来自显式 LaTeX 源码，并由 XeTeX 数学引擎编译。"
        )
        open_text = "开放教材方法改写"
        classic = "经典方法变式"
        original = "原创综合 / 诊断"
        advice = [
            "第一次作答只打开习题册，并在答题区完整写出推导。",
            "订正时记录错因，而不是只抄最终答案。",
            "48 小时后重做错题，一周后按知识点交叉抽题。",
        ]
        scope = "题源原则"
        scope_text = (
            "题目结合开放教材、公开课和通行教材中的经典方法重新设计。"
            "受版权保护的教材只用于范围和方法核对，不逐字复制题干或解析；"
            "具体来源谱系见 SOURCES.md。"
        )
    else:
        title = "How to Use This Workbook"
        intro = (
            "The material progresses from basic to challenging. IDs Q001--Q100 match across "
            "both languages and both document types. Every formula comes from explicit LaTeX "
            "source and is compiled by the XeTeX mathematics engine."
        )
        open_text = "Open-text method adaptations"
        classic = "Classic-method variants"
        original = "Original synthesis / diagnosis"
        advice = [
            "On the first attempt, use only the exercise workbook and show complete reasoning.",
            "During correction, record the cause of each error instead of copying the final answer.",
            "Redo errors after 48 hours and interleave topics one week later.",
        ]
        scope = "Source-lineage policy"
        scope_text = (
            "Problems are redesigned around classic methods found in open textbooks, public "
            "courses, and standard calculus teaching. Copyrighted books are used only for scope "
            "and method alignment; their wording and solutions are not copied. See SOURCES.md."
        )
    lineage_counts = Counter(
        item["source_lineage"]["category"]
        for item in items
    )
    return rf"""
\thispagestyle{{plain}}
\pdfbookmark[0]{{{_escape_prose(title)}}}{{front-matter}}
{{\sffamily\bfseries\fontsize{{22}}{{28}}\selectfont\color{{Navy}} {_escape_prose(title)}\par}}
\vspace{{4mm}}
{latex_text(intro)}

\boxheading{{PaleBlue}}{{{_escape_prose(open_text)}}}
{lineage_counts['open_text_adaptation']} / {len(items)}

\boxheading{{PaleTeal}}{{{_escape_prose(classic)}}}
{lineage_counts['classic_method_variant']} / {len(items)}

\boxheading{{PalePurple}}{{{_escape_prose(original)}}}
{lineage_counts['original_synthesis']} / {len(items)}

\boxheading{{PaleBlue}}{{{_escape_prose(scope)}}}
{latex_text(scope_text)}

{_tex_list(advice, numbered=True)}
\clearpage
"""


def _question_heading(item: dict[str, Any], *, language: str) -> str:
    difficulty = _localized_label(DIFFICULTY_LABELS, item["difficulty"], language)
    type_name = _localized_label(TYPE_LABELS, item["type"], language)
    tier = _localized_label(TIER_LABELS, item["tier"], language)
    color = _DIFFICULTY_COLORS[item["difficulty"]]
    lineage = _LINEAGE_LABELS[language][item["source_lineage"]["category"]]
    badges = (
        rf"\badge{{{color}}}{{{_escape_prose(difficulty)}}}\hspace{{2mm}}"
        rf"\softbadge{{{_escape_prose(type_name)}}}\hspace{{2mm}}"
        rf"\softbadge{{{_escape_prose(tier)}}}"
    )
    badges += rf"\hspace{{2mm}}\softbadge{{{_escape_prose(lineage)}}}"
    return badges


def _workspace(space: str, language: str) -> str:
    height = _WORKSPACE_HEIGHTS[space]
    rows = max(5, int(height / 7.1))
    label = "答题区 · 可继续加页" if language == "zh" else "Workspace · add pages as needed"
    return rf"""
\vfill
\noindent\fcolorbox{{Grid}}{{white}}{{%
\begin{{minipage}}[t][{height}mm][t]{{\dimexpr\linewidth-2\fboxsep-2\fboxrule\relax}}
\raggedleft\scriptsize\color{{Muted}} {_escape_prose(label)}\par
\vspace{{2mm}}
{''.join(r'\dotrow' + chr(10) for _ in range(rows))}
\end{{minipage}}}}
"""


def _exercise_question(item: dict[str, Any], *, language: str) -> str:
    localized = item[language]
    section_name = SECTION_INFO[item["section"]][0 if language == "zh" else 1]
    choices = localized.get("choices", [])
    choice_tex = ""
    if choices:
        choice_tex = (
            r"\begin{itemize}[leftmargin=4mm,label={},itemsep=1.4mm,topsep=1mm]"
            + "\n"
            + "\n".join(r"\item " + latex_text(choice) for choice in choices)
            + "\n"
            + r"\end{itemize}"
        )
    tags = " · ".join(item["tags"][language])
    return rf"""
\pdfbookmark[1]{{{item['id']} {_escape_prose(bookmark_text(localized['title']))}}}{{{item['id']}}}
{{\small\color{{Muted}}\sffamily {_escape_prose(section_name)}\hfill
{item['minutes']} min · {latex_text(tags)}\par}}
\vspace{{2mm}}
{_question_heading(item, language=language)}
\vspace{{3mm}}

{{\sffamily\bfseries\fontsize{{17}}{{21}}\selectfont\color{{Navy}}
{item['id']} · {latex_text(localized['title'])}\par}}
\vspace{{2mm}}
{{\fontsize{{12.3}}{{18}}\selectfont {latex_text(localized['prompt'])}\par}}
{choice_tex}
{_workspace(item['space'], language)}
\clearpage
"""


def _choice_list(choices: list[str]) -> str:
    if not choices:
        return ""
    return (
        r"\begin{itemize}[leftmargin=4mm,label={},itemsep=1.4mm,topsep=1mm]"
        + "\n"
        + "\n".join(r"\item " + latex_text(choice) for choice in choices)
        + "\n"
        + r"\end{itemize}"
    )


def _solution_section(title: str, color: str, body: str) -> str:
    return rf"\boxheading{{{color}}}{{{_escape_prose(title)}}}" + "\n" + body + "\n"


def _lineage_note(item: dict[str, Any], language: str) -> str:
    lineage = item["source_lineage"]
    category = _LINEAGE_LABELS[language][lineage["category"]]
    references = ", ".join(lineage["references"])
    if language == "zh":
        return (
            f"题源谱系：{category} · 参考编号：{references}。"
            "编号解释及改编边界见 SOURCES.md；此标注不表示逐字转载原题。"
        )
    return (
        f"Source lineage: {category} · {lineage['method_family']} · "
        f"reference IDs: {references}. See SOURCES.md for scope and adaptation boundaries; "
        "this note does not claim verbatim reproduction."
    )


def _solution_question(item: dict[str, Any], *, language: str) -> str:
    localized = item[language]
    solution = localized["solution"]
    labels = (
        {
            "prompt": "题目",
            "answer": "答案",
            "knowledge": "知识点",
            "analysis": "审题与方法选择",
            "steps": "逐步推导",
            "pitfalls": "易错点",
            "verification": "检验",
            "takeaway": "方法总结",
            "extension": "变式与进一步训练",
        }
        if language == "zh"
        else {
            "prompt": "Problem",
            "answer": "Answer",
            "knowledge": "Knowledge points",
            "analysis": "Reading and method choice",
            "steps": "Detailed derivation",
            "pitfalls": "Common pitfalls",
            "verification": "Verification",
            "takeaway": "Method takeaway",
            "extension": "Extension",
        }
    )
    lineage_note = _lineage_note(item, language)
    prompt_body = latex_text(localized["prompt"])
    if localized.get("choices"):
        prompt_body += "\n" + _choice_list(localized["choices"])
    return rf"""
\clearpage
\pdfbookmark[1]{{{item['id']} {_escape_prose(bookmark_text(localized['title']))}}}{{solution-{item['id']}}}
{_question_heading(item, language=language)}
\vspace{{3mm}}

{{\sffamily\bfseries\fontsize{{18}}{{23}}\selectfont\color{{Navy}}
{item['id']} · {latex_text(localized['title'])}\par}}
{_solution_section(labels['prompt'], 'PaleBlue', prompt_body)}
{_solution_section(labels['answer'], 'PaleTeal', r'\textbf{' + latex_text(localized['answer']) + '}')}
{_solution_section(labels['knowledge'], 'PaleGold', _tex_list(solution['knowledge']))}
{_solution_section(labels['analysis'], 'PalePurple', latex_text(solution['analysis']))}
{_solution_section(labels['steps'], 'PaleBlue', _tex_list(solution['steps'], numbered=True))}
{_solution_section(labels['pitfalls'], 'PaleCoral', _tex_list(solution['pitfalls']))}
{_solution_section(labels['verification'], 'PaleTeal', latex_text(solution['verification']))}
{_solution_section(labels['takeaway'], 'PaleGold', latex_text(solution['takeaway']))}
{_solution_section(labels['extension'], 'PalePurple', latex_text(solution['extension']))}
\vspace{{2mm}}
{{\small\color{{Muted}} {latex_text(lineage_note)}\par}}
"""


def build_tex(
    items: list[dict[str, Any]],
    *,
    language: str,
    kind: str,
    chapter: int,
    pdf_title: str,
) -> str:
    body = [
        _document_preamble(
            language=language,
            kind=kind,
            chapter=chapter,
            pdf_title=pdf_title,
        ),
        _cover(language=language, kind=kind, chapter=chapter),
        _front_matter(items, language=language, kind=kind, chapter=chapter),
    ]
    if kind == "exercises":
        body.extend(_exercise_question(item, language=language) for item in items)
    else:
        body.extend(_solution_question(item, language=language) for item in items)
    body.append("\n\\end{document}\n")
    return "".join(body)


def _find_tectonic(root: Path) -> tuple[Path, Path | None]:
    configured = os.environ.get("TECTONIC")
    if configured:
        path = Path(configured).expanduser().resolve()
        return path, None
    system = shutil.which("tectonic")
    if system:
        return Path(system), None
    candidates = [
        root / "work" / "tools" / "tectonic" / "tectonic",
        root.parent / "tools" / "tectonic" / "tectonic",
    ]
    for path in candidates:
        if path.is_file():
            return path, path.parents[2] / "tectonic-cache"
    raise FileNotFoundError(
        "Tectonic 0.16.9 is required. Install that exact version "
        "or set the TECTONIC environment variable."
    )


def compile_pdf(
    items: list[dict[str, Any]],
    *,
    language: str,
    kind: str,
    chapter: int,
    output_path: Path,
    root: Path,
) -> None:
    build_dir = root / "work" / "latex-build" / output_path.stem
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True, exist_ok=True)
    tex_path = build_dir / f"{output_path.stem}.tex"
    tex_path.write_text(
        build_tex(
            items,
            language=language,
            kind=kind,
            chapter=chapter,
            pdf_title=output_path.stem,
        ),
        encoding="utf-8",
    )
    tectonic, cache = _find_tectonic(root)
    version = subprocess.run(
        [str(tectonic), "--version"],
        text=True,
        capture_output=True,
        check=False,
    )
    version_text = (version.stdout + version.stderr).strip()
    if version.returncode or version_text != f"Tectonic {TECTONIC_VERSION}":
        raise RuntimeError(
            f"Tectonic {TECTONIC_VERSION} is required for reproducible builds; "
            f"found {version_text or 'an unreadable executable'}."
        )
    environment = os.environ.copy()
    if cache is not None:
        cache.mkdir(parents=True, exist_ok=True)
        environment["XDG_CACHE_HOME"] = str(cache)
    environment["SOURCE_DATE_EPOCH"] = SOURCE_DATE_EPOCH
    environment["FORCE_SOURCE_DATE"] = "1"
    command = [
        str(tectonic),
        "-X",
        "compile",
        "--bundle",
        TECTONIC_BUNDLE,
        "--keep-logs",
        "--outdir",
        str(build_dir),
        str(tex_path),
    ]
    completed = subprocess.run(
        command,
        cwd=root,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    transcript = completed.stdout + completed.stderr
    if completed.returncode:
        raise RuntimeError(f"Tectonic failed for {output_path.name}:\n{transcript}")
    fatal_patterns = (
        "Undefined control sequence",
        "Missing $ inserted",
        "Missing character:",
        "LaTeX Error",
        "Overfull \\hbox",
        "Overfull \\vbox",
        "LaTeX Font Warning",
        "Token not allowed in a PDF string",
        "There were undefined references",
    )
    found = [pattern for pattern in fatal_patterns if pattern in transcript]
    log_path = build_dir / f"{output_path.stem}.log"
    log_text = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
    found.extend(pattern for pattern in fatal_patterns if pattern in log_text and pattern not in found)
    if found:
        raise RuntimeError(
            f"Tectonic produced fatal diagnostics for {output_path.name}: {found}"
        )
    generated = build_dir / f"{output_path.stem}.pdf"
    if not generated.is_file():
        raise RuntimeError(f"Tectonic did not create {generated}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(generated, output_path)
