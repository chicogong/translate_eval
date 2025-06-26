# 翻译评估工具 (Translation Evaluation Tool)

一个功能完整的多语言翻译评估平台，支持实时翻译、智能评估、语音合成和批量处理。

## ✨ 主要功能

### 🌐 多语言翻译
- **支持语言**: 中文、英文、日文、葡萄牙语、西班牙语
- **自动检测**: 智能识别源语言
- **实时翻译**: 基于DeepSeek API的高质量翻译
- **批量处理**: 支持10并发的批量翻译

### 📊 智能评估系统
- **多维度评估**: 语义准确度、BLEU分数、流畅度、综合评分
- **实时评分**: 1-10分评分制，提供详细评估理由
- **统计分析**: 平均分数、流畅度率等统计指标
- **历史追踪**: 完整的翻译和评估历史记录

### 🎵 语音合成 (TTS)
- **MiniMax集成**: 基于MiniMax T2A V2 API
- **多语言支持**: 针对不同语言优化的声音选择
- **实时播放**: 支持源文本和翻译结果的语音播放
- **智能优化**: 自动处理文本长度和编码问题

### 🎮 交互式界面
- **翻译游乐场**: 现代化的Web界面，支持文件上传
- **拖拽上传**: 支持.txt文件的拖拽式上传
- **响应式设计**: 完美适配桌面和移动设备
- **实时图表**: 使用Chart.js展示评估统计

## 🚀 快速开始

### 环境要求
- Python 3.8+
- pip (Python包管理器)

### 安装步骤

1. **克隆项目**
```bash
git clone 
cd translate_eval
```

2. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
创建 `.env` 文件或设置环境变量：
```bash
# DeepSeek API (必需)
DEEPSEEK_API_KEY=your_deepseek_api_key

# MiniMax TTS API (可选，用于语音功能)
MINIMAX_API_KEY=your_minimax_api_key
MINIMAX_GROUP_ID=your_minimax_group_id

# 自定义端口 (可选，默认8888)
FLASK_PORT=8889
```

5. **启动应用**
```bash
python run_app.py
```

6. **访问应用**
打开浏览器访问: http://127.0.0.1:8888

## 📖 使用指南

### 基础翻译
1. 在源文本框输入要翻译的文本
2. 选择源语言和目标语言（支持自动检测）
3. 点击"翻译"按钮
4. 查看翻译结果和评估分数

### 语音功能
1. 完成翻译后，点击播放按钮 🔊
2. 支持播放源文本和翻译结果
3. 自动选择适合的语音模型

### 文件上传
1. 拖拽.txt文件到上传区域
2. 或点击上传区域选择文件
3. 系统自动读取文件内容到文本框

### 批量处理
1. 访问 `/batch` 页面
2. 选择语言对和示例文本
3. 点击"翻译 & 评估"进行批量处理
4. 查看统计图表和历史记录

## 🛠️ API接口

### 翻译接口
```bash
POST /api/translate
Content-Type: application/json

{
    "source_lang": "zh",
    "target_lang": "en", 
    "text": "你好世界"
}
```

### 评估接口
```bash
POST /api/evaluate
Content-Type: application/json

{
    "source_lang": "zh",
    "target_lang": "en",
    "source_text": "你好世界",
    "translation": "Hello world"
}
```

### 语音合成接口
```bash
POST /api/tts
Content-Type: application/json

{
    "text": "Hello world",
    "language": "en"
}
```

### 历史记录接口
```bash
GET /api/history
```

更多API文档请参考 [API_DOCS.md](API_DOCS.md)

## 🧪 测试

### 运行所有测试
```bash
python scripts/run_tests.py
```

### 运行特定测试
```bash
# 只运行TTS测试
python scripts/run_tests.py --tts-only

# 只运行编码测试
python scripts/run_tests.py --encoding-only
```

## 📁 项目结构

```
translate_eval/
├── backend/                    # 后端服务
│   ├── app.py                 # Flask主应用
│   ├── batch.py               # 批量处理
│   ├── config.py              # 配置管理
│   ├── services.py            # 翻译/评估服务
│   ├── tts_service.py         # TTS语音服务
│   ├── utils.py               # 工具函数
│   ├── examples.py            # 示例数据
│   ├── templates/             # HTML模板
│   └── static/                # 静态资源
├── scripts/                   # 脚本工具
│   └── run_tests.py          # 测试运行器
├── tests/                     # 测试套件
│   └── test_tts_service.py   # TTS服务测试
├── data/                      # 数据存储
│   ├── translations/         # 翻译结果
│   ├── evaluations/          # 评估结果
│   └── testcases/            # 测试用例
├── evaluation/               # 评估模块
│   └── eval.py              # 独立评估脚本
└── run_app.py               # 应用启动器
```

## ⚙️ 配置说明

### DeepSeek API配置
1. 访问 [DeepSeek平台](https://platform.deepseek.com/)
2. 获取API密钥
3. 设置环境变量 `DEEPSEEK_API_KEY`

### MiniMax TTS配置（可选）
1. 访问 [MiniMax平台](https://www.minimax.chat/)
2. 获取API密钥和Group ID
3. 设置环境变量：
   - `MINIMAX_API_KEY`
   - `MINIMAX_GROUP_ID`

### 端口配置
默认端口为8888，可通过环境变量修改：
```bash
FLASK_PORT=8889 python run_app.py
```

## 🔧 故障排除

### 常见问题

1. **TTS无法播放**
   - 确保MiniMax API配置正确
   - 检查浏览器是否支持音频播放
   - 查看浏览器控制台错误信息

2. **翻译失败**
   - 检查DeepSeek API密钥是否有效
   - 确认网络连接正常
   - 查看日志文件获取详细错误

### 日志查看
日志文件位于 `logs/` 目录下，包含详细的错误信息和调试信息。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

本项目采用MIT许可证，详见 [LICENSE](LICENSE) 文件。

## 🔗 相关链接

- [API接口文档](API_DOCS.md)
- [DeepSeek API文档](https://platform.deepseek.com/api-docs/)
- [MiniMax TTS文档](https://www.minimax.chat/document/guides/T2A)