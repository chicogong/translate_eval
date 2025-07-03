# Multi-Model Translation Configuration

This document explains how to configure multiple translation models for comparison.

## Configuration Method

Add the following environment variables to your `.env` file or set them as system environment variables.

### Multi-Model Configuration (up to 6 models)

For each model, you need to configure the following variables where `N` is the model number (1-6):

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

### Example Configuration

Based on your provided models, here's how to configure them:

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

# Model 5: Server 261571
TRANSLATION_API_KEY_5=xxx
TRANSLATION_API_URL_5=http://xxx.com/llmproxy/chat/completions
TRANSLATION_MODEL_5=xxx
TRANSLATION_MODEL_NAME_5=xxx

# Model 6: DeepSeek V3 Local II
TRANSLATION_API_KEY_6=xxx
TRANSLATION_API_URL_6=http://xxx.com/llmproxy/chat/completions
TRANSLATION_MODEL_6=xxx
TRANSLATION_MODEL_NAME_6=xxx
```

## Usage

1. **Web Interface**: Navigate to `/compare` or click the "Multi-Model Compare" button in the main interface.

2. **API Endpoints**:
   - `GET /api/models` - Get available models
   - `POST /api/translate/compare` - Compare translations from multiple models

3. **Model Selection**: You can select 2-6 models for comparison. The system will automatically use the first two models by default.

## Features

- **Parallel Translation**: All selected models translate simultaneously for faster results
- **Error Handling**: Failed translations are clearly marked while successful ones are displayed
- **Copy Functionality**: Easy one-click copying of translation results
- **Responsive Design**: Works well on different screen sizes

## Backward Compatibility

The original single-model configuration is still supported:

```bash
TRANSLATION_API_KEY=your-api-key
TRANSLATION_API_URL=your-api-url
TRANSLATION_MODEL=your-model-name
```

If no multi-model configurations are found, the system will fall back to the single model configuration.

## Notes

- Only the first 6 model configurations will be loaded (TRANSLATION_API_KEY_1 through TRANSLATION_API_KEY_6)
- All three required fields (API_KEY, API_URL, MODEL) must be present for a model to be available
- The evaluation model configuration remains unchanged and uses the original `EVALUATION_*` variables 