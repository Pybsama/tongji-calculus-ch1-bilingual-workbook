# 同济高数第七版第一章双语习题册

[English README](README.md)

这是一套面向 Goodnotes 的双语学习资料，范围与同济大学《高等数学》第七版上册第一章“函数与极限”对齐。

## 成品下载

- [中文版习题册](dist/同济高数第七版_第一章_习题册_中文.pdf)
- [中文版超详细解析](dist/同济高数第七版_第一章_超详细解析_中文.pdf)
- [English Exercise Workbook](dist/Tongji_Calculus_7e_Chapter_1_Exercises_EN.pdf)
- [English Detailed Solutions](dist/Tongji_Calculus_7e_Chapter_1_Detailed_Solutions_EN.pdf)
- [SHA-256 校验值](SHA256SUMS)

校验值用于核对仓库中已发布的 PDF。构建过程固定源时间、每次清理独立构建目录，
并锁定 Tectonic bundle，可进一步检查连续两次构建是否逐字节一致。

## 内容构成

- 100 道题，由基础逐步过渡到挑战。
- 覆盖第一章十节，包括 2 道明确标为选做的一致连续性拓展题。
- 题型包括单选、多选、判断辨析、填空、计算、证明、参数/综合/应用和错解诊断。
- 每题解析包含知识点、审题与方法选择、逐步推导、易错点、检验、方法总结和变式提示。
- 题目和解析中的数学内容均使用显式 LaTeX 源码；每个公式片段先由锁定的 KaTeX 0.17.0 严格解析，再由 XeTeX 与 STIX Two Math 编译进 PDF。迁移审计会拒绝 Unicode 数学快捷符号和斜杠除法。
- 题源谱系可审计：20 道开放教材方法改写、37 道经典方法变式、43 道原创综合/诊断。
- 四份 PDF 使用完全一致的 Q001-Q100 编号。
- 习题册采用 4:3 横版，便于在 Goodnotes 中边看题边书写；解析册采用 4:3 竖版，适合连续阅读。

## 范围边界

整套题只使用第一章方法，不使用导数、洛必达法则、泰勒公式或幂级数。

谱系标注严格区分“开放教材方法改写”“经典方法变式”和“原创综合/诊断”。
这些标签说明方法传统，不声称逐字来自某本书；题干、参数和解析均独立编写，
商业教材只用于核对章节范围。

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

经过验证的构建环境使用 Python 3.12+、Node.js 20+、KaTeX 0.17.0、
精确版本 Tectonic 0.16.9 和锁定的
`default_bundle_v33`。中文、正文与数学分别使用 bundle 内的 Fandol、TeX Gyre
Heros 和 STIX Two Math 开源字体，不依赖 macOS 系统字体。所有页面通过
`pypdfium2` 调用 PDFium 做渲染烟雾检查（尺寸、非空、触边和异常稀疏页）；
公式语义由逐题审计与 KaTeX 严格解析负责，代表性高密度公式页另做人工目视检查。

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
npm ci
# 安装精确版本 Tectonic 0.16.9，或通过 TECTONIC 指向该版本
python scripts/merge_corpus.py
python scripts/migrate_latex.py  # 只审计，必须报告 0 个变更
python scripts/validate_content.py
pytest -q
npm run validate:katex  # 对题目和解析中的每个公式做严格 KaTeX 解析
python scripts/build_pdfs.py
python scripts/verify_reproducible.py
python scripts/update_checksums.py
python scripts/validate_pdfs.py
python scripts/render_validate.py  # 用 PDFium 渲染并检查每一页
```

可编辑的创作源文件位于 [`content/parts`](content/parts)。
`scripts/merge_corpus.py` 会将它们合并为规范语料
[`content/questions.json`](content/questions.json)，四份 PDF 均由该合并语料生成。

## 声明

本项目是独立编写的学习资料，不是同济大学或高等教育出版社的官方出版物，与二者不存在隶属或合作关系。逐题谱系规则和公开方法来源见 [SOURCES.md](SOURCES.md)，排版工具与字体许可见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

原创内容的使用条件见 [LICENSE](LICENSE)。
CC BY-NC-SA 4.0 允许非商业分享与改编；由于包含“非商业”限制，本仓库准确地说是
公开源代码/源文件（source-available），并不是 OSI 定义下的开源软件。
