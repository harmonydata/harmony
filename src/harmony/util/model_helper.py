import os
import requests

# List of model files that constitute the spaCy models.

files = ["11_ner_0_spacy/model-best/config.cfg",
"11_ner_0_spacy/model-best/meta.json",
"11_ner_0_spacy/model-best/ner/cfg",
"11_ner_0_spacy/model-best/ner/model",
"11_ner_0_spacy/model-best/ner/moves",
"11_ner_0_spacy/model-best/tok2vec/.gitattributes",
"11_ner_0_spacy/model-best/tok2vec/cfg",
"11_ner_0_spacy/model-best/tok2vec/model",
"11_ner_0_spacy/model-best/tokenizer",
"11_ner_0_spacy/model-best/vocab/key2row",
"11_ner_0_spacy/model-best/vocab/lookups.bin",
"11_ner_0_spacy/model-best/vocab/strings.json",
"11_ner_0_spacy/model-best/vocab/vectors",
"11_ner_0_spacy/model-best/vocab/vectors.cfg",
"29_classifier_spacy/model-best/.gitattributes",
"29_classifier_spacy/model-best/config.cfg",
"29_classifier_spacy/model-best/meta.json",
"29_classifier_spacy/model-best/textcat/cfg",
"29_classifier_spacy/model-best/textcat/model",
"29_classifier_spacy/model-best/tok2vec/cfg",
"29_classifier_spacy/model-best/tok2vec/model",
"29_classifier_spacy/model-best/tokenizer",
"29_classifier_spacy/model-best/vocab/key2row",
"29_classifier_spacy/model-best/vocab/lookups.bin",
"29_classifier_spacy/model-best/vocab/strings.json",
"29_classifier_spacy/model-best/vocab/vectors",
"29_classifier_spacy/model-best/vocab/vectors.cfg",
]
def download_models(is_force=False):
    """
    Downloads spaCy models to local.
    """
    local_path = os.getenv("HARMONY_DATA_PATH", os.path.expanduser("~") + "/harmony")

    print ("Downloading spaCy models to " + local_path + ".\nSet environment variable HARMONY_DATA_PATH if you want to change model file location.")

    # Base URL of the model files in Git LFS.
    remote_base = "https://media.githubusercontent.com/media/harmonydata/models/main/"

    for file_to_download in files:
        url = remote_base + file_to_download
        local_filename = local_path + "/" + file_to_download
        if os.path.exists(local_filename) and not is_force:
            print ("Error: File already exists on your computer: ", local_filename)
            print ("Exiting spaCy model downloader.\nRun download_models(True) to force redownload.")
            break

        print (f"Downloading {url}...")
        r = requests.get(url)

        if not os.path.isdir(os.path.dirname(local_filename)):
            os.makedirs(os.path.dirname(local_filename))

        with open(local_filename, 'wb') as f:
            f.write(r.content)
        print(f"\tWrote to {local_filename}")