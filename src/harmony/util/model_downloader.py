'''
MIT License

Copyright (c) 2023 Ulster University (https://www.ulster.ac.uk).
Project: Harmony (https://harmonydata.ac.uk)
Maintainer: Thomas Wood (https://fastdatascience.com)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''

import os
import shutil
import sys
import tarfile

import wget


def bar_custom(current, total, width=80):
    """
    Display a progress bar to track the download.
    :param current: Current bytes downloaded
    :param total: Total bytes.
    :param width: Width of the bar in chars.
    """
    print("Downloading: %d%% [%d / %d] bytes" % (current / total * 100, current, total), end="\r")


def download_models(is_force=False):
    """
    Downloads spaCy models to local path HARMONY_SPACY_PATH, defaulting to home directory.
    """
    local_path = os.getenv("HARMONY_SPACY_PATH", os.path.expanduser("~") + "/harmony")

    print(
        "Downloading spaCy models to " + local_path + ".\nSet environment variable HARMONY_SPACY_PATH if you want to change model file location.")

    # Base URL of the model files in Azure Blob Storage static hosted site.
    url = "https://harmonyapistorage.z33.web.core.windows.net/harmony_spacy_models.tar.bz2"

    if os.path.exists(local_path + "/harmony_spacy_models"):
        if not is_force:
            print("Error: Path already exists on your computer: ", local_path + "/harmony_spacy_models")
            print("Exiting spaCy model downloader.\nRun download_models(True) to force redownload.")
            return
        else:
            print("Removing ", local_path + "/harmony_spacy_models")
            shutil.rmtree(local_path + "/harmony_spacy_models")
            print("Removed ", local_path + "/harmony_spacy_models")

    if not os.path.exists(local_path):
        os.makedirs(local_path)

    tmpfile = local_path + "/harmony_spacy_models.tar.bz2"

    print(f"Downloading {url} to {tmpfile}...")

    wget.download(url, out=tmpfile, bar=bar_custom)

    print(f"Downloaded {url} to {tmpfile}.")
    print(f"Unzipping {tmpfile}...")

    file = tarfile.open(tmpfile)
    file.extractall(local_path)

    print(f"\tWrote models to {local_path}")

    print(f"Deleting {tmpfile}...")
    os.remove(tmpfile)
    print(f"Deleted {tmpfile}.")


if __name__ == "__main__":
    print("Usage: python model_downloader.py --force [if you want to force overwrite of existing folder]")
    is_force = False
    if len(sys.argv) > 1 and "force" in sys.argv[1]:
        is_force = True
    download_models(is_force)
