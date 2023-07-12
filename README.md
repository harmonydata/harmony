# Harmony Python library

<!-- badges: start -->
![my badge](https://badgen.net/badge/Status/In%20Development/orange)

[![PyPI package](https://img.shields.io/badge/pip%20install-harmonydata-brightgreen)](https://pypi.org/project/harmonydata/) [![version number](https://img.shields.io/pypi/v/harmonydata?color=green&label=version)](https://github.com/harmonydata/harmony/releases) [![License](https://img.shields.io/github/license/harmonydata/harmony)](https://github.com/harmonydata/harmony/blob/main/LICENSE)

<!-- badges: end -->

# The Harmony Project

Harmony is a tool using AI which allows you to compare items from questionnaires and identify similar content. You can try Harmony at https://app.harmonydata.org and you can read our blog at https://harmonydata.org/blog/.

## Who to contact?

You can contact Harmony team at https://harmonydata.org/, or Thomas Wood at https://fastdatascience.com/.

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

## Loading all models

Harmony uses spaCy to help with text extraction from PDFs. spaCy models can be downloaded with the following command in Python:

```
import harmony
harmony.download_models()
```

## Matching example instruments

```
instruments = harmony.example_instruments["CES_D English"], harmony.example_instruments["GAD-7 Portuguese"]
questions, similarity, query_similarity, new_vectors_dict = harmony.match_instruments(instruments)
```

## How to load a PDF, Excel or Word into an instrument

```
harmony.load_instruments_from_local_file("gad-7.pdf")
```

## Optional environment variables

As an alternative to downloading models, you can set environment variables so that Harmony calls spaCy on a remote server. This is only necessary if you are making a server deployment of Harmony.

* `HARMONY_CLASSIFIER_ENDPOINT` - this can be an Azure Functions deployment of the text triage spaCy model. Example: https://twspacytest.azurewebsites.net/api/triage
* `HARMONY_NER_ENDPOINT` - this can be an Azure Functions deployment of the NER spaCy model. Example: https://twspacytest.azurewebsites.net/api/ner
* `HARMONY_SPACY_PATH` - determines where model files are stored. Defaults to `HOME DIRECTORY/harmony`
* `HARMONY_DATA_PATH` - determines where data files are stored. Defaults to `HOME DIRECTORY/harmony`
* `HARMONY_NO_PARSING` - set to 1 to import a lightweight variant of Harmony which doesn't support PDF parsing.
* `HARMONY_NO_MATCHING` - set to 1 to import a lightweight variant of Harmony which doesn't support matching.

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

## Using a different vectorisation function

Harmony defaults to `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` ([HuggingFace link](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)). However you can use other sentence transformers from HuggingFace by setting the environment `HARMONY_SENTENCE_TRANSFORMER_PATH` before importing Harmony:

```
export HARMONY_SENTENCE_TRANSFORMER_PATH=sentence-transformers/distiluse-base-multilingual-cased-v2
```

## Using OpenAI or other LLMs for vectorisation

Any word vector representation can be used by Harmony. The below example works for OpenAI's [text-embedding-ada-002](https://openai.com/blog/new-and-improved-embedding-model) model as of July 2023, provided you have create a paid OpenAI account. However, since LLMs are progressing rapidly, we have chosen not to integrate Harmony directly into the OpenAI client libraries, but instead allow you to pass Harmony any vectorisation function of your choice.

```
import openai
import numpy as np
from harmony import match_instruments_with_function, example_instruments
model_name = "text-embedding-ada-002"
def convert_texts_to_vector(texts):
    vectors = openai.Embedding.create(input = texts, model=model_name)['data']
    return [vectors[i]["embedding"] for i in range(len(vectors))]
instruments = example_instruments["CES_D English"], example_instruments["GAD-7 Portuguese"]
all_questions, similarity, query_similarity, new_vectors_dict = match_instruments_with_function(instruments, None, convert_texts_to_vector)
```
 
## Do you want to run Harmony in your browser locally?

Download and install Docker:

* https://docs.docker.com/desktop/install/mac-install/
* https://docs.docker.com/desktop/install/windows-install/
* https://docs.docker.com/desktop/install/linux-install/

Open a Terminal and run

```
docker run -p 8000:8000 -p 3000:3000 harmonydata/harmonylocal
```

Then go to http://localhost:3000 in your browser.

## Looking for the Harmony API?

Visit: https://github.com/harmonydata/harmonyapi

## Docker images

If you are a Docker user, you can run Harmony from a pre-built Docker image.

* https://hub.docker.com/repository/docker/harmonydata/harmonyapi - just the Harmony API
* https://hub.docker.com/repository/docker/harmonydata/harmonylocal - Harmony API and React front end

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

## Who worked on Harmony?

Harmony is a collaboration project between the University of Ulster, University College London, the Universidade Federal de Santa Maria in Brazil, and Fast Data Science Ltd.

The team at Harmony is made up of:

* Bettina Moltrecht, PhD (UCL)
* Dr Eoin McElroy (University of Ulster)
* Dr George Ploubidis (UCL)
* Dr Mauricio Scopel Hoffman (Universidade Federal de Santa Maria, Brazil)
* Thomas Wood ([Fast Data Science](https://fastdatascience.com))

## License

MIT License. Copyright (c) 2023 Ulster University (https://www.ulster.ac.uk)

## How do I cite Harmony?

McElroy, E., Moltrecht, B., Ploubidis, G.B., Scopel Hoffman, M., Wood, T.A., Harmony [Computer software], Version 1.0, accessed at https://app.harmonydata.org. Ulster University (2022)
