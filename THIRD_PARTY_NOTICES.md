# Third-party typesetting notices

The repository does not commit font binaries or a TeX bundle. Reproducible
builds use [Tectonic](https://github.com/tectonic-typesetting/tectonic) with
the pinned `default_bundle_v33`; generated PDFs embed subset fonts as permitted
by their upstream licenses.

## Fonts embedded in generated PDFs

- **Fandol Song / Fandol Hei** — Chinese text; distributed under the GNU GPL
  with the font embedding exception. See the
  [CTAN Fandol package](https://ctan.org/pkg/fandol).
- **TeX Gyre Heros** — Latin text; distributed under the GUST Font License.
  See the [CTAN TeX Gyre package](https://ctan.org/pkg/tex-gyre).
- **STIX Two Math** — mathematics; distributed under the SIL Open Font
  License 1.1. See the
  [STIX Fonts repository](https://github.com/stipub/stixfonts).

## Build and validation tools

- **Tectonic / XeTeX-compatible engine** compiles the LaTeX sources. Upstream
  license terms are in the
  [Tectonic repository](https://github.com/tectonic-typesetting/tectonic).
- **KaTeX 0.17.0** and its **Commander** CLI dependency are used only to
  validate that every delimited formula belongs to the supported KaTeX
  syntax. Both are distributed under the MIT License; see the
  [KaTeX repository](https://github.com/KaTeX/KaTeX).
- **pypdf**, **pypdfium2/PDFium**, **Pillow**, and **pytest** are development
  and validation dependencies. Their packages retain their respective
  upstream licenses; they are not incorporated into the workbook content.

The workbook's own license is in [LICENSE](LICENSE).
