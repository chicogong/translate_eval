# Translation Evaluation Tool

A modern, open-source platform for multilingual translation, evaluation, and TTS synthesis. All translation and evaluation are powered by AI Large Language Models (LLMs). Supports real-time translation, intelligent evaluation, batch processing, and audio synthesis with a user-friendly web interface.

## Features

- 🌐 **Multilingual Translation (AI LLM-based)**: Translate between major languages using state-of-the-art LLMs
- 🤖 **Automatic Language Detection**
- 🚀 **Batch Translation & Evaluation**
- 📊 **AI-powered Evaluation (LLM-based)**: Semantic accuracy, BLEU, fluency, and overall score
- 🎵 **Text-to-Speech (TTS)**: MiniMax T2A V2 API integration
- 🖥️ **Modern Web UI**: Playground, file upload, history, and statistics
- 📦 **API-first Design**: Easy integration for developers

### Supported Languages

- 🇺🇸 English (`en`)
- 🇨🇳 Chinese (`zh`)
- 🇯🇵 Japanese (`ja`)
- 🇧🇷 Portuguese (`pt`)
- 🇪🇸 Spanish (`es`)
- 🇫🇷 French (`fr`)
- 🇩🇪 German (`de`)
- 🇮🇹 Italian (`it`)
- 🇰🇷 Korean (`ko`)
- 🇷🇺 Russian (`ru`)
- 🇳🇱 Dutch (`nl`)
- 🇸🇪 Swedish (`sv`)
- 🇳🇴 Norwegian (`no`)
- 🇩🇰 Danish (`da`)
- 🇫🇮 Finnish (`fi`)
- 🇵🇱 Polish (`pl`)
- 🇨🇿 Czech (`cs`)
- 🇭🇺 Hungarian (`hu`)
- 🇹🇷 Turkish (`tr`)
- 🇦🇷 Arabic (`ar`)

240 translation directions are supported between these languages.

## Quick Start

### Requirements
- Python 3.8+
- pip

### Installation

```bash
git clone https://github.com/chicogong/translate_eval
cd translate_eval
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration
Set the following environment variables (in your shell or a `.env` file):

```bash
# Required for translation (AI LLM)
deepseek_api_key=your_deepseek_api_key
# Optional for TTS
minimax_api_key=your_minimax_api_key
minimax_group_id=your_minimax_group_id
# Optional: custom port
FLASK_PORT=8888
```

### Run the App

```bash
# Development (default: http://127.0.0.1:8888)
python run_app.py

# Production
FLASK_ENV=production FLASK_HOST=0.0.0.0 python run_app.py
```

Open your browser at [http://127.0.0.1:8888](http://127.0.0.1:8888)

## API Overview

See [API_DOCS.md](API_DOCS.md) for full details.

- `POST /api/translate` — Translate text (AI LLM)
- `POST /api/evaluate` — Evaluate translation (AI LLM)
- `POST /api/tts` — Text-to-speech synthesis
- `GET /api/history` — Translation & evaluation history

## Project Structure

```
translate_eval/
├── backend/           # Backend Flask app & services
│   ├── app.py
│   ├── batch.py
│   ├── config.py
│   ├── services.py
│   ├── tts_service.py
│   ├── utils.py
│   ├── examples.py
│   ├── templates/
│   └── static/
├── scripts/           # Test runner
├── tests/             # Unit tests
├── data/              # Translation/evaluation data
├── evaluation/        # Evaluation scripts
├── logs/              # Log files
├── Dockerfile         # Docker build config
├── requirements.txt
├── run_app.py         # App launcher
└── API_DOCS.md        # API documentation
```

## Contributing

Contributions are welcome! Please open issues or pull requests to help improve this project.

## License

MIT License. See [LICENSE](LICENSE) for details.