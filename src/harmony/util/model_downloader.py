import os
import shutil
import tarfile
import wget
import sys

def bar_custom(current, total, width=80):
    print("Downloading: %d%% [%d / %d] bytes" % (current / total * 100, current, total), end="\r")

# List of model files that constitute the spaCy models.

def download_models(is_force=False):
    """
    Downloads spaCy models to local.
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
    print ("Usage: python model_downloader.py --force [if you want to force overwrite of existing folder]")
    is_force = False
    if len(sys.argv) > 1 and "force" in sys.argv[1]:
        is_force = True
    download_models(is_force)
