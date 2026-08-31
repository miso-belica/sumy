# Setup

sumy uses [uv](https://docs.astral.sh/uv/). Install the development environment with the language
extras so the tokenizer tests can run:

```sh
$ uv sync --all-extras
$ uv run pytest
```

Some tests need optional dependencies (`numpy`, `jieba`, `tinysegmenter`) and NLTK data. If they
fail before you change anything, that is an environment problem, not a regression.

## Checking the browser build

sumy is also published for Pyodide, so a change to the dependency list or to a module-level
import can break it in the browser without touching pytest. The checks run in node against a
real Pyodide runtime (node 20.11+):

```sh
$ uv build --wheel
$ cd tools/wasm && npm ci && cd -
$ node tools/wasm/check-wheel.mjs   # wheel installs, every module imports
$ node tools/wasm/check-demo.mjs    # a document really gets summarized
```

See @docs/in-the-browser.md for what does and does not work there.

## Always practice red/green TDD

Every behavioral change starts with a test that fails for the right reason.

1. **RED** — write one test that expresses the behaviour you want, or that reproduces the bug
   through the public interface. Run it and read the failure. A test that passes on the first run,
   or fails with an unrelated error such as `ImportError`, proves nothing yet.
2. **GREEN** — write the smallest change that makes it pass, then run the tests again.
3. **REFACTOR** — clean up only once the tests are green. Never refactor while red.

Work in vertical slices: one test, then the code for it, then the next test. Do not write a batch
of tests up front and implement them all afterwards. Ask and wait for review and commit after every
minimal change.

## Update the CHANGELOG for every change worth mentioning

Add a line to the `## Unreleased` section of @CHANGELOG.md for anything an end user
could notice: bug fixes, new features, new languages, dependency and support changes. Follow the
existing style and prefixes.

Purely internal work with no observable effect — a refactor, a typo in a comment, test-only
changes — does not need an entry.
