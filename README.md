# Translation Evaluation Tool

一个基于AI的翻译质量评估工具，支持多语言翻译和自动化质量评估。

## 🌟 特性

- **多语言支持**: 支持英语、中文、日语、葡萄牙语、西班牙语之间的互译（20个翻译方向）
- **AI驱动评估**: 使用大语言模型进行翻译质量评估，提供1-10分评分和详细反馈
- **批量处理**: 支持批量翻译和评估，提高工作效率
- **现代化界面**: 美观的Web界面，支持实时批量操作和结果可视化
- **完整API**: RESTful API接口，支持程序化调用

## 🚀 快速开始

### 1. 安装和配置

```bash
# 安装依赖
pip install -r requirements.txt

# 配置API密钥
cp .env.example .env
# 编辑 .env 文件，添加你的API密钥
```

### 2. 启动应用

```bash
python run_app.py
```

### 3. 访问应用

- **主界面**: http://localhost:8888 - 单次翻译和评估
- **批量仪表板**: http://localhost:8888/batch - 批量操作和结果分析

## 📁 项目结构

```
translate_eval/
├── backend/                 # Flask后端应用
│   ├── app.py              # 主应用文件（包含所有API端点和提示词）
│   ├── templates/          # HTML模板
│   └── static/             # 静态资源（CSS、JS）
├── data/                   # 数据存储
│   ├── translations/       # 翻译结果（按时间戳组织）
│   ├── evaluations/        # 评估结果（按时间戳组织）
│   └── testcases/          # 测试用例（各语言）
├── scripts/                # 工具脚本
│   ├── translate_single.py # 单次翻译脚本
│   ├── evaluate_single.py  # 单次评估脚本
│   └── batch_operations.py # 批量操作脚本
├── evaluation/             # 评估模块
│   └── eval.py            # 核心评估逻辑
├── API_DOCS.md            # 完整API文档
└── run_app.py             # 应用启动入口
```

## 💻 使用方法

### Web界面操作

1. **单次翻译**: 访问主界面，输入文本进行翻译和评估
2. **批量操作**: 访问批量仪表板，选择语言对后点击"Translate"或"Evaluate"按钮
3. **查看结果**: 在批量仪表板中查看评估统计和详细结果

### 命令行操作

```bash
# 翻译
python scripts/translate_single.py en zh --lines 5

# 评估（使用上一步的运行ID）
python scripts/evaluate_single.py en zh 20241226_1400

# 批量操作
python scripts/batch_operations.py translate-all
python scripts/batch_operations.py evaluate-all --translation-run-id 20241226_1400
```

## 🔧 API使用

详细的API文档请查看 [API_DOCS.md](API_DOCS.md)

### 基本API调用示例

```python
import requests

# 翻译
response = requests.post('http://localhost:8888/api/translate', json={
    'source_lang': 'en',
    'target_lang': 'zh', 
    'text': 'Hello world'
})

# 评估
response = requests.post('http://localhost:8888/api/evaluate', json={
    'source_lang': 'en',
    'target_lang': 'zh',
    'source_text': 'Hello world',
    'translation': '你好世界'
})
```

## ⚙️ 配置

在 `.env` 文件中配置API密钥：

```env
# 翻译API配置
TRANSLATION_API_KEY=your_api_key
TRANSLATION_API_URL=https://api.openai.com/v1/chat/completions
TRANSLATION_MODEL=gpt-4

# 评估API配置
EVALUATION_API_KEY=your_api_key
EVALUATION_API_URL=https://api.openai.com/v1/chat/completions
EVALUATION_MODEL=gpt-4

# 服务器配置
FLASK_HOST=127.0.0.1
FLASK_PORT=8888
FLASK_DEBUG=True
```

## 📊 支持的语言

| 代码 | 语言 | 原生名称 |
|------|------|----------|
| `en` | English | English |
| `zh` | Chinese | 中文 |
| `ja` | Japanese | 日本語 |
| `pt` | Portuguese | Português |
| `es` | Spanish | Español |

## 🎯 评分标准

- **1-3分**: 差（意思错误或不流畅）
- **4-6分**: 一般（有错误但可理解）
- **7-8分**: 好（轻微错误，基本准确）
- **9-10分**: 优秀（接近完美或完美翻译）

## 📝 数据组织

结果按时间戳组织，格式为 `YYYYMMDD_HHMM`：

```
data/
├── translations/20241226_1500/en-zh/line_1_translation.json
├── evaluations/20241226_1500/en-zh/line_1_evaluation.json
└── testcases/en/test_suite.txt
```

## 🔍 故障排除

1. **API密钥错误**: 检查 `.env` 文件中的API密钥配置
2. **端口占用**: 修改 `.env` 中的 `FLASK_PORT` 设置
3. **依赖问题**: 运行 `pip install -r requirements.txt` 重新安装依赖
4. **网络问题**: 确保API端点可访问

## 📄 许可证

MIT License