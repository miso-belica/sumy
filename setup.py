# -*- coding: utf-8 -*-

import sys

from setuptools import find_packages, setup

VERSION_SUFFIX = "%d.%d" % sys.version_info[:2]


with open("README.md") as readme:
    long_description = readme.read()


dependencies = [
    "docopt>=0.6.1,<0.7",
    "breadability>=0.1.20",
    "requests>=2.7.0",
    "pycountry>=18.2.23",
    "nltk>=3.0.2,<3.2.0" if VERSION_SUFFIX == "3.3" else "nltk>=3.0.2",  # NLTK 3.2 dropped support for Python 3.3
]
if VERSION_SUFFIX == "3.4":  # lxml 4.4.0 dropped support for Python 3.4
    dependencies.append("lxml<4.4.0")


# https://blog.ionelmc.ro/presentations/packaging/
setup(
    name="sumy",
    version="0.8.1",
    description="Module for automatic summarization of text documents and HTML pages.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Mišo Belica",
    author_email="miso.belica@gmail.com",
    url="https://github.com/miso-belica/sumy",
    license="Apache License, Version 2.0",
    keywords=[
        "data mining",
        "automatic summarization",
        "data reduction",
        "web-data extraction",
        "NLP",
        "natural language processing",
        "latent semantic analysis",
        "LSA",
        "TextRank",
        "LexRank",
    ],
    install_requires=dependencies,
    tests_require=[
        "pytest>=3.0.0",
        "pytest-cov",
        "pytest-watch",
    ],
    extras_require={
        "LSA": ["numpy"],
        "LexRank": ["numpy"],
        "Japanese": ["tinysegmenter"],
        "Chinese": ["jieba"],
        "Korean": ["konlpy"],
    },
    packages=find_packages(),
    package_data={"sumy": [
        "data/stopwords/*.txt",
    ]},
    entry_points={
        "console_scripts": [
            "sumy = sumy.__main__:main",
            "sumy-%s = sumy.__main__:main" % VERSION_SUFFIX,
            "sumy_eval = sumy.evaluation.__main__:main",
            "sumy_eval-%s = sumy.evaluation.__main__:main" % VERSION_SUFFIX,
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: Apache Software License",

        "Natural Language :: Chinese (Simplified)",
        "Natural Language :: Czech",
        "Natural Language :: English",
        "Natural Language :: French",
        "Natural Language :: German",
        "Natural Language :: Italian",
        "Natural Language :: Japanese",
        "Natural Language :: Portuguese",
        "Natural Language :: Slovak",
        "Natural Language :: Spanish",

        "Topic :: Education",
        "Topic :: Internet",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Text Processing :: Filters",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Text Processing :: Markup :: HTML",

        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
)
