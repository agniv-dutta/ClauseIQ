import pdfplumber
import fitz  # PyMuPDF
import docx
from PIL import Image
import pytesseract
import io
from typing import Optional, Tuple
from app.utils.logging_config import logger


class DocumentParser:
    """Service for extracting text from PDF and DOCX files with OCR fallback."""
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> Tuple[str, int]:
        """
        Extract text from PDF using pdfplumber first, then PyMuPDF as fallback.
        Returns tuple of (extracted_text, page_count).
        """
        text = ""
        page_count = 0
        
        # Try pdfplumber first
        try:
            with pdfplumber.open(file_path) as pdf:
                page_count = len(pdf.pages)
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            logger.warning(f"pdfplumber failed: {e}, trying PyMuPDF")
        
        # If text is too short relative to page count, try PyMuPDF
        if len(text) < 100 * page_count and page_count > 0:
            try:
                doc = fitz.open(file_path)
                text = ""
                for page in doc:
                    text += page.get_text() + "\n"
                doc.close()
            except Exception as e:
                logger.warning(f"PyMuPDF failed: {e}")
        
        # If still too short, try OCR
        if len(text) < 100 * page_count and page_count > 0:
            logger.info("Text extraction suspiciously short, attempting OCR")
            text = DocumentParser._extract_text_with_ocr(file_path)
        
        return text, page_count
    
    @staticmethod
    def _extract_text_with_ocr(file_path: str) -> str:
        """
        Extract text from PDF using OCR (pytesseract).
        This is a fallback for scanned/image-based PDFs.
        """
        text = ""
        try:
            doc = fitz.open(file_path)
            for page_num, page in enumerate(doc):
                # Render page to image
                pix = page.get_pixmap()
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                
                # Perform OCR
                page_text = pytesseract.image_to_string(img)
                text += page_text + "\n"
                
                logger.info(f"OCR completed for page {page_num + 1}")
            doc.close()
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return ""
        
        return text
    
    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"DOCX extraction failed: {e}")
            raise
    
    @staticmethod
    def extract_text(file_path: str, file_type: str) -> Tuple[str, int]:
        """
        Extract text from a document based on file type.
        Returns tuple of (extracted_text, page_count).
        For DOCX, page_count is 0.
        """
        if file_type.lower() == "pdf":
            return DocumentParser.extract_text_from_pdf(file_path)
        elif file_type.lower() == "docx":
            text = DocumentParser.extract_text_from_docx(file_path)
            return text, 0
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
