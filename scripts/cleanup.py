#!/usr/bin/env python3
"""
Project Cleanup Script
Removes temporary files, caches, and unused directories
"""

import os
import shutil
from pathlib import Path

def cleanup_python_cache():
    """Remove Python cache files and directories"""
    print("🧹 Cleaning Python cache files...")
    
    # Find and remove __pycache__ directories
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            cache_dir = os.path.join(root, '__pycache__')
            print(f"  Removing: {cache_dir}")
            shutil.rmtree(cache_dir)
            dirs.remove('__pycache__')
    
    # Remove .pyc files
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                pyc_file = os.path.join(root, file)
                print(f"  Removing: {pyc_file}")
                os.remove(pyc_file)

def cleanup_logs():
    """Clean old log files"""
    print("📋 Cleaning old log files...")
    
    log_dirs = ['logs/', 'backend/logs/']
    for log_dir in log_dirs:
        if os.path.exists(log_dir):
            for file in os.listdir(log_dir):
                if file.endswith('.log') and file != 'app.log':
                    log_file = os.path.join(log_dir, file)
                    print(f"  Removing old log: {log_file}")
                    os.remove(log_file)

def cleanup_temp_files():
    """Remove temporary and backup files"""
    print("🗑️  Cleaning temporary files...")
    
    patterns = ['*.tmp', '*.bak', '*.swp', '*~', '.DS_Store']
    
    for root, dirs, files in os.walk('.'):
        for file in files:
            for pattern in patterns:
                if file.endswith(pattern.replace('*', '')):
                    temp_file = os.path.join(root, file)
                    print(f"  Removing: {temp_file}")
                    os.remove(temp_file)

def cleanup_empty_dirs():
    """Remove empty directories"""
    print("📁 Removing empty directories...")
    
    # Skip these important directories even if empty
    skip_dirs = {'.git', 'venv', 'node_modules', 'data', 'logs', 'backend/logs'}
    
    for root, dirs, files in os.walk('.', topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            relative_path = os.path.relpath(dir_path)
            
            # Skip important directories
            if any(skip in relative_path for skip in skip_dirs):
                continue
                
            try:
                if not os.listdir(dir_path):  # Directory is empty
                    print(f"  Removing empty directory: {dir_path}")
                    os.rmdir(dir_path)
            except OSError:
                pass  # Directory not empty or permission denied

def cleanup_old_results():
    """Archive or remove very old result files"""
    print("📊 Checking old result files...")
    
    from datetime import datetime, timedelta
    cutoff_date = datetime.now() - timedelta(days=30)  # 30 days ago
    
    result_dirs = ['data/translations', 'data/evaluations']
    
    for result_dir in result_dirs:
        if not os.path.exists(result_dir):
            continue
            
        for run_dir in os.listdir(result_dir):
            run_path = os.path.join(result_dir, run_dir)
            if not os.path.isdir(run_path):
                continue
                
            # Try to parse run ID as date
            try:
                if len(run_dir) == 13 and '_' in run_dir:  # YYYYMMDD_HHMM format
                    date_str = run_dir.split('_')[0]
                    run_date = datetime.strptime(date_str, '%Y%m%d')
                    
                    if run_date < cutoff_date:
                        print(f"  Old result found (consider archiving): {run_path}")
                        # Don't auto-delete, just notify
            except ValueError:
                pass  # Not a valid date format

def show_disk_usage():
    """Show disk usage of main directories"""
    print("💾 Disk usage summary:")
    
    dirs_to_check = [
        'data/translations',
        'data/evaluations', 
        'data/testcases',
        'logs',
        'backend/logs'
    ]
    
    for dir_path in dirs_to_check:
        if os.path.exists(dir_path):
            total_size = 0
            file_count = 0
            
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        total_size += os.path.getsize(file_path)
                        file_count += 1
                    except OSError:
                        pass
            
            size_mb = total_size / (1024 * 1024)
            print(f"  {dir_path}: {size_mb:.2f} MB ({file_count} files)")

def main():
    print("🚀 Starting Project Cleanup")
    print("=" * 50)
    
    # Change to project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    
    try:
        cleanup_python_cache()
        cleanup_temp_files()
        cleanup_logs()
        cleanup_empty_dirs()
        cleanup_old_results()
        
        print("\n" + "=" * 50)
        print("✅ Cleanup completed successfully!")
        
        print("\n")
        show_disk_usage()
        
        print("\n💡 Tips:")
        print("  - Run this script regularly to keep the project clean")
        print("  - Archive old results if they're important")
        print("  - Check .gitignore to ensure temp files are excluded")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 