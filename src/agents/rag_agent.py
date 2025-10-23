"""
RAG Agent - Retrieval-Augmented Generation from knowledge base
"""
from typing import List, Dict
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class RAGAgent:
    """Agent for retrieval-augmented generation"""
    
    def __init__(self, llm, vector_store_manager):
        """
        Initialize RAG agent
        
        Args:
            llm: Language model instance
            vector_store_manager: VectorStoreManager instance
        """
        self.llm = llm
        self.vector_store_manager = vector_store_manager
        
        # Define RAG prompt
        self.rag_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an AI assistant with access to TechNova Inc.'s financial documents and company information.

Guidelines:
- Answer questions based ONLY on the provided context from company documents
- If the context doesn't contain the answer, say so honestly
- Cite specific reports when possible (e.g., "According to the Q1 2024 Earnings Report...")
- Provide specific numbers, dates, and details when available
- If asked about trends, analyze across multiple time periods if available

{conversation_context}"""),
            ("user", """Query: {query}

Relevant Context from Company Documents:
{context}

Please answer the query based on the above context.""")
        ])
    
    def retrieve_context(self, query: str, k: int = 3) -> List[Dict]:
        """
        Retrieve relevant documents from vector store
        
        Args:
            query: User query
            k: Number of documents to retrieve
        
        Returns:
            List of relevant documents with scores
        """
        try:
            results = self.vector_store_manager.similarity_search_with_score(query, k=k)
            
            documents = []
            for doc, score in results:
                documents.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "relevance_score": float(score)
                })
            
            return documents
            
        except Exception as e:
            print(f"Retrieval error: {e}")
            return []
    
    def process_query(self, query: str, conversation_context: str = "", k: int = 3) -> dict:
        """
        Process a query using RAG
        
        Args:
            query: User query
            conversation_context: Previous conversation context
            k: Number of documents to retrieve
        
        Returns:
            Dictionary with response and metadata
        """
        try:
            # Retrieve relevant documents
            documents = self.retrieve_context(query, k=k)
            
            if not documents:
                return {
                    "response": "I apologize, but I couldn't find relevant information in our company documents. Please try rephrasing your query or ask about a different topic.",
                    "agent": "rag",
                    "sources": [],
                    "retrieved_docs": [],
                    "metadata": {"error": "No relevant documents found"}
                }
            
            # Format context
            context = self._format_context(documents)
            
            # Prepare conversation context
            context_text = ""
            if conversation_context:
                context_text = f"Previous conversation:\n{conversation_context}\n"
            
            # Generate answer using LLM
            chain = self.rag_prompt | self.llm | StrOutputParser()
            
            response = chain.invoke({
                "query": query,
                "context": context,
                "conversation_context": context_text
            })
            
            # Extract sources
            sources = self._extract_sources(documents)
            
            return {
                "response": response,
                "agent": "rag",
                "sources": sources,
                "retrieved_docs": documents,
                "metadata": {
                    "num_docs_retrieved": len(documents),
                    "avg_relevance_score": sum(doc["relevance_score"] for doc in documents) / len(documents),
                    "context_used": bool(conversation_context)
                }
            }
            
        except Exception as e:
            return {
                "response": f"I encountered an error accessing company documents: {str(e)}",
                "agent": "rag",
                "sources": [],
                "retrieved_docs": [],
                "metadata": {"error": str(e)}
            }
    
    def _format_context(self, documents: List[Dict]) -> str:
        """Format retrieved documents as context"""
        formatted = []
        
        for i, doc in enumerate(documents, 1):
            content = doc["content"]
            metadata = doc.get("metadata", {})
            source = metadata.get("source", "Unknown document")
            
            formatted.append(f"[Document {i} - {source}]\n{content}\n")
        
        return "\n".join(formatted)
    
    def _extract_sources(self, documents: List[Dict]) -> List[Dict]:
        """Extract source information from documents"""
        sources = []
        seen_sources = set()
        
        for doc in documents:
            metadata = doc.get("metadata", {})
            source = metadata.get("source", "Unknown")
            
            if source not in seen_sources:
                sources.append({
                    "document": source,
                    "relevance_score": doc["relevance_score"]
                })
                seen_sources.add(source)
        
        return sources
    
    def search_documents(self, query: str, k: int = 5) -> List[Dict]:
        """
        Search documents without LLM generation (for debugging/inspection)
        
        Args:
            query: Search query
            k: Number of results
        
        Returns:
            List of documents
        """
        return self.retrieve_context(query, k=k)

if __name__ == "__main__":
    # Test RAG agent
    import os
    import sys
    
    # Add parent directory to path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    
    from src.utils.llm_config import get_general_llm
    from src.utils.vector_store import initialize_vectorstore
    
    try:
        # Initialize components
        llm = get_general_llm()
        
        data_path = os.path.join(os.path.dirname(__file__), "..", "data", "financial_reports")
        vector_store_manager = initialize_vectorstore(data_path)
        
        agent = RAGAgent(llm, vector_store_manager)
        
        # Test queries
        test_queries = [
            "What was TechNova's revenue in Q1 2024?",
            "What products does TechNova offer?",
            "What are TechNova's main risk factors?"
        ]
        
        print("📚 RAG Agent Test\n")
        
        for query in test_queries:
            print(f"Query: {query}")
            result = agent.process_query(query)
            print(f"Response: {result['response'][:300]}...")
            print(f"Agent: {result['agent']}")
            print(f"Sources: {len(result['sources'])} documents")
            print()
        
        print("✅ RAG agent test successful!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()