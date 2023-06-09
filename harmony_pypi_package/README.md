# Harmony

Package template taken from https://pypi.org/project/example-pypi-package/

This package

- uses GitHub Actions for both testing and publishing
- is tested when pushing `master` or `main` branch, and is published when create a release
- includes test files in the source distribution
- uses **setup.cfg** for [version single-sourcing](https://packaging.python.org/guides/single-sourcing-package-version/) (setuptools 46.4.0+)

### Automated tests

Test code is in **tests/** folder using [unittest](https://docs.python.org/3/library/unittest.html).

The testing tool `tox` will be used in the automation with GitHub Actions CI/CD.

### Use tox locally

Install tox and run it:

```bash
pip install tox
tox
```

In our configuration, tox runs a check of source distribution using [check-manifest](https://pypi.org/project/check-manifest/) (which requires your repo to be git-initialized (`git init`) and added (`git add .`) at least), setuptools's check, and unit tests using pytest. You don't need to install check-manifest and pytest though, tox will install them in a separate environment.

The automated tests are run against several Python versions, but on your machine, you might be using only one version of Python, if that is Python 3.9, then run:

```bash
tox -e py39
```

Thanks to GitHub Actions' automated process, you don't need to generate distribution files locally. But if you insist, click to read the "Generate distribution files" section.

## Generate distribution files

### Install tools

Install or upgrade `setuptools` and `wheel`:

```bash
python -m pip install --user --upgrade setuptools wheel
```

(If `python3` is the command on your machine, change `python` to `python3` in the above command, or add a line `alias python=python3` to **~/.bashrc** or **~/.bash_aliases** file if you use bash on Linux)

### Generate `dist`

From `example_pypi_package` directory, run the following command, in order to generate production version for source distribution (sdist) in `dist` folder:

```bash
python setup.py sdist bdist_wheel
```

### Install locally

Optionally, you can install dist version of your package locally before uploading to [PyPI](https://pypi.org/) or [TestPyPI](https://test.pypi.org/):

```bash
pip install dist/example_pypi_package-0.1.0.tar.gz
```

(You may need to uninstall existing package first:

```bash
pip uninstall example_pypi_package
```

There may be several installed packages with the same name, so run `pip uninstall` multiple times until it says no more package to remove.)

## Upload to PyPI

### Register on PyPI and get token

Register an account on [PyPI](https://pypi.org/), go to [Account settings § API tokens](https://pypi.org/manage/account/#api-tokens), "Add API token". The PyPI token only appears once, copy it somewhere. If you missed it, delete the old and add a new token.

(Register a [TestPyPI](https://test.pypi.org/) account if you are uploading to TestPyPI)

### Set secret in GitHub repo

On the page of your newly created or existing GitHub repo, click **Settings** -> **Secrets** -> **New repository secret**, the **Name** should be `PYPI_API_TOKEN` and the **Value** should be your PyPI token (which starts with `pypi-`).

### Push or release

The example package has automated tests and upload (publishing) already set up with GitHub Actions:

- Every time you `git push` or a pull request is submitted on your `master` or `main` branch, the package is automatically tested against the desired Python versions with GitHub Actions.
- Every time a new release (either the initial version or an updated version) is created, the latest version of the package is automatically uploaded to PyPI with GitHub Actions.

### View it on pypi.org

After your package is published on PyPI, go to [https://pypi.org/project/example-pypi-package/](https://pypi.org/project/example-pypi-package/) (`_` becomes `-`). Copy the command on the page, execute it to download and install your package from PyPI. (or test.pypi.org if you use that)

If you want to modify the description / README of your package on pypi.org, you have to publish a new version.

If you publish your package to PyPI manually, read below:

### Install Twine

Install or upgrade Twine:

```bash
python -m pip install --user --upgrade twine
```

Create a **.pypirc** file in your **$HOME** (**~**) directory, its content should be:

```ini
[pypi]
username = __token__
password = <PyPI token>
```

(Use `[testpypi]` instead of `[pypi]` if you are uploading to [TestPyPI](https://test.pypi.org/))

Replace `<PyPI token>` with your real PyPI token (which starts with `pypi-`).

(if you don't manually create **$HOME/.pypirc**, you will be prompted for a username (which should be `__token__`) and password (which should be your PyPI token) when you run Twine)

### Upload

Run Twine to upload all of the archives under **dist** folder:

```bash
python -m twine upload --repository pypi dist/*
```

(use `testpypi` instead of `pypi` if you are uploading to [TestPyPI](https://test.pypi.org/))

### Update

When you finished developing a newer version of your package, do the following things.

Modify the version number `__version__` in **src\examplepy\_\_init\_\_.py**.

Delete all old versions in **dist**.

Run the following command again to regenerate **dist**:

```bash
python setup.py sdist bdist_wheel
```

Run the following command again to upload **dist**:

```bash
python -m twine upload --repository pypi dist/*
```

(use `testpypi` instead of `pypi` if needed)
`