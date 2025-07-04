# Multi-Model Translation Configuration

This document explains how to configure multiple translation models for comparison and evaluation.

## Configuration Method

Add the following environment variables to your `.env` file or set them as system environment variables.

### Multi-Model Configuration (No Limit)

For each model, you need to configure the following variables where `N` is the model number (1, 2, 3, ...):

```bash
# Model N Configuration
TRANSLATION_API_KEY_N=your-api-key
TRANSLATION_API_URL_N=your-api-url
TRANSLATION_MODEL_N=your-model-name
TRANSLATION_MODEL_NAME_N=display-name-for-model  # Optional, defaults to model name
TRANSLATION_STREAM_N=true                          # Optional, defaults to true
TRANSLATION_TEMPERATURE_N=0.0                     # Optional, defaults to 0.0
TRANSLATION_MAX_LENGTH_N=16384                    # Optional, defaults to 16384
TRANSLATION_TOP_P_N=1.0                           # Optional, defaults to 1.0
TRANSLATION_NUM_BEAMS_N=1                         # Optional, defaults to 1
TRANSLATION_DO_SAMPLE_N=false                     # Optional, defaults to false
```

### Multi-Evaluator Configuration (up to 2 evaluators)

For evaluation, you can configure up to 2 different evaluator models:

```bash
# Primary Evaluator
EVALUATION_API_KEY=your-primary-evaluator-key
EVALUATION_API_URL=your-primary-evaluator-url
EVALUATION_MODEL=your-primary-evaluator-model
EVALUATION_MODEL_NAME=Primary Evaluator  # Optional

# Secondary Evaluator (optional)
EVALUATION_API_KEY_2=your-secondary-evaluator-key
EVALUATION_API_URL_2=your-secondary-evaluator-url
EVALUATION_MODEL_2=your-secondary-evaluator-model
EVALUATION_MODEL_NAME_2=Secondary Evaluator  # Optional
```

### Example Configuration

Here's how to configure multiple translation models:

```bash
# Model 1: DeepSeek V3 Local
TRANSLATION_API_KEY_1=xxx
TRANSLATION_API_URL_1=http://xxx.com/llmproxy/chat/completions
TRANSLATION_MODEL_1=xxx
TRANSLATION_MODEL_NAME_1=xxx

# Model 2: Doubao Seed
TRANSLATION_API_KEY_2=xxx
TRANSLATION_API_URL_2=http://xxx.com/llmproxy/chat/completions
TRANSLATION_MODEL_2=xxx
TRANSLATION_MODEL_NAME_2=xxx

# Model 3: Qwen2.5 7B
TRANSLATION_API_KEY_3=xxx
TRANSLATION_API_URL_3=http://xxx.com/llmproxy/chat/completions
TRANSLATION_MODEL_3=xxx
TRANSLATION_MODEL_NAME_3=xxx

# Model 4: Server 259168
TRANSLATION_API_KEY_4=xxx
TRANSLATION_API_URL_4=http://xxx.com/llmproxy/chat/completions
TRANSLATION_MODEL_4=xxx
TRANSLATION_MODEL_NAME_4=xxx

# Model 5: Hunyuan Translation (Special Configuration)
TRANSLATION_API_KEY_5=your-hunyuan-api-key
TRANSLATION_API_URL_5=http://hunyuanapi.xxx.com/openapi/v1/translations
TRANSLATION_MODEL_5=hunyuan-translation-lite
TRANSLATION_MODEL_NAME_5=Hunyuan Translation Lite

# Additional models can be configured by incrementing the number
# Model 6, 7, 8, ... (no limit)
# TRANSLATION_API_KEY_N=your-api-key-n
# TRANSLATION_API_URL_N=your-api-url-n
# TRANSLATION_MODEL_N=your-model-name-n
# TRANSLATION_MODEL_NAME_N=Your Model Display Name N

# Evaluation Models
# Primary Evaluator
EVALUATION_API_KEY=your-primary-evaluator-key
EVALUATION_API_URL=your-primary-evaluator-url
EVALUATION_MODEL=your-primary-evaluator-model
EVALUATION_MODEL_NAME=Primary Judge

# Secondary Evaluator (optional)
EVALUATION_API_KEY_2=your-secondary-evaluator-key
EVALUATION_API_URL_2=your-secondary-evaluator-url
EVALUATION_MODEL_2=your-secondary-evaluator-model
EVALUATION_MODEL_NAME_2=Secondary Judge
```

## Usage

1. **Web Interface**: Navigate to `/compare` or click the "Multi-Model Compare" button in the main interface.

2. **API Endpoints**:
   - `GET /api/models` - Get available models
   - `POST /api/translate/compare` - Compare translations from multiple models
   - `POST /api/evaluate/compare` - Evaluate translations from multiple models
   - `GET /api/examples/<language>` - Get translation challenge examples for specific language

3. **Model Selection**: You can select any number of models for comparison (no limit). The system will process all selected models in parallel.

4. **Evaluation**: After translation, you can evaluate all results with up to 2 different evaluators for comprehensive scoring.

## Features

- **Unlimited Models**: Support for any number of translation models (no artificial limits)
- **Parallel Translation**: All selected models translate simultaneously for faster results
- **Multi-Evaluator Support**: Up to 2 different evaluators can score translations
- **Dynamic Examples**: Language-specific translation challenge examples with common pitfalls
- **Comprehensive Scoring**: Get detailed evaluation from multiple perspectives
- **Error Handling**: Failed translations are clearly marked while successful ones are displayed
- **Copy Functionality**: Easy one-click copying of translation results
- **Responsive Design**: Works well on different screen sizes
- **Modular Architecture**: Hunyuan translation service separated for easy maintenance

## Backward Compatibility

The original single-model and single-evaluator configurations are still supported:

```bash
# Single model
TRANSLATION_API_KEY=your-api-key
TRANSLATION_API_URL=your-api-url
TRANSLATION_MODEL=your-model-name

# Single evaluator
EVALUATION_API_KEY=your-evaluation-api-key
EVALUATION_API_URL=your-evaluation-api-url
EVALUATION_MODEL=your-evaluation-model
```

## Notes

- **No Model Limit**: The system will load all available model configurations (TRANSLATION_API_KEY_1, TRANSLATION_API_KEY_2, ..., TRANSLATION_API_KEY_N)
- Up to 2 evaluators are supported (primary and secondary)
- All three required fields (API_KEY, API_URL, MODEL) must be present for a model/evaluator to be available
- Evaluation results from multiple evaluators are averaged for the final score
- **Translation Challenge Examples**: Each language includes carefully curated examples of common translation pitfalls:
  - Polysemy and ambiguity
  - Idioms and cultural references
  - Complex grammar structures
  - False friends and cognates
  - Modern slang and colloquialisms
- **Hunyuan Translation Support**: Models with 'hunyuan' in the model name or 'hunyuanapi.woa.com' in the API URL will automatically use the Hunyuan translation protocol
- **Special Features**:
  - Hunyuan models support automatic language code mapping (zh → zh-CN, etc.)
  - Moderation can be configured per model (set `moderation: false` in config for faster translation)
  - All models support parallel translation for optimal performance
  - Modular service architecture allows easy addition/removal of special translation services 