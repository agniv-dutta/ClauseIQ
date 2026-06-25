from typing import List, Dict, Any
from app.models.clause import RiskLevel
from app.utils.logging_config import logger


class RiskScorer:
    """Service for computing overall risk scores from clause assessments."""
    
    # Risk weights for scoring
    RISK_WEIGHTS = {
        RiskLevel.HIGH: 10,
        RiskLevel.MEDIUM: 4,
        RiskLevel.LOW: 1,
        RiskLevel.NONE: 0
    }
    
    @staticmethod
    def compute_overall_risk_score(clauses: List[Dict[str, Any]]) -> int:
        """
        Compute overall risk score (0-100) from clause risk levels.
        
        Formula:
        - HIGH = 10 points
        - MEDIUM = 4 points
        - LOW = 1 point
        - NONE = 0 points
        
        Then normalize to 0-100 scale and cap at 100.
        """
        total_points = 0
        
        for clause in clauses:
            risk_level = clause.get('risk_level', RiskLevel.NONE)
            total_points += RiskScorer.RISK_WEIGHTS.get(risk_level, 0)
        
        # Normalize: assume 30 points is "100% risk" for a typical contract
        # This can be adjusted based on actual usage patterns
        normalized_score = min(int((total_points / 30) * 100), 100)
        
        logger.info(f"Computed overall risk score: {normalized_score} (raw points: {total_points})")
        return normalized_score
    
    @staticmethod
    def count_risks(clauses: List[Dict[str, Any]]) -> tuple[int, int, int]:
        """
        Count clauses by risk level.
        Returns tuple of (high_count, medium_count, low_count).
        """
        high_count = sum(1 for c in clauses if c.get('risk_level') == RiskLevel.HIGH)
        medium_count = sum(1 for c in clauses if c.get('risk_level') == RiskLevel.MEDIUM)
        low_count = sum(1 for c in clauses if c.get('risk_level') == RiskLevel.LOW)
        
        return high_count, medium_count, low_count
    
    @staticmethod
    def get_risk_distribution(clauses: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Get distribution of risk levels across clauses.
        Returns dict with counts for each risk level.
        """
        distribution = {
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0,
            "NONE": 0
        }
        
        for clause in clauses:
            risk_level = clause.get('risk_level', RiskLevel.NONE)
            distribution[risk_level.value] += 1
        
        return distribution
