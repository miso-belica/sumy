/**
 * Runs sumy inside Pyodide, in a browser -- or in node, which is how CI tests this file.
 *
 * Three things have to happen before sumy can summarize anything in a browser:
 *
 *   1. `micropip.install("sumy")` -- possible since PyPI started accepting wheels for the
 *      PyEmscripten platform (PEP 783). sumy itself is pure Python; only the dependencies it
 *      declares for Emscripten are installed here.
 *   2. numpy, for the LSA and LexRank summarizers. Pyodide ships it as a built-in package.
 *   3. NLTK's `punkt_tab` sentence tokenizer data. `nltk.download()` cannot be used -- it
 *      opens a socket -- so the zip is fetched and written into the Emscripten filesystem,
 *      where NLTK reads it in place.
 */

/** NLTK's own data repository, served with CORS headers by jsDelivr. About 4 MB. */
export const PUNKT_TAB_URL =
  "https://cdn.jsdelivr.net/gh/nltk/nltk_data@gh-pages/packages/tokenizers/punkt_tab.zip";

/** Where the tokenizer data is put; NLTK is told to look here. */
export const NLTK_DATA_DIRECTORY = "/nltk_data";

/** Summarizers usable with nothing but sumy, numpy and punkt_tab installed. */
export const METHODS = ["lsa", "luhn", "lex_rank", "text_rank", "sum_basic", "kl", "reduction", "random"];

/**
 * Languages needing no further packages.
 *
 * The ones left out (arabic, chinese, hebrew, japanese, korean, greek, polish, thai) each need
 * their own tokenizer or stemmer package, which the page would have to install separately.
 */
export const LANGUAGES = [
  "english",
  "czech",
  "french",
  "german",
  "italian",
  "portuguese",
  "slovak",
  "spanish",
  "swedish",
  "ukrainian",
];

const BOOTSTRAP = `
import nltk

if ${JSON.stringify(NLTK_DATA_DIRECTORY)} not in nltk.data.path:
    nltk.data.path.append(${JSON.stringify(NLTK_DATA_DIRECTORY)})

from sumy.nlp.stemmers import Stemmer
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.kl import KLSummarizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.summarizers.luhn import LuhnSummarizer
from sumy.summarizers.random import RandomSummarizer
from sumy.summarizers.reduction import ReductionSummarizer
from sumy.summarizers.sum_basic import SumBasicSummarizer
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.utils import get_stop_words

_SUMMARIZERS = {
    "kl": KLSummarizer,
    "lex_rank": LexRankSummarizer,
    "lsa": LsaSummarizer,
    "luhn": LuhnSummarizer,
    "random": RandomSummarizer,
    "reduction": ReductionSummarizer,
    "sum_basic": SumBasicSummarizer,
    "text_rank": TextRankSummarizer,
}


def _sumy_summarize(text, language, method, sentence_count):
    """Summarize plain text, the same way sumy's own command line does."""
    stemmer = Stemmer(language)
    parser = PlaintextParser.from_string(text, Tokenizer(language))

    summarizer = _SUMMARIZERS[method](stemmer)
    summarizer.stop_words = get_stop_words(language)

    return [str(sentence) for sentence in summarizer(parser.document, sentence_count)]
`;

/**
 * Put NLTK's punkt_tab data where NLTK will find it.
 *
 * The zip is left packed: NLTK reads the models straight out of it, and unpacking 100+ files
 * into the Emscripten filesystem is only slower.
 */
async function installPunktTab(pyodide, url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Could not download NLTK punkt_tab data from ${url}: HTTP ${response.status}`);
  }

  const directory = `${NLTK_DATA_DIRECTORY}/tokenizers`;
  pyodide.FS.mkdirTree(directory);
  pyodide.FS.writeFile(`${directory}/punkt_tab.zip`, new Uint8Array(await response.arrayBuffer()));
}

/**
 * Install sumy and its browser prerequisites into a loaded Pyodide runtime.
 *
 * @param pyodide loaded Pyodide runtime
 * @param wheel what micropip installs; "sumy" takes the latest release from PyPI, and a URL
 *   or an "emfs:" path installs a locally built wheel instead
 * @param punktTabUrl where to fetch the NLTK sentence tokenizer data from
 * @param onProgress called with a short message before each step, for a status line
 */
export async function loadSumy(pyodide, { wheel = "sumy", punktTabUrl = PUNKT_TAB_URL, onProgress } = {}) {
  const report = onProgress || (() => {});

  report("Loading numpy…");
  await pyodide.loadPackage(["micropip", "numpy"]);

  report(`Installing ${wheel === "sumy" ? "sumy from PyPI" : "the sumy wheel"}…`);
  const micropip = pyodide.pyimport("micropip");
  try {
    await micropip.install(wheel);
  } finally {
    micropip.destroy();
  }

  report("Downloading the NLTK sentence tokenizer…");
  await installPunktTab(pyodide, punktTabUrl);

  report("Ready.");
  pyodide.runPython(BOOTSTRAP);
}

/**
 * Summarize text with an already loaded sumy.
 *
 * @returns the picked sentences, in document order
 */
export function summarize(pyodide, { text, language = "english", method = "lsa", sentenceCount = 3 }) {
  if (!METHODS.includes(method)) throw new Error(`Unknown summarization method: ${method}`);

  const summarizeInPython = pyodide.globals.get("_sumy_summarize");
  if (!summarizeInPython) throw new Error("sumy is not loaded yet -- await loadSumy() first.");

  let sentences;
  try {
    sentences = summarizeInPython(text, language, method, sentenceCount);
    return sentences.toJs();
  } finally {
    if (sentences) sentences.destroy();
    summarizeInPython.destroy();
  }
}
