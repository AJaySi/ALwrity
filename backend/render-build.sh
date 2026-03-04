#!/usr/bin/env bash
set -euo pipefail

python -m pip install --upgrade pip setuptools wheel
python -m pip install --retries 10 --timeout 120 -r requirements.txt

# Download required NLTK and spaCy models during build phase
python -m spacy download en_core_web_sm
python -m nltk.downloader punkt_tab stopwords averaged_perceptron_tagger
