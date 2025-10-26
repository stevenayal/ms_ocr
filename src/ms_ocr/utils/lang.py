"""Language detection and processing utilities."""

from typing import List, Optional

import langdetect
from langdetect import LangDetectException


def detect_language(text: str, fallback: str = "spa") -> str:
    """Detect language of text.

    Args:
        text: Text to analyze
        fallback: Fallback language code if detection fails

    Returns:
        ISO 639-1 language code (e.g., 'spa', 'eng')
    """
    if not text or len(text.strip()) < 10:
        return fallback

    try:
        # langdetect returns ISO 639-1 codes (e.g., 'es', 'en')
        lang = langdetect.detect(text)
        # Convert to ISO 639-2 for tesseract (es -> spa, en -> eng)
        return _iso639_1_to_tesseract(lang)
    except LangDetectException:
        return fallback


def detect_languages_multi(text: str, top_n: int = 2) -> List[str]:
    """Detect multiple languages in text.

    Args:
        text: Text to analyze
        top_n: Number of top languages to return

    Returns:
        List of language codes
    """
    if not text or len(text.strip()) < 10:
        return ["spa"]

    try:
        langs = langdetect.detect_langs(text)
        # Get top N languages with probability > 0.1
        result = []
        for lang in langs[:top_n]:
            if lang.prob > 0.1:
                result.append(_iso639_1_to_tesseract(lang.lang))
        return result if result else ["spa"]
    except LangDetectException:
        return ["spa"]


def _iso639_1_to_tesseract(lang_code: str) -> str:
    """Convert ISO 639-1 to tesseract language codes.

    Args:
        lang_code: ISO 639-1 code (e.g., 'es', 'en')

    Returns:
        Tesseract language code (e.g., 'spa', 'eng')
    """
    mapping = {
        "es": "spa",
        "en": "eng",
        "fr": "fra",
        "de": "deu",
        "it": "ita",
        "pt": "por",
        "ca": "cat",
        "eu": "eus",
        "gl": "glg",
    }
    return mapping.get(lang_code, lang_code)


def normalize_tesseract_langs(langs: List[str]) -> str:
    """Normalize language list for tesseract.

    Args:
        langs: List of language codes

    Returns:
        Tesseract-compatible language string (e.g., 'spa+eng')
    """
    # Remove duplicates while preserving order
    seen = set()
    unique_langs = []
    for lang in langs:
        if lang not in seen:
            seen.add(lang)
            unique_langs.append(lang)

    return "+".join(unique_langs)


def is_spanish_dominant(text: str, threshold: float = 0.5) -> bool:
    """Check if Spanish is the dominant language.

    Args:
        text: Text to analyze
        threshold: Minimum probability threshold

    Returns:
        True if Spanish is dominant
    """
    if not text or len(text.strip()) < 10:
        return True  # Default to Spanish

    try:
        langs = langdetect.detect_langs(text)
        for lang in langs:
            if lang.lang == "es" and lang.prob >= threshold:
                return True
        return False
    except LangDetectException:
        return True
