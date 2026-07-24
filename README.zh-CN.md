# 同济高数第七版第一章双语习题册

[English README](README.md)

这是一套面向 Goodnotes 的双语学习资料，范围与同济大学《高等数学》第七版上册第一章“函数与极限”对齐。

## 成品下载

- [中文版习题册](dist/同济高数第七版_第一章_习题册_中文.pdf)
- [中文版超详细解析](dist/同济高数第七版_第一章_超详细解析_中文.pdf)
- [English Exercise Workbook](dist/Tongji_Calculus_7e_Chapter_1_Exercises_EN.pdf)
- [English Detailed Solutions](dist/Tongji_Calculus_7e_Chapter_1_Detailed_Solutions_EN.pdf)
- [SHA-256 校验值](SHA256SUMS)

校验值用于核对仓库中已发布的 PDF。本地重新生成后，内容与版式仍可验证一致，但
PDF 时间戳和 trailer ID 会使文件级哈希发生变化。

## 内容构成

- 100 道题，由基础逐步过渡到挑战。
- 覆盖第一章十节，包括 2 道明确标为选做的一致连续性拓展题。
- 题型包括单选、多选、判断辨析、填空、计算、证明、参数/综合/应用和错解诊断。
- 每题解析包含知识点、审题与方法选择、逐步推导、易错点、检验、方法总结和变式提示。
- 四份 PDF 使用完全一致的 Q001-Q100 编号。
- 习题册采用 4:3 横版，便于在 Goodnotes 中边看题边书写；解析册采用 4:3 竖版，适合连续阅读。

## 范围边界

整套题只使用第一章方法，不使用导数、洛必达法则、泰勒公式或幂级数。

标记为“教材经典方法变式”的题目只保留代表性解题思想，并重新设计函数结构、参数、趋近过程或问法；没有逐字复制教材例题或习题。

## 推荐训练方法

1. 按“基础篇—方法篇—综合篇—挑战篇”依次完成。
2. 第一次作答不要打开解析册。
3. 订正时把错误归类为概念、代数、方法选择或书写严谨性。
4. 48 小时后重新完成错题。
5. 一周后按照知识点标签抽题，不再按原顺序机械重做。

## 优点与局限

这套题兼顾概念、计算、证明、参数、反例和错解诊断，而不是重复同一种代数变形；困难题也严格守在第一章工具范围内。

100 道题无法穷尽所有极限变形，难度判断也会受到个人代数基础影响。静态 PDF 不能自动根据错题调整训练。一致连续性属于教材星号拓展内容，课堂未讲时可以先跳过。

## 本地生成

经过验证的构建环境使用 Python 3.12 或更高版本；当前以 macOS 为目标，因为中文排版使用
系统自带字体。请先安装 `requirements.txt` 中的 Python 依赖。若要执行完整的
逐页图片质检，还需安装 Poppler；仅生成 PDF 和做结构校验不需要它。

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/merge_corpus.py
python scripts/validate_content.py
python scripts/build_pdfs.py
python scripts/validate_pdfs.py
python scripts/render_validate.py  # 可选：完整逐页图片质检
pytest -q
```

可编辑的创作源文件位于 [`content/parts`](content/parts)。
`scripts/merge_corpus.py` 会将它们合并为规范语料
[`content/questions.json`](content/questions.json)，四份 PDF 均由该合并语料生成。

## 声明

本项目是独立编写的学习资料，不是同济大学或高等教育出版社的官方出版物，与二者不存在隶属或合作关系。范围核对来源见 [SOURCES.md](SOURCES.md)。

原创内容的使用条件见 [LICENSE](LICENSE)。
CC BY-NC-SA 4.0 允许非商业分享与改编；由于包含“非商业”限制，本仓库准确地说是
公开源代码/源文件（source-available），并不是 OSI 定义下的开源软件。
