"""
Web Research Agent - Fetches current information from the web
"""
import os
from typing import List, Dict
from tavily import TavilyClient
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

class WebResearchAgent:
    """Agent for conducting web research"""
    
    def __init__(self, llm, tavily_api_key: str = None):
        """
        Initialize web research agent
        
        Args:
            llm: Language model instance
            tavily_api_key: Tavily API key (optional, will use env var if not provided)
        """
        self.llm = llm
        
        # Initialize Tavily client
        api_key = tavily_api_key or os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("TAVILY_API_KEY not found in environment variables")
        
        self.tavily_client = TavilyClient(api_key=api_key)
        
        # Define synthesis prompt
        self.synthesis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a research assistant that synthesizes web search results into clear, informative answers.

Guidelines:
- Provide accurate information based on the search results
- Cite sources when relevant
- Present information in a structured, easy-to-read format
- If results are insufficient or conflicting, acknowledge this
- Focus on the most recent and authoritative sources

{conversation_context}"""),
            ("user", """Query: {query}

Search Results:
{search_results}

Please provide a comprehensive answer based on these search results.""")
        ])
    
    def search_web(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Perform web search using Tavily
        
        Args:
            query: Search query
            max_results: Maximum number of results
        
        Returns:
            List of search results
        """
        try:
            # Perform search
            response = self.tavily_client.search(
                query=query,
                max_results=max_results,
                search_depth="advanced",
                include_answer=True,
                include_raw_content=False
            )
            
            results = []
            
            # Add Tavily's answer if available
            if response.get("answer"):
                results.append({
                    "title": "AI Summary",
                    "content": response["answer"],
                    "url": "tavily://summary",
                    "score": 1.0
                })
            
            # Add search results
            for result in response.get("results", []):
                results.append({
                    "title": result.get("title", ""),
                    "content": result.get("content", ""),
                    "url": result.get("url", ""),
                    "score": result.get("score", 0.0)
                })
            
            return results
            
        except Exception as e:
            print(f"Web search error: {e}")
            return []
    
    def process_query(self, query: str, conversation_context: str = "") -> dict:
        """
        Process a query requiring web research
        
        Args:
            query: User query
            conversation_context: Previous conversation context
        
        Returns:
            Dictionary with response and metadata
        """
        try:
            # Perform web search
            search_results = self.search_web(query)
            
            if not search_results:
                return {
                    "response": "I apologize, but I couldn't find relevant information from web search. Please try rephrasing your query.",
                    "agent": "web_research",
                    "sources": [],
                    "search_results": [],
                    "metadata": {"error": "No search results found"}
                }
            
            # Format search results for LLM
            formatted_results = self._format_search_results(search_results)
            
            # Prepare context
            context_text = ""
            if conversation_context:
                context_text = f"Previous conversation:\n{conversation_context}\n"
            
            # Synthesize answer using LLM
            chain = self.synthesis_prompt | self.llm | StrOutputParser()
            
            response = chain.invoke({
                "query": query,
                "search_results": formatted_results,
                "conversation_context": context_text
            })
            
            # Extract sources
            sources = [
                {"title": result["title"], "url": result["url"]}
                for result in search_results
                if result["url"] != "tavily://summary"
            ]
            
            return {
                "response": response,
                "agent": "web_research",
                "sources": sources,
                "search_results": search_results,
                "metadata": {
                    "num_results": len(search_results),
                    "context_used": bool(conversation_context)
                }
            }
            
        except Exception as e:
            return {
                "response": f"I encountered an error while researching: {str(e)}",
                "agent": "web_research",
                "sources": [],
                "search_results": [],
                "metadata": {"error": str(e)}
            }
    
    def _format_search_results(self, results: List[Dict]) -> str:
        """Format search results for LLM consumption"""
        formatted = []
        
        for i, result in enumerate(results, 1):
            title = result.get("title", "Untitled")
            content = result.get("content", "")
            url = result.get("url", "")
            
            if url != "tavily://summary":
                formatted.append(f"{i}. **{title}**\n   Source: {url}\n   {content}\n")
            else:
                formatted.append(f"{i}. {content}\n")
        
        return "\n".join(formatted)
    
    def get_quick_answer(self, query: str) -> str:
        """
        Get a quick answer using Tavily's answer feature
        
        Args:
            query: Search query
        
        Returns:
            Quick answer string
        """
        try:
            response = self.tavily_client.search(
                query=query,
                max_results=3,
                include_answer=True
            )
            
            return response.get("answer", "No quick answer available")
            
        except Exception as e:
            return f"Error getting quick answer: {str(e)}"

if __name__ == "__main__":
    # Test web research agent
    from src.utils.llm_config import get_general_llm
    
    try:
        llm = get_general_llm()
        agent = WebResearchAgent(llm)
        
        # Test query
        query = "What are the latest developments in artificial intelligence in 2025?"
        
        print("🌐 Web Research Agent Test\n")
        print(f"Query: {query}\n")
        
        result = agent.process_query(query)
        
        print(f"Response: {result['response']}\n")
        print(f"Agent: {result['agent']}")
        print(f"\nSources ({len(result['sources'])}):")
        for i, source in enumerate(result['sources'][:3], 1):
            print(f"{i}. {source['title']}")
            print(f"   {source['url']}")
        
        print("\n✅ Web research agent test successful!")
        
    except Exception as e:
        print(f"❌ Error: {e}")