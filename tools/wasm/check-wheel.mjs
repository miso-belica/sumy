/**
 * Installs the sumy wheel into a real Pyodide runtime and imports it.
 *
 * PEP 783 lets PyPI serve wheels for the PyEmscripten platform, and micropip installs them
 * straight from PyPI. sumy is pure Python, so its `py3-none-any` wheel is already the artifact
 * a browser needs -- what actually has to hold is that every dependency sumy declares *for
 * Emscripten* can be resolved and imported there. This checks exactly that, so a release
 * cannot silently stop being installable in the browser.
 *
 * Usage: node check-wheel.mjs [path/to/sumy-*.whl]
 */

import path from "node:path";
import process from "node:process";
import { loadPyodide } from "pyodide";

import { findWheel, mountWheel } from "./wheel.mjs";

// Imported in a browser without breadability (docopt has no wheel) or requests (no sockets),
// so these must not reach for either at import time.
const REQUIRED_MODULES = [
  "sumy.utils",
  "sumy.nlp.tokenizers",
  "sumy.nlp.stemmers",
  "sumy.parsers.plaintext",
  "sumy.parsers.html",
  "sumy.summarizers.luhn",
  "sumy.summarizers.lsa",
  "sumy.summarizers.lex_rank",
  "sumy.summarizers.text_rank",
];

async function main() {
  const wheel = findWheel(process.argv[2]);
  const pyodide = await loadPyodide();
  const wheelUrl = mountWheel(pyodide, wheel);

  await pyodide.loadPackage("micropip");
  const micropip = pyodide.pyimport("micropip");
  await micropip.install(wheelUrl);

  const failures = pyodide.runPython(`
import importlib

failures = []
for name in ${JSON.stringify(REQUIRED_MODULES)}:
    try:
        importlib.import_module(name)
    except Exception as error:
        failures.append(f"{name}: {type(error).__name__}: {error}")

failures
`).toJs();

  if (failures.length) {
    throw new Error("Modules that do not import under Pyodide:\n  " + failures.join("\n  "));
  }

  console.log(`${path.basename(wheel)} installs and imports under Pyodide ${pyodide.version}.`);
}

// Reported by hand: an unhandled rejection from inside Pyodide dumps the whole
// pyodide.asm.mjs source into the log, which buries the actual message.
try {
  await main();
} catch (error) {
  console.error(error.message);
  process.exit(1);
}
