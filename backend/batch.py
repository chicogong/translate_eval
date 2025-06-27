"""
Batch Translation and Evaluation Processing
"""
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from backend.services import TranslationService, EvaluationService
from backend.utils import (load_test_cases, save_translation_result,
                           load_translation_results, save_evaluation_result)

logger = logging.getLogger(__name__)

MAX_CONCURRENCY = 10


def run_batch_translation(source_lang: str, target_lang: str, run_id: str, lines: int):
    """
    Performs batch translation using concurrent API calls.
    """
    logger.info(
        f"Starting batch translation run '{run_id}' for {source_lang}->{target_lang}, {lines} lines."
    )
    translation_service = TranslationService()
    test_cases = load_test_cases(source_lang)

    if not test_cases:
        logger.warning(f"No test cases found for source language '{source_lang}'.")
        return

    tasks = []
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENCY) as executor:
        for i, source_text in enumerate(test_cases[:lines]):
            line_num = i + 1
            task = executor.submit(
                _translate_and_save,
                translation_service,
                source_lang,
                target_lang,
                source_text,
                line_num,
                run_id,
            )
            tasks.append(task)

        for future in as_completed(tasks):
            try:
                future.result()
            except Exception as e:
                logger.error(f"A translation task in run '{run_id}' failed: {e}", exc_info=True)

    logger.info(f"Batch translation run '{run_id}' completed.")


def _translate_and_save(service, source_lang, target_lang, text, line_num, run_id):
    """Helper function to translate a single text and save the result."""
    try:
        logger.info(f"Translating line {line_num} for run '{run_id}': {text[:50]}...")
        result = service.translate_text(source_lang, target_lang, text)

        if result.get("success"):
            translation = result.get("translation", "").strip()
            if translation:
                save_translation_result(
                    source_lang, target_lang, line_num, text, translation, run_id
                )
                logger.info(f"Successfully saved translation for line {line_num} in run '{run_id}'.")
            else:
                logger.error(f"Translation failed for line {line_num} in run '{run_id}': Empty response.")
        else:
            error_msg = result.get("error", "Unknown API error")
            logger.error(f"API error for line {line_num} in run '{run_id}': {error_msg}")
    except Exception as e:
        logger.error(
            f"Exception during translation of line {line_num} in run '{run_id}': {e}",
            exc_info=True
        )


def run_batch_evaluation(source_lang: str, target_lang: str, translation_run_id: str, eval_run_id: str):
    """
    Performs batch evaluation using concurrent API calls.
    """
    logger.info(
        f"Starting batch evaluation run '{eval_run_id}' for translation run '{translation_run_id}' ({source_lang}->{target_lang})."
    )
    evaluation_service = EvaluationService()
    translations_to_eval = load_translation_results(source_lang, target_lang, translation_run_id)

    if not translations_to_eval:
        logger.warning(f"No translation results found for run '{translation_run_id}'.")
        return

    tasks = []
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENCY) as executor:
        for item in translations_to_eval:
            task = executor.submit(
                _evaluate_and_save,
                evaluation_service,
                source_lang,
                target_lang,
                item,
                eval_run_id,
            )
            tasks.append(task)

        for future in as_completed(tasks):
            try:
                future.result()
            except Exception as e:
                logger.error(f"An evaluation task in run '{eval_run_id}' failed: {e}", exc_info=True)

    logger.info(f"Batch evaluation run '{eval_run_id}' completed.")


def _evaluate_and_save(service, source_lang, target_lang, item, eval_run_id):
    """Helper function to evaluate a single translation and save the result."""
    line_num = item.get("line_number")
    source_text = item.get("source_text")
    translation = item.get("translation")

    if not all([line_num, source_text, translation]):
        logger.warning(f"Skipping evaluation for invalid item in run '{eval_run_id}': {item}")
        return

    try:
        logger.info(f"Evaluating line {line_num} for run '{eval_run_id}': {translation[:50]}...")
        result = service.evaluate_translation(source_lang, target_lang, source_text, translation)

        if result.get("success"):
            score = result.get("score", "N/A")
            justification = result.get("justification", "N/A")
            save_evaluation_result(
                source_lang, target_lang, line_num, source_text, translation, score, justification, eval_run_id
            )
            logger.info(f"Successfully saved evaluation for line {line_num} in run '{eval_run_id}'.")
        else:
            error_msg = result.get("error", "Unknown API error")
            logger.error(f"API error for line {line_num} in run '{eval_run_id}': {error_msg}")
    except Exception as e:
        logger.error(
            f"Exception during evaluation of line {line_num} in run '{eval_run_id}': {e}",
            exc_info=True
        )

# ========= Live Playground Processing =========

def run_live_translation_and_evaluation(source_lang: str, target_lang: str, texts: list[str]) -> list[dict]:
    """
    Translates and then evaluates a list of texts, returning results directly.
    """
    logger.info(f"Starting live run for {source_lang}->{target_lang} with {len(texts)} texts.")
    
    results = []
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENCY) as executor:
        future_to_line = {
            executor.submit(_translate_then_evaluate, source_lang, target_lang, text, i + 1): i + 1
            for i, text in enumerate(texts) if text.strip()
        }
        
        for future in as_completed(future_to_line):
            try:
                result_data = future.result()
                results.append(result_data)
            except Exception as exc:
                line_num = future_to_line[future]
                logger.error(f"Line {line_num} generated an exception: {exc}", exc_info=True)
                results.append({
                    "line_number": line_num,
                    "source_text": texts[line_num - 1],
                    "translation": "Error",
                    "evaluation_score": "N/A",
                    "justification": f"Processing failed: {exc}",
                    "error": True
                })

    results.sort(key=lambda x: x.get("line_number", 0))
    logger.info(f"Live run completed for {source_lang}->{target_lang}.")
    return results

def _translate_then_evaluate(source_lang: str, target_lang: str, source_text: str, line_number: int) -> dict:
    """Worker function: translates, then evaluates a single text."""
    translation_service = TranslationService()
    evaluation_service = EvaluationService()

    # Step 1: Translate
    trans_result = translation_service.translate_text(source_lang, target_lang, source_text)
    if not trans_result.get("success"):
        raise Exception(f"Translation failed: {trans_result.get('error', 'Unknown error')}")
    
    translation = trans_result.get("translation", "").strip()
    if not translation:
        raise Exception("Translation resulted in an empty string.")

    # Step 2: Evaluate
    eval_result = evaluation_service.evaluate_translation(source_lang, target_lang, source_text, translation)
    if not eval_result.get("success"):
        return {
            "line_number": line_number,
            "source_text": source_text,
            "translation": translation,
            "evaluation_score": "N/A",
            "justification": f"Evaluation failed: {eval_result.get('error', 'Unknown error')}"
        }

    return {
        "line_number": line_number,
        "source_text": source_text,
        "translation": translation,
        "evaluation_score": eval_result.get("score"),
        "justification": eval_result.get("justification"),
        "bleu_score": None  # Placeholder for consistency
    } 