from __future__ import annotations

import re


_FUNCTION_NAMES = {
    "arccos",
    "arcsin",
    "arctan",
    "cos",
    "cot",
    "csc",
    "det",
    "exp",
    "ln",
    "log",
    "lim",
    "max",
    "min",
    "sec",
    "sin",
    "sup",
    "tan",
}
_MATH_OPERATOR_CHARS = set(
    "=<>≤≥≠→←↔↦⇒⇔∀∃∈∉∪∩±·×÷≈≡∼+−-*/^_|:!'√∛∞∑∏∫∘⋯′″‴ℕℤℚℝ"
)
_MATH_BRACKETS = set("()[]{}⌊⌋⌈⌉")
_SUPERSCRIPTS = str.maketrans(
    "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁽⁾ⁿʰʲˢˣᵃᵇᵉᵏᵐᵘᵛⁱ",
    "0123456789+-()nhjsxabekmuvi",
)
_SUBSCRIPTS = str.maketrans(
    "₀₁₂₃₄₅₆₇₈₉₊₋₍₎ₐₑₕᵢⱼₖₗₘₙₒₚᵣₛₜᵤᵥₓ",
    "0123456789+-()aehijklmnoprstuvx",
)
_SUPERSCRIPT_CHARS = set("⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁽⁾ⁿʰʲˢˣᵃᵇᵉᵏᵐᵘᵛⁱ")
_SUBSCRIPT_CHARS = set("₀₁₂₃₄₅₆₇₈₉₊₋₍₎ₐₑₕᵢⱼₖₗₘₙₒₚᵣₛₜᵤᵥₓ")
_CIRCLED_ENUMERATORS = str.maketrans(
    {
        "①": "（1）",
        "②": "（2）",
        "③": "（3）",
        "④": "（4）",
        "⑤": "（5）",
        "⑥": "（6）",
        "⑦": "（7）",
        "⑧": "（8）",
        "⑨": "（9）",
        "⑩": "（10）",
    }
)
_GREEK = {
    "Δ": r"\Delta",
    "Γ": r"\Gamma",
    "Θ": r"\Theta",
    "Λ": r"\Lambda",
    "Ξ": r"\Xi",
    "Π": r"\Pi",
    "Σ": r"\Sigma",
    "Φ": r"\Phi",
    "Ψ": r"\Psi",
    "Ω": r"\Omega",
    "α": r"\alpha",
    "β": r"\beta",
    "γ": r"\gamma",
    "δ": r"\delta",
    "ε": r"\varepsilon",
    "ζ": r"\zeta",
    "η": r"\eta",
    "θ": r"\theta",
    "ι": r"\iota",
    "κ": r"\kappa",
    "λ": r"\lambda",
    "ℓ": r"\ell",
    "μ": r"\mu",
    "ν": r"\nu",
    "ξ": r"\xi",
    "ο": "o",
    "π": r"\pi",
    "ρ": r"\rho",
    "σ": r"\sigma",
    "τ": r"\tau",
    "υ": r"\upsilon",
    "φ": r"\varphi",
    "χ": r"\chi",
    "ψ": r"\psi",
    "ω": r"\omega",
}
_OPERATOR_REPLACEMENTS = {
    "∞": r"\infty",
    "≤": r"\le",
    "≥": r"\ge",
    "≠": r"\ne",
    "→": r"\to",
    "←": r"\leftarrow",
    "↔": r"\leftrightarrow",
    "↦": r"\mapsto",
    "⇒": r"\Rightarrow",
    "⇔": r"\Leftrightarrow",
    "∀": r"\forall",
    "∃": r"\exists",
    "∈": r"\in",
    "∉": r"\notin",
    "∪": r"\cup",
    "∩": r"\cap",
    "±": r"\pm",
    "·": r"\cdot",
    "×": r"\times",
    "÷": r"\div",
    "≈": r"\approx",
    "≡": r"\equiv",
    "∼": r"\sim",
    "∑": r"\sum",
    "∏": r"\prod",
    "∫": r"\int",
    "ℕ": r"\mathbb{N}",
    "ℤ": r"\mathbb{Z}",
    "ℚ": r"\mathbb{Q}",
    "ℝ": r"\mathbb{R}",
    "∘": r"\circ",
    "⋯": r"\cdots",
    "⌊": r"\lfloor",
    "⌋": r"\rfloor",
    "⌈": r"\lceil",
    "⌉": r"\rceil",
    "′": "'",
    "″": "''",
    "‴": "'''",
    "−": "-",
}
_FUNCTION_CALL_PATTERN = "|".join(sorted(_FUNCTION_NAMES, key=len, reverse=True))
_FRACTION_LEFT_BOUNDARY_COMMANDS = {
    "Rightarrow",
    "Leftrightarrow",
    "approx",
    "equiv",
    "ge",
    "in",
    "le",
    "lceil",
    "leftarrow",
    "leftrightarrow",
    "lfloor",
    "ne",
    "notin",
    "pm",
    "rightarrow",
    "sim",
    "to",
}
_FRACTION_RIGHT_BOUNDARY_COMMANDS = _FRACTION_LEFT_BOUNDARY_COMMANDS | {
    "cdot",
    "div",
    "times",
    "rceil",
    "rfloor",
}
_FRACTION_LEFT_BOUNDARY_CHARS = set("=<>≤≥≠→←↔⇒⇔∈∉±≈≡+−-,;:&")
_FRACTION_RIGHT_BOUNDARY_CHARS = _FRACTION_LEFT_BOUNDARY_CHARS | set("*")
_OUTSIDE_MATH_SEED = re.compile(
    r"[=<>≤≥≠→←↔↦⇒⇔∀∃∞√∛∑∏∫∈∉∪∩±·×÷≈≡−∼∘⋯′″‴ℕℤℚℝ"
    r"⌊⌋⌈⌉²³⁴⁵⁶⁷⁸⁹⁰⁺⁻⁽⁾ⁿʰʲˢˣᵃᵇᵉᵏᵐᵘᵛⁱ"
    r"₀₁₂₃₄₅₆₇₈₉₊₋₍₎ₐₑₕᵢⱼₖₗₘₙₒₚᵣₛₜᵤᵥₓ"
    r"ΔΓΘΛΞΠΣΦΨΩαβγδεζηθικλμνξοπρστυφχψωℓ]"
    rf"|(?<![A-Za-z])(?:[A-Za-z]|{_FUNCTION_CALL_PATTERN})\s*\("
)
_UNICODE_MATH_SHORTCUT = re.compile(
    r"[√∛∞≤≥≠→←↔↦⇒⇔∀∃∈∉∪∩±·×÷≈≡∼∑∏∫⋯−ℕℤℚℝ"
    r"²³⁴⁵⁶⁷⁸⁹⁰⁺⁻⁽⁾ⁿʰʲˢˣᵃᵇᵉᵏᵐᵘᵛⁱ"
    r"₀₁₂₃₄₅₆₇₈₉₊₋₍₎ₐₑₕᵢⱼₖₗₘₙₒₚᵣₛₜᵤᵥₓ"
    r"′″‴⌊⌋⌈⌉ΔΓΘΛΞΠΣΦΨΩαβγδεζηθικλμνξοπρστυφχψωℓ]"
)
_ANSWER_BLANK = re.compile(r"_{4,}")


def _segments(text: str) -> tuple[list[tuple[bool, str]], bool]:
    """Return ``(is_math, value)`` segments and whether delimiters balance."""

    segments: list[tuple[bool, str]] = []
    start = 0
    in_math = False
    index = 0
    while index < len(text):
        if text[index] != "$" or (index and text[index - 1] == "\\"):
            index += 1
            continue
        if index > start:
            segments.append((in_math, text[start:index]))
        in_math = not in_math
        index += 1
        start = index
    if start < len(text):
        segments.append((in_math, text[start:]))
    return segments, not in_math


def audit_text(text: str) -> list[str]:
    """Report formula-like content that is not explicitly delimited as LaTeX."""

    segments, balanced = _segments(text)
    errors: list[str] = []
    if not balanced:
        errors.append("unbalanced LaTeX delimiters")
    for is_math, value in segments:
        if not is_math and _OUTSIDE_MATH_SEED.search(value):
            errors.append(f"formula-like text outside LaTeX delimiters: {value!r}")
        if is_math and _UNICODE_MATH_SHORTCUT.search(value):
            errors.append(f"Unicode math shortcut inside LaTeX formula: {value!r}")
        if is_math and re.search(r"(?<!\\)/", value):
            errors.append(f"slash-style division inside LaTeX formula: {value!r}")
    return errors


def _read_identifier(text: str, index: int) -> tuple[str, int] | None:
    if text[index] in _GREEK:
        return text[index], index + 1
    if index and text[index - 1].isascii() and text[index - 1].isalpha():
        return None
    if text[index] == "\\":
        match = re.match(r"\\[A-Za-z]+", text[index:])
        if match:
            return match.group(0), index + len(match.group(0))
        return None
    if not (text[index].isascii() and text[index].isalpha()):
        return None
    end = index + 1
    while end < len(text) and text[end].isascii() and text[end].isalpha():
        end += 1
    word = text[index:end]
    if len(word) == 1 or word in _FUNCTION_NAMES or word in {"dx", "dy", "dt", "du", "rad"}:
        return word, end
    if re.fullmatch(r"[A-Za-z](?:sin|cos|tan|ln|log|exp)", word):
        return word, end
    if len(word) == 2:
        before = text[index - 1] if index else ""
        after = text[end] if end < len(text) else ""
        hyphenated_word = before in "-−" and after in "-−"
        adjacent_math = (
            (after and not after.isspace() and (after in _MATH_OPERATOR_CHARS or after in _MATH_BRACKETS))
            or (before and not before.isspace() and (before in _MATH_OPERATOR_CHARS or before in _MATH_BRACKETS))
        )
        if word.isupper() or (adjacent_math and not hyphenated_word):
            return word, end
    return None


def _read_math_token(text: str, index: int) -> tuple[str, int, bool] | None:
    char = text[index]
    identifier = _read_identifier(text, index)
    if identifier:
        token, end = identifier
        strong = (
            token.startswith("\\")
            or token in _FUNCTION_NAMES
            or token == "rad"
            or token in _GREEK
            or (end < len(text) and text[end] == "(")
        )
        return token, end, strong
    if char in _SUPERSCRIPT_CHARS or char in _SUBSCRIPT_CHARS or char in {"′", "″", "‴"}:
        return char, index + 1, True
    if (char.isascii() and char.isdigit()) or (
        char == "." and index + 1 < len(text) and text[index + 1].isascii() and text[index + 1].isdigit()
    ):
        match = re.match(r"(?:\d+(?:\.\d+)?|\.\d+)", text[index:])
        assert match
        return match.group(0), index + len(match.group(0)), False
    if char in _MATH_OPERATOR_CHARS:
        return char, index + 1, True
    if char in _MATH_BRACKETS or char in ",;":
        return char, index + 1, char in "⌊⌋⌈⌉"
    return None


def _consume_math_run(text: str, start: int) -> tuple[str, int] | None:
    if text[start].isspace():
        return None
    if text[start] in ",;:'":
        return None
    if start and text[start - 1] == "'" and text[start].isascii() and text[start].isalpha():
        return None
    if re.match(r"[A-Za-z]'[A-Z][^\x00-\x7F]", text[start:]):
        return None
    if re.match(r"[A-Za-z]+(?:-[A-Za-z]+)+", text[start:]):
        return None
    if (
        text[start] in "-−"
        and start
        and start + 1 < len(text)
        and text[start - 1].isascii()
        and text[start - 1].isalpha()
        and text[start + 1].isascii()
        and text[start + 1].isalpha()
    ):
        return None
    if re.match(r"a\s+\d", text[start:]):
        return None
    if re.match(r"[A-Z],\s+[A-Za-z]", text[start:]):
        return None
    index = start
    pieces: list[str] = []
    strong = False
    token_count = 0
    number_count = 0
    bracket_count = 0
    while index < len(text):
        if text[index].isspace():
            space_start = index
            while index < len(text) and text[index].isspace():
                index += 1
            if index >= len(text) or _read_math_token(text, index) is None:
                index = space_start
                break
            pieces.append(text[space_start:index])
            continue
        token = _read_math_token(text, index)
        if token is None:
            break
        value, index, is_strong = token
        pieces.append(value)
        strong = strong or is_strong
        token_count += 1
        number_count += int(bool(re.fullmatch(r"(?:\d+(?:\.\d+)?|\.\d+)", value)))
        bracket_count += int(value in _MATH_BRACKETS)
    while pieces and pieces[-1] in {",", ";", " ", "\t", "\n"}:
        index -= len(pieces.pop())
    coordinate_like = number_count >= 2 and bracket_count >= 2 and "," in pieces
    standalone_symbol = bool(pieces) and token_count == 1 and pieces[0] in {
        "∞",
        "∑",
        "∏",
        "∫",
        "⌊",
        "⌋",
        "⌈",
        "⌉",
        "!",
        "rad",
        "·",
        "×",
        "÷",
        "≈",
        "≡",
        "∼",
        "∘",
        "⋯",
        "∀",
        "∃",
        "ℕ",
        "ℤ",
        "ℚ",
        "ℝ",
        *tuple(_GREEK),
    }
    if not pieces or (not strong and not coordinate_like) or (token_count < 2 and not standalone_symbol):
        return None
    return "".join(pieces), index


def _replace_radicals(value: str) -> str:
    output: list[str] = []
    index = 0
    while index < len(value):
        if value[index] not in {"√", "∛"}:
            output.append(value[index])
            index += 1
            continue
        degree = "[3]" if value[index] == "∛" else ""
        index += 1
        if index < len(value) and value[index] == "(":
            depth = 0
            end = index
            while end < len(value):
                if value[end] == "(":
                    depth += 1
                elif value[end] == ")":
                    depth -= 1
                    if depth == 0:
                        break
                end += 1
            if end < len(value):
                output.append(
                    r"\sqrt"
                    + degree
                    + "{"
                    + _replace_radicals(value[index + 1 : end])
                    + "}"
                )
                index = end + 1
                continue
        atom = re.match(r"(?:\\[A-Za-z]+|[A-Za-z]|\d+(?:\.\d+)?)", value[index:])
        if atom:
            output.append(r"\sqrt" + degree + "{" + atom.group(0) + "}")
            index += len(atom.group(0))
        else:
            output.append(r"\sqrt" + degree + "{}")
    return "".join(output)


def _replace_script_runs(value: str, chars: set[str], marker: str, table: dict[int, str]) -> str:
    output: list[str] = []
    index = 0
    while index < len(value):
        if value[index] not in chars:
            output.append(value[index])
            index += 1
            continue
        end = index + 1
        while end < len(value) and value[end] in chars:
            end += 1
        output.append(marker + "{" + value[index:end].translate(table) + "}")
        index = end
    return "".join(output)


def _control_sequence_before(value: str, index: int) -> tuple[str, int] | None:
    """Return a control sequence ending at ``index`` while scanning backwards."""

    if not value[index].isascii() or not value[index].isalpha():
        return None
    start = index
    while start and value[start - 1].isascii() and value[start - 1].isalpha():
        start -= 1
    if not start or value[start - 1] != "\\":
        return None
    return value[start : index + 1], start - 1


def _inside_text_command(value: str, index: int) -> bool:
    r"""Whether ``index`` lies in a ``\text{...}`` group."""

    stack: list[str | None] = []
    cursor = 0
    while cursor < index:
        if value[cursor] == "\\":
            match = re.match(r"\\([A-Za-z]+)", value[cursor:])
            if match:
                cursor += len(match.group(0))
                continue
        if value[cursor] == "{":
            prefix = value[:cursor]
            match = re.search(r"\\([A-Za-z]+)\s*$", prefix)
            stack.append(match.group(1) if match else None)
        elif value[cursor] == "}" and stack:
            stack.pop()
        cursor += 1
    return "text" in stack


def _fraction_left_boundary(value: str, slash: int) -> int:
    depths = {")": 0, "]": 0, "}": 0}
    delimiter_depths = {"ceil": 0, "floor": 0}
    opener_to_closer = {"(": ")", "[": "]", "{": "}"}
    unmatched_bar: int | None = None
    index = slash - 1
    while index >= 0:
        char = value[index]
        if char == "|" and not any(depths.values()):
            unmatched_bar = None if unmatched_bar is not None else index
            index -= 1
            continue
        if char in depths:
            depths[char] += 1
            index -= 1
            continue
        if char in opener_to_closer:
            closer = opener_to_closer[char]
            if depths[closer]:
                depths[closer] -= 1
                index -= 1
                continue
            if unmatched_bar is not None:
                index -= 1
                continue
            return index + 1
        if any(depths.values()) or unmatched_bar is not None:
            index -= 1
            continue
        control = _control_sequence_before(value, index)
        if control:
            command, command_start = control
            if command == "rceil":
                delimiter_depths["ceil"] += 1
                index = command_start - 1
                continue
            if command == "rfloor":
                delimiter_depths["floor"] += 1
                index = command_start - 1
                continue
            if command == "lceil":
                if delimiter_depths["ceil"]:
                    delimiter_depths["ceil"] -= 1
                    index = command_start - 1
                    continue
                return index + 1
            if command == "lfloor":
                if delimiter_depths["floor"]:
                    delimiter_depths["floor"] -= 1
                    index = command_start - 1
                    continue
                return index + 1
            if command in _FRACTION_LEFT_BOUNDARY_COMMANDS:
                return index + 1
            index = command_start - 1
            continue
        if char in _FRACTION_LEFT_BOUNDARY_CHARS:
            return index + 1
        index -= 1
    if unmatched_bar is not None:
        return unmatched_bar + 1
    return 0


def _fraction_right_boundary(value: str, slash: int) -> int:
    depths = {"(": 0, "[": 0, "{": 0}
    closer_to_opener = {")": "(", "]": "[", "}": "{"}
    unmatched_bar = False
    index = slash + 1
    first_nonspace = index
    while first_nonspace < len(value) and value[first_nonspace].isspace():
        first_nonspace += 1
    while index < len(value):
        char = value[index]
        if char == "|" and not any(depths.values()):
            if index == first_nonspace:
                unmatched_bar = True
                index += 1
                continue
            if unmatched_bar:
                unmatched_bar = False
                index += 1
                continue
            return index
        if value.startswith(r"\}", index) and not any(depths.values()) and not unmatched_bar:
            return index
        if char == "\\":
            match = re.match(r"\\([A-Za-z]+)", value[index:])
            if match and not any(depths.values()) and not unmatched_bar:
                if match.group(1) in _FRACTION_RIGHT_BOUNDARY_COMMANDS:
                    return index
            if match:
                index += len(match.group(0))
                continue
        if char in depths:
            depths[char] += 1
            index += 1
            continue
        if char in closer_to_opener:
            opener = closer_to_opener[char]
            if depths[opener]:
                depths[opener] -= 1
                index += 1
                continue
            if unmatched_bar:
                index += 1
                continue
            return index
        if not any(depths.values()) and not unmatched_bar:
            if char == "/":
                return index
            if (
                char in _FRACTION_RIGHT_BOUNDARY_CHARS
                and not (index == first_nonspace and char in "+−-")
            ):
                return index
        index += 1
    return len(value)


def _unwrap_fraction_group(value: str) -> str:
    pairs = {"(": ")", "[": "]"}
    if len(value) < 2 or value[0] not in pairs or value[-1] != pairs[value[0]]:
        return value
    depth = 0
    for index, char in enumerate(value):
        if char == value[0]:
            depth += 1
        elif char == value[-1]:
            depth -= 1
            if depth == 0 and index != len(value) - 1:
                return value
    return value[1:-1] if depth == 0 else value


def _split_prefix_operator(value: str) -> tuple[str, str]:
    match = re.match(r"\\(?:lim|sum|prod|int)(?![A-Za-z])", value)
    if not match:
        return "", value
    cursor = match.end()
    while cursor < len(value) and value[cursor].isspace():
        cursor += 1
    while cursor < len(value) and value[cursor] in "_^":
        cursor += 1
        while cursor < len(value) and value[cursor].isspace():
            cursor += 1
        if cursor < len(value) and value[cursor] == "{":
            depth = 1
            cursor += 1
            while cursor < len(value) and depth:
                if value[cursor] == "{":
                    depth += 1
                elif value[cursor] == "}":
                    depth -= 1
                cursor += 1
        elif cursor < len(value):
            control = re.match(r"\\[A-Za-z]+|.", value[cursor:])
            if control:
                cursor += len(control.group(0))
        while cursor < len(value) and value[cursor].isspace():
            cursor += 1
    if cursor >= len(value):
        return "", value
    return value[:cursor], value[cursor:]


def _replace_divisions(value: str) -> str:
    cursor = 0
    while True:
        slash = value.find("/", cursor)
        if slash < 0:
            return value
        if slash and value[slash - 1] == "\\":
            cursor = slash + 1
            continue
        if _inside_text_command(value, slash):
            cursor = slash + 1
            continue
        left = _fraction_left_boundary(value, slash)
        right = _fraction_right_boundary(value, slash)
        numerator = value[left:slash].strip()
        denominator = value[slash + 1 : right].strip()
        if not numerator or not denominator:
            cursor = slash + 1
            continue
        prefix, numerator = _split_prefix_operator(numerator)
        numerator = _unwrap_fraction_group(numerator)
        denominator = _unwrap_fraction_group(denominator)
        value = (
            value[:left]
            + prefix
            + r"\frac{"
            + numerator
            + "}{"
            + denominator
            + "}"
            + value[right:]
        )
        cursor = 0


def _matching_unescaped_brace(value: str, opening: int) -> int | None:
    depth = 0
    index = opening
    while index < len(value):
        if value[index] == "\\" and index + 1 < len(value):
            index += 2
            continue
        if value[index] == "{":
            depth += 1
        elif value[index] == "}":
            depth -= 1
            if depth == 0:
                return index
        index += 1
    return None


def _escape_outer_literal_braces(value: str) -> str:
    if not value.startswith("{"):
        return value
    closing = _matching_unescaped_brace(value, 0)
    if closing != len(value) - 1:
        return value
    return r"\{" + value[1:-1] + r"\}"


def _escape_operator_literal_braces(value: str) -> str:
    cursor = 0
    pattern = re.compile(r"\\(?:min|max)\{")
    while True:
        match = pattern.search(value, cursor)
        if match is None:
            return value
        opening = match.end() - 1
        closing = _matching_unescaped_brace(value, opening)
        if closing is None:
            cursor = match.end()
            continue
        value = (
            value[:opening]
            + r"\{"
            + value[opening + 1 : closing]
            + r"\}"
            + value[closing + 1 :]
        )
        cursor = closing + 2


def normalize_latex(value: str) -> str:
    """Convert legacy Unicode math shortcuts to canonical LaTeX syntax."""

    value = re.sub(r"\\in\s+R\b", r"\\in \\mathbb{R}", value)
    value = re.sub(r"\\mathbb\s+([A-Za-z])\b", r"\\mathbb{\1}", value)
    value = _escape_outer_literal_braces(value)
    value = re.sub(
        r"(^|[=,:])\{([-+0-9A-Za-z,\s]+)\}",
        lambda match: match.group(1) + r"\{" + match.group(2) + r"\}",
        value,
    )
    value = _replace_radicals(value)
    value = _replace_script_runs(value, _SUPERSCRIPT_CHARS, "^", _SUPERSCRIPTS)
    value = _replace_script_runs(value, _SUBSCRIPT_CHARS, "_", _SUBSCRIPTS)
    for source, target in _GREEK.items():
        value = value.replace(source, target + " ")
    for source, target in _OPERATOR_REPLACEMENTS.items():
        value = value.replace(source, target + (" " if target.startswith("\\") else ""))
    value = re.sub(
        r"(?<![A-Za-z])([A-Za-z])(sin|cos|tan|ln|log|exp)\b",
        lambda match: match.group(1) + "\\" + match.group(2),
        value,
    )
    for function in sorted(_FUNCTION_NAMES, key=len, reverse=True):
        value = re.sub(rf"(?<![\\A-Za-z]){function}(?![A-Za-z])", rf"\\{function}", value)
    value = re.sub(
        r"\\lim\s*_\s*\(([^()]*)\)",
        lambda match: r"\lim_{" + match.group(1).strip() + "}",
        value,
    )
    value = re.sub(
        r"\\lim\s*\(([^()]*(?:\\to|\\rightarrow)[^()]*)\)",
        lambda match: r"\lim_{" + match.group(1).strip() + "}",
        value,
    )
    value = re.sub(
        r"(\\to\s*(?:-?\\infty|[A-Za-z0-9.]+))([+-])(?=\s*(?:\}|[,;]|$))",
        lambda match: match.group(1) + "^{" + match.group(2) + "}",
        value,
    )
    value = re.sub(r"(?<!\\mathrm\{)\brad\b", r"\\mathrm{rad}", value)
    value = _replace_divisions(value)
    value = _escape_operator_literal_braces(value)
    value = re.sub(r"\s+", " ", value).strip()
    value = re.sub(r"\s+([,;)}}\]])", r"\1", value)
    value = re.sub(r"([{(\[])\s+", r"\1", value)
    return value


def _markup_prose(text: str) -> str:
    output: list[str] = []
    index = 0
    while index < len(text):
        run = _consume_math_run(text, index)
        if run is None:
            output.append(text[index])
            index += 1
            continue
        value, end = run
        output.append("$" + normalize_latex(value) + "$")
        index = end
    return "".join(output)


def _markup_prose_with_answer_blanks(text: str) -> str:
    output: list[str] = []
    start = 0
    for match in _ANSWER_BLANK.finditer(text):
        output.append(_markup_prose(text[start : match.start()]))
        output.append(r"$\underline{\qquad}$")
        start = match.end()
    output.append(_markup_prose(text[start:]))
    return "".join(output)


def auto_markup_text(text: str) -> str:
    """Wrap formula-like runs and normalize their contents to LaTeX."""

    text = text.translate(_CIRCLED_ENUMERATORS)
    segments, balanced = _segments(text)
    if not balanced:
        raise ValueError("unbalanced LaTeX delimiters")
    output: list[str] = []
    for is_math, value in segments:
        if is_math:
            value = _ANSWER_BLANK.sub(
                lambda _match: r"\underline{\qquad}",
                value,
            )
            output.append("$" + normalize_latex(value) + "$")
        else:
            output.append(_markup_prose_with_answer_blanks(value))
    merged = "".join(output)
    merged = re.sub(r"(\\[A-Za-z]+)\$\$(?=[A-Za-z])", r"\1 ", merged)
    merged = merged.replace("$$", "")
    merged = re.sub(
        r"\$([^$]+?)-\$([A-Za-z])",
        lambda match: "$" + match.group(1).rstrip() + "$-" + match.group(2),
        merged,
    )
    merged = re.sub(
        r"\b(Dom|Range)\$([^$]+)\$",
        lambda match: (
            r"$\operatorname{" + match.group(1) + "}" + match.group(2) + "$"
        ),
        merged,
    )
    merged = re.sub(r"\$\s+\$", r"\\,", merged)
    canonical_segments, canonical_balanced = _segments(merged)
    if not canonical_balanced:
        raise ValueError("unbalanced LaTeX delimiters after merging math fragments")
    return "".join(
        "$" + normalize_latex(value) + "$" if is_math else value
        for is_math, value in canonical_segments
    )
