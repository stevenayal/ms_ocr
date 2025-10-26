"""Image preprocessing for OCR."""

import cv2
import numpy as np
from PIL import Image


class ImagePreprocessor:
    """Preprocess images for better OCR results."""

    def __init__(
        self,
        deskew: bool = True,
        denoise: bool = True,
        binarize: bool = True,
        contrast: bool = True,
    ):
        """Initialize preprocessor.

        Args:
            deskew: Apply deskewing
            denoise: Apply denoising
            binarize: Apply binarization
            contrast: Apply contrast enhancement
        """
        self.deskew = deskew
        self.denoise = denoise
        self.binarize = binarize
        self.contrast = contrast

    def process(self, image: Image.Image) -> Image.Image:
        """Process image through pipeline.

        Args:
            image: Input PIL Image

        Returns:
            Processed PIL Image
        """
        # Convert to OpenCV format
        img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply preprocessing steps
        if self.denoise:
            gray = self._denoise(gray)

        if self.contrast:
            gray = self._enhance_contrast(gray)

        if self.binarize:
            gray = self._binarize(gray)

        if self.deskew:
            gray = self._deskew(gray)

        # Convert back to PIL
        return Image.fromarray(gray)

    def _denoise(self, img: np.ndarray) -> np.ndarray:
        """Remove noise from image.

        Args:
            img: Grayscale image

        Returns:
            Denoised image
        """
        # Morphological opening (erosion followed by dilation)
        kernel = np.ones((1, 1), np.uint8)
        img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)

        # Gaussian blur to reduce noise
        img = cv2.GaussianBlur(img, (3, 3), 0)

        return img

    def _enhance_contrast(self, img: np.ndarray) -> np.ndarray:
        """Enhance image contrast.

        Args:
            img: Grayscale image

        Returns:
            Enhanced image
        """
        # CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(img)

    def _binarize(self, img: np.ndarray) -> np.ndarray:
        """Convert to binary image.

        Args:
            img: Grayscale image

        Returns:
            Binary image
        """
        # Otsu's thresholding
        _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return binary

    def _deskew(self, img: np.ndarray) -> np.ndarray:
        """Correct skew in image.

        Args:
            img: Grayscale or binary image

        Returns:
            Deskewed image
        """
        # Detect edges
        edges = cv2.Canny(img, 50, 150, apertureSize=3)

        # Detect lines using Hough transform
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)

        if lines is None or len(lines) == 0:
            return img

        # Calculate median angle
        angles = []
        for rho, theta in lines[:, 0]:
            angle = np.degrees(theta) - 90
            # Filter near-horizontal lines
            if abs(angle) < 45:
                angles.append(angle)

        if not angles:
            return img

        median_angle = np.median(angles)

        # Only deskew if angle is significant
        if abs(median_angle) > 0.5:
            # Rotate image
            (h, w) = img.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
            img = cv2.warpAffine(
                img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
            )

        return img


def resize_for_ocr(image: Image.Image, target_dpi: int = 300) -> Image.Image:
    """Resize image to target DPI for optimal OCR.

    Args:
        image: Input image
        target_dpi: Target DPI

    Returns:
        Resized image
    """
    # Assume original is 72 DPI if not specified
    scale = target_dpi / 72
    new_size = (int(image.width * scale), int(image.height * scale))

    # Use high-quality resampling
    return image.resize(new_size, Image.Resampling.LANCZOS)
