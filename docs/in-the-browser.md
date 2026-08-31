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
list: `micropip` has to resolve every requirement, and four of sumy's cannot be resolved or
used under Emscripten. They are declared `sys_platform != "emscripten"` in `pyproject.toml`:

| Dependency         | Why it is skipped in a browser                                             |
| ------------------ | -------------------------------------------------------------------------- |
| `breadability`     | requires `docopt`, which PyPI carries only as a source distribution        |
| `lxml-html-clean`  | requires `lxml`, which has no pure-Python wheel                            |
| `requests`         | cannot open a socket in a browser                                          |
| `setuptools`       | only needed for `breadability`'s `pkg_resources` import                     |
| `docopt-ng`        | drives the `sumy` command line, and a browser has no terminal              |

So in a browser sumy can summarize plain text, but not extract an article from an HTML page
(`HtmlParser`) or download a URL itself (`sumy.utils.fetch_url`). Both explain that when
called; fetch the page with `fetch()` and hand sumy the text.

## Doing it yourself

```html
<script type="module">
  import { loadPyodide } from "https://cdn.jsdelivr.net/pyodide/v314.0.6/full/pyodide.mjs";

  const pyodide = await loadPyodide();

  // numpy is needed by the LSA and LexRank summarizers; Pyodide ships it.
  await pyodide.loadPackage(["micropip", "numpy"]);
  const micropip = pyodide.pyimport("micropip");
  await micropip.install("sumy");

  // NLTK's sentence tokenizer data. nltk.download() opens a socket, so fetch the zip and
  // write it where NLTK looks; NLTK reads the models out of the zip as it is.
  const punkt = await fetch(
    "https://cdn.jsdelivr.net/gh/nltk/nltk_data@gh-pages/packages/tokenizers/punkt_tab.zip",
  );
  pyodide.FS.mkdirTree("/nltk_data/tokenizers");
  pyodide.FS.writeFile("/nltk_data/tokenizers/punkt_tab.zip", new Uint8Array(await punkt.arrayBuffer()));

  console.log(pyodide.runPython(`
import nltk
nltk.data.path.append("/nltk_data")

from sumy.nlp.stemmers import Stemmer
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lsa import LsaSummarizer
from sumy.utils import get_stop_words

parser = PlaintextParser.from_string("Some long text. Split into sentences.", Tokenizer("english"))
summarizer = LsaSummarizer(Stemmer("english"))
summarizer.stop_words = get_stop_words("english")

"\\n".join(str(sentence) for sentence in summarizer(parser.document, 2))
`));
</script>
```

The demo does exactly this in [`docs/demo/sumy-browser.mjs`](demo/sumy-browser.mjs), which is
a plain ES module you can import instead of copying the above.

Languages needing an extra tokenizer or stemmer package (Arabic, Chinese, Greek, Hebrew,
Japanese, Korean, Polish, Thai) also work if you `micropip.install` that package first; the
demo leaves them out only to keep its download small.

## Checking it

Two scripts in `tools/wasm` run this in a real Pyodide runtime from node, and CI runs both on
every pull request and once more on the artifact of every release:

```sh
$ uv build --wheel
$ cd tools/wasm && npm ci && cd -
$ node tools/wasm/check-wheel.mjs   # the wheel installs and every module imports
$ node tools/wasm/check-demo.mjs    # a document really gets summarized
```

To try an unreleased wheel in the demo page itself, serve the `docs` directory and pass the
wheel's URL: `.../demo/?wheel=/demo/sumy-0.13.0-py3-none-any.whl`.
