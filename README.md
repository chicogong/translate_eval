# 翻译评估工具 (Translation Evaluation Tool)

一个基于AI的多语言翻译质量评估系统，采用分离式翻译和评估工作流，支持日期时间运行标识和批量处理功能。

## 🌟 功能特点

- **🔄 分离式工作流**: 独立的翻译和评估流程，便于管理和复用
- **📅 日期时间标识**: 使用 YYYYMMDD_HHMM 格式组织结果
- **🌐 多语言支持**: 支持中英日葡西5种语言的20个翻译方向
- **🤖 AI智能评估**: 使用LLM对翻译质量进行1-10分评分
- **📊 批量评估仪表板**: 可视化分析评估结果，包含图表和统计
- **💡 示例数据**: 内置示例数据用于测试和演示
- **🔧 RESTful API**: 提供完整的API接口

## 🏗️ 项目结构

```
translate_eval/
├── backend/                    # Flask Web应用
│   ├── app.py                 # 主应用文件
│   ├── templates/             # HTML模板
│   │   ├── index.html        # 翻译界面
│   │   └── batch.html        # 批量评估仪表板
│   └── static/               # 静态资源
│       ├── css/style.css     # 样式文件
│       └── js/
│           ├── app.js        # 翻译界面脚本
│           └── batch.js      # 批量仪表板脚本
│
├── data/
│   ├── translations/         # 翻译结果（按运行ID组织）
│   │   └── YYYYMMDD_HHMM/   # 运行时间戳
│   │       └── lang-pair/   # 语言对目录
│   ├── evaluations/          # 评估结果（按运行ID组织）
│   │   └── YYYYMMDD_HHMM/   # 运行时间戳
│   │       └── lang-pair/   # 语言对目录
│   └── testcases/           # 测试用例
│       ├── en/test_suite.txt
│       ├── zh/test_suite.txt
│       └── ...              # 其他语言
│
├── evaluation/              # 核心评估逻辑
│   ├── eval.py             # 评估核心函数
│   └── prompts/            # 提示词模板
│
├── scripts/                # 翻译和评估脚本
│   ├── translate_single.py # 单语言对翻译
│   └── evaluate_single.py  # 单语言对评估
│
└── docs/                   # 文档和报告
```

## 🚀 快速开始

### 1. 环境配置

```bash
# 克隆项目
git clone <repository-url>
cd translate_eval

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的API密钥
```

### 2. API密钥配置

在 `.env` 文件中配置API凭证：

```env
# 翻译API
TRANSLATION_API_KEY=your_translation_api_key
TRANSLATION_API_URL=https://your.translation.api/v1/chat/completions
TRANSLATION_MODEL=your_model_name

# 评估API  
EVALUATION_API_KEY=your_evaluation_api_key
EVALUATION_API_URL=https://your.evaluation.api/v1/chat/completions
EVALUATION_MODEL=your_model_name
```

### 3. 准备测试数据

```bash
# 生成所有语言的测试用例
python data/setup_testcases.py
```

### 4. 运行翻译和评估

#### 步骤1：翻译
```bash
# 翻译单个语言对
python scripts/translate_single.py en zh --lines 5

# 翻译结果保存到：
# data/translations/YYYYMMDD_HHMM/en-zh/
```

#### 步骤2：评估
```bash
# 评估翻译结果（使用步骤1的运行ID）
python scripts/evaluate_single.py en zh 20241226_1400

# 评估结果保存到：
# data/evaluations/YYYYMMDD_HHMM/en-zh/
```

### 5. 查看结果

```bash
# 启动Web界面
python run_app.py

# 访问 http://localhost:8888 - 翻译界面
# 访问 http://localhost:8888/batch - 批量评估仪表板
```

## 📖 使用示例

### 翻译工作流

```bash
# 基础翻译
python scripts/translate_single.py en zh

# 自定义设置
python scripts/translate_single.py en zh --run-id 20241226_1500 --delay 2.0 --lines 10

# 参数说明：
# --run-id: 运行标识（默认：当前时间）
# --delay: API调用间隔秒数（默认：1.0）
# --lines: 最大处理行数（默认：全部）
```

### 评估工作流

```bash
# 评估现有翻译
python scripts/evaluate_single.py en zh 20241226_1400

# 自定义设置
python scripts/evaluate_single.py en zh 20241226_1400 --eval-run-id 20241226_1600 --delay 1.5

# 参数说明：
# translation_run_id: 要评估的翻译运行ID
# --eval-run-id: 评估运行标识（默认：当前时间）
# --delay: API调用间隔秒数（默认：1.0）
```

### Web界面功能

#### 翻译界面 (/)
- **实时翻译**: 输入文本即时翻译
- **质量评估**: AI评分和详细分析
- **多语言支持**: 5种语言相互翻译
- **示例文本**: 技术、对话、学术文本示例

#### 批量评估仪表板 (/batch)
- **示例数据**: 点击"查看示例数据"查看演示结果
- **最新运行**: 自动加载最近的评估运行
- **运行选择**: 从可读时间戳格式的运行中选择
- **可视化分析**: 带颜色编码的分数分布图表
- **详细结果**: 可展开的结果表格

## 🔧 API端点

- `POST /api/translate` - 单文本翻译
- `POST /api/evaluate` - 单文本评估  
- `GET /api/available-runs` - 获取可用的翻译/评估运行
- `GET /api/evaluation-results` - 获取特定运行的评估结果

## 📁 文件命名规范

- **翻译文件**: `line_{N}_translation.json`
- **评估文件**: `line_{N}_evaluation.json`
- **运行ID**: `YYYYMMDD_HHMM` (例如：`20241226_1400` 表示2024年12月26日14:00)

## 📊 批量仪表板特性

- **示例数据**: 内置演示数据，无需真实API调用
- **最新运行**: 自动选择最新的评估运行
- **运行选择**: 可读的时间戳格式显示
- **可视化分析**: 
  - 绿色：8-10分（优秀）
  - 黄色：6-7分（良好）
  - 红色：1-5分（需改进）
- **详细表格**: 源文本、翻译、评分、理由完整展示

## 🔧 批量操作

### 批量操作脚本
```bash
# 翻译所有语言对（演示模式，每个语言对5行）
python scripts/batch_operations.py translate-all

# 评估所有翻译结果
python scripts/batch_operations.py evaluate-all --translation-run-id 20241226_1400

# 完整流水线：翻译 → 评估 → 启动Web界面
python scripts/batch_operations.py full-pipeline

# 单语言对操作
python scripts/batch_operations.py translate-single --source en --target zh --lines 10
python scripts/batch_operations.py evaluate-single --source en --target zh --translation-run-id 20241226_1400

# 仅启动Web界面
python scripts/batch_operations.py web
```

### Web界面批量操作
在批量评估仪表板 (http://localhost:8888/batch) 中：
- **批量翻译**: 点击"Batch Translate"按钮启动翻译
- **批量评估**: 点击"Batch Evaluate"按钮启动评估
- **进度监控**: 实时显示操作进度和状态

## 🎯 最佳实践

### 首次使用流程
```bash
# 1. 配置API密钥
cp .env.example .env
# 编辑 .env 文件，填入真实API密钥

# 2. 生成测试用例
python data/setup_testcases.py

# 3. 运行演示翻译（快速测试）
python scripts/translate_single.py en zh --lines 3

# 4. 运行评估
python scripts/evaluate_single.py en zh <run_id>

# 5. 启动Web界面查看结果
python run_app.py
```

### 版本管理建议
```bash
# 为不同模型创建不同的运行
python scripts/translate_single.py en zh --run-id gpt4_20241226_1400
python scripts/translate_single.py en zh --run-id claude_20241226_1400

# 在Web界面中对比不同版本结果
```

### 性能优化
```bash
# 调整API调用间隔（避免速率限制）
python scripts/translate_single.py en zh --delay 0.5

# 限制处理行数进行快速测试
python scripts/translate_single.py en zh --lines 3
```

## 🔍 故障排除

### API配置问题
1. 检查 `.env` 文件是否存在且包含正确的API密钥
2. 验证API端点是否可访问
3. 先测试单个翻译：`python scripts/translate_single.py en zh --lines 1`

### 常见错误及解决方案

1. **"No test cases found"**
   ```bash
   python data/setup_testcases.py
   ```

2. **"Invalid URL"错误**
   - 检查 `.env` 文件中的API_URL格式
   - 确保包含完整的 `https://` 前缀

3. **"No valid result files found"**
   - 先运行翻译脚本生成结果
   - 检查 `data/translations/` 目录是否存在

4. **Web界面无法加载结果**
   - 确保运行ID存在于 `data/evaluations/` 目录
   - 尝试点击"View Sample Data"查看演示数据

### 文件结构问题
```bash
# 验证目录结构
ls -la data/translations/
ls -la data/evaluations/

# 重新生成测试用例
python data/setup_testcases.py
```

### 无评估运行可用
1. 先运行翻译：`python scripts/translate_single.py en zh`
2. 再运行评估：`python scripts/evaluate_single.py en zh <run_id>`
3. 或在Web界面中使用示例数据

### Web界面问题
1. 确保Flask应用正在运行：`python run_app.py`
2. 检查浏览器控制台的JavaScript错误
3. 如无真实运行数据，可使用示例数据

## 🎯 最佳实践

### 运行管理
- 使用描述性的运行ID便于识别
- 定期清理旧的运行数据
- 保持翻译和评估运行的对应关系

### 批量处理
- 先用少量数据测试API配置
- 根据API限制调整延迟时间
- 监控API使用量和成本

### 结果分析
- 使用批量仪表板进行可视化分析
- 关注低分项目进行质量改进
- 比较不同运行的结果趋势

## 📈 系统架构优势

1. **模块化设计**: 翻译和评估独立，便于维护
2. **时间戳管理**: 清晰的版本控制和历史追踪
3. **可扩展性**: 易于添加新语言和评估指标
4. **用户友好**: 直观的Web界面和示例数据
5. **API优先**: 完整的RESTful API支持

## 🤝 贡献指南

1. Fork 本仓库
2. 创建功能分支
3. 提交你的更改
4. 添加测试（如适用）
5. 提交Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。