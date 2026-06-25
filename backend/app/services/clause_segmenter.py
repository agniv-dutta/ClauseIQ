import re
from typing import List, Dict, Tuple
from app.utils.logging_config import logger


class ClauseSegmenter:
    """Service for splitting contract text into discrete clauses."""
    
    # Common section header patterns
    SECTION_PATTERNS = [
        r'^\d+\.\s+[A-Z][A-Z\s]+$',  # "1. PAYMENT TERMS"
        r'^[A-Z][A-Z\s]+:$',  # "PAYMENT TERMS:"
        r'^Section\s+\d+\.',  # "Section 1."
        r'^\d+\.\d+\s+',  # "1.1 "
        r'^[IVX]+\.\s+[A-Z]',  # "I. INTRODUCTION"
        r'^ARTICLE\s+\d+',  # "ARTICLE 1"
        r'^Clause\s+\d+',  # "Clause 1"
    ]
    
    @staticmethod
    def segment_by_regex(text: str) -> List[Tuple[str, int, int]]:
        """
        Segment text using regex patterns for section headers.
        Returns list of tuples: (clause_text, start_position, end_position)
        """
        clauses = []
        lines = text.split('\n')
        
        current_clause = []
        current_start = 0
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Check if this line is a section header
            is_header = False
            for pattern in ClauseSegmenter.SECTION_PATTERNS:
                if re.match(pattern, line_stripped, re.IGNORECASE):
                    is_header = True
                    break
            
            if is_header and current_clause:
                # Save previous clause
                clause_text = '\n'.join(current_clause).strip()
                if clause_text:
                    clauses.append((clause_text, current_start, current_start + len(clause_text)))
                # Start new clause
                current_clause = [line]
                current_start = text.find(line, current_start)
            else:
                current_clause.append(line)
        
        # Don't forget the last clause
        if current_clause:
            clause_text = '\n'.join(current_clause).strip()
            if clause_text:
                clauses.append((clause_text, current_start, current_start + len(clause_text)))
        
        # If no clauses found, treat entire text as one clause
        if not clauses and text.strip():
            clauses.append((text.strip(), 0, len(text)))
        
        return clauses
    
    @staticmethod
    def segment_by_paragraph(text: str) -> List[Tuple[str, int, int]]:
        """
        Fallback: segment by paragraphs (double newlines).
        Returns list of tuples: (clause_text, start_position, end_position)
        """
        paragraphs = re.split(r'\n\s*\n', text)
        clauses = []
        current_pos = 0
        
        for para in paragraphs:
            para = para.strip()
            if para:
                start = text.find(para, current_pos)
                end = start + len(para)
                clauses.append((para, start, end))
                current_pos = end
        
        return clauses
    
    @staticmethod
    def segment(text: str, use_llm_fallback: bool = False) -> List[Tuple[str, int, int]]:
        """
        Main segmentation method.
        Uses regex/heuristics first, with LLM fallback if enabled.
        Returns list of tuples: (clause_text, start_position, end_position)
        """
        # Try regex-based segmentation first
        clauses = ClauseSegmenter.segment_by_regex(text)
        
        # If we got reasonable results, return them
        if len(clauses) > 1:
            logger.info(f"Segmented into {len(clauses)} clauses using regex")
            return clauses
        
        # Fallback to paragraph-based segmentation
        clauses = ClauseSegmenter.segment_by_paragraph(text)
        
        if len(clauses) > 1:
            logger.info(f"Segmented into {len(clauses)} clauses using paragraphs")
            return clauses
        
        # Last resort: treat entire text as one clause
        logger.warning("Could not segment text, treating as single clause")
        return [(text.strip(), 0, len(text))]
    
    @staticmethod
    async def segment_with_llm(text: str, ai_service) -> List[Tuple[str, int, int]]:
        """
        Segment text using LLM for contracts without clear structure.
        This is a placeholder - actual implementation would call ai_service.
        """
        # For now, fall back to regex segmentation
        # In production, this would call the LLM to identify clause boundaries
        logger.info("LLM segmentation not yet implemented, using regex fallback")
        return ClauseSegmenter.segment(text)
