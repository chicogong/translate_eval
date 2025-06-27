"""
Utility functions and logging setup
"""

import logging
from pathlib import Path
from config import LOGGING_CONFIG
from langdetect import detect

def setup_logging():
    """配置日志系统"""
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, LOGGING_CONFIG['level']),
        format=LOGGING_CONFIG['format'],
        handlers=[
            logging.FileHandler(LOGGING_CONFIG['file'], encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def format_run_id(run_id: str) -> str:
    """格式化运行ID为可读格式"""
    # Convert YYYYMMDD_HHMM to readable format
    import re
    if re.match(r'^\d{8}_\d{4}$', run_id):
        date = run_id[:8]
        time = run_id[9:]
        year = date[:4]
        month = date[4:6]
        day = date[6:8]
        hour = time[:2]
        minute = time[2:4]
        
        return f"{year}-{month}-{day} {hour}:{minute}"
    return run_id

def escape_html(text: str) -> str:
    """转义HTML字符"""
    if not text:
        return ''
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#039;'))

def validate_language_pair(source_lang: str, target_lang: str) -> tuple[bool, str]:
    """验证语言对"""
    from config import LANGUAGES
    
    if not source_lang or not target_lang:
        return False, "Source and target languages are required"
    
    if source_lang not in LANGUAGES:
        return False, f"Unsupported source language: {source_lang}"
    
    if target_lang not in LANGUAGES:
        return False, f"Unsupported target language: {target_lang}"
    
    if source_lang == target_lang:
        return False, "Source and target languages must be different"
    
    return True, ""

LANG_MAP = {
    'zh-cn': 'zh',
    'zh-tw': 'zh',
    'zh': 'zh',
    'en': 'en',
    'ja': 'ja',
    'es': 'es',
    'pt': 'pt',
    'ko': 'ko'
}

def detect_language(text: str) -> str:
    """自动检测文本语言，返回简化语言代码(zh,en,ja,es,pt)"""
    try:
        lang_code = detect(text)
        return LANG_MAP.get(lang_code, lang_code)
    except Exception:
        return 'en'

# ========= Data Handling Utilities =========

import json
from datetime import datetime
from config import PROJECT_ROOT

def load_test_cases(lang: str) -> list:
    """Load test cases for a specific language"""
    test_file = PROJECT_ROOT / f"data/testcases/{lang}/test_suite.txt"
    if not test_file.exists():
        logging.warning(f"Test file not found: {test_file}")
        return []

    with open(test_file, 'r', encoding='utf-8') as f:
        test_cases = [line.strip() for line in f if line.strip()]

    logging.info(f"Loaded {len(test_cases)} test cases from {test_file}")
    return test_cases

def save_translation_result(source_lang: str, target_lang: str, line_number: int,
                          source_text: str, translation: str, run_id: str):
    """Save translation result to file"""
    translations_dir = PROJECT_ROOT / f"data/translations/{run_id}/{source_lang}-{target_lang}"
    translations_dir.mkdir(parents=True, exist_ok=True)

    result_file = translations_dir / f"line_{line_number}_translation.json"

    translation_data = {
        "source_lang": source_lang,
        "target_lang": target_lang,
        "line_number": line_number,
        "source_text": source_text,
        "translation": translation,
        "run_id": run_id,
        "timestamp": datetime.now().isoformat()
    }

    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(translation_data, f, ensure_ascii=False, indent=2)

    logging.debug(f"Translation saved to {result_file}")

def save_evaluation_result(source_lang: str, target_lang: str, line_number: int,
                         source_text: str, translation: str, score: int,
                         justification: str, eval_run_id: str):
    """Save evaluation result to file"""
    evaluations_dir = PROJECT_ROOT / f"data/evaluations/{eval_run_id}/{source_lang}-{target_lang}"
    evaluations_dir.mkdir(parents=True, exist_ok=True)

    result_file = evaluations_dir / f"line_{line_number}_evaluation.json"

    evaluation_data = {
        "source_lang": source_lang,
        "target_lang": target_lang,
        "line_number": line_number,
        "source_text": source_text,
        "translation": translation,
        "evaluation_score": score,
        "justification": justification,
        "eval_run_id": eval_run_id,
        "timestamp": datetime.now().isoformat(),
    }

    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(evaluation_data, f, ensure_ascii=False, indent=2)

    logging.debug(f"Evaluation saved to {result_file}")

def load_translation_results(source_lang: str, target_lang: str, run_id: str) -> list:
    """Load translation results from a specific run"""
    translations_dir = PROJECT_ROOT / f"data/translations/{run_id}/{source_lang}-{target_lang}"

    if not translations_dir.exists():
        logging.warning(f"Translation directory not found: {translations_dir}")
        return []

    results = []
    json_files = sorted(translations_dir.glob("*.json"))

    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                results.append(data)
        except Exception as e:
            logging.warning(f"Failed to load translation result {json_file}: {e}")

    # Sort by line number
    results.sort(key=lambda x: x.get('line_number', 0))
    logging.info(f"Loaded {len(results)} translation results from {translations_dir}")
    return results

def load_evaluation_results(source_lang: str, target_lang: str, eval_run_id: str) -> list:
    """Load evaluation results from a specific run"""
    evaluations_dir = PROJECT_ROOT / f"data/evaluations/{eval_run_id}/{source_lang}-{target_lang}"

    if not evaluations_dir.exists():
        logging.warning(f"Evaluation directory not found: {evaluations_dir}")
        return []

    results = []
    json_files = sorted(evaluations_dir.glob("*.json"))

    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                results.append(data)
        except Exception as e:
            logging.warning(f"Failed to load evaluation result {json_file}: {e}")

    # Sort by line number
    results.sort(key=lambda x: x.get('line_number', 0))
    logging.info(f"Loaded {len(results)} evaluation results from {evaluations_dir}")
    return results

def generate_report(version: str):
    """Generate a summary report from result files"""
    logging.info("Generating evaluation report")

    results_dir = PROJECT_ROOT / "data/results" / version
    if not results_dir.exists():
        logging.warning("No results directory found")
        return

    report_file = PROJECT_ROOT / f"docs/Test_Report_{version}.md"
    report_file.parent.mkdir(exist_ok=True)

    all_results = []

    # Collect all result files
    for lang_pair_dir in results_dir.iterdir():
        if lang_pair_dir.is_dir():
            for result_file in lang_pair_dir.glob("test_suite_line_*_result.json"):
                try:
                    with open(result_file, 'r', encoding='utf-8') as f:
                        result_data = json.load(f)
                        all_results.append(result_data)
                except Exception as e:
                    logging.error(f"Error reading result file {result_file}: {e}")

    logging.info(f"Collected {len(all_results)} results for report")

    # Generate markdown report
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# Translation Evaluation Report\n\n")
        f.write(f"**Report Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("| Src | Tgt | Line | Score | Justification | Source Text (truncated) | Result File | Status |\n")
        f.write("|-----|-----|------|-------|---------------|-------------------------|-------------|--------|\n")

        for result in sorted(all_results, key=lambda x: (x['source_lang'], x['target_lang'], x['line_number'])):
            source_text_truncated = result['source_text'][:50] + "..." if len(result['source_text']) > 50 else result['source_text']
            justification_truncated = result['justification'][:50] + "..." if len(result['justification']) > 50 else result['justification']

            f.write(f"| {result['source_lang']} | {result['target_lang']} | {result['line_number']} | "
                   f"{result['evaluation_score']} | {justification_truncated} | {source_text_truncated} | "
                   f"`data/results/{version}/{result['source_lang']}-{result['target_lang']}/test_suite_line_{result['line_number']}_result.json` | Success |\n")

    logging.info(f"Report generated: {report_file}") 