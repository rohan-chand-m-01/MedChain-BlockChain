"""
Advanced OCR extraction for medical reports.
Supports both Tesseract (free) and Google Vision (paid, better accuracy).
"""
import io
import os
import logging
from typing import Dict, Optional
from PIL import Image
import PyPDF2

logger = logging.getLogger(__name__)


class OCRExtractor:
    """Extract text from images and PDFs with high accuracy."""
    
    def __init__(self, use_google_vision: bool = False):
        """
        Initialize OCR extractor.
        
        Args:
            use_google_vision: Use Google Cloud Vision (requires API key)
        """
        self.use_google_vision = use_google_vision
        
        if use_google_vision:
            try:
                from google.cloud import vision
                self.vision_client = vision.ImageAnnotatorClient()
                logger.info("✅ Google Cloud Vision initialized")
            except Exception as e:
                logger.warning(f"Google Vision not available: {e}, falling back to Tesseract")
                self.use_google_vision = False
        
        if not use_google_vision:
            try:
                import pytesseract
                
                # Try to find Tesseract in common Windows locations
                possible_paths = [
                    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                    r'C:\Tesseract-OCR\tesseract.exe',
                ]
                
                tesseract_found = False
                for path in possible_paths:
                    if os.path.exists(path):
                        pytesseract.pytesseract.tesseract_cmd = path
                        tesseract_found = True
                        logger.info(f"✅ Tesseract OCR found at: {path}")
                        break
                
                if not tesseract_found:
                    # Try default (in PATH)
                    pytesseract.get_tesseract_version()
                    logger.info("✅ Tesseract OCR initialized (from PATH)")
                    
            except Exception as e:
                logger.warning(f"Tesseract not available: {e}, using basic extraction")
    
    def extract_from_pdf(self, pdf_bytes: bytes) -> str:
        """
        Extract text from PDF with fallback strategies.
        
        Strategy:
        1. Try native PDF text extraction (fast, accurate for digital PDFs)
        2. If fails, convert to images and use OCR (for scanned PDFs)
        """
        try:
            # Strategy 1: Native PDF text extraction
            pdf_file = io.BytesIO(pdf_bytes)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            # Check if extraction was successful (not just whitespace)
            if text.strip() and len(text.strip()) > 50:
                logger.info(f"✓ Extracted {len(text)} chars from PDF (native)")
                return text
            
            # Strategy 2: OCR on PDF images (for scanned PDFs)
            logger.info("Native extraction failed, trying OCR...")
            return self._extract_from_pdf_images(pdf_bytes)
            
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            return "[PDF text extraction failed]"
    
    def extract_from_image(self, image_bytes: bytes) -> str:
        """Extract text from image using OCR."""
        try:
            if self.use_google_vision:
                return self._extract_with_google_vision(image_bytes)
            else:
                return self._extract_with_tesseract(image_bytes)
        except Exception as e:
            logger.error(f"Image OCR error: {e}")
            return "[Image OCR failed]"
    
    def _extract_with_google_vision(self, image_bytes: bytes) -> str:
        """Extract text using Google Cloud Vision API."""
        try:
            from google.cloud import vision
            
            image = vision.Image(content=image_bytes)
            response = self.vision_client.text_detection(image=image)
            
            if response.error.message:
                raise Exception(response.error.message)
            
            text = response.full_text_annotation.text
            logger.info(f"✓ Google Vision extracted {len(text)} chars")
            return text
            
        except Exception as e:
            logger.error(f"Google Vision error: {e}")
            # Fallback to Tesseract
            return self._extract_with_tesseract(image_bytes)
    
    def _extract_with_tesseract(self, image_bytes: bytes) -> str:
        """Extract text using Tesseract OCR."""
        try:
            import pytesseract
            
            # Open image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Preprocess for better OCR
            # Convert to grayscale
            image = image.convert('L')
            
            # Enhance contrast
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            
            # OCR with medical-optimized config
            custom_config = r'--oem 3 --psm 6'  # LSTM + assume uniform block of text
            text = pytesseract.image_to_string(image, config=custom_config)
            
            logger.info(f"✓ Tesseract extracted {len(text)} chars")
            return text
            
        except Exception as e:
            logger.error(f"Tesseract error: {e}")
            return "[OCR extraction failed - Tesseract not installed]"
    
    def _extract_from_pdf_images(self, pdf_bytes: bytes) -> str:
        """Convert PDF pages to images and OCR them."""
        try:
            import pdf2image
            
            # Try to find poppler in common Windows locations
            poppler_paths = [
                r'C:\Program Files\poppler\Library\bin',
                r'C:\Program Files (x86)\poppler\Library\bin',
                r'C:\poppler\Library\bin',
                r'C:\Program Files\poppler-24.08.0\Library\bin',
                r'C:\Program Files (x86)\poppler-24.08.0\Library\bin',
            ]
            
            poppler_path = None
            for path in poppler_paths:
                if os.path.exists(path):
                    poppler_path = path
                    logger.info(f"✓ Found poppler at: {path}")
                    break
            
            # Convert PDF to images
            if poppler_path:
                images = pdf2image.convert_from_bytes(pdf_bytes, poppler_path=poppler_path)
            else:
                # Try without explicit path (might be in PATH)
                try:
                    images = pdf2image.convert_from_bytes(pdf_bytes)
                except Exception as e:
                    logger.warning(f"Poppler not found in PATH or common locations: {e}")
                    logger.info("💡 To enable scanned PDF support, install poppler:")
                    logger.info("   1. Download from: https://github.com/oschwartz10612/poppler-windows/releases/")
                    logger.info("   2. Extract to C:\\Program Files\\poppler")
                    logger.info("   3. Add C:\\Program Files\\poppler\\Library\\bin to PATH")
                    return "[Scanned PDF - Poppler not installed. Install from: https://github.com/oschwartz10612/poppler-windows/releases/]"
            
            text = ""
            for i, image in enumerate(images):
                # Convert PIL image to bytes
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='PNG')
                img_bytes = img_byte_arr.getvalue()
                
                # OCR the image
                page_text = self.extract_from_image(img_bytes)
                text += f"\n--- Page {i+1} ---\n{page_text}\n"
            
            logger.info(f"✓ OCR extracted {len(text)} chars from {len(images)} pages")
            return text
            
        except ImportError:
            logger.warning("pdf2image not installed, cannot OCR scanned PDFs")
            return "[Scanned PDF - OCR not available]"
        except Exception as e:
            logger.error(f"PDF image OCR error: {e}")
            return "[PDF OCR failed]"


def get_ocr_extractor(use_google_vision: bool = False) -> OCRExtractor:
    """Get configured OCR extractor."""
    return OCRExtractor(use_google_vision=use_google_vision)
