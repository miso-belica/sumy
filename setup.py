# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import sys


VERSION_SUFFIX = "%d.%d" % sys.version_info[:2]


with open("README.rst") as readme:
    long_description = readme.read()


setup(
    name="sumy",
    version="0.4.0",
    description="Module for automatic summarization of text documents and HTML pages.",
    long_description=long_description,
    author="Michal Belica",
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
    install_requires=[
        "docopt>=0.6.1,<0.7",
        "breadability>=0.1.20",
        "nltk>=3.0.2",
        "requests>=2.7.0",
    ],
    tests_require=[
        "pytest",
        "pytest-cov",
        "pytest-watch",
    ],
    extras_require={
        "LSA": ["numpy"],
        "LexRank": ["numpy"],
    },
    packages=[
        "sumy",
        "sumy.evaluation",
        "sumy.models",
        "sumy.models.dom",
        "sumy.nlp",
        "sumy.nlp.stemmers",
        "sumy.parsers",
        "sumy.summarizers",
    ],
    package_data={"sumy": [
        "data/stopwords/*.txt",
    ]},
    entry_points={
        "console_scripts": [
            "sumy = sumy.__main__:main",
            "sumy-%s = sumy.__main__:main" % VERSION_SUFFIX,
            "sumy_eval = sumy.evaluation.__main__:main",
            "sumy_eval-%s = sumy.evaluation.__main__:main" % VERSION_SUFFIX,
        ]
    },
    classifiers=[
        "Development Status :: 3 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: Apache Software License",

        "Natural Language :: Czech",
        "Natural Language :: Slovak",
        "Natural Language :: English",
        "Natural Language :: German",
        "Natural Language :: French",

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
        "Programming Language :: Python :: Implementation :: CPython",
    ],
)
