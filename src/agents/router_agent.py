"""
Router Agent - Determines query routing strategy
"""
from typing import Literal
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field

class RouteDecision(BaseModel):
    """Route decision model"""
    route: Literal["llm", "web_research", "rag"] = Field(
        description="The route to take: 'llm' for general knowledge, 'web_research' for current information, 'rag' for company documents"
    )
    reasoning: str = Field(description="Brief explanation of why this route was chosen")
    confidence: float = Field(description="Confidence score between 0 and 1")

class RouterAgent:
    """Intelligent query router using LLM"""
    
    def __init__(self, llm):
        """
        Initialize router agent
        
        Args:
            llm: Language model instance
        """
        self.llm = llm
        
        # Define routing prompt
        self.routing_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an intelligent query router for a multi-agent research system.
Your job is to analyze user queries and determine the best route to answer them.

Available routes:
1. **llm**: Use for general knowledge questions that don't require current information or specific company data.
   - Examples: "What is machine learning?", "Explain blockchain technology", "How does photosynthesis work?"
   
2. **web_research**: Use for queries requiring current, up-to-date information.
   - Keywords to watch for: "latest", "current", "recent", "today", "2025", "news"
   - Examples: "What's the latest AI news?", "Current stock price of NVIDIA", "Recent developments in quantum computing"
   
3. **rag**: Use for queries about TechNova Inc. company information, financial reports, or products.
   - Keywords to watch for: "TechNova", "our company", "our revenue", "our products", "financial report"
   - Examples: "What was TechNova's Q1 revenue?", "What products does TechNova offer?", "Summarize our risk factors"

Consider the conversation history if provided.

Analyze the query and respond with ONLY ONE of these exact words: llm, web_research, or rag"""),
            ("user", """Query: {query}

{conversation_context}

Routing decision:""")
        ])
    
    def route_query(self, query: str, conversation_context: str = "") -> dict:
        """
        Route a query to the appropriate agent
        
        Args:
            query: User query
            conversation_context: Previous conversation context
        
        Returns:
            Dictionary with route decision
        """
        # Prepare context
        context_text = ""
        if conversation_context:
            context_text = f"Conversation context:\n{conversation_context}"
        
        # Create chain
        chain = self.routing_prompt | self.llm | StrOutputParser()
        
        # Get routing decision
        try:
            response = chain.invoke({
                "query": query,
                "conversation_context": context_text
            })
            
            # Parse response
            route = response.strip().lower()
            
            # Validate route
            if route not in ["llm", "web_research", "rag"]:
                # Fallback logic based on keywords
                route = self._fallback_routing(query)
            
            # Determine reasoning
            reasoning = self._get_reasoning(query, route)
            
            # Calculate confidence (simple heuristic)
            confidence = self._calculate_confidence(query, route)
            
            return {
                "route": route,
                "reasoning": reasoning,
                "confidence": confidence
            }
            
        except Exception as e:
            print(f"Router error: {e}")
            # Fallback to keyword-based routing
            route = self._fallback_routing(query)
            return {
                "route": route,
                "reasoning": "Fallback routing based on keywords",
                "confidence": 0.6
            }
    
    def _fallback_routing(self, query: str) -> str:
        """Fallback keyword-based routing"""
        query_lower = query.lower()
        
        # Check for web research keywords
        web_keywords = ["latest", "current", "recent", "today", "2025", "news", "now", "price"]
        if any(keyword in query_lower for keyword in web_keywords):
            return "web_research"
        
        # Check for RAG keywords
        rag_keywords = ["technova", "our company", "our revenue", "our product", "financial report", "q1", "q2", "annual"]
        if any(keyword in query_lower for keyword in rag_keywords):
            return "rag"
        
        # Default to LLM for general questions
        return "llm"
    
    def _get_reasoning(self, query: str, route: str) -> str:
        """Generate reasoning for routing decision"""
        if route == "web_research":
            return "Query requires current/recent information from the web"
        elif route == "rag":
            return "Query is about TechNova company information from our knowledge base"
        else:
            return "General knowledge query that can be answered by LLM"
    
    def _calculate_confidence(self, query: str, route: str) -> float:
        """Calculate confidence score for routing decision"""
        query_lower = query.lower()
        
        # High confidence indicators
        if route == "web_research":
            web_keywords = ["latest", "current", "recent", "today", "news"]
            matches = sum(1 for kw in web_keywords if kw in query_lower)
            return min(0.7 + (matches * 0.1), 1.0)
        
        elif route == "rag":
            rag_keywords = ["technova", "our", "company", "revenue", "financial"]
            matches = sum(1 for kw in rag_keywords if kw in query_lower)
            return min(0.7 + (matches * 0.1), 1.0)
        
        else:  # llm
            return 0.75
    
    def get_route_statistics(self, queries: list) -> dict:
        """Get routing statistics for a list of queries"""
        routes = {"llm": 0, "web_research": 0, "rag": 0}
        
        for query in queries:
            result = self.route_query(query)
            routes[result["route"]] += 1
        
        total = len(queries)
        return {
            route: {"count": count, "percentage": (count / total) * 100}
            for route, count in routes.items()
        }

if __name__ == "__main__":
    # Test router agent
    from src.utils.llm_config import get_router_llm
    
    try:
        llm = get_router_llm()
        router = RouterAgent(llm)
        
        # Test queries
        test_queries = [
            "What is artificial intelligence?",
            "What's the latest news on AI regulation?",
            "What was TechNova's revenue in Q1 2024?",
            "Explain quantum computing",
            "Current Bitcoin price",
            "What products does TechNova offer?"
        ]
        
        print("🧭 Router Agent Test\n")
        
        for query in test_queries:
            result = router.route_query(query)
            print(f"Query: {query}")
            print(f"Route: {result['route']}")
            print(f"Reasoning: {result['reasoning']}")
            print(f"Confidence: {result['confidence']:.2f}")
            print()
        
        print("✅ Router agent test successful!")
        
    except Exception as e:
        print(f"❌ Error: {e}")