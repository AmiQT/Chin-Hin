"""
Azure OpenAI Vision OCR Service for Receipt Processing.
Uses GPT-4o (Azure OpenAI) untuk extract structured data dari gambar resit.
"""

import logging
import base64
import json
from typing import Optional, List
from pydantic import BaseModel, Field
from openai import AzureOpenAI
from app.config import get_settings

logger = logging.getLogger(__name__)


class ExtractedItem(BaseModel):
    name: str
    price: float


class ReceiptData(BaseModel):
    """Extracted receipt data dengan smart categorization."""
    merchant_name: Optional[str] = Field(None, description="Name of the merchant or store")
    total_amount: Optional[float] = Field(None, description="Total amount paid in RM")
    date: Optional[str] = Field(None, description="Receipt date in YYYY-MM-DD or DD/MM/YYYY")
    items: List[ExtractedItem] = Field(default_factory=list, description="List of items purchased")
    category_suggestion: Optional[str] = Field(None, description="Suggested category: Meals, Transport, Parking, Medical, Others")
    confidence: float = 1.0

    def to_dict(self) -> dict:
        return {
            "merchant_name": self.merchant_name,
            "total_amount": self.total_amount,
            "date": self.date,
            "items": [item.model_dump() for item in self.items],
            "category": self.category_suggestion,
            "confidence": self.confidence
        }


class OCRService:
    """Azure OpenAI Vision OCR Service untuk process resit."""

    def __init__(self):
        self._client: Optional[AzureOpenAI] = None

    def _get_client(self) -> Optional[AzureOpenAI]:
        """Get or create Azure OpenAI client."""
        if self._client is not None:
            return self._client

        settings = get_settings()
        if not settings.azure_openai_api_key:
            logger.warning("⚠️ Azure OpenAI API Key belum dikonfigure untuk OCR!")
            return None

        try:
            self._client = AzureOpenAI(
                api_key=settings.azure_openai_api_key,
                azure_endpoint=settings.azure_openai_endpoint,
                api_version=settings.azure_openai_api_version,
            )
            logger.info("✅ Azure OpenAI client initialized untuk OCR")
            return self._client
        except Exception as e:
            logger.error(f"❌ Failed to initialize Azure client: {e}")
            return None

    async def extract_receipt_data(self, image_content: bytes) -> ReceiptData:
        """
        Extract structured data dari gambar resit guna Azure OpenAI Vision.
        """
        client = self._get_client()
        settings = get_settings()

        if client is None:
            return ReceiptData(confidence=0.0)

        try:
            image_b64 = base64.b64encode(image_content).decode("utf-8")

            prompt = """Extract structured info from this receipt image. Return JSON with these fields:
- merchant_name: string (name of store/restaurant)
- total_amount: number (total in RM)
- date: string (YYYY-MM-DD format)
- items: array of {name: string, price: number}
- category_suggestion: one of [Meals, Transport, Parking, Medical, Others]
- confidence: number 0-1

Return ONLY valid JSON, no extra text."""

            response = client.chat.completions.create(
                model=settings.azure_openai_deployment,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_b64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1024,
            )

            raw_text = response.choices[0].message.content
            # Clean JSON response
            if "```json" in raw_text:
                raw_text = raw_text.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_text:
                raw_text = raw_text.split("```")[1].split("```")[0].strip()

            data = json.loads(raw_text)
            extracted = ReceiptData(**data)
            logger.info(f"✅ Azure OCR Extracted: {extracted.merchant_name}, RM{extracted.total_amount}")
            return extracted

        except Exception as e:
            logger.error(f"❌ Azure OCR Error: {e}")
            return ReceiptData(confidence=0.0)


# Singleton instance
_ocr_service: Optional[OCRService] = None


def get_ocr_service() -> OCRService:
    """Get OCR service singleton."""
    global _ocr_service
    if _ocr_service is None:
        _ocr_service = OCRService()
    return _ocr_service
