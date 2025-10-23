"""
LLM Configuration using Groq API
"""
import os
from typing import Optional
from langchain_groq import ChatGroq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_llm(
    model: str = "meta-llama/llama-4-scout-17b-16e-instruct",
    temperature: float = 0.7,
    max_tokens: Optional[int] = 2048,
    streaming: bool = False
) -> ChatGroq:
    """
    Get configured Groq LLM instance
    
    Args:
        model: Model name to use
        temperature: Sampling temperature (0-1)
        max_tokens: Maximum tokens to generate
        streaming: Enable streaming responses
    
    Returns:
        ChatGroq: Configured LLM instance
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")
    
    return ChatGroq(
        groq_api_key=api_key,
        model_name=model,
        temperature=temperature,
        max_tokens=max_tokens,
        streaming=streaming
    )

def get_router_llm() -> ChatGroq:
    """Get LLM configured for routing decisions (lower temperature for consistency)"""
    return get_llm(temperature=0.1, max_tokens=512)

def get_summarization_llm() -> ChatGroq:
    """Get LLM configured for summarization (balanced temperature)"""
    return get_llm(temperature=0.5, max_tokens=1024)

def get_general_llm() -> ChatGroq:
    """Get LLM configured for general queries"""
    return get_llm(temperature=0.7, max_tokens=2048)

if __name__ == "__main__":
    # Test the configuration
    try:
        llm = get_llm()
        response = llm.invoke("Say hello!")
        print("✅ LLM Configuration successful!")
        print(f"Response: {response.content}")
    except Exception as e:
        print(f"❌ Error: {e}")