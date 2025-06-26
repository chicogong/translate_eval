# Translation Evaluation API Documentation

## Overview

The Translation Evaluation API provides endpoints for translating text and evaluating translation quality using AI models. The API supports 5 languages (English, Chinese, Japanese, Portuguese, Spanish) with 20 translation directions.

## Base URL

```
http://localhost:8888
```

## Authentication

API keys are configured via environment variables. No authentication headers are required for API calls.

## Supported Languages

| Code | Language | Native Name |
|------|----------|-------------|
| `en` | English | English |
| `zh` | Chinese | 中文 |
| `ja` | Japanese | 日本語 |
| `pt` | Portuguese | Português |
| `es` | Spanish | Español |

## API Endpoints

### 1. Translate Text

Translate text from one language to another using AI translation models.

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

Evaluate the quality of a translation using AI evaluation models.

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

### 3. Get Available Runs

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

### 4. Get Evaluation Results

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

### 5. Start Batch Translation

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

### 6. Start Batch Evaluation

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

## Error Handling

All API endpoints return JSON responses with a `success` field indicating the operation status.

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
  "error": "Translation API key not found"
}
```

## Rate Limiting

The API implements request delays to avoid overwhelming external translation services. Default delays:
- Translation requests: 1.0 second between calls
- Evaluation requests: 1.0 second between calls

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

# Usage
result = translate_text("Hello world", "en", "zh")
if result["success"]:
    translation = result["translation"]
    
    eval_result = evaluate_translation("Hello world", translation, "en", "zh")
    if eval_result["success"]:
        print(f"Score: {eval_result['score']}/10")
        print(f"Justification: {eval_result['justification']}")
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

// Usage
translateText("Hello world", "en", "zh")
    .then(result => {
        if (result.success) {
            const translation = result.translation;
            return evaluateTranslation("Hello world", translation, "en", "zh");
        }
    })
    .then(evalResult => {
        if (evalResult.success) {
            console.log(`Score: ${evalResult.score}/10`);
            console.log(`Justification: ${evalResult.justification}`);
        }
    });
```

## Configuration

The API requires environment variables for external service configuration:

```bash
# Translation API Configuration
TRANSLATION_API_KEY=your_translation_api_key
TRANSLATION_API_URL=https://api.openai.com/v1/chat/completions
TRANSLATION_MODEL=gpt-4

# Evaluation API Configuration  
EVALUATION_API_KEY=your_evaluation_api_key
EVALUATION_API_URL=https://api.openai.com/v1/chat/completions
EVALUATION_MODEL=gpt-4

# Server Configuration
FLASK_HOST=127.0.0.1
FLASK_PORT=8888
FLASK_DEBUG=True
```

## Getting Started

1. Install dependencies: `pip install -r requirements.txt`
2. Configure environment variables in `.env` file
3. Start the server: `python run_app.py`
4. Access the API at `http://localhost:8888`
5. Visit the dashboard at `http://localhost:8888/batch` 