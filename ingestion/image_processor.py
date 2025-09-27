import time
from pathlib import Path
from typing import Optional
from ingestion.config import ExtractedContent, ContentType, ProcessingModel


class ImageProcessor:
    """Process image files and prepare data for Gemini vision analysis"""

    @staticmethod
    def extract_content(file_path: str) -> ExtractedContent:
        start_time = time.time()

        # Read binary image bytes (keep raw_text minimal; images don't have text)
        image_bytes: Optional[bytes] = None
        try:
            with open(file_path, 'rb') as f:
                image_bytes = f.read()
        except Exception:
            image_bytes = None

        suffix = Path(file_path).suffix.lower()
        mime_map = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".bmp": "image/bmp",
            ".webp": "image/webp",
        }
        mime_type = mime_map.get(suffix, "image/png")

        structured_data = {
            "image_bytes": image_bytes,
            "image_url": None,
        }

        metadata = {
            "mime_type": mime_type,
            "file_extension": suffix,
            "has_bytes": image_bytes is not None,
        }

        processing_time = time.time() - start_time

        return ExtractedContent(
            content_type=ContentType.IMAGE,
            file_path=file_path,
            raw_text="",  # No inherent text in images
            structured_data=structured_data,
            metadata=metadata,
            processing_model=ProcessingModel.GEMINI_FLASH,
            processing_time=processing_time,
        )


