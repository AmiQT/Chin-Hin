"""
Gemini Multimodal OCR Service for Receipt Processing.
Uses Gemini 2.5 Flash to intelligently extract structured data from receipt images.
Lagi padu dari traditional OCR! 🚀
"""

import logging
import base64
from typing import Optional, List
from pydantic import BaseModel, Field
from google import genai
from app.config import get_settings

logger = logging.getLogger(__name__)

class ExtractedItem(BaseModel):
    name: str
    price: float

class ReceiptData(BaseModel):
    """Extracted receipt data with smart categorization."""
    merchant_name: Optional[str] = Field(None, description="Name of the merchant or store")
    total_amount: Optional[float] = Field(None, description="Total amount paid in RM")
    date: Optional[str] = Field(None, description="Receipt date in YYYY-MM-DD or DD/MM/YYYY")
    items: List[ExtractedItem] = Field(default_factory=list, description="List of items purchased")
    category_suggestion: Optional[str] = Field(None, description="Suggested category (e.g., Meals, Transport, Parking, etc.)")
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
    """Gemini 2.5 Multimodal Extraction Service."""
    
    def __init__(self):
        self._client: Optional[genai.Client] = None
        self._initialized = False
    
    def _get_client(self) -> Optional[genai.Client]:
        """Get or create Gemini client."""
        if self._client is not None:
            return self._client
        
        settings = get_settings()
        api_keys = settings.gemini_api_key_list
        if not api_keys:
            logger.warning("⚠️ No Gemini API keys configured for Multimodal Extraction!")
            return None
        
        try:
            # Use the first available key for now (rotation handled primarily in chat)
            self._client = genai.Client(api_key=api_keys[0])
            self._initialized = True
            logger.info("✅ Gemini Client initialized for Multimodal Extraction")
            return self._client
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini client: {e}")
            return None
    
    async def extract_receipt_data(self, image_content: bytes) -> ReceiptData:
        """
        Extract structured data from receipt image using Gemini 2.5 Flash.
        """
        client = self._get_client()
        if client is None:
            return ReceiptData(confidence=0.0)
        
        try:
            # Prepare image part
            # Use base64 if needed, or direct bytes if SDK supports it
            image_b64 = base64.b64encode(image_content).decode("utf-8")
            
            prompt = """
            Extract structured info from this receipt. Be precise with the amount and merchant name.
            Suggest a relevant claim category (Meals, Transport, Parking, Medical, Others).
            """
            
            # Using Gemini 2.5 Flash for multimodal extraction
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    prompt,
                    # Image part
                    {"mime_type": "image/jpeg", "data": image_b64}
                ],
                config={
                    "response_mime_type": "application/json",
                    "response_schema": ReceiptData,
                }
            )
            
            if not response.parsed:
                logger.error("❌ Failed to parse Gemini response as JSON")
                return ReceiptData(confidence=0.0)
            
            extracted = response.parsed
            logger.info(f"✅ Gemini Extracted: {extracted.merchant_name}, RM{extracted.total_amount}")
            return extracted
            
        except Exception as e:
            logger.error(f"❌ Gemini Multimodal Error: {e}")
            import traceback
            traceback.print_exc()
            return ReceiptData(confidence=0.0)

# Singleton instance
_ocr_service: Optional[OCRService] = None

def get_ocr_service() -> OCRService:
    """Get OCR service singleton."""
    global _ocr_service
    if _ocr_service is None:
        _ocr_service = OCRService()
    return _ocr_service
