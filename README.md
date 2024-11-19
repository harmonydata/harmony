![The Harmony Project logo](https://raw.githubusercontent.com/harmonydata/brand/main/Logo/PNG/%D0%BB%D0%BE%D0%B3%D0%BE%20%D1%84%D1%83%D0%BB-05.png)

<a href="https://harmonydata.ac.uk"><span align="left">🌐 harmonydata.ac.uk</span></a>
<a href="https://www.linkedin.com/company/harmonydata"><img align="left" src="https://raw.githubusercontent.com//harmonydata/.github/main/profile/linkedin.svg" alt="Harmony | LinkedIn" width="21px"/></a>
<a href="https://twitter.com/harmony_data"><img align="left" src="https://raw.githubusercontent.com//harmonydata/.github/main/profile/x.svg" alt="Harmony | X" width="21px"/></a>
<a href="https://www.instagram.com/harmonydata/"><img align="left" src="https://raw.githubusercontent.com//harmonydata/.github/main/profile/instagram.svg" alt="Harmony | Instagram" width="21px"/></a>
<a href="https://www.facebook.com/people/Harmony-Project/100086772661697/"><img align="left" src="https://raw.githubusercontent.com//harmonydata/.github/main/profile/fb.svg" alt="Harmony | Facebook" width="21px"/></a>
<a href="https://www.youtube.com/channel/UCraLlfBr0jXwap41oQ763OQ"><img align="left" src="https://raw.githubusercontent.com//harmonydata/.github/main/profile/yt.svg" alt="Harmony | YouTube" width="21px"/></a>

 [![Harmony on Twitter](https://img.shields.io/twitter/follow/harmony_data.svg?style=social&label=Follow)](https://twitter.com/harmony_data) 


# Harmony Python library

<!-- badges: start -->
[![PyPI package](https://img.shields.io/badge/pip%20install-harmonydata-brightgreen)](https://pypi.org/project/harmonydata/) ![my badge](https://badgen.net/badge/Status/In%20Development/orange) [![License](https://img.shields.io/github/license/harmonydata/harmony)](https://github.com/harmonydata/harmony/blob/main/LICENSE)
[![tests](https://github.com/harmonydata/harmony/actions/workflows/test.yml/badge.svg)](https://github.com/harmonydata/harmony/actions/workflows/test.yml)
[![Current Release Version](https://img.shields.io/github/release/harmonydata/harmony.svg?style=flat-square&logo=github)](https://github.com/harmonydata/harmony/releases)
[![pypi Version](https://img.shields.io/pypi/v/harmonydata.svg?style=flat-square&logo=pypi&logoColor=white)](https://pypi.org/project/harmonydata/)
 [![version number](https://img.shields.io/pypi/v/harmonydata?color=green&label=version)](https://github.com/harmonydata/harmony/releases) [![PyPi downloads](https://static.pepy.tech/personalized-badge/harmonydata?period=total&units=international_system&left_color=grey&right_color=orange&left_text=pip%20downloads)](https://pypi.org/project/harmonydata/)
[![forks](https://img.shields.io/github/forks/harmonydata/harmony)](https://github.com/harmonydata/harmony/forks)
[![docker](https://img.shields.io/badge/docker-pull-blue.svg?logo=docker&logoColor=white)](https://hub.docker.com/r/harmonydata/harmonyapi)

You can also join [our Discord server](https://discord.gg/harmonydata)! If you found Harmony helpful, you can [leave us a review](https://g.page/r/CaRWc2ViO653EBM/review)!

# What does Harmony do?

* Psychologists and social scientists often have to match items in different questionnaires, such as "I often feel anxious" and "Feeling nervous, anxious or afraid". 
* This is called **harmonisation**.
* Harmonisation is a time consuming and subjective process.
* Going through long PDFs of questionnaires and putting the questions into Excel is no fun.
* Enter [Harmony](https://harmonydata.ac.uk/app), a tool that uses [natural language processing](naturallanguageprocessing.com) and generative AI models to help researchers harmonise questionnaire items, even in different languages.

# Quick start with the code

[Read our guide to contributing to Harmony here](https://harmonydata.ac.uk/contributing-to-harmony/) or read [CONTRIBUTING.md](./CONTRIBUTING.md).

You can run the walkthrough Python notebook in [Google Colab](https://colab.research.google.com/github/harmonydata/harmony/blob/main/Harmony_example_walkthrough.ipynb) with a single click: <a href="https://colab.research.google.com/github/harmonydata/harmony/blob/main/Harmony_example_walkthrough.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

You can also download an R markdown notebook to run in R Studio: <a href="https://harmonydata.ac.uk/harmony_r_example.nb.html" target="_parent"><img src="https://img.shields.io/badge/RStudio-4285F4" alt="Open In R Studio"/></a>

You can run the walkthrough R notebook in Google Colab with a single click: <a href="https://colab.research.google.com/github/harmonydata/experiments/blob/main/Harmony_R_example.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a> [View the PDF documentation of the R package on CRAN](https://cran.r-project.org/web/packages/harmonydata/harmonydata.pdf)

# Looking for examples?

Check out our examples repository at [https://github.com/harmonydata/harmony_examples](https://github.com/harmonydata/harmony_examples)


<!-- badges: end -->

# The Harmony Project

Harmony is a tool using AI which allows you to compare items from questionnaires and identify similar content. You can try Harmony at https://harmonydata.ac.uk/app and you can read our blog at https://harmonydata.ac.uk/blog/.

## Who to contact?

You can contact Harmony team at https://harmonydata.ac.uk/, or Thomas Wood at https://fastdatascience.com/.

## 🖥 Installation instructions (video)

[![Installing Harmony](https://raw.githubusercontent.com/harmonydata/.github/main/profile/installation_video.jpg)](https://www.youtube.com/watch?v=enWh0-4I0Sg "Installing Harmony")

## 🖱 Looking to try Harmony in the browser?

Visit: https://harmonydata.ac.uk/app/

You can also visit our blog at https://harmonydata.ac.uk/

## ✅ You need Tika if you want to extract instruments from PDFs

Download and install Java if you don't have it already. Download and install Apache Tika and run it on your computer https://tika.apache.org/download.html

```
java -jar tika-server-standard-2.3.0.jar
```

## Requirements

You need a Windows, Linux or Mac system with

* Python 3.8 or above
* the requirements in [requirements.txt](./requirements.txt)
* Java (if you want to extract items from PDFs)
* [Apache Tika](https://tika.apache.org/download.html) (if you want to extract items from PDFs)

## 🖥 Installing Harmony Python package

You can install from [PyPI](https://pypi.org/project/harmonydata/).

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

* `HARMONY_SPACY_PATH` - determines where model files are stored. Defaults to `HOME DIRECTORY/harmony`
* `HARMONY_DATA_PATH` - determines where data files are stored. Defaults to `HOME DIRECTORY/harmony`
* `HARMONY_NO_PARSING` - set to 1 to import a lightweight variant of Harmony which doesn't support PDF parsing.
* `HARMONY_NO_MATCHING` - set to 1 to import a lightweight variant of Harmony which doesn't support matching.

## Creating instruments from a list of strings

You can also create instruments quickly from a list of strings

```
from harmony import create_instrument_from_list, match_instruments
instrument1 = create_instrument_from_list(["I feel anxious", "I feel nervous"])
instrument2 = create_instrument_from_list(["I feel afraid", "I feel worried"])
all_questions, similarity, query_similarity, new_vectors_dict = match_instruments([instrument1, instrument2])
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
all_questions, similarity, query_similarity, new_vectors_dict = match_instruments(instruments)
```

* `all_questions` is a list of the questions passed to Harmony, in order.
* `similarity` is the similarity matrix returned by Harmony.
* `query_similarity` is the degree of similarity of each item to an optional query passed as argument to `match_instruments`.

## ⇗⇗ Using a different vectorisation function

Harmony defaults to `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` ([HuggingFace link](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)). However you can use other sentence transformers from HuggingFace by setting the environment `HARMONY_SENTENCE_TRANSFORMER_PATH` before importing Harmony:

```
export HARMONY_SENTENCE_TRANSFORMER_PATH=sentence-transformers/distiluse-base-multilingual-cased-v2
```

## Using OpenAI or other LLMs for vectorisation

Any word vector representation can be used by Harmony. The below example works for OpenAI's [text-embedding-ada-002](https://openai.com/blog/new-and-improved-embedding-model) model as of July 2023, provided you have create a paid OpenAI account. However, since LLMs are progressing rapidly, we have chosen not to integrate Harmony directly into the OpenAI client libraries, but instead allow you to pass Harmony any vectorisation function of your choice.

```
import numpy as np
from harmony import match_instruments_with_function, example_instruments
from openai import OpenAI

client = OpenAI()
model_name = "text-embedding-ada-002"
def convert_texts_to_vector(texts):
    vectors = client.embeddings.create(input = texts, model=model_name).data
    return np.asarray([vectors[i].embedding for i in range(len(vectors))])
instruments = example_instruments["CES_D English"], example_instruments["GAD-7 Portuguese"]
all_questions, similarity, query_similarity, new_vectors_dict = match_instruments_with_function(instruments, None, convert_texts_to_vector)
```
 
## 💻 Do you want to run Harmony in your browser locally?

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

* 📰 The code for training the PDF extraction is here: https://github.com/harmonydata/pdf-questionnaire-extraction

## Docker images

If you are a Docker user, you can run Harmony from a pre-built Docker image.

* https://hub.docker.com/repository/docker/harmonydata/harmonyapi - just the Harmony API
* https://hub.docker.com/repository/docker/harmonydata/harmonylocal - Harmony API and React front end

## Contributing to Harmony

If you'd like to contribute to this project, you can contact us at https://harmonydata.ac.uk/ or make a pull request on our [Github repository](https://github.com/harmonydata/harmonyapi). You can also [raise an issue](https://github.com/harmonydata/harmony/issues). 

## Developing Harmony

### 🧪 Automated tests

Test code is in **tests/** folder using [unittest](https://docs.python.org/3/library/unittest.html).

The testing tool `tox` is used in the automation with GitHub Actions CI/CD. **Since the PDF extraction also needs Java and Tika installed, you cannot run the unit tests without first installing Java and Tika. See above for instructions.**

### 🧪 Use tox locally

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

Thanks to GitHub Actions' automated process, you don't need to generate distribution files locally. 

### ⚙️Continuous integration/deployment to PyPI

This package is based on the template https://pypi.org/project/example-pypi-package/

This package

- uses GitHub Actions for both testing and publishing
- is tested when pushing `master` or `main` branch, and is published when create a release
- includes test files in the source distribution
- uses **setup.cfg** for [version single-sourcing](https://packaging.python.org/guides/single-sourcing-package-version/) (setuptools 46.4.0+)

## ⚙️Re-releasing the package manually

The code to re-release Harmony on PyPI is as follows:

```
source activate py311
pip install twine
rm -rf dist
python setup.py sdist
twine upload dist/*
```

## ‎😃💁 Who worked on Harmony?

Harmony is a collaboration project between [Ulster University](https://ulster.ac.uk/), [University College London](https://ucl.ac.uk/), the [Universidade Federal de Santa Maria](https://www.ufsm.br/), and [Fast Data Science](http://fastdatascience.com/).  Harmony is funded by [Wellcome](https://wellcome.org/) as part of the [Wellcome Data Prize in Mental Health](https://wellcome.org/grant-funding/schemes/wellcome-mental-health-data-prize).

The core team at Harmony is made up of:

* [Dr Bettina Moltrecht, PhD](https://profiles.ucl.ac.uk/60736-bettina-moltrecht) (UCL)
* [Dr Eoin McElroy](https://www.ulster.ac.uk/staff/e-mcelroy) (University of Ulster)
* [Dr George Ploubidis](https://profiles.ucl.ac.uk/48171-george-ploubidis) (UCL)
* [Dr Mauricio Scopel Hoffmann](https://ufsmpublica.ufsm.br/docente/18264) (Universidade Federal de Santa Maria, Brazil)
* [Thomas Wood](https://freelancedatascientist.net/) ([Fast Data Science](https://fastdatascience.com))

## 📜 License

MIT License. Copyright (c) 2023 Ulster University (https://www.ulster.ac.uk)

## 📜 How do I cite Harmony?

You can cite our validation paper:

 McElroy, Wood, Bond, Mulvenna, Shevlin, Ploubidis, Scopel Hoffmann, Moltrecht, [Using natural language processing to facilitate the harmonisation of mental health questionnaires: a validation study using real-world data](https://bmcpsychiatry.biomedcentral.com/articles/10.1186/s12888-024-05954-2#citeas). BMC Psychiatry 24, 530 (2024), https://doi.org/10.1186/s12888-024-05954-2
 

A BibTeX entry for LaTeX users is

```
@article{mcelroy2024using,
  title={Using natural language processing to facilitate the harmonisation of mental health questionnaires: a validation study using real-world data},
  author={McElroy, Eoin and Wood, Thomas and Bond, Raymond and Mulvenna, Maurice and Shevlin, Mark and Ploubidis, George B and Hoffmann, Mauricio Scopel and Moltrecht, Bettina},
  journal={BMC psychiatry},
  volume={24},
  number={1},
  pages={530},
  year={2024},
  publisher={Springer}
}
```
