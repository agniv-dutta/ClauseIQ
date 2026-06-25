import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Optional
from app.config import settings
from app.models.clause import ClauseType
from app.models.market_standard import ContractType
from app.utils.logging_config import logger


class BenchmarkService:
    """Service for comparing clauses against market standards using ChromaDB."""
    
    def __init__(self):
        self.client = None
        self.collection = None
        self._initialize_chroma()
    
    def _initialize_chroma(self):
        """Initialize ChromaDB client and collection."""
        try:
            self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
            
            # Use a simple embedding function (in production, use a better one)
            self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="market_standard_clauses",
                embedding_function=self.embedding_function
            )
            
            logger.info("ChromaDB initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
    
    def add_market_standard_clause(
        self,
        clause_id: str,
        contract_type: ContractType,
        clause_type: ClauseType,
        standard_text: str
    ):
        """Add a market standard clause to the vector database."""
        try:
            self.collection.add(
                documents=[standard_text],
                metadatas=[{
                    "clause_id": clause_id,
                    "contract_type": contract_type.value,
                    "clause_type": clause_type.value
                }],
                ids=[clause_id]
            )
            logger.info(f"Added market standard clause {clause_id} to ChromaDB")
        except Exception as e:
            logger.error(f"Failed to add clause to ChromaDB: {e}")
            raise
    
    def find_similar_clauses(
        self,
        clause_text: str,
        clause_type: ClauseType,
        n_results: int = 3
    ) -> List[Dict]:
        """
        Find similar market standard clauses for a given clause.
        Returns list of similar clauses with similarity scores.
        """
        try:
            results = self.collection.query(
                query_texts=[clause_text],
                where={"clause_type": clause_type.value},
                n_results=n_results
            )
            
            similar_clauses = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    similar_clauses.append({
                        "text": doc,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                        "distance": results['distances'][0][i] if results['distances'] else 0
                    })
            
            logger.info(f"Found {len(similar_clauses)} similar clauses")
            return similar_clauses
        except Exception as e:
            logger.error(f"Failed to query similar clauses: {e}")
            return []
    
    def generate_comparison(
        self,
        clause_text: str,
        clause_type: ClauseType
    ) -> str:
        """
        Generate a comparison string between the clause and market standards.
        """
        similar_clauses = self.find_similar_clauses(clause_text, clause_type)
        
        if not similar_clauses:
            return "No similar market standard clauses found for comparison."
        
        # Get the most similar clause
        most_similar = similar_clauses[0]
        standard_text = most_similar["text"]
        similarity_score = 1 - most_similar.get("distance", 1)  # Convert distance to similarity
        
        if similarity_score > 0.8:
            return f"This clause closely matches market standard language (similarity: {similarity_score:.2f})."
        elif similarity_score > 0.5:
            return f"This clause is moderately similar to market standards (similarity: {similarity_score:.2f}). Some deviations exist."
        else:
            return f"This clause significantly deviates from market standard language (similarity: {similarity_score:.2f}). Review recommended."
    
    def clear_collection(self):
        """Clear all market standard clauses from the collection."""
        try:
            self.client.delete_collection("market_standard_clauses")
            self.collection = self.client.get_or_create_collection(
                name="market_standard_clauses",
                embedding_function=self.embedding_function
            )
            logger.info("Cleared market standard clauses collection")
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            raise


# Global benchmark service instance
benchmark_service = BenchmarkService()
