#!/usr/bin/env python3
"""
Anti-plagiarism paraphrasing via translation round-trip.

Paraphrases text by translating English → Chinese → English,
preserving technical terms and detecting changes.
"""

import argparse
import json
import sys
import subprocess
import difflib
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

try:
    from deep_translator import GoogleTranslator
except ImportError:
    logger.error("deep_translator not installed. Install with: pip install deep-translator")
    sys.exit(1)


def read_input_file(file_path: str) -> str:
    """Read input text file and return content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"Input file not found: {file_path}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error reading input file: {e}")
        sys.exit(1)


def read_terms_file(file_path: Optional[str]) -> List[str]:
    """Read technical terms from file (one per line)."""
    if not file_path:
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            terms = [line.strip() for line in f if line.strip()]
        return terms
    except FileNotFoundError:
        logger.error(f"Terms file not found: {file_path}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error reading terms file: {e}")
        sys.exit(1)


def split_into_paragraphs(text: str) -> List[str]:
    """Split text into paragraphs (separated by blank lines)."""
    paragraphs = text.split('\n\n')
    return [p.strip() for p in paragraphs if p.strip()]


def translate_en_to_zh(text: str, max_retries: int = 3) -> str:
    """Translate English text to Chinese using Google Translate."""
    for attempt in range(max_retries):
        try:
            translator = GoogleTranslator(source='en', target='zh-CN')
            result = translator.translate(text)
            return result
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Translation attempt {attempt + 1} failed: {e}. Retrying...")
            else:
                logger.error(f"Failed to translate to Chinese after {max_retries} attempts: {e}")
                raise


def translate_zh_to_en_apple(text: str) -> Optional[str]:
    """
    Translate Chinese text to English using macOS Apple Translate.

    Attempts multiple approaches:
    1. shortcuts run "Translate" -i <input>
    2. osascript with Translate application
    3. Fallback to Google Translate (with warning)
    """

    # Approach 1: Try shortcuts command
    try:
        result = subprocess.run(
            ['shortcuts', 'run', 'Translate', '-i', text],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            logger.info("Used shortcuts for translation")
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
        logger.debug(f"Shortcuts approach failed: {e}")

    # Approach 2: Try osascript with Translate application
    try:
        escaped_text = text.replace('"', '\\"')
        applescript = f'tell application "Translate" to translate "{escaped_text}" from "Chinese" to "English"'
        result = subprocess.run(
            ['osascript', '-e', applescript],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            logger.info("Used osascript Translate application")
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
        logger.debug(f"osascript Translate approach failed: {e}")

    # Approach 3: Fallback to Google Translate
    logger.warning("Apple Translate not available, falling back to Google Translate for ZH→EN")
    try:
        translator = GoogleTranslator(source='zh-CN', target='en')
        result = translator.translate(text)
        return result
    except Exception as e:
        logger.error(f"Google Translate fallback failed: {e}")
        return None


def translate_zh_to_en(text: str) -> str:
    """Translate Chinese text to English, preferring Apple Translate."""
    result = translate_zh_to_en_apple(text)
    if result:
        return result
    logger.error("All translation approaches failed")
    raise RuntimeError("Failed to translate Chinese text to English")


def extract_technical_terms_from_text(text: str, terms: List[str]) -> Dict[str, int]:
    """
    Find all technical terms in the original text (case-insensitive).
    Returns dict of {term: count}.
    """
    found_terms = {}
    for term in terms:
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        matches = pattern.findall(text)
        if matches:
            found_terms[term] = len(matches)
    return found_terms


def find_mangled_term(original_term: str, translated_back: str) -> Optional[str]:
    """
    Try to find a mangled version of the original term in the translated text.
    This is a heuristic approach using string similarity.
    """
    original_lower = original_term.lower()

    # Extract candidate words/phrases from translated text
    # Look for sequences of words that might correspond to the original
    words_in_original = original_term.split()

    if len(words_in_original) == 1:
        # Single word: look for similar words
        for word_match in re.finditer(r'\b\w+\b', translated_back):
            candidate = word_match.group()
            if candidate.lower() != original_lower:
                # Calculate similarity (very basic)
                if _string_similarity(original_lower, candidate.lower()) > 0.5:
                    return candidate
    else:
        # Multi-word: look for sequences that might be the mangled version
        # This is more complex; for now, try to find word sequences
        candidates = re.findall(r'\b\w+(?:\s+\w+)*\b', translated_back)
        for candidate in candidates:
            if candidate.lower() != original_lower:
                if _string_similarity(original_lower, candidate.lower()) > 0.4:
                    return candidate

    return None


def _string_similarity(s1: str, s2: str) -> float:
    """Calculate basic string similarity using SequenceMatcher."""
    return difflib.SequenceMatcher(None, s1, s2).ratio()


def restore_technical_terms(
    paraphrased: str,
    original_text: str,
    terms: List[str]
) -> Tuple[str, List[str]]:
    """
    Restore technical terms that may have been mangled during translation.
    Returns (updated_text, list_of_restored_terms).
    """
    restored_terms = []
    updated_text = paraphrased

    for term in terms:
        # Check if original term exists in original text
        if re.search(re.escape(term), original_text, re.IGNORECASE):
            # Check if it's missing or mangled in paraphrased text
            if not re.search(re.escape(term), updated_text, re.IGNORECASE):
                # Try to find and replace mangled version
                mangled = find_mangled_term(term, updated_text)
                if mangled:
                    # Replace first occurrence of mangled term with original
                    updated_text = updated_text.replace(mangled, term, 1)
                    restored_terms.append(term)
                    logger.info(f"Restored term '{term}' (was '{mangled}')")

    return updated_text, restored_terms


def generate_diff(original: str, paraphrased: str) -> str:
    """Generate unified diff between original and paraphrased text."""
    original_lines = original.splitlines(keepends=True)
    paraphrased_lines = paraphrased.splitlines(keepends=True)

    diff_lines = difflib.unified_diff(
        original_lines,
        paraphrased_lines,
        fromfile='original',
        tofile='paraphrased',
        lineterm=''
    )

    return '\n'.join(diff_lines)


def paraphrase_text(
    text: str,
    terms: Optional[List[str]] = None
) -> Tuple[str, List[str]]:
    """
    Paraphrase text via EN→ZH→EN translation round-trip.
    Returns (paraphrased_text, restored_terms_list).
    """
    if terms is None:
        terms = []

    paragraphs = split_into_paragraphs(text)
    paraphrased_paragraphs = []

    for i, paragraph in enumerate(paragraphs, 1):
        logger.info(f"Processing paragraph {i}/{len(paragraphs)}")

        # Step 1: Translate EN to ZH
        logger.debug(f"Translating to Chinese: {paragraph[:50]}...")
        zh_text = translate_en_to_zh(paragraph)
        logger.debug(f"Chinese translation: {zh_text[:50]}...")

        # Step 2: Translate ZH back to EN
        logger.debug(f"Translating back to English...")
        en_text = translate_zh_to_en(zh_text)
        logger.debug(f"English translation: {en_text[:50]}...")

        paraphrased_paragraphs.append(en_text)

    # Join paragraphs back together
    paraphrased = '\n\n'.join(paraphrased_paragraphs)

    # Step 3: Restore technical terms
    paraphrased, restored_terms = restore_technical_terms(
        paraphrased,
        text,
        terms
    )

    return paraphrased, restored_terms


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Anti-plagiarism paraphrasing via translation round-trip'
    )
    parser.add_argument(
        '--input',
        required=True,
        help='Input text file'
    )
    parser.add_argument(
        '--output',
        help='Output JSON file (if not specified, write to stdout)'
    )
    parser.add_argument(
        '--terms-file',
        help='File containing technical terms (one per line)'
    )
    parser.add_argument(
        '--diff',
        action='store_true',
        help='Include unified diff in output'
    )

    args = parser.parse_args()

    # Read input
    logger.info(f"Reading input from {args.input}")
    text = read_input_file(args.input)

    # Read technical terms
    terms = []
    if args.terms_file:
        logger.info(f"Reading technical terms from {args.terms_file}")
        terms = read_terms_file(args.terms_file)
        logger.info(f"Loaded {len(terms)} technical terms")

    # Paraphrase
    logger.info("Starting paraphrasing process...")
    paraphrased, restored_terms = paraphrase_text(text, terms)
    logger.info(f"Paraphrasing complete. Restored {len(restored_terms)} terms")

    # Generate diff if requested
    diff_output = ""
    if args.diff:
        logger.info("Generating diff...")
        diff_output = generate_diff(text, paraphrased)

    # Prepare output
    output_data = {
        "paraphrased": paraphrased,
        "preserved_terms": restored_terms,
        "diff": diff_output if args.diff else None
    }

    # Write output
    output_json = json.dumps(output_data, ensure_ascii=False, indent=2)

    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output_json)
            logger.info(f"Output written to {args.output}")
        except Exception as e:
            logger.error(f"Error writing output file: {e}")
            sys.exit(1)
    else:
        print(output_json)

    logger.info("Done")


if __name__ == '__main__':
    main()
