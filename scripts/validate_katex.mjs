import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import katex from "katex";


const expectedKatexVersion = "0.17.0";
if (katex.version !== expectedKatexVersion) {
  throw new Error(
    `KaTeX ${expectedKatexVersion} is required; found ${katex.version ?? "unknown"}.`
  );
}

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const corpusPath = path.join(root, "content", "questions.json");
const reportPath = path.join(root, "reports", "katex_validation.md");


function mathSegments(value) {
  const segments = [];
  let start = 0;
  let inMath = false;
  for (let index = 0; index < value.length; index += 1) {
    if (value[index] !== "$" || (index > 0 && value[index - 1] === "\\")) {
      continue;
    }
    if (inMath) {
      segments.push(value.slice(start, index));
    }
    inMath = !inMath;
    start = index + 1;
  }
  if (inMath) {
    throw new Error("unbalanced $ delimiters");
  }
  return segments;
}


function* walkStrings(value, fieldPath = "root") {
  if (typeof value === "string") {
    yield [fieldPath, value];
    return;
  }
  if (Array.isArray(value)) {
    for (let index = 0; index < value.length; index += 1) {
      yield* walkStrings(value[index], `${fieldPath}[${index}]`);
    }
    return;
  }
  if (value !== null && typeof value === "object") {
    for (const [key, child] of Object.entries(value)) {
      yield* walkStrings(child, `${fieldPath}.${key}`);
    }
  }
}


const questions = JSON.parse(fs.readFileSync(corpusPath, "utf8"));
const errors = [];
let formulaCount = 0;
const uniqueFormulas = new Set();

for (const question of questions) {
  for (const [fieldPath, value] of walkStrings(question, question.id)) {
    let formulas;
    try {
      formulas = mathSegments(value);
    } catch (error) {
      errors.push(`${fieldPath}: ${error.message}`);
      continue;
    }
    for (let index = 0; index < formulas.length; index += 1) {
      const formula = formulas[index];
      formulaCount += 1;
      uniqueFormulas.add(formula);
      if (formula.trim() === "") {
        errors.push(`${fieldPath} formula ${index + 1}: empty formula`);
        continue;
      }
      try {
        const rendered = katex.renderToString(formula, {
          displayMode: false,
          output: "htmlAndMathml",
          strict: "error",
          throwOnError: true,
          trust: false
        });
        if (!rendered.includes('class="katex"') || rendered.includes("katex-error")) {
          errors.push(`${fieldPath} formula ${index + 1}: KaTeX returned error markup`);
        }
      } catch (error) {
        errors.push(
          `${fieldPath} formula ${index + 1}: ${error.name}: ${error.message}; source=${JSON.stringify(formula)}`
        );
      }
    }
  }
}

const report = [
  "# KaTeX compatibility validation",
  "",
  `- KaTeX version: \`${katex.version}\``,
  `- Questions checked: ${questions.length}`,
  `- Formula occurrences checked: ${formulaCount}`,
  `- Unique formulas checked: ${uniqueFormulas.size}`,
  `- Parse errors: ${errors.length}`,
  "- Options: `throwOnError=true`, `strict=error`, `trust=false`, `output=htmlAndMathml`",
  "",
  "## Errors",
  "",
  ...(errors.length === 0 ? ["- None"] : errors.map((error) => `- ${error}`)),
  ""
].join("\n");
fs.writeFileSync(reportPath, report, "utf8");

if (errors.length > 0) {
  process.stderr.write(`${errors.join("\n")}\n`);
  process.exitCode = 1;
} else {
  process.stdout.write(
    `KaTeX ${katex.version} parsed ${formulaCount} formula occurrences (${uniqueFormulas.size} unique) with zero errors.\n`
  );
}
