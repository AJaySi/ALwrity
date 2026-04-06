#!/usr/bin/env bash
set -euo pipefail

python -m pip install --upgrade pip setuptools wheel

# Check if podcast-only mode is enabled - skip heavy ML models if so
ENABLED_FEATURES="${ALWRITY_ENABLED_FEATURES:-all}"
IS_PODCAST_ONLY=false

if [[ "$ENABLED_FEATURES" == "podcast" ]]; then
    IS_PODCAST_ONLY=true
    echo "🔊 Podcast-only mode detected - skipping spaCy/NLTK model download"
fi

python -m pip install --retries 10 --timeout 120 -r requirements.txt

# Download required NLTK and spaCy models during build phase (skip for podcast-only)
if [[ "$IS_PODCAST_ONLY" == "false" ]]; then
    python -m spacy download en_core_web_sm
    python -m nltk.downloader punkt_tab stopwords averaged_perceptron_tagger
else
    echo "🔊 Skipping spaCy/NLTK download for podcast-only mode"
fi
