import hashlib
import time
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator
import google.generativeai as genai
from app.config import settings
from app.models.clause import ClauseType, RiskLevel
from app.utils.logging_config import logger

# Initialize Gemini
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)


class ClauseClassificationResponse(BaseModel):
    clause_type: ClauseType
    confidence: float = Field(ge=0.0, le=1.0)


class RiskAssessmentResponse(BaseModel):
    risk_level: RiskLevel
    risk_explanation: str
    red_flags: List[str] = Field(default_factory=list)


class ExecutiveSummaryResponse(BaseModel):
    summary: str
    key_points: List[str] = Field(default_factory=list)


class NegotiationSuggestionResponse(BaseModel):
    suggestion: str
    priority: str = Field(default="medium")  # high, medium, low


class AIService:
    """Single abstraction layer for all LLM calls using Gemini API."""
    
    def __init__(self):
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        self.cache: Dict[str, Any] = {}
    
    def _get_cache_key(self, text: str, task_type: str) -> str:
        """Generate a cache key from text and task type."""
        combined = f"{task_type}:{text}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Get result from cache if available."""
        return self.cache.get(cache_key)
    
    def _set_cache(self, cache_key: str, value: Any):
        """Set result in cache."""
        self.cache[cache_key] = value
    
    def _call_llm_with_retry(self, prompt: str, max_retries: int = 3) -> str:
        """Call LLM with exponential backoff retry logic."""
        for attempt in range(max_retries):
            try:
                start_time = time.time()
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        response_mime_type="application/json",
                        temperature=0.3,
                    )
                )
                latency = time.time() - start_time
                logger.info(f"LLM call completed in {latency:.2f}s (attempt {attempt + 1})")
                return response.text
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"LLM call failed after {max_retries} attempts: {e}")
                    raise
                wait_time = 2 ** attempt  # Exponential backoff
                logger.warning(f"LLM call failed (attempt {attempt + 1}), retrying in {wait_time}s: {e}")
                time.sleep(wait_time)
    
    def _validate_response(self, response_text: str, schema_class: type) -> Any:
        """Validate LLM response against Pydantic schema."""
        try:
            import json
            response_dict = json.loads(response_text)
            return schema_class(**response_dict)
        except Exception as e:
            logger.error(f"Response validation failed: {e}")
            raise ValueError(f"Invalid response format: {e}")
    
    async def classify_clause(self, clause_text: str) -> ClauseType:
        """
        Classify a clause into its type (PRICING, LIABILITY, etc.).
        Returns the clause type.
        """
        cache_key = self._get_cache_key(clause_text, "classify")
        cached = self._get_from_cache(cache_key)
        if cached:
            logger.info("Cache hit for clause classification")
            return cached
        
        prompt = f"""
        Analyze the following contract clause and classify it into one of these types:
        PRICING, TERM_TERMINATION, LIABILITY, INDEMNIFICATION, IP_OWNERSHIP, 
        CONFIDENTIALITY, AUTO_RENEWAL, GOVERNING_LAW, LIMITATION_OF_LIABILITY, OTHER
        
        Clause text: {clause_text[:2000]}
        
        Return a JSON object with:
        - clause_type: the classified type (must be one of the above)
        - confidence: a float between 0.0 and 1.0 indicating confidence
        """
        
        response_text = self._call_llm_with_retry(prompt)
        response = self._validate_response(response_text, ClauseClassificationResponse)
        
        self._set_cache(cache_key, response.clause_type)
        return response.clause_type
    
    async def assess_risk(
        self, 
        clause_text: str, 
        clause_type: ClauseType
    ) -> tuple[RiskLevel, str]:
        """
        Assess the risk level of a clause and provide explanation.
        Returns tuple of (risk_level, risk_explanation).
        """
        cache_key = self._get_cache_key(f"{clause_text}:{clause_type}", "assess_risk")
        cached = self._get_from_cache(cache_key)
        if cached:
            logger.info("Cache hit for risk assessment")
            return cached
        
        # Define red flag patterns for each clause type
        red_flag_examples = {
            ClauseType.LIABILITY: [
                "unlimited liability",
                "joint and several liability",
                "liability for consequential damages"
            ],
            ClauseType.INDEMNIFICATION: [
                "broad indemnification obligations",
                "indemnification for third-party claims",
                "unlimited indemnification"
            ],
            ClauseType.IP_OWNERSHIP: [
                "broad IP assignment",
                "work for hire without limitations",
                "ownership of all derivative works"
            ],
            ClauseType.AUTO_RENEWAL: [
                "automatic renewal with less than 30 days notice",
                "unlimited renewal terms",
                "no opt-out mechanism"
            ],
            ClauseType.PRICING: [
                "unilateral price increases",
                "no price cap",
                "hidden fees"
            ]
        }
        
        examples = red_flag_examples.get(clause_type, ["unusual terms", "one-sided obligations"])
        
        prompt = f"""
        Assess the risk level of the following {clause_type.value} clause.
        
        Red flag patterns to look for: {', '.join(examples)}
        
        Clause text: {clause_text[:2000]}
        
        Return a JSON object with:
        - risk_level: one of HIGH, MEDIUM, LOW, NONE
        - risk_explanation: a brief explanation (1-2 sentences) of why this risk level was assigned
        - red_flags: a list of specific red flags found (empty list if none)
        """
        
        response_text = self._call_llm_with_retry(prompt)
        response = self._validate_response(response_text, RiskAssessmentResponse)
        
        result = (response.risk_level, response.risk_explanation)
        self._set_cache(cache_key, result)
        return result
    
    async def generate_summary(
        self, 
        clauses: List[Dict[str, Any]], 
        overall_risk_score: int
    ) -> str:
        """
        Generate an executive summary for the contract analysis.
        Returns the summary text.
        """
        # Create a summary of clauses for context
        clause_summary = []
        high_risk_count = sum(1 for c in clauses if c.get('risk_level') == RiskLevel.HIGH)
        medium_risk_count = sum(1 for c in clauses if c.get('risk_level') == RiskLevel.MEDIUM)
        
        for clause in clauses[:10]:  # Limit to first 10 clauses for context
            clause_summary.append(
                f"- {clause.get('clause_type', 'OTHER')}: {clause.get('risk_level', 'NONE')} risk"
            )
        
        prompt = f"""
        Generate a 1-paragraph executive summary for a contract analysis.
        
        Overall risk score: {overall_risk_score}/100
        High risk clauses: {high_risk_count}
        Medium risk clauses: {medium_risk_count}
        
        Key clauses identified:
        {chr(10).join(clause_summary)}
        
        Return a JSON object with:
        - summary: a concise 1-paragraph executive summary
        - key_points: a list of 3-5 key takeaways
        """
        
        response_text = self._call_llm_with_retry(prompt)
        response = self._validate_response(response_text, ExecutiveSummaryResponse)
        
        return response.summary
    
    async def suggest_negotiation(
        self, 
        clause_text: str, 
        clause_type: ClauseType,
        risk_explanation: str
    ) -> str:
        """
        Suggest negotiation points for a high/medium risk clause.
        Returns the suggestion text.
        """
        cache_key = self._get_cache_key(f"{clause_text}:{clause_type}:{risk_explanation}", "negotiate")
        cached = self._get_from_cache(cache_key)
        if cached:
            logger.info("Cache hit for negotiation suggestion")
            return cached
        
        prompt = f"""
        Provide a negotiation suggestion for the following {clause_type.value} clause.
        
        Risk explanation: {risk_explanation}
        
        Clause text: {clause_text[:2000]}
        
        Return a JSON object with:
        - suggestion: a specific, actionable negotiation point (1-2 sentences)
        - priority: one of high, medium, low
        """
        
        response_text = self._call_llm_with_retry(prompt)
        response = self._validate_response(response_text, NegotiationSuggestionResponse)
        
        self._set_cache(cache_key, response.suggestion)
        return response.suggestion


# Global AI service instance
ai_service = AIService()
