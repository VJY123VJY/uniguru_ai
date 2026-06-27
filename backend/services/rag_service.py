from RAG.new_rag_query import get_engine
import logging

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        try:
            self.engine = get_engine()
        except Exception as e:
            logger.warning(f"RAG engine not available: {e}")
            self.engine = None

    def search_vectorstore(self, query: str):
        """
        Searches the semantic vector store for relevant context.
        """
        if not self.engine:
            return None
            
        try:
            results = self.engine.retrieve(query, top_k=3)
            if not results:
                return None
                
            best = results[0]
            # Map score to confidence
            return {
                "answer": best["text"],
                "confidence": float(best["score"]),
                "source": "vectorstore"
            }
        except Exception as e:
            logger.error(f"RAG search error: {str(e)}")
            return None

rag_service = RAGService()
