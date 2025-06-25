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

# Import and run the Flask app
from backend.app import app

if __name__ == '__main__':
    print("🚀 启动翻译评估工具...")
    print("访问地址: http://127.0.0.1:8888")
    print("按 Ctrl+C 停止服务")
    print("-" * 50)
    
    # Set Flask app environment
    os.environ['FLASK_APP'] = str(backend_dir / 'app.py')
    
    app.run(debug=True, port=8888, host='127.0.0.1') 