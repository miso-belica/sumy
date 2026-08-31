/** Shared helpers for handing a locally built sumy wheel to Pyodide. */

import fs from "node:fs";
import path from "node:path";

const REPOSITORY_ROOT = path.resolve(import.meta.dirname, "..", "..");

/** Resolve an explicit wheel path, or find the one `uv build --wheel` left in dist/. */
export function findWheel(explicitPath) {
  if (explicitPath) return path.resolve(explicitPath);

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

/**
 * Copy the wheel into the Emscripten filesystem and return the URL micropip installs it from.
 *
 * micropip takes a wheel only from a URL or from that filesystem ("emfs:"), and it parses the
 * file name for the package name, version and tags -- so the name has to be kept as it is.
 */
export function mountWheel(pyodide, wheel) {
  const name = path.basename(wheel);
  pyodide.FS.mkdirTree("/wheels");
  pyodide.FS.writeFile(path.join("/wheels", name), fs.readFileSync(wheel));
  return "emfs:/wheels/" + name;
}
