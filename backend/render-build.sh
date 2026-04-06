#!/usr/bin/env bash
set -euo pipefail

python -m pip install --upgrade pip setuptools wheel

# Check if podcast-only mode is enabled
ENABLED_FEATURES="${ALWRITY_ENABLED_FEATURES:-all}"

if [[ "$ENABLED_FEATURES" == "podcast" ]]; then
    echo "🔊 Podcast-only mode - installing minimal dependencies"
    # Create minimal requirements on-the-fly
    cat > requirements_min.txt << 'EOF'
fastapi>=0.115.14
starlette>=0.40.0,<0.47.0
sse-starlette<3.0.0
uvicorn>=0.24.0
uvicorn[standard]>=0.24.0
python-multipart>=0.0.6
python-dotenv>=1.0.0
loguru>=0.7.2
tenacity>=8.2.3
pydantic>=2.5.2,<3.0.0
typing-extensions>=4.8.0
PyJWT>=2.8.0
cryptography>=41.0.0
fastapi-clerk-auth>=0.0.7
sqlalchemy>=2.0.25
stripe>=8.0.0
httpx>=0.27.2,<0.28.0
openai>=1.3.0
google-genai>=1.0.0
gtts>=2.4.0
pyttsx3>=2.90
markdown>=3.5.0
pandas>=2.0.0
numpy>=1.24.0
Pillow>=10.0.0
huggingface_hub>=1.1.4
moviepy==2.1.2
imageio>=2.31.0
imageio-ffmpeg>=0.4.9
pytest>=7.4.0
pytest-asyncio>=0.21.0
apscheduler>=3.10.0
redis>=5.0.0
schedule>=1.2.0
EOF
    python -m pip install --retries 10 --timeout 120 -r requirements_min.txt
else
    echo "📦 Full mode - installing all dependencies"
    python -m pip install --retries 10 --timeout 120 -r requirements.txt
    # Download spaCy/NLTK models for full mode
    python -m spacy download en_core_web_sm
    python -m nltk.downloader punkt_tab stopwords averaged_perceptron_tagger
fi

echo "✅ Build dependencies installed"
