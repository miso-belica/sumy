# Running sumy in the browser

There is a live demo at **<https://miso-belica.github.io/sumy/demo/>**. It downloads sumy from
PyPI into your browser and summarizes text there; no text ever leaves the tab.

## How it works

[PEP 783](https://peps.python.org/pep-0783/) defines the *PyEmscripten* platform and lets PyPI
serve wheels tagged for it, such as `pyemscripten_2026_0_wasm32`. Since
[Pyodide 314.0](https://pyodide.org/) a page can therefore install packages straight from PyPI
with `micropip`, instead of waiting for them to be built into the Pyodide distribution.

sumy is pure Python, so it needs no wheel of its own for that platform -- the ordinary
`sumy-*-py3-none-any.whl` is what runs in the browser. What did need work is the dependency
list: `micropip` has to resolve every requirement, and five of sumy's cannot be resolved or
used under Emscripten. They are declared `sys_platform != "emscripten"` in `pyproject.toml`:

| Dependency         | Why it is skipped in a browser                                             |
| ------------------ | -------------------------------------------------------------------------- |
| `breadability`     | requires `docopt`, which PyPI carries only as a source distribution        |
| `lxml-html-clean`  | requires `lxml`, which has no pure-Python wheel                            |
| `requests`         | cannot open a socket in a browser                                          |
| `setuptools`       | only needed for `breadability`'s `pkg_resources` import                     |
| `docopt-ng`        | drives the `sumy` command line, and a browser has no terminal              |

So a browser install summarizes plain text. The two things that dependency list pays for are
still reachable, with a caveat each:

* **`sumy.utils.fetch_url` works**, through Pyodide's own synchronous XMLHttpRequest client
  rather than `requests`. It is the *browser* doing the download, so the same-origin policy
  applies: only this page's origin, or a server sending CORS headers, will answer. Nothing can
  be done about that from Python -- for any other page, fetch it through a proxy you control.
  The `timeout` argument is ignored, since a synchronous request cannot carry one.
* **`HtmlParser` needs a manual dependency dance.** micropip cannot resolve breadability
  (docopt is a source distribution) and cannot get lxml from PyPI -- but the Pyodide
  distribution *has* lxml, so installing the two without their dependency metadata works:

  ```js
  await pyodide.loadPackage("lxml");                    // Pyodide's own build
  const micropip = pyodide.pyimport("micropip");
  await micropip.install(["chardet", "setuptools"]);    // breadability needs both
  // deps=False: docopt has no wheel, and lxml-html-clean asks for a newer lxml than Pyodide's
  await micropip.install.callKwargs(["lxml-html-clean", "breadability"], { deps: false });
  ```

  After that `HtmlParser.from_string(html, url, tokenizer)` really does extract the article.
  It is left out of sumy's own dependency list because pinning it would break plain
  `micropip.install("sumy")` for everyone, and because it leans on a version mismatch that
  can stop working with any Pyodide release.

## Doing it yourself

Three things have to happen in the page, and
[`docs/demo/sumy-browser.mjs`](demo/sumy-browser.mjs) is a plain ES module that does all
three -- import it instead of writing them again:

```html
<script type="module">
  import { loadPyodide } from "https://cdn.jsdelivr.net/pyodide/v314.0.6/full/pyodide.mjs";
  import { loadSumy, summarize } from "https://miso-belica.github.io/sumy/demo/sumy-browser.mjs";

  const pyodide = await loadPyodide();
  await loadSumy(pyodide);

  console.log(summarize(pyodide, { text: "Some long text. Split into sentences.", sentenceCount: 2 }));
</script>
```

What it does, if you would rather do it by hand:

1. `micropip.install("sumy")`, plus `pyodide.loadPackage("numpy")` -- the LSA and LexRank
   summarizers need numpy, and Pyodide ships it.
2. NLTK's `punkt_tab` sentence tokenizer data. This is the part with no obvious answer:
   `nltk.download()` opens a socket, so instead fetch
   [the zip](https://cdn.jsdelivr.net/gh/nltk/nltk_data@gh-pages/packages/tokenizers/punkt_tab.zip)
   yourself, write it to `/nltk_data/tokenizers/punkt_tab.zip` through `pyodide.FS`, and
   `nltk.data.path.append("/nltk_data")`. NLTK reads the models out of the zip as it is, so
   there is no need to unpack it.
3. The ordinary sumy API -- `PlaintextParser`, `Tokenizer`, a summarizer and
   `get_stop_words` -- exactly as on any other platform.

Languages needing an extra tokenizer or stemmer package (Arabic, Chinese, Greek, Hebrew,
Japanese, Korean, Polish, Thai) also work if you `micropip.install` that package first; the
demo leaves them out only to keep its download small.

## Checking it

Two scripts in `tools/wasm` run this in a real Pyodide runtime from node 20.11 or newer, and
CI runs both on every pull request and once more on the artifact of every release:

```sh
$ uv build --wheel
$ cd tools/wasm && npm ci && cd -
$ node tools/wasm/check-wheel.mjs   # the wheel installs and every module imports
$ node tools/wasm/check-demo.mjs    # a document really gets summarized
```

To try an unreleased wheel in the demo page itself, serve the `docs` directory and pass the
wheel's URL: `.../demo/?wheel=/demo/sumy-0.13.0-py3-none-any.whl`.
