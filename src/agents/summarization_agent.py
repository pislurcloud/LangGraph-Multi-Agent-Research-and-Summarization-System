"""
Summarization Agent - Synthesizes final structured response
"""
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import Dict, List, Optional

class SummarizationAgent:
    """Agent for summarizing and synthesizing final responses"""
    
    def __init__(self, llm):
        """
        Initialize summarization agent
        
        Args:
            llm: Language model instance
        """
        self.llm = llm
        
        # Define summarization prompt
        self.summary_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at synthesizing information into clear, well-structured responses.

Your task is to take the information gathered by specialized agents and create a comprehensive, user-friendly final answer.

CRITICAL FOR WEB RESEARCH:
- If the agent_type is 'web_research', the information is CURRENT and UP-TO-DATE
- DO NOT add disclaimers about knowledge cutoffs or training data
- DO NOT say "as of my last update" or similar phrases
- Present web research findings as current and factual
- The information has been gathered from live web sources

Guidelines:
- Organize information logically with clear structure
- Use markdown formatting for readability (headers, lists, bold text)
- Cite sources when provided
- Be concise but thorough
- Highlight key insights and important numbers
- If information is from web research, present it as current/recent information
- If information is from company documents, reference the specific documents
- Maintain a professional yet conversational tone
- DO NOT mention AI training dates or knowledge limitations

{conversation_context}"""),
            ("user", """Original Query: {query}

Agent Type: {agent_type}
{agent_type_context}

Information Gathered:
{agent_response}

{sources_text}

Please provide a well-structured, comprehensive answer. If this is from web_research, present the information as current without mentioning knowledge cutoffs.""")
        ])
    
    def summarize(
        self,
        query: str,
        agent_response: str,
        agent_type: str,
        sources: List[Dict],
        conversation_context: str = "",
        metadata: Optional[Dict] = None
    ) -> dict:
        """
        Summarize and structure the final response
        
        Args:
            query: Original user query
            agent_response: Response from the specialized agent
            agent_type: Type of agent (llm/web_research/rag)
            sources: List of sources used
            conversation_context: Previous conversation context
            metadata: Additional metadata
        
        Returns:
            Dictionary with final response
        """
        try:
            # Format sources
            sources_text = self._format_sources(sources, agent_type)
            
            # Prepare context
            context_text = ""
            if conversation_context:
                context_text = f"Previous conversation:\n{conversation_context}\n"
            
            # Add agent-specific context
            agent_type_context = ""
            if agent_type == "web_research":
                from datetime import datetime
                current_date = datetime.now().strftime("%B %d, %Y")
                agent_type_context = f"This information was gathered from LIVE WEB SEARCH on {current_date}. It is CURRENT and UP-TO-DATE."
            elif agent_type == "rag":
                agent_type_context = "This information is from internal company documents."
            else:
                agent_type_context = "This information is from general knowledge."
            
            # Generate summary
            chain = self.summary_prompt | self.llm | StrOutputParser()
            
            final_response = chain.invoke({
                "query": query,
                "agent_type": agent_type,
                "agent_type_context": agent_type_context,
                "agent_response": agent_response,
                "sources_text": sources_text,
                "conversation_context": context_text
            })
            
            return {
                "final_response": final_response,
                "original_response": agent_response,
                "agent_used": agent_type,
                "sources": sources,
                "metadata": metadata or {}
            }
            
        except Exception as e:
            # Fallback: return original response if summarization fails
            return {
                "final_response": agent_response,
                "original_response": agent_response,
                "agent_used": agent_type,
                "sources": sources,
                "metadata": {"error": f"Summarization failed: {str(e)}"}
            }
    
    def _format_sources(self, sources: List[Dict], agent_type: str) -> str:
        """Format sources for the prompt"""
        if not sources:
            return "No external sources were used for this response."
        
        formatted = ["Sources:"]
        
        if agent_type == "web_research":
            for i, source in enumerate(sources, 1):
                title = source.get("title", "Untitled")
                url = source.get("url", "")
                formatted.append(f"{i}. {title} - {url}")
        
        elif agent_type == "rag":
            for i, source in enumerate(sources, 1):
                doc = source.get("document", "Unknown document")
                score = source.get("relevance_score", 0)
                formatted.append(f"{i}. {doc} (relevance: {score:.2f})")
        
        return "\n".join(formatted)
    
    def create_structured_summary(
        self,
        query: str,
        responses: Dict[str, str],
        all_sources: List[Dict]
    ) -> str:
        """
        Create a structured summary from multiple agent responses
        (Useful if multiple agents are queried)
        
        Args:
            query: Original query
            responses: Dictionary mapping agent_type to response
            all_sources: All sources from all agents
        
        Returns:
            Structured summary string
        """
        summary_parts = [f"# Response to: {query}\n"]
        
        for agent_type, response in responses.items():
            agent_name = agent_type.replace("_", " ").title()
            summary_parts.append(f"## From {agent_name}\n{response}\n")
        
        if all_sources:
            summary_parts.append("## Sources")
            for i, source in enumerate(all_sources, 1):
                if "url" in source:
                    summary_parts.append(f"{i}. [{source.get('title', 'Source')}]({source['url']})")
                elif "document" in source:
                    summary_parts.append(f"{i}. {source['document']}")
        
        return "\n".join(summary_parts)
    
    def quick_summarize(self, text: str, max_length: int = 200) -> str:
        """
        Quick summarization of long text
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary
        
        Returns:
            Summarized text
        """
        if len(text) <= max_length:
            return text
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Summarize the following text concisely in about {max_length} words."),
            ("user", "{text}")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            summary = chain.invoke({
                "text": text,
                "max_length": max_length
            })
            return summary
        except Exception:
            # Fallback: truncate
            return text[:max_length] + "..."

if __name__ == "__main__":
    # Test summarization agent
    from src.utils.llm_config import get_summarization_llm
    
    try:
        llm = get_summarization_llm()
        agent = SummarizationAgent(llm)
        
        # Test summarization
        query = "What was TechNova's revenue in Q1 2024?"
        agent_response = "TechNova Inc. reported total revenue of $2.8 billion in Q1 2024, representing a 28% year-over-year increase. The Cloud Services & AI Platform segment contributed $1.6 billion (57% of revenue), Enterprise Software brought in $780 million (28%), and Hardware & IoT accounted for $420 million (15%)."
        
        sources = [
            {"document": "Q1_2024_Earnings_Report.txt", "relevance_score": 0.95}
        ]
        
        print("📝 Summarization Agent Test\n")
        print(f"Query: {query}\n")
        
        result = agent.summarize(
            query=query,
            agent_response=agent_response,
            agent_type="rag",
            sources=sources
        )
        
        print(f"Final Response:\n{result['final_response']}\n")
        print(f"Agent Used: {result['agent_used']}")
        print(f"Sources: {len(result['sources'])}")
        
        print("\n✅ Summarization agent test successful!")
        
    except Exception as e:
        print(f"❌ Error: {e}")