/**
 * Runs the browser demo's own loader against a real Pyodide runtime.
 *
 * docs/demo/sumy-browser.mjs is the module the demo page uses; nothing in it is
 * browser-specific, so the same code can be driven from node. This is the test for it: if
 * summarizing text through Pyodide breaks, this fails in CI instead of in the page.
 *
 * Usage: node check-demo.mjs [path/to/sumy-*.whl]
 */

import path from "node:path";
import process from "node:process";
import { loadPyodide } from "pyodide";

import { loadSumy, summarize } from "../../docs/demo/sumy-browser.mjs";
import { findWheel, mountWheel } from "./wheel.mjs";

const TEXT = `
Automatic summarization is the process of shortening a text document with software.
It creates a summary with the most important points of the original document.
Technologies that can make a coherent summary take into account variables such as length,
writing style and syntax. Extractive summarization picks whole sentences from the source.
Abstractive summarization instead writes sentences that may not appear in the source at all.
`;

async function main() {
  const wheel = findWheel(process.argv[2]);
  const pyodide = await loadPyodide();
  const wheelUrl = mountWheel(pyodide, wheel);

  await loadSumy(pyodide, { wheel: wheelUrl });

  const sentences = summarize(pyodide, {
    text: TEXT,
    language: "english",
    method: "lsa",
    sentenceCount: 2,
  });

  if (sentences.length !== 2) {
    throw new Error(`Expected 2 sentences, got ${sentences.length}: ${JSON.stringify(sentences)}`);
  }
  // Extractive summarization returns sentences of the document verbatim, except that the
  // tokenizer joins the lines they were wrapped over.
  const document = TEXT.replace(/\s+/g, " ");
  for (const sentence of sentences) {
    if (!document.includes(sentence.replace(/\s+/g, " "))) {
      throw new Error(`Summary sentence is not part of the document: ${sentence}`);
    }
  }

  console.log(`${path.basename(wheel)} summarizes under Pyodide ${pyodide.version}:`);
  for (const sentence of sentences) console.log("  * " + sentence);
}

try {
  await main();
} catch (error) {
  console.error(error.message);
  process.exit(1);
}
