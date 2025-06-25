# 翻译评估工具 (Translation Evaluation Tool)

一个基于AI的多语言翻译质量评估系统，支持中文、英文、西班牙文、葡萄牙文、日文之间的相互翻译和智能评分。

## 🌟 功能特点

- **🌐 多语言支持**: 支持5种语言的20个翻译方向
- **🤖 AI智能评估**: 使用LLM对翻译质量进行1-10分评分
- **📊 批量评估**: 支持大规模数据集的自动化评估
- **🎨 现代化界面**: 响应式Web界面，支持实时翻译和评估
- **📈 详细报告**: 生成完整的评估报告和统计分析
- **🔧 API接口**: 提供RESTful API供程序化调用

## 🏗️ 项目结构

```
translate_eval/
├── README.md                   # 项目说明文档
├── LICENSE                     # 开源协议
├── .env.example               # 环境变量配置示例
├── .gitignore                 # Git忽略文件配置
├── run_app.py                 # 应用启动脚本
│
├── backend/                   # 后端服务
│   ├── app.py                # Flask Web应用主文件
│   ├── templates/            # HTML模板
│   │   └── index.html       # 主页面模板
│   └── static/               # 静态资源
│       ├── css/
│       │   └── style.css    # 样式文件
│       └── js/
│           └── app.js       # 前端JavaScript
│
├── evaluation/               # 评估系统
│   ├── eval.py              # 批量评估脚本
│   ├── api_test.py          # API连接测试
│   └── prompts/             # 翻译提示词
│       ├── en-zh.txt        # 英文→中文提示词
│       ├── zh-en.txt        # 中文→英文提示词
│       ├── ...              # 其他语言对提示词
│       └── evaluator-prompt.txt # 评估提示词
│
├── data/                     # 数据文件
│   ├── testcases/           # 测试用例
│   │   ├── en/
│   │   │   └── test_suite.txt
│   │   ├── zh/
│   │   │   └── test_suite.txt
│   │   └── ...              # 其他语言测试用例
│   ├── results/             # 翻译结果
│   │   ├── en-zh/           # 英文→中文结果
│   │   ├── zh-en/           # 中文→英文结果
│   │   └── ...              # 其他语言对结果
│   ├── references/          # 参考翻译（用于BLEU评分）
│   ├── setup.py            # 数据初始化脚本
│   └── setup_references.py # 参考数据生成脚本
│
├── docs/                    # 文档
│   ├── USAGE_GUIDE.md      # 使用指南
│   └── Test_Report.md      # 评估报告
│
└── venv/                   # Python虚拟环境
```

## 🚀 快速开始

### 方式一：Docker 部署（推荐）

```bash
# 1. 克隆项目
git clone <repository-url>
cd translate_eval

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的API密钥和配置

# 3. 构建并运行Docker容器
docker build -t translate-eval .
docker run -d --name translate-eval -p 8888:8888 --env-file .env translate-eval

# 4. 访问应用
# 浏览器打开 http://localhost:8888
```

### 方式二：本地开发

```bash
# 1. 克隆项目
git clone <repository-url>
cd translate_eval

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的API密钥和配置
```

### 2. 配置环境变量

```bash
# 复制环境变量配置文件
cp .env.example .env

# 编辑 .env 文件，填入你的API密钥
# ENV_VENUS_OPENAPI_SECRET_ID=your_api_key_here
```

### 3. 初始化数据

```bash
# 生成翻译提示词和测试用例
python data/setup.py

# 生成参考翻译文件
python data/setup_references.py
```

### 4. 启动Web应用

```bash
# 启动Web服务
python run_app.py

# 或者直接运行
cd backend && python app.py
```

访问 http://127.0.0.1:8888 开始使用！

## �� 使用方法

### Web界面使用

#### 启动应用
- **本地运行**: `python run_app.py`，访问 http://127.0.0.1:8888
- **Docker运行**: `docker run -d --name translate-eval -p 8888:8888 --env-file .env translate-eval`，访问 http://localhost:8888

#### 主要功能

##### 📝 文本翻译
- **源语言选择**: 支持中文、英文、西班牙文、葡萄牙文、日文
- **目标语言选择**: 支持所有上述语言的相互翻译
- **语言交换**: 点击中间的交换按钮可以快速切换源语言和目标语言
- **实时翻译**: 输入文本后点击"Translate"按钮即可获得翻译结果

##### ⭐ 质量评估
- **AI评分**: 翻译完成后，点击"Evaluate Translation"获得1-10分的质量评分
- **详细分析**: 提供AI生成的翻译质量分析和改进建议
- **可视化显示**: 评分以进度条和颜色编码显示

##### 💡 快速示例
右侧面板提供三种类型的示例文本：
- **Technical Text**: 技术文档翻译
- **Casual Conversation**: 日常对话翻译  
- **Academic Text**: 学术文本翻译

#### 功能特点

##### 🎨 用户界面
- 现代化响应式设计
- Bootstrap 5 + Font Awesome 图标
- 实时字符计数
- 加载动画和状态提示

##### 🔧 技术特性
- RESTful API架构
- 异步请求处理
- 错误处理和用户反馈
- 支持键盘快捷键 (Ctrl+Enter 翻译)

### API端点

如果你想直接使用API：

#### 翻译API
```bash
curl -X POST http://127.0.0.1:8888/api/translate \
  -H "Content-Type: application/json" \
  -d '{
    "source_lang": "en",
    "target_lang": "zh",
    "text": "Hello, world!"
  }'
```

#### 评估API
```bash
curl -X POST http://127.0.0.1:8888/api/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "source_lang": "en",
    "target_lang": "zh",
    "source_text": "Hello, world!",
    "translation": "你好，世界！"
  }'
```

### 批量评估

对于大规模的翻译质量评估，可以使用命令行工具：

```bash
# 评估所有语言对
python evaluation/eval.py

# 评估特定语言对
python evaluation/eval.py --source en --target zh

# 评估特定行
python evaluation/eval.py --source en --target zh --line 1

# 设置API调用延迟
python evaluation/eval.py --delay 3.0

# 后台运行
nohup python evaluation/eval.py > evaluation.log 2>&1 &
```

## 🌍 支持的语言

| 语言代码 | 语言名称 | 支持的翻译方向 |
|---------|---------|---------------|
| `en` | English (英文) | ↔ zh, ja, pt, es |
| `zh` | 中文 | ↔ en, ja, pt, es |
| `ja` | 日本語 (日文) | ↔ en, zh, pt, es |
| `pt` | Português (葡萄牙文) | ↔ en, zh, ja, es |
| `es` | Español (西班牙文) | ↔ en, zh, ja, pt |

**总计**: 20个翻译方向

## 🔧 技术栈

### 后端
- **Flask**: Python Web框架
- **Requests**: HTTP客户端库
- **python-dotenv**: 环境变量管理
- **NLTK**: 自然语言处理（BLEU评分）
- **Logging**: 完整的日志记录系统

### 前端
- **Bootstrap 5**: CSS框架
- **Font Awesome**: 图标库
- **Vanilla JavaScript**: 前端交互逻辑

### AI服务
- **Venus OpenAPI**: 翻译和评估服务
- **可配置模型**: 支持不同的翻译和评估模型

### 部署
- **Docker**: 容器化部署

## 📊 评估指标

### AI评分 (1-10分)
- **9-10分**: 优秀 - 翻译准确流畅，完美传达原意
- **7-8分**: 良好 - 翻译基本准确，少量小问题
- **5-6分**: 一般 - 翻译可理解，但有明显错误
- **3-4分**: 较差 - 翻译有严重问题，影响理解
- **1-2分**: 很差 - 翻译错误严重，基本不可用

### 详细分析
- **准确性**: 翻译是否准确传达原文含义
- **流畅性**: 译文是否自然流畅
- **术语处理**: 专业术语翻译是否恰当
- **语法正确性**: 译文语法是否正确
- **改进建议**: AI提供的具体改进建议

## 🐳 Docker 部署

### 基础部署

```bash
# 构建镜像
docker build -t translate-eval .

# 运行容器
docker run -d \
  --name translate-eval \
  -p 8888:8888 \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/data:/app/data \
  translate-eval

# 查看容器状态
docker ps

# 查看日志
docker logs -f translate-eval

# 停止容器
docker stop translate-eval
docker rm translate-eval
```

### Docker 常用命令

```bash
# 进入容器调试
docker exec -it translate-eval bash

# 重启容器
docker restart translate-eval

# 查看容器资源使用
docker stats translate-eval
```

## 🛠️ 开发指南

### 添加新语言

1. 在 `data/testcases/` 中创建新语言目录
2. 在 `evaluation/prompts/` 中添加相应的提示词文件
3. 更新 `backend/app.py` 中的 `LANGUAGES` 字典
4. 更新 `evaluation/eval.py` 中的 `languages` 列表

### 自定义评估标准

编辑 `evaluation/prompts/evaluator-prompt.txt` 文件，修改评估标准和评分规则。

### 扩展API功能

在 `backend/app.py` 中添加新的路由和功能函数。

## 🔒 安全说明

- ✅ **API密钥安全**: 使用 `.env` 文件管理敏感信息
- ✅ **环境隔离**: `.env` 文件已添加到 `.gitignore`
- ✅ **配置示例**: 提供 `.env.example` 作为配置模板
- ⚠️ **注意**: 永远不要将真实的API密钥提交到版本控制系统

## 📝 配置文件说明

### .env 配置项

```bash
# 翻译API配置
TRANSLATION_API_KEY=your_translation_api_key_here
TRANSLATION_API_URL=your_translation_api_url_here
TRANSLATION_MODEL=your_translation_model_name

# 评估API配置
EVALUATION_API_KEY=your_evaluation_api_key_here
EVALUATION_API_URL=your_evaluation_api_url_here
EVALUATION_MODEL=your_evaluation_model_name

# Flask 应用配置
FLASK_HOST=127.0.0.1
FLASK_PORT=8888
FLASK_DEBUG=True

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d in %(funcName)s] - %(message)s
```

## 🐛 故障排除

### 常见问题

1. **API连接失败**
   ```bash
   # 测试API连接
   python evaluation/api_test.py
   ```

2. **找不到提示词文件**
   ```bash
   # 重新生成数据文件
   python data/setup.py
   ```

3. **端口被占用**
   ```bash
   # 修改 .env 文件中的 FLASK_PORT
   FLASK_PORT=8889
   ```

4. **权限错误**
   ```bash
   # 给脚本添加执行权限
   chmod +x run_app.py
   ```

5. **环境变量未加载**
   - 确保 `.env` 文件存在且格式正确
   - 检查API密钥是否正确设置
   - 重启应用以重新加载环境变量

6. **翻译或评估失败**
   - 检查API密钥是否有效
   - 确认模型名称是否正确
   - 查看日志文件获取详细错误信息

### 日志查看

```bash
# 查看应用日志
tail -f logs/app.log

# 查看批量评估日志
tail -f logs/evaluation.log

# 检查Flask应用日志
tail -f flask.log
```

### 重启应用
```bash
# 停止当前应用 (Ctrl+C)
# 重新启动
python run_app.py
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 创建 Issue
- 发送 Pull Request
- 邮件联系项目维护者

---

## 🎉 开始使用

现在就运行 `python run_app.py` 开始使用翻译评估工具吧！

访问 http://127.0.0.1:8888 体验完整功能。