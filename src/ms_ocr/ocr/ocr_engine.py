"""OCR engine using Tesseract."""

from dataclasses import dataclass
from typing import List, Optional

import pytesseract
from PIL import Image

from ms_ocr.ocr.preprocess import ImagePreprocessor
from ms_ocr.utils.lang import normalize_tesseract_langs


@dataclass
class OCRResult:
    """OCR result with confidence scores."""

    text: str
    confidence: float  # 0-100
    words: List[dict]  # Word-level data


class OCREngine:
    """Tesseract OCR engine wrapper."""

    def __init__(
        self,
        languages: List[str] = None,
        min_confidence: int = 0,
        preprocess: bool = True,
        dpi: int = 300,
        **preprocess_kwargs,
    ):
        """Initialize OCR engine.

        Args:
            languages: List of language codes (e.g., ['spa', 'eng'])
            min_confidence: Minimum confidence threshold (0-100)
            preprocess: Whether to preprocess images
            dpi: Target DPI for preprocessing
            **preprocess_kwargs: Arguments for ImagePreprocessor
        """
        self.languages = languages or ["spa", "eng"]
        self.min_confidence = min_confidence
        self.dpi = dpi

        if preprocess:
            self.preprocessor = ImagePreprocessor(**preprocess_kwargs)
        else:
            self.preprocessor = None

    def extract_text(self, image: Image.Image) -> OCRResult:
        """Extract text from image.

        Args:
            image: PIL Image

        Returns:
            OCR result
        """
        # Preprocess if enabled
        if self.preprocessor:
            image = self.preprocessor.process(image)

        # Prepare language string
        lang_str = normalize_tesseract_langs(self.languages)

        # Configure tesseract
        config = f"--oem 3 --psm 3"  # LSTM OCR Engine, Fully automatic page segmentation

        # Get detailed data
        data = pytesseract.image_to_data(
            image, lang=lang_str, config=config, output_type=pytesseract.Output.DICT
        )

        # Extract words with confidence
        words = []
        text_parts = []

        for i in range(len(data["text"])):
            word = data["text"][i].strip()
            conf = int(data["conf"][i]) if data["conf"][i] != "-1" else 0

            if word and conf >= self.min_confidence:
                words.append(
                    {
                        "text": word,
                        "confidence": conf,
                        "bbox": (
                            data["left"][i],
                            data["top"][i],
                            data["left"][i] + data["width"][i],
                            data["top"][i] + data["height"][i],
                        ),
                    }
                )
                text_parts.append(word)

        # Calculate average confidence
        if words:
            avg_confidence = sum(w["confidence"] for w in words) / len(words)
        else:
            avg_confidence = 0.0

        # Combine text
        text = " ".join(text_parts)

        return OCRResult(text=text, confidence=avg_confidence, words=words)

    def extract_text_simple(self, image: Image.Image) -> str:
        """Extract text from image (simple version).

        Args:
            image: PIL Image

        Returns:
            Extracted text
        """
        if self.preprocessor:
            image = self.preprocessor.process(image)

        lang_str = normalize_tesseract_langs(self.languages)
        config = f"--oem 3 --psm 3"

        return pytesseract.image_to_string(image, lang=lang_str, config=config)

    def get_confidence(self, image: Image.Image) -> float:
        """Get OCR confidence for an image.

        Args:
            image: PIL Image

        Returns:
            Confidence score (0-100)
        """
        result = self.extract_text(image)
        return result.confidence
