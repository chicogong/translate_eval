# Translation Evaluation API Documentation

## Overview

The Translation Evaluation API provides endpoints for translating text and evaluating translation quality using AI Large Language Models (LLMs). The API supports 20 languages with 240 translation directions, plus text-to-speech synthesis and batch processing capabilities.

## Base URL

```
http://localhost:8888
```

## Authentication

API keys are configured via environment variables. No authentication headers are required for API calls.

## Supported Languages

| Code | Language | Native Name | Flag |
|------|----------|-------------|------|
| `en` | English | English | 🇺🇸 |
| `zh` | Chinese | 中文 | 🇨🇳 |
| `ja` | Japanese | 日本語 | 🇯🇵 |
| `pt` | Portuguese | Português | 🇧🇷 |
| `es` | Spanish | Español | 🇪🇸 |
| `fr` | French | Français | 🇫🇷 |
| `de` | German | Deutsch | 🇩🇪 |
| `it` | Italian | Italiano | 🇮🇹 |
| `ko` | Korean | 한국어 | 🇰🇷 |
| `ru` | Russian | Русский | 🇷🇺 |
| `nl` | Dutch | Nederlands | 🇳🇱 |
| `sv` | Swedish | Svenska | 🇸🇪 |
| `no` | Norwegian | Norsk | 🇳🇴 |
| `da` | Danish | Dansk | 🇩🇰 |
| `fi` | Finnish | Suomi | 🇫🇮 |
| `pl` | Polish | Polski | 🇵🇱 |
| `cs` | Czech | Čeština | 🇨🇿 |
| `hu` | Hungarian | Magyar | 🇭🇺 |
| `tr` | Turkish | Türkçe | 🇹🇷 |
| `ar` | Arabic | العربية | 🇦🇷 |

## API Endpoints

### 1. Translate Text

Translate text from one language to another using AI LLM models.

**Endpoint:** `POST /api/translate`

**Request Body:**
```json
{
  "source_lang": "en",
  "target_lang": "zh", 
  "text": "The novel algorithm leverages machine learning techniques."
}
```

**Parameters:**
- `source_lang` (string, required): Source language code
- `target_lang` (string, required): Target language code  
- `text` (string, required): Text to translate

**Response:**
```json
{
  "success": true,
  "translation": "这种新颖的算法利用机器学习技术。"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Source and target languages must be different"
}
```

**Example Usage:**
```bash
curl -X POST http://localhost:8888/api/translate \
  -H "Content-Type: application/json" \
  -d '{
    "source_lang": "en",
    "target_lang": "zh",
    "text": "Hello world"
  }'
```

### 2. Evaluate Translation

Evaluate the quality of a translation using AI LLM evaluation models.

**Endpoint:** `POST /api/evaluate`

**Request Body:**
```json
{
  "source_lang": "en",
  "target_lang": "zh",
  "source_text": "The novel algorithm leverages machine learning techniques.",
  "translation": "这种新颖的算法利用机器学习技术。"
}
```

**Parameters:**
- `source_lang` (string, required): Source language code
- `target_lang` (string, required): Target language code
- `source_text` (string, required): Original text
- `translation` (string, required): Translation to evaluate

**Response:**
```json
{
  "success": true,
  "score": 9,
  "justification": "Excellent translation with accurate technical terminology and natural flow."
}
```

**Scoring Scale:**
- 1-3: Poor (major errors in meaning or fluency)
- 4-6: Fair (some errors but generally understandable)
- 7-8: Good (minor errors, mostly accurate)
- 9-10: Excellent (near-perfect or perfect translation)

**Example Usage:**
```bash
curl -X POST http://localhost:8888/api/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "source_lang": "en",
    "target_lang": "zh", 
    "source_text": "Hello world",
    "translation": "你好世界"
  }'
```

### 3. Text-to-Speech (TTS)

Convert text to speech using MiniMax T2A V2 API.

**Endpoint:** `POST /api/tts`

**Request Body:**
```json
{
  "text": "Hello world",
  "language": "en"
}
```

**Parameters:**
- `text` (string, required): Text to convert to speech
- `language` (string, required): Language code (en, zh, ja, pt, es)

**Response:**
```json
{
  "success": true,
  "audio_data": "base64_encoded_audio_data",
  "format": "mp3",
  "voice_id": "male-qn-qingse",
              "text_length": 11
}
```

**Timing Fields:**
- `ttft_ms`: Time to First Token in milliseconds (only for translation API)

**Example Usage:**
```bash
curl -X POST http://localhost:8888/api/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello world",
    "language": "en"
  }'
```

### 4. Get TTS Voices

Get available TTS voices for a language.

**Endpoint:** `GET /api/tts/voices`

**Query Parameters:**
- `language` (string, optional): Language code to filter voices

**Response:**
```json
{
  "success": true,
  "voices": [
    {
      "voice_id": "male-01",
      "name": "Male Voice 1",
      "language": "en"
    }
  ]
}
```

### 5. Get Translation History

Retrieve translation and evaluation history.

**Endpoint:** `GET /api/history`

**Response:**
```json
{
  "success": true,
  "history": [
    {
      "run_id": "20241226_1500",
      "type": "translation",
      "timestamp": "20241226_1500",
      "language_pairs": [
        {
          "pair": "en-zh",
          "items": 15
        }
      ],
      "total_items": 15
    }
  ]
}
```

### 6. Get Available Runs

Retrieve available translation and evaluation runs.

**Endpoint:** `GET /api/available-runs`

**Response:**
```json
{
  "success": true,
  "translation_runs": ["20241226_1500", "20241226_1400"],
  "evaluation_runs": ["20241226_1500", "20241226_1400"]
}
```

**Example Usage:**
```bash
curl http://localhost:8888/api/available-runs
```

### 7. Get Evaluation Results

Retrieve evaluation results for a specific run and language pair.

**Endpoint:** `GET /api/evaluation-results`

**Query Parameters:**
- `eval_run_id` (string, required): Evaluation run ID (format: YYYYMMDD_HHMM)
- `source_lang` (string, required): Source language code
- `target_lang` (string, required): Target language code

**Response:**
```json
{
  "success": true,
  "eval_run_id": "20241226_1500",
  "avg_score": 8.5,
  "avg_bleu": 0.78,
  "count": 3,
  "results": [
    {
      "line_number": 1,
      "evaluation_score": 9,
      "bleu_score": 0.82,
      "source_text": "The novel algorithm...",
      "translation": "这种新颖的算法...",
      "justification": "Excellent translation..."
    }
  ]
}
```

**Example Usage:**
```bash
curl "http://localhost:8888/api/evaluation-results?eval_run_id=20241226_1500&source_lang=en&target_lang=zh"
```

### 8. Start Batch Translation

Start a batch translation process for a language pair.

**Endpoint:** `POST /api/batch-translate`

**Request Body:**
```json
{
  "source_lang": "en",
  "target_lang": "zh",
  "lines": 15
}
```

**Parameters:**
- `source_lang` (string, required): Source language code
- `target_lang` (string, required): Target language code
- `lines` (integer, optional): Number of lines to process (default: 15)

**Response:**
```json
{
  "success": true,
  "run_id": "20241226_1600",
  "message": "Batch translation started for en-zh",
  "processed": 15
}
```

**Example Usage:**
```bash
curl -X POST http://localhost:8888/api/batch-translate \
  -H "Content-Type: application/json" \
  -d '{
    "source_lang": "en",
    "target_lang": "zh",
    "lines": 10
  }'
```

### 9. Start Batch Evaluation

Start a batch evaluation process for translated content.

**Endpoint:** `POST /api/batch-evaluate`

**Request Body:**
```json
{
  "source_lang": "en", 
  "target_lang": "zh",
  "translation_run_id": "20241226_1500"
}
```

**Parameters:**
- `source_lang` (string, required): Source language code
- `target_lang` (string, required): Target language code
- `translation_run_id` (string, required): ID of the translation run to evaluate

**Response:**
```json
{
  "success": true,
  "eval_run_id": "20241226_1600",
  "translation_run_id": "20241226_1500", 
  "message": "Batch evaluation started for en-zh",
  "processed": 15
}
```

**Example Usage:**
```bash
curl -X POST http://localhost:8888/api/batch-evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "source_lang": "en",
    "target_lang": "zh",
    "translation_run_id": "20241226_1500"
  }'
```

### 10. Get Examples

Get example sentences for testing translation quality.

**Endpoint:** `GET /api/examples`

**Query Parameters:**
- `language` (string, optional): Language code to filter examples (e.g., 'en', 'zh', 'ja')

**Response (All Examples):**
```json
{
  "success": true,
  "languages": ["en", "zh", "ja", "es", "pt", "ko", "fr", "de", "it", "ru", "nl", "sv", "no", "da", "fi", "pl", "cs", "hu", "tr", "ar"],
  "examples": {
    "en": [
      {
        "label": "Polysemy & Ambiguity",
        "texts": [
          "The bank by the river was closed.",
          "I saw her duck under the table."
        ]
      }
    ]
  }
}
```

**Response (Specific Language):**
```json
{
  "success": true,
  "language": "en",
  "examples": [
    {
      "label": "Polysemy & Ambiguity",
      "texts": [
        "The bank by the river was closed.",
        "I saw her duck under the table."
      ]
    }
  ]
}
```

### 11. Playground Run

Run translation and evaluation for multiple texts in real-time.

**Endpoint:** `POST /api/playground-run`

**Request Body:**
```json
{
  "source_lang": "en",
  "target_lang": "zh",
  "texts": ["Hello world", "How are you?"]
}
```

**Parameters:**
- `source_lang` (string, required): Source language code
- `target_lang` (string, required): Target language code
- `texts` (array, required): Array of texts to process (max 20)

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "source_text": "Hello world",
      "translation": "你好世界",
      "evaluation_score": 9,
      "justification": "Excellent translation"
    }
  ],
  "avg_score": 8.5
}
```

## Error Handling

All API endpoints return JSON responses with a `success` field indicating the operation status.

**Error Response Format:**

```json
{
  "success": false,
  "error": "API key not found or invalid"
}
```

**Common Error Responses:**

```json
{
  "success": false,
  "error": "Missing required parameters"
}
```

```json
{
  "success": false, 
  "error": "Source and target languages must be different"
}
```

```json
{
  "success": false,
  "error": "API key not found or invalid"
}
```

## Rate Limiting

The API implements request delays to avoid overwhelming external translation services. Default delays:
- Translation requests: 1.0 second between calls
- Evaluation requests: 1.0 second between calls
- TTS requests: 0.5 second between calls

## File Structure

Results are organized by timestamp-based run IDs:

```
data/
├── translations/
│   └── YYYYMMDD_HHMM/
│       └── lang-pair/
│           └── line_N_translation.json
└── evaluations/
    └── YYYYMMDD_HHMM/
        └── lang-pair/
            └── line_N_evaluation.json
```

## Sample Integration

### Python Example

```python
import requests
import json

# Translate text
def translate_text(text, source_lang, target_lang):
    url = "http://localhost:8888/api/translate"
    data = {
        "source_lang": source_lang,
        "target_lang": target_lang,
        "text": text
    }
    response = requests.post(url, json=data)
    return response.json()

# Evaluate translation
def evaluate_translation(source_text, translation, source_lang, target_lang):
    url = "http://localhost:8888/api/evaluate"
    data = {
        "source_lang": source_lang,
        "target_lang": target_lang,
        "source_text": source_text,
        "translation": translation
    }
    response = requests.post(url, json=data)
    return response.json()

# Text-to-speech
def text_to_speech(text, language):
    url = "http://localhost:8888/api/tts"
    data = {
        "text": text,
        "language": language
    }
    response = requests.post(url, json=data)
    return response.json()

# Usage
result = translate_text("Hello world", "en", "zh")
if result["success"]:
    translation = result["translation"]
    
    eval_result = evaluate_translation("Hello world", translation, "en", "zh")
    if eval_result["success"]:
        print(f"Score: {eval_result['score']}/10")
        print(f"Justification: {eval_result['justification']}")
    
    tts_result = text_to_speech(translation, "zh")
    if tts_result["success"]:
        print(f"Audio generated: {tts_result['format']}")
```

### JavaScript Example

```javascript
// Translate text
async function translateText(text, sourceLang, targetLang) {
    const response = await fetch('/api/translate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            source_lang: sourceLang,
            target_lang: targetLang,
            text: text
        })
    });
    return await response.json();
}

// Evaluate translation
async function evaluateTranslation(sourceText, translation, sourceLang, targetLang) {
    const response = await fetch('/api/evaluate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            source_lang: sourceLang,
            target_lang: targetLang,
            source_text: sourceText,
            translation: translation
        })
    });
    return await response.json();
}

// Text-to-speech
async function textToSpeech(text, language) {
    const response = await fetch('/api/tts', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            text: text,
            language: language
        })
    });
    return await response.json();
}

// Usage
translateText("Hello world", "en", "zh")
    .then(result => {
        if (result.success) {
            const translation = result.translation;
            return Promise.all([
                evaluateTranslation("Hello world", translation, "en", "zh"),
                textToSpeech(translation, "zh")
            ]);
        }
    })
    .then(([evalResult, ttsResult]) => {
        if (evalResult.success) {
            console.log(`Score: ${evalResult.score}/10`);
            console.log(`Justification: ${evalResult.justification}`);
        }
        if (ttsResult.success) {
            console.log(`Audio generated: ${ttsResult.format}`);
        }
    });
```

## Configuration

The API requires environment variables for external service configuration:

```bash
# Translation API Configuration (Required for translation)
TRANSLATION_API_KEY=your_translation_api_key
TRANSLATION_API_URL=https://api.openai.com/v1/chat/completions
TRANSLATION_MODEL=gpt-4

# Evaluation API Configuration (Required for evaluation)
EVALUATION_API_KEY=your_evaluation_api_key
EVALUATION_API_URL=https://api.openai.com/v1/chat/completions
EVALUATION_MODEL=gpt-4

# MiniMax TTS API Configuration (Optional for TTS)
MINIMAX_API_KEY=your_minimax_api_key
MINIMAX_GROUP_ID=your_minimax_group_id

# Server Configuration
FLASK_HOST=127.0.0.1
FLASK_PORT=8888
FLASK_ENV=production
```

## Getting Started

1. Install dependencies: `pip install -r requirements.txt`
2. Configure environment variables in `.env` file
3. Start the server: `python run_app.py`
4. Access the API at `http://localhost:8888`
5. Visit the dashboard at `http://localhost:8888/batch` 