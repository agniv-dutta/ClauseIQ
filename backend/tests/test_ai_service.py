import pytest
from unittest.mock import Mock, patch
from app.services.ai_service import AIService
from app.models.clause import ClauseType, RiskLevel


@pytest.fixture
def ai_service():
    return AIService()


@pytest.mark.asyncio
async def test_classify_clause(ai_service):
    # Mock the LLM call
    mock_response = Mock()
    mock_response.text = '{"clause_type": "LIABILITY", "confidence": 0.95}'
    
    with patch.object(ai_service.model, 'generate_content', return_value=mock_response):
        result = await ai_service.classify_clause("The parties agree to unlimited liability.")
        assert result == ClauseType.LIABILITY


@pytest.mark.asyncio
async def test_assess_risk(ai_service):
    # Mock the LLM call
    mock_response = Mock()
    mock_response.text = '{"risk_level": "HIGH", "risk_explanation": "Unlimited liability is a red flag.", "red_flags": ["unlimited liability"]}'
    
    with patch.object(ai_service.model, 'generate_content', return_value=mock_response):
        risk_level, explanation = await ai_service.assess_risk(
            "The parties agree to unlimited liability.",
            ClauseType.LIABILITY
        )
        assert risk_level == RiskLevel.HIGH
        assert "red flag" in explanation.lower()


@pytest.mark.asyncio
async def test_generate_summary(ai_service):
    # Mock the LLM call
    mock_response = Mock()
    mock_response.text = '{"summary": "This contract has high risk due to unlimited liability clauses.", "key_points": ["High risk", "Liability concerns"]}'
    
    clauses = [
        {"clause_type": ClauseType.LIABILITY, "risk_level": RiskLevel.HIGH, "risk_explanation": "Unlimited liability"}
    ]
    
    with patch.object(ai_service.model, 'generate_content', return_value=mock_response):
        summary = await ai_service.generate_summary(clauses, 85)
        assert "high risk" in summary.lower()


@pytest.mark.asyncio
async def test_suggest_negotiation(ai_service):
    # Mock the LLM call
    mock_response = Mock()
    mock_response.text = '{"suggestion": "Negotiate to cap liability at contract value.", "priority": "high"}'
    
    with patch.object(ai_service.model, 'generate_content', return_value=mock_response):
        suggestion = await ai_service.suggest_negotiation(
            "The parties agree to unlimited liability.",
            ClauseType.LIABILITY,
            "Unlimited liability is a red flag."
        )
        assert "cap" in suggestion.lower()


@pytest.mark.asyncio
async def test_cache_hit(ai_service):
    # Test that caching works
    clause_text = "The parties agree to unlimited liability."
    
    # Mock the LLM call
    mock_response = Mock()
    mock_response.text = '{"clause_type": "LIABILITY", "confidence": 0.95}'
    
    with patch.object(ai_service.model, 'generate_content', return_value=mock_response):
        # First call
        result1 = await ai_service.classify_clause(clause_text)
        # Second call should hit cache
        result2 = await ai_service.classify_clause(clause_text)
        
        assert result1 == result2 == ClauseType.LIABILITY
        # LLM should only be called once due to cache
        assert ai_service.model.generate_content.call_count == 1


@pytest.mark.asyncio
async def test_retry_logic(ai_service):
    # Test retry logic on failure
    mock_response = Mock()
    mock_response.text = '{"clause_type": "LIABILITY", "confidence": 0.95}'
    
    # Fail twice, then succeed
    call_count = [0]
    
    def side_effect(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] < 3:
            raise Exception("API Error")
        return mock_response
    
    with patch.object(ai_service.model, 'generate_content', side_effect=side_effect):
        result = await ai_service.classify_clause("Test clause")
        assert result == ClauseType.LIABILITY
        assert call_count[0] == 3  # Should have retried twice
