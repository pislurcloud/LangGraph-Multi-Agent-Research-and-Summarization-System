"""
LLM Agent - Handles general knowledge queries
"""
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class LLMAgent:
    """Agent for handling general knowledge queries"""
    
    def __init__(self, llm):
        """
        Initialize LLM agent
        
        Args:
            llm: Language model instance
        """
        self.llm = llm
        
        # Define prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful AI assistant that provides accurate and informative answers to general knowledge questions.

Guidelines:
- Provide clear, concise, and accurate information
- Use examples when helpful
- If you're not certain, acknowledge limitations
- Structure responses for readability
- Be conversational but professional

{conversation_context}"""),
            ("user", "{query}")
        ])
    
    def process_query(self, query: str, conversation_context: str = "") -> dict:
        """
        Process a general knowledge query
        
        Args:
            query: User query
            conversation_context: Previous conversation context
        
        Returns:
            Dictionary with response and metadata
        """
        try:
            # Prepare context
            context_text = ""
            if conversation_context:
                context_text = f"Previous conversation:\n{conversation_context}\n"
            
            # Create chain
            chain = self.prompt | self.llm | StrOutputParser()
            
            # Generate response
            response = chain.invoke({
                "query": query,
                "conversation_context": context_text
            })
            
            return {
                "response": response,
                "agent": "llm",
                "sources": [],
                "metadata": {
                    "query_type": "general_knowledge",
                    "context_used": bool(conversation_context)
                }
            }
            
        except Exception as e:
            return {
                "response": f"I apologize, but I encountered an error processing your query: {str(e)}",
                "agent": "llm",
                "sources": [],
                "metadata": {
                    "error": str(e)
                }
            }
    
    def answer_with_context(self, query: str, context: str) -> str:
        """
        Answer query with provided context
        
        Args:
            query: User query
            context: Context information
        
        Returns:
            Response string
        """
        enhanced_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful AI assistant. Use the provided context to answer the user's query.
            
Context:
{context}

If the context is relevant, use it to inform your answer. If not, answer based on your general knowledge."""),
            ("user", "{query}")
        ])
        
        chain = enhanced_prompt | self.llm | StrOutputParser()
        
        return chain.invoke({
            "query": query,
            "context": context
        })

if __name__ == "__main__":
    # Test LLM agent
    from src.utils.llm_config import get_general_llm
    
    try:
        llm = get_general_llm()
        agent = LLMAgent(llm)
        
        # Test queries
        test_queries = [
            "What is machine learning?",
            "Explain the concept of neural networks",
            "What are the benefits of cloud computing?"
        ]
        
        print("🤖 LLM Agent Test\n")
        
        for query in test_queries:
            print(f"Query: {query}")
            result = agent.process_query(query)
            print(f"Response: {result['response'][:200]}...")
            print(f"Agent: {result['agent']}")
            print()
        
        print("✅ LLM agent test successful!")
        
    except Exception as e:
        print(f"❌ Error: {e}")