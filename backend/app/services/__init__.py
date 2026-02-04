"""
Services module - OCR, file storage, notifications.
"""

from app.services.ocr_service import OCRService, ReceiptData, get_ocr_service

__all__ = [
    "OCRService",
    "ReceiptData", 
    "get_ocr_service",
]
