# Scope references, method lineage, and attribution

## What the lineage metadata means

Every question contains a `source_lineage` object with four fields:

- `category`: one of `open_text_adaptation`, `classic_method_variant`, or
  `original_synthesis`;
- `method_family`: the mathematical method or concept being trained;
- `relation`: a plain-language statement of the question's relationship to
  its references;
- `references`: one or more identifiers from the public-source registry below.

`open_text_adaptation` means that an openly available source displays the same
general exposition or exercise pattern. Constants, wording, prompts, and
solutions in this workbook were independently rewritten.

`classic_method_variant` means that the item is an independently authored
variant of a widely taught method. Its references document the method family;
they are not asserted to be the source of the exact question.

`original_synthesis` means that the item combines concepts, proof moves,
counterexamples, or applications specifically for this workbook. Its
references are background reading, not source problems.

No lineage category claims verbatim reproduction. The metadata does not claim
that an item came from Tongji, Stewart, Thomas, or another proprietary
textbook.

## Public method-reference registry

The following stable identifiers are used in `content/parts/*.json` and the
merged `content/questions.json`:

- `openstax-v1-1.1-functions` — OpenStax, *Calculus Volume 1*,
  [1.1 Review of Functions](https://openstax.org/books/calculus-volume-1/pages/1-1-review-of-functions)
- `openstax-v1-1.4-inverse-functions` — OpenStax, *Calculus Volume 1*,
  [1.4 Inverse Functions](https://openstax.org/books/calculus-volume-1/pages/1-4-inverse-functions)
- `openstax-v1-2.2-function-limits` — OpenStax, *Calculus Volume 1*,
  [2.2 The Limit of a Function](https://openstax.org/books/calculus-volume-1/pages/2-2-the-limit-of-a-function)
- `openstax-v1-2.3-limit-laws` — OpenStax, *Calculus Volume 1*,
  [2.3 The Limit Laws](https://openstax.org/books/calculus-volume-1/pages/2-3-the-limit-laws)
- `openstax-v1-2.4-continuity` — OpenStax, *Calculus Volume 1*,
  [2.4 Continuity](https://openstax.org/books/calculus-volume-1/pages/2-4-continuity)
- `openstax-v1-2.5-precise-limit` — OpenStax, *Calculus Volume 1*,
  [2.5 The Precise Definition of a Limit](https://openstax.org/books/calculus-volume-1/pages/2-5-the-precise-definition-of-a-limit)
- `openstax-v1-4.3-extrema` — OpenStax, *Calculus Volume 1*,
  [4.3 Maxima and Minima](https://openstax.org/books/calculus-volume-1/pages/4-3-maxima-and-minima)
- `openstax-v2-5.1-sequences` — OpenStax, *Calculus Volume 2*,
  [5.1 Sequences](https://openstax.org/books/calculus-volume-2/pages/5-1-sequences)
- `mit-18.01sc-session-4-limits-continuity` — MIT OpenCourseWare 18.01SC,
  [Session 4: Limits and Continuity](https://ocw.mit.edu/courses/18-01sc-single-variable-calculus-fall-2010/pages/1.-differentiation/part-a-definition-and-basic-rules/session-4-limits-and-continuity/)
- `mit-18.01sc-session-5-discontinuity` — MIT OpenCourseWare 18.01SC,
  [Session 5: Discontinuity](https://ocw.mit.edu/courses/18-01sc-single-variable-calculus-fall-2010/pages/1.-differentiation/part-a-definition-and-basic-rules/session-5-discontinuity/)
- `mit-18.01sc-session-8-trig-limits` — MIT OpenCourseWare 18.01SC,
  [Session 8: Limits of Sine and Cosine](https://ocw.mit.edu/courses/18-01sc-single-variable-calculus-fall-2010/pages/1.-differentiation/part-a-definition-and-basic-rules/session-8-limits-of-sine-and-cosine/)
- `mit-18.01sc-session-19-limit-involving-e` — MIT OpenCourseWare
  18.01SC,
  [Session 19: An Interesting Limit Involving e](https://ocw.mit.edu/courses/18-01sc-single-variable-calculus-fall-2010/pages/1.-differentiation/part-b-implicit-differentiation-and-inverse-functions/session-19-an-interesting-limit-involving-e/)

OpenStax states the applicable licensing and attribution terms in its
[Calculus Volume 1 preface](https://openstax.org/books/calculus-volume-1/pages/preface).
This workbook cites public concepts and method patterns and does not reproduce
OpenStax problem statements verbatim.

## Scope-only references

The following pages are used only to verify edition metadata, Chapter 1
structure, and course scope. They are not used as per-question lineage claims:

- Higher Education Press, *Advanced Mathematics (7th edition), Volume I*:  
  <https://www.hep.com.cn/book/show/f9a5ba29-e58e-4a42-9c1b-830a0e28f1f3>
- Higher Education Press, companion learning guide for the seventh edition:  
  <https://xuanshu.hep.com.cn/front/book/findBookDetails?bookId=59cdd60dba9eb884cf81c6dc>
- Tongji University, Advanced Mathematics synchronous course, Chapter 1:  
  <https://gaoshutongbu.tongji.edu.cn/kcyx/dyz_hsyjx.htm>
- Tongji University, description of supplementary examples and exercise
  resources:
  <https://gaoshutongbu.tongji.edu.cn/gywz.htm>

“Tongji University,” “Higher Education Press,” and the textbook title are used
descriptively to identify the study scope. This repository is unofficial and
unaffiliated.
