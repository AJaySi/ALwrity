#!/usr/bin/env bash
set -euo pipefail

echo "🚀 Starting ALwrity Build Process..."

# 1. Update pip and essential build tools
python -m pip install --upgrade pip setuptools wheel

# 2. Install requirements based on mode
echo "📦 Checking ALWRITY_ENABLED_FEATURES..."
ENABLED_FEATURES="${ALWRITY_ENABLED_FEATURES:-all}"
echo "DEBUG: ENABLED_FEATURES='$ENABLED_FEATURES'"

case "$ENABLED_FEATURES" in
    all)
        echo "📦 Full mode: Installing all requirements..."
        python -m pip install --no-cache-dir -r requirements.txt --only-binary :all: --retries 10 --timeout 120
        # Download spaCy/NLTK models for full mode
        echo "🧠 Installing spaCy and NLTK models..."
        python -m spacy download en_core_web_sm
        python -m nltk.downloader punkt_tab stopwords averaged_perceptron_tagger
        ;;
    podcast)
        echo "🔊 Podcast-only mode: Installing lean requirements..."
        python -m pip install --no-cache-dir -r requirements-podcast.txt --only-binary :all: --retries 10 --timeout 120
        ;;
    *)
        echo "🎯 Feature-limited mode ($ENABLED_FEATURES): Installing requirements..."
        req_file="requirements-${ENABLED_FEATURES}.txt"
        if [[ -f "$req_file" ]]; then
            python -m pip install --no-cache-dir -r "$req_file" --only-binary :all: --retries 10 --timeout 120
        else
            echo "⚠️  No feature-specific requirements file found ($req_file), installing full requirements..."
            python -m pip install --no-cache-dir -r requirements.txt --only-binary :all: --retries 10 --timeout 120
        fi
        ;;
esac

# 3. Clean up unnecessary build artifacts
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
rm -rf /root/.cache/pip 2>/dev/null || true

echo "✅ Build Complete!"
