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

import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { loadPyodide } from "pyodide";

const REPOSITORY_ROOT = path.resolve(import.meta.dirname, "..", "..");

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

function findWheel() {
  if (process.argv[2]) return path.resolve(process.argv[2]);

  const distribution = path.join(REPOSITORY_ROOT, "dist");
  const wheels = fs.existsSync(distribution)
    ? fs.readdirSync(distribution).filter((name) => name.startsWith("sumy-") && name.endsWith(".whl"))
    : [];
  if (wheels.length !== 1) {
    throw new Error(
      `Expected exactly one sumy wheel in ${distribution}, found ${wheels.length}. ` +
        "Run `uv build --wheel` first or pass the wheel path as an argument.",
    );
  }
  return path.join(distribution, wheels[0]);
}

async function main() {
  const wheel = findWheel();
  const pyodide = await loadPyodide();

  // micropip only accepts a wheel from a URL or from the Emscripten filesystem ("emfs:"),
  // and it parses the file name, so the name on that filesystem has to be kept.
  pyodide.FS.mkdirTree("/wheels");
  pyodide.FS.writeFile(path.join("/wheels", path.basename(wheel)), fs.readFileSync(wheel));

  await pyodide.loadPackage("micropip");
  const micropip = pyodide.pyimport("micropip");
  await micropip.install("emfs:/wheels/" + path.basename(wheel));

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
