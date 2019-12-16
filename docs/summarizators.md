# Summarization methods

I found quite a good explanation in the book [Mastering Data Mining with Python – Find patterns hidden in your data](https://books.google.cz/books?id=_qXWDQAAQBAJ&lpg=PA197&ots=L92PdXy51V&dq=edmundson%20stigma%20words%20example&hl=sk&pg=PA185#v=onepage&q&f=false). You can search for one in your local library and read tips, not only, about the Sumy there.

## Random
**Test method** - you should not use this one for real-world applications. It's used only during the evaluation of the summaries for comparison with the other algorithms. The idea behind it is that if any summarizer has a worse score than this one it's probably a really bad algorithm or there is some serious flaw/bug in the implementation.

## [Luhn]((http://ieeexplore.ieee.org/xpl/articleDetails.jsp?arnumber=5392672))
**Heuristic method** - the simplest real-world algorithm. It's the first one known and it's based on the assumption that the most important sentences are those with the most significant words. The significant words are those which are more often in the text but at the same time, they don't belong among stop-words. That's why if you want to use this one you need a list of stop-words for your language. Without it, it would probably produce really bad results.

## [Edmundson](http://dl.acm.org/citation.cfm?doid=321510.321519)
**Heuristic method with previous statistic research** - the enhancement of the Luhn method mentioned previously. Edmundson added 3 more heuristics to the method to measure the importance of the sentences. He finds so-called _pragmatic words_, the words that are in headings and the position of the extracted terms. Therefore this method has 4 sub-methods and the proper combination of them results in the Edmundson method. The important part is that this method is the most **language-dependent** because it needs the list of **bonus words** and **stigma words** except for the stop-words (called the **null words** here). If you are serious about the summary you should read how Edmundson mined these words from the corpus in the original paper. Otherwise here are some hints that Edmundson noticed and described there. 

* **bonus words** - positively relevant. Edmundson found here most of the comparatives, superlatives, adverbs of conclusion, value terms, relative interrogatives, and causality terms. E.g: significant, great, famous, glorious, interesting, famous, optimal, super.
* **stigma words** - negatively relevant. Edmundson found here most of the anaphoric expressions, belittling expressions, insignificant-detail expressions, and hedging expressions. E.g: hardly, impossible.
* **null words** - irrelevant words. Edmundson found here the most of the ordinals, cardinals, the verb "to be", prepositions, pronouns, adjectives, verbal auxiliaries, articles and coordinating conjunctions. E.g.: with, be, from, or, and, every, why, here.

```python
summarizer = EdmundsonSummarizer(stemmer)
summarizer.null_words = stop_words
summarizer.bonus_words = significant_words
summarizer.stigma_words = stigma_words
```

Sumy's `HtmlParser` can extract such words from the HTML markup if the document is marked semantically. According to my findings, it may even beat the LSA method for the HTML documents in that case.

## [Latent Semantic Analysis, LSA](http://scholar.google.com/citations?user=0fTuW_YAAAAJ&hl=en)
**Algebraic method** - the most advanced method is independent of the language. But also the most complicated (computationally and mentally). The method is able to identify synonyms in the text and the topics that are not explicitly written in the `Document`. The best for the plain text documents without any markup but it shines also for the HTML documents. I think the author is using more advanced algorithms now described in [Steinberger, J. a Ježek, K. Using latent semantic an and summary evaluation. In In Proceedings ISIM '04. 2004. S. 93-100.](http://www.kiv.zcu.cz/~jstein/publikace/isim2004.pdf).

## [LexRank](http://tangra.si.umich.edu/~radev/lexrank/lexrank.pdf) and [TextRank](https://web.eecs.umich.edu/~mihalcea/papers/mihalcea.emnlp04.pdf)
**Unsupervised approach inspired by algorithms PageRank and HITS** - algorithms inspired on the world wide web. They try to find connections between the sentences and identify the ones connected with the most significant words/topics. You should read the original papers to find out if they are suitable for your use-case.    
    
## [SumBasic](http://www.cis.upenn.edu/~nenkova/papers/ipm.pdf)
**Method often used as a baseline in the literature** - another one used to compare the score of the algorithms. I think you can use it if you want but it has no special advantage over the LSA or TextRank.

## [KL-Sum](http://www.aclweb.org/anthology/N09-1041)
Method that greedily adds sentences to a summary so long as it decreases the KL Divergence.

## Reduction
**Graph-based summarization**, where a sentence salience is computed as the sum of the weights of its edges to other sentences. The weight of an edge between two sentences is computed in the same manner as TextRank.
