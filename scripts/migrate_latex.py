from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PARTS = ROOT / "content" / "parts"
sys.path.insert(0, str(ROOT))

from src.math_markup import audit_text, auto_markup_text

MANUAL_OVERRIDES = {
    "C(t)={6, 0<t≤2；6+3(t-2)=3t, 2<t≤5}。定义域为 (0,5]，值域为 [6,15]；函数单调不减，且 6≤C(t)≤15。": (
        r"$C(t)=\begin{cases}"
        r"6,&0<t\le 2,\\"
        r"3t,&2<t\le 5."
        r"\end{cases}$"
        r"定义域为 $(0,5]$，值域为 $[6,15]$；函数单调不减，且 "
        r"$6\le C(t)\le 15$。"
    ),
    "C(t)={6 for 0<t≤2; 6+3(t-2)=3t for 2<t≤5}. The domain is (0,5], the range is [6,15], C is nondecreasing, and 6≤C(t)≤15.": (
        r"$C(t)=\begin{cases}"
        r"6,&0<t\le 2,\\"
        r"3t,&2<t\le 5."
        r"\end{cases}$ "
        r"The domain is $(0,5]$, the range is $[6,15]$, $C$ is "
        r"nondecreasing, and $6\le C(t)\le 15$."
    ),
    "设 f(x)={2x+a，当 x<1；x²+1，当 x>1}。要使 lim(x→1)f(x) 存在，应有 a=______，此时极限为______。": (
        r"设 $f(x)=\begin{cases}"
        r"2x+a,&x<1,\\"
        r"x^{2}+1,&x>1."
        r"\end{cases}$ "
        r"要使 $\lim_{x\to 1}f(x)$ 存在，应有 "
        r"$a=\underline{\qquad}$，此时极限为 $\underline{\qquad}$。"
    ),
    "Let f(x)={2x+a for x<1; x²+1 for x>1}. For lim(x→1)f(x) to exist, a must equal ______, and the limit is then ______.": (
        r"Let $f(x)=\begin{cases}"
        r"2x+a,&x<1,\\"
        r"x^{2}+1,&x>1."
        r"\end{cases}$ "
        r"For $\lim_{x\to 1}f(x)$ to exist, $a$ must equal "
        r"$\underline{\qquad}$, and the limit is then $\underline{\qquad}$."
    ),
    "双侧极限存在等价于“左极限=右极限=同一有限值”。": (
        r"双侧极限存在等价于“$\text{左极限}=\text{右极限}=\text{同一有限值}$”。"
    ),
    "分段函数连接点的极限参数由“左极限=右极限”确定，与点值无关。": (
        r"分段函数连接点的极限参数由“$\text{左极限}=\text{右极限}$”确定，与点值无关。"
    ),
    "C 正确：体积的量纲为长度³，除以时间后得到长度³/时间。": (
        r"C 正确：体积的量纲为$\text{长度}^{3}$，除以时间后得到"
        r"$\frac{\text{长度}^{3}}{\text{时间}}$。"
    ),
    "C. 体积变化率 $dV/dt$ 的单位应是长度$^{3}/$时间": (
        r"C. 体积变化率 $\frac{dV}{dt}$ 的单位应是"
        r"$\frac{\text{长度}^{3}}{\text{时间}}$"
    ),
    "C. 体积变化率 dV/dt 的单位应是长度³/时间": (
        r"C. 体积变化率 $\frac{dV}{dt}$ 的单位应是"
        r"$\frac{\text{长度}^{3}}{\text{时间}}$"
    ),
    "C. The unit of $dV/dt$ is length$^{3}/$time": (
        r"C. The unit of $\frac{dV}{dt}$ is "
        r"$\frac{\mathrm{length}^{3}}{\mathrm{time}}$"
    ),
    "C. The unit of dV/dt is length³/time": (
        r"C. The unit of $\frac{dV}{dt}$ is "
        r"$\frac{\mathrm{length}^{3}}{\mathrm{time}}$"
    ),
    "C is correct because volume has dimension length$^{3}$, so its rate has dimension length$^{3}/$time.": (
        r"C is correct because volume has dimension $\mathrm{length}^{3}$, "
        r"so its rate has dimension $\frac{\mathrm{length}^{3}}{\mathrm{time}}$."
    ),
    "C is correct because volume has dimension length³, so its rate has dimension length³/time.": (
        r"C is correct because volume has dimension $\mathrm{length}^{3}$, "
        r"so its rate has dimension $\frac{\mathrm{length}^{3}}{\mathrm{time}}$."
    ),
    "|dA|≈0.4π cm²；|dA|/A≈0.004=0.4%。": (
        r"$|dA|\approx 0.4\pi\ \mathrm{cm}^{2}$；"
        r"$\frac{|dA|}{A}\approx 0.004=0.4\%$。"
    ),
    "若 α>1，则 |sgn(h)|h|^{α-1}|=|h|^{α-1}→0，所以双侧极限存在且 f′_α(0)=0。": (
        r"若 $\alpha>1$，则 "
        r"$\left|\operatorname{sgn}(h)\,|h|^{\alpha-1}\right|"
        r"=|h|^{\alpha-1}\to 0$，所以双侧极限存在且 "
        r"$f'_{\alpha}(0)=0$。"
    ),
    "设 f(x)={x², x≤1; ax+b, x>1}。求 a,b，使 f 在 x=1 处可导，并求 f′(1)。": (
        r"设 $f(x)=\begin{cases}"
        r"x^{2},&x\le 1,\\"
        r"ax+b,&x>1."
        r"\end{cases}$ "
        r"求 $a,b$，使 $f$ 在 $x=1$ 处可导，并求 $f'(1)$。"
    ),
    "Let f(x)={x², x≤1; ax+b, x>1}. Find a,b so that f is differentiable at x=1, and find f′(1).": (
        r"Let $f(x)=\begin{cases}"
        r"x^{2},&x\le 1,\\"
        r"ax+b,&x>1."
        r"\end{cases}$ "
        r"Find $a,b$ so that $f$ is differentiable at $x=1$, and find $f'(1)$."
    ),
    "设 f(x)={x²sin(1/x), x≠0; 0, x=0}。判断 f 在 0 处是否可导，并求完整的导函数 f′(x)。": (
        r"设 $f(x)=\begin{cases}"
        r"x^{2}\sin\!\left(\frac{1}{x}\right),&x\ne 0,\\"
        r"0,&x=0."
        r"\end{cases}$ "
        r"判断 $f$ 在 0 处是否可导，并求完整的导函数 $f'(x)$。"
    ),
    "Let f(x)={x²sin(1/x), x≠0; 0, x=0}. Decide whether f is differentiable at 0, and find the complete derivative f′(x).": (
        r"Let $f(x)=\begin{cases}"
        r"x^{2}\sin\!\left(\frac{1}{x}\right),&x\ne 0,\\"
        r"0,&x=0."
        r"\end{cases}$ "
        r"Decide whether $f$ is differentiable at 0, and find the complete derivative $f'(x)$."
    ),
    "设 f(x)={x²sin(1/x²), x≠0; 0, x=0}。(1) 证明 f 在 0 连续；(2) 证明 f 在 0 可导并写出原点切线；(3) 求 x≠0 时的 f′(x)；(4) 构造 x_n→0⁺，说明 f′(x) 在 0 不连续。": (
        r"设 $f(x)=\begin{cases}"
        r"x^{2}\sin\!\left(\frac{1}{x^{2}}\right),&x\ne 0,\\"
        r"0,&x=0."
        r"\end{cases}$ "
        r"(1) 证明 $f$ 在 0 连续；(2) 证明 $f$ 在 0 可导并写出原点切线；"
        r"(3) 求 $x\ne 0$ 时的 $f'(x)$；(4) 构造 $x_n\to 0^{+}$，"
        r"说明 $f'(x)$ 在 0 不连续。"
    ),
    "Let f(x)={x²sin(1/x²), x≠0; 0, x=0}. (1) Prove continuity at 0. (2) Prove differentiability at 0 and write the tangent there. (3) Find f′(x) for x≠0. (4) Construct x_n→0⁺ showing that f′ is not continuous at 0.": (
        r"Let $f(x)=\begin{cases}"
        r"x^{2}\sin\!\left(\frac{1}{x^{2}}\right),&x\ne 0,\\"
        r"0,&x=0."
        r"\end{cases}$ "
        r"(1) Prove continuity at 0. (2) Prove differentiability at 0 and write "
        r"the tangent there. (3) Find $f'(x)$ for $x\ne 0$. "
        r"(4) Construct $x_n\to 0^{+}$ showing that $f'$ is not continuous at 0."
    ),
    "设 α,β>0，且 f_{α,β}(x)={|x|^α sin(1/|x|^β), x≠0; 0, x=0}。(1) 证明 f_{α,β} 在 0 连续；(2) 完整判定它在 0 可导的充要条件；(3) 在可导情形下，完整判定 f′_{α,β} 在 0 连续的充要条件。": (
        r"设 $\alpha,\beta>0$，且 "
        r"$f_{\alpha,\beta}(x)=\begin{cases}"
        r"|x|^{\alpha}\sin\!\left(\frac{1}{|x|^{\beta}}\right),&x\ne 0,\\"
        r"0,&x=0."
        r"\end{cases}$ "
        r"(1) 证明 $f_{\alpha,\beta}$ 在 0 连续；"
        r"(2) 完整判定它在 0 可导的充要条件；"
        r"(3) 在可导情形下，完整判定 $f'_{\alpha,\beta}$ 在 0 连续的充要条件。"
    ),
    "Let α,β>0 and f_{α,β}(x)={|x|^α sin(1/|x|^β), x≠0; 0, x=0}. (1) Prove that f_{α,β} is continuous at 0. (2) Completely classify differentiability at 0. (3) When it is differentiable, completely classify continuity of f′_{α,β} at 0.": (
        r"Let $\alpha,\beta>0$ and "
        r"$f_{\alpha,\beta}(x)=\begin{cases}"
        r"|x|^{\alpha}\sin\!\left(\frac{1}{|x|^{\beta}}\right),&x\ne 0,\\"
        r"0,&x=0."
        r"\end{cases}$ "
        r"(1) Prove that $f_{\alpha,\beta}$ is continuous at 0. "
        r"(2) Completely classify differentiability at 0. "
        r"(3) When it is differentiable, completely classify continuity of "
        r"$f'_{\alpha,\beta}$ at 0."
    ),
    "设 f(x)={ax+b，x<1；x²+1，x≥1}。要使 f 在 x=1 处可导，应有 a=________，b=________。": (
        r"设 $f(x)=\begin{cases}"
        r"ax+b,&x<1,\\"
        r"x^{2}+1,&x\ge 1."
        r"\end{cases}$ "
        r"要使 $f$ 在 $x=1$ 处可导，应有 "
        r"$a=\underline{\qquad}$，$b=\underline{\qquad}$。"
    ),
    "Let f(x)={ax+b for x<1; x²+1 for x≥1}. For f to be differentiable at x=1, a=________ and b=________.": (
        r"Let $f(x)=\begin{cases}"
        r"ax+b,&x<1,\\"
        r"x^{2}+1,&x\ge 1."
        r"\end{cases}$ "
        r"For $f$ to be differentiable at $x=1$, "
        r"$a=\underline{\qquad}$ and $b=\underline{\qquad}$."
    ),
    "设 f(x)={x²+ax+b，x<1；c ln x+2，x≥1}。求所有使 f 在 x=1 处可导的实参数三元组 (a,b,c)，并写出此时 f′(1)。": (
        r"设 $f(x)=\begin{cases}"
        r"x^{2}+ax+b,&x<1,\\"
        r"c\ln x+2,&x\ge 1."
        r"\end{cases}$ "
        r"求所有使 $f$ 在 $x=1$ 处可导的实参数三元组 $(a,b,c)$，"
        r"并写出此时 $f'(1)$。"
    ),
    "Let f(x)={x²+ax+b for x<1; c ln x+2 for x≥1}. Find all real triples (a,b,c) for which f is differentiable at x=1, and give f′(1).": (
        r"Let $f(x)=\begin{cases}"
        r"x^{2}+ax+b,&x<1,\\"
        r"c\ln x+2,&x\ge 1."
        r"\end{cases}$ "
        r"Find all real triples $(a,b,c)$ for which $f$ is differentiable at "
        r"$x=1$, and give $f'(1)$."
    ),
    "在 r=10 cm 且 |dr|≤0.02 cm 时，|dA|≈2π·10·0.02=0.4π cm²。": (
        r"在 $r=10\ \mathrm{cm}$ 且 $|dr|\le 0.02\ \mathrm{cm}$ 时，"
        r"$|dA|\approx 2\pi\cdot 10\cdot 0.02=0.4\pi\ \mathrm{cm}^{2}$。"
    ),
    "量纲 2πrdr 为 cm²；相对误差无单位。半径相对误差为 0.2%，面积约为其 2 倍，即 0.4%。": (
        r"量纲 $2\pi r\,dr$ 为 $\mathrm{cm}^{2}$；相对误差无单位。"
        r"半径相对误差为 $0.2\%$，面积约为其 2 倍，即 $0.4\%$。"
    ),
    "At r=10 cm with |dr|≤0.02 cm, |dA|≈2π·10·0.02=0.4π cm².": (
        r"At $r=10\ \mathrm{cm}$ with $|dr|\le 0.02\ \mathrm{cm}$, "
        r"$|dA|\approx 2\pi\cdot 10\cdot 0.02=0.4\pi\ \mathrm{cm}^{2}$."
    ),
    "Using cm instead of cm²": r"using $\mathrm{cm}$ instead of $\mathrm{cm}^{2}$",
}


def _normalize_notation_labels(value: str) -> str:
    value = value.replace("epsilon$-N$", r"$\varepsilon$-$N$")
    value = value.replace("epsilon-N", r"$\varepsilon$-$N$")
    value = value.replace(r"$\varepsilon -N$", r"$\varepsilon$-$N$")
    value = value.replace(r"$\varepsilon-N$", r"$\varepsilon$-$N$")
    return value


def _convert(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _convert(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_convert(item) for item in value]
    if not isinstance(value, str):
        return value
    if value in MANUAL_OVERRIDES:
        converted = MANUAL_OVERRIDES[value]
    else:
        converted = auto_markup_text(value)
    return _normalize_notation_labels(converted)


def _localized_payload(question: dict[str, Any]) -> dict[str, Any]:
    question = dict(question)
    question["zh"] = _convert(question["zh"])
    question["en"] = _convert(question["en"])
    question["tags"] = _convert(question["tags"])
    if "source_lineage" in question:
        lineage = dict(question["source_lineage"])
        lineage["method_family"] = _convert(lineage["method_family"])
        lineage["relation"] = _convert(lineage["relation"])
        lineage["references"] = [
            reference.replace("$", "")
            for reference in lineage["references"]
        ]
        question["source_lineage"] = lineage
    return question


def migrate(path: Path) -> list[dict[str, Any]]:
    items = json.loads(path.read_text(encoding="utf-8"))
    return [_localized_payload(item) for item in items]


def _audit(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            _audit(item, f"{path}.{key}", errors)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _audit(item, f"{path}[{index}]", errors)
    elif isinstance(value, str):
        for message in audit_text(value):
            errors.append(f"{path}: {message}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="rewrite part files in place")
    args = parser.parse_args()

    errors: list[str] = []
    changed = 0
    for path in sorted(PARTS.glob("*.json")):
        before = json.loads(path.read_text(encoding="utf-8"))
        after = [_localized_payload(item) for item in before]
        changed += int(before != after)
        for item in after:
            _audit(item["zh"], f"{item['id']}.zh", errors)
            _audit(item["en"], f"{item['id']}.en", errors)
            _audit(item["tags"], f"{item['id']}.tags", errors)
            if "source_lineage" in item:
                _audit(
                    item["source_lineage"],
                    f"{item['id']}.source_lineage",
                    errors,
                )
        if args.write and before != after:
            path.write_text(
                json.dumps(after, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

    if errors:
        print("\n".join(errors))
        return 1
    mode = "rewritten" if args.write else "would change"
    print(f"LaTeX migration audit passed; {changed} part files {mode}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
