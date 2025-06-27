#!/usr/bin/env python3
"""
翻译评估工具启动脚本
"""

import os
import sys
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent
backend_dir = project_root / 'backend'

# Add backend directory to Python path
sys.path.insert(0, str(backend_dir))

# Set working directory to project root for proper file access
os.chdir(project_root)

# Create logs directory if not exists
logs_dir = project_root / 'logs'
logs_dir.mkdir(exist_ok=True)

# Import and run the Flask app
from backend.app import app

if __name__ == '__main__':
    # 环境配置
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', 8888))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    print("🚀 启动翻译评估工具...")
    print(f"访问地址: http://{host}:{port}")
    print(f"环境模式: {'开发' if debug else '生产'}")
    print("按 Ctrl+C 停止服务")
    print("-" * 50)
    
    # Set Flask app environment
    os.environ['FLASK_APP'] = str(backend_dir / 'app.py')
    
    app.run(debug=debug, port=port, host=host) 