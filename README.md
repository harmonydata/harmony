# Harmony Python library

<!-- badges: start -->
![my badge](https://badgen.net/badge/Status/In%20Development/orange)

[![PyPI package](https://img.shields.io/badge/pip%20install-harmonydata-brightgreen)](https://pypi.org/project/harmonydata/) [![version number](https://img.shields.io/pypi/v/harmonydata?color=green&label=version)](https://github.com/harmonydata/harmony/releases) [![License](https://img.shields.io/github/license/harmonydata/harmony)](https://github.com/harmonydata/harmony/blob/main/LICENSE)

<!-- badges: end -->

## Who to contact?

You can contact Harmony team at https://harmonydata.org/, or Thomas Wood at http://fastdatascience.com/.

## Looking to try Harmony in the browser?

Visit: https://app.harmonydata.org/

You can also visit our blog at https://harmonydata.org/

## You need Tika if you want to extract instruments from PDFs

Download and install Java if you don't have it already. Download and install Apache Tika and run it on your computer https://tika.apache.org/download.html

```
java -jar tika-server-standard-2.3.0.jar
```

## Installing Harmony Python package

You can install from [PyPI](https://pypi.org/project/harmonydata/0.1.0/).

```
pip install harmonydata
```

## Loading instruments from PDFs

If you have a local file, you can load it into a list of `Instrument` instances:

```
from harmony import load_instruments_from_local_file
instruments = load_instruments_from_local_file("gad-7.pdf")
```

## Matching instruments

Once you have some instruments, you can match them with each other with a call to `match_instruments`.

```
from harmony import match_instruments
all_questions, similarity, query_similarity = match_instruments(instruments)
```

* `all_questions` is a list of the questions passed to Harmony, in order.
* `similarity` is the similarity matrix returned by Harmony.
* `query_similarity` is the degree of similarity of each item to an optional query passed as argument to `match_instruments`.

## Contributing to Harmony

If you'd like to contribute to this project, you can contact us at https://harmonydata.org/ or make a pull request on our [Github repository](https://github.com/harmonydata/harmonyapi). You can also [raise an issue](https://github.com/harmony/harmony/issues). 

## Developing Harmony

### Automated tests

Test code is in **tests/** folder using [unittest](https://docs.python.org/3/library/unittest.html).

The testing tool `tox` is used in the automation with GitHub Actions CI/CD.

### Use tox locally

Install tox and run it:

```
pip install tox
tox
```

In our configuration, tox runs a check of source distribution using [check-manifest](https://pypi.org/project/check-manifest/) (which requires your repo to be git-initialized (`git init`) and added (`git add .`) at least), setuptools's check, and unit tests using pytest. You don't need to install check-manifest and pytest though, tox will install them in a separate environment.

The automated tests are run against several Python versions, but on your machine, you might be using only one version of Python, if that is Python 3.9, then run:

```
tox -e py39
```

Thanks to GitHub Actions' automated process, you don't need to generate distribution files locally. But if you insist, click to read the "Generate distribution files" section.

### Continuous integration/deployment to PyPI

This package is based on the template https://pypi.org/project/example-pypi-package/

This package

- uses GitHub Actions for both testing and publishing
- is tested when pushing `master` or `main` branch, and is published when create a release
- includes test files in the source distribution
- uses **setup.cfg** for [version single-sourcing](https://packaging.python.org/guides/single-sourcing-package-version/) (setuptools 46.4.0+)

## Re-releasing the package manually

The code to re-release Harmony on PyPI is as follows:

```
source activate py311
pip install twine
rm -rf dist
python setup.py sdist
twine upload dist/*
```

## License

MIT License. Copyright (c) 2023 Ulster University (https://www.ulster.ac.uk)
