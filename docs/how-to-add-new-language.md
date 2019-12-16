# How to add new natural language support into Sumy

Let's say [someone wants](https://github.com/miso-belica/sumy/issues/62) to summarize documents in the Russian language by the Sumy. The first thing you will need is a [tokenizer](docs/index.md#Tokenizer). So we can try if there is some support in Sumy.

```python
from sumy.nlp.tokenizers import Tokenizer
tokenizer = Tokenizer("ru")

# https://ru.m.wikipedia.org/wiki/Тунберг,_Грета
sentences = tokenizer.to_sentences("Гре́та Тинтин Элеонора Э́рнман Ту́нберг (швед. Greta Tintin Eleonora Ernman Thunberg; род. 3 января 2003[1][2], Стокгольм[1]) — шведская школьница, экологическая активистка. В 15 лет начала протестовать возле шведского парламента с плакатом «Школьная забастовка за климат», призывая к незамедлительным действиям по борьбе с изменением климата в соответствии с Парижским соглашением. Её действия нашли отклик по всему миру, породив массовые мероприятия, известные как «школьные забастовки за климат» или «пятницы ради будущего»")

for sentence in sentences:
    print(tokenizer.to_words(sentence))
```

So we are good here. But you know, what if the tokenizer is missing? Then you need to implement one by yourself. Or to find some library for your language and wrap it into the API for Sumy. It should be easy because Sumy expects an object with two methods. The simplest naive tokenizer would look like this.

```python
from typing import List

class Tokenizer:
    @staticmethod
    def to_sentences(text: str) -> List[str]:
        return [s.strip() for s in text.split(".")]

    @staticmethod
    def to_words(sentence: str) -> List[str]:
        return [w.strip() for w in sentence.split(" ")]
```

Another language-specific thing is **Stemmer**. For Sumy, the stemmer is any callable object which accepts word (string) and returns word (string). But the word may be somehow changed. The role of the stemmer is to normalize words into the same form. For example, you have words: _teacher_, _teaching_, _teach_ and you want to return the root of the word _teach_ for all these because they have the same meaning. But of course, you want to return _sleep_ for _sleeping_. Some languages like the Japanese language does not care and can simply return the original word. But for another like Slovak/Czech/English language, it's quite important to normalize all the different forms of the word. The simplest stemmer looks like the one below:

```python
def null_stemmer(word):
    """I am the same as from sumy.nlp.stemmers import null_stemmer :)"""
    return word
```

```python
# seems NLTK covers our back again :)
from sumy.nlp.stemmers import Stemmer
stemmer = Stemmer("ru")
stem = stemmer("Элеонора")  # элеонор
```

The last piece is a list of stop-words. Sumy has some stop-words in, but you can download any free list from the internet. This piece is also optional because the summarizers can work without it but it's **highly recommended** to provide one because it may increase the quality of the summaries dramatically.

And that's all. You will these parts together with the other parts from the README and send a pull request with your code :) 
