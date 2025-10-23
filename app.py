"""
Streamlit UI for LangGraph Multi-Agent Research and Summarization System
"""
import streamlit as st
import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.graph.workflow import create_workflow
from src.utils.memory import reset_memory
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="TechNova AI Research Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .agent-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 0.5rem;
        font-size: 0.85rem;
        font-weight: bold;
        margin-right: 0.5rem;
    }
    .badge-llm {
        background-color: #e3f2fd;
        color: #1976d2;
    }
    .badge-web {
        background-color: #e8f5e9;
        color: #388e3c;
    }
    .badge-rag {
        background-color: #fff3e0;
        color: #f57c00;
    }
    .source-box {
        background-color: #f5f5f5;
        padding: 0.75rem;
        border-radius: 0.5rem;
        margin-top: 0.5rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'workflow' not in st.session_state:
        st.session_state.workflow = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False

def check_api_keys():
    """Check if required API keys are set"""
    groq_key = os.getenv("GROQ_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    
    status = {
        "groq": bool(groq_key and len(groq_key) > 0),
        "tavily": bool(tavily_key and len(tavily_key) > 0)
    }
    
    return status

def display_agent_badge(agent_type: str):
    """Display agent type badge"""
    badges = {
        "llm": ("💡 LLM", "badge-llm"),
        "web_research": ("🌐 Web Research", "badge-web"),
        "rag": ("📚 Knowledge Base", "badge-rag")
    }
    
    label, css_class = badges.get(agent_type, ("❓ Unknown", ""))
    return f'<span class="agent-badge {css_class}">{label}</span>'

def display_sources(sources: list, agent_type: str):
    """Display sources in a formatted way"""
    if not sources:
        return
    
    with st.expander(f"📎 Sources ({len(sources)})", expanded=False):
        for i, source in enumerate(sources, 1):
            if agent_type == "web_research":
                st.markdown(f"{i}. [{source.get('title', 'Untitled')}]({source.get('url', '#')})")
            elif agent_type == "rag":
                doc_name = source.get('document', 'Unknown')
                score = source.get('relevance_score', 0)
                st.markdown(f"{i}. {doc_name} (relevance: {score:.2f})")

def main():
    """Main application"""
    initialize_session_state()
    
    # Header
    st.markdown('<div class="main-header">🤖 TechNova AI Research Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Multi-Agent Research & Summarization System powered by LangGraph</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # API Key Status
        st.subheader("🔑 API Keys Status")
        api_status = check_api_keys()
        
        col1, col2 = st.columns(2)
        with col1:
            if api_status["groq"]:
                st.success("✅ Groq")
            else:
                st.error("❌ Groq")
        
        with col2:
            if api_status["tavily"]:
                st.success("✅ Tavily")
            else:
                st.error("❌ Tavily")
        
        if not all(api_status.values()):
            st.warning("⚠️ Some API keys are missing. Please set them in your .env file.")
            st.info("Required: GROQ_API_KEY, TAVILY_API_KEY")
        
        st.divider()
        
        # Initialize workflow
        if st.button("🚀 Initialize System", type="primary", use_container_width=True):
            if all(api_status.values()):
                with st.spinner("Initializing multi-agent system..."):
                    try:
                        data_path = os.path.join(os.path.dirname(__file__), "src", "data", "financial_reports")
                        st.session_state.workflow = create_workflow(data_path=data_path)
                        st.session_state.initialized = True
                        st.success("✅ System initialized successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Initialization failed: {str(e)}")
            else:
                st.error("Please set all required API keys first!")
        
        if st.session_state.initialized:
            st.success("✅ System Ready")
        else:
            st.info("👆 Click to initialize the system")
        
        st.divider()
        
        # Memory controls
        st.subheader("💾 Conversation Memory")
        
        if st.session_state.workflow:
            stats = st.session_state.workflow.get_memory_stats()
            st.metric("Total Messages", stats.get("total_messages", 0))
            
            if stats.get("routes_used"):
                st.write("**Routes Used:**")
                for route, count in stats["routes_used"].items():
                    st.write(f"• {route}: {count}")
        
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.chat_history = []
            if st.session_state.workflow:
                st.session_state.workflow.reset_memory()
            st.success("History cleared!")
            st.rerun()
        
        st.divider()
        
        # Example queries
        st.subheader("💡 Example Queries")
        
        examples = {
            "💡 General Knowledge": [
                "What is artificial intelligence?",
                "Explain machine learning"
            ],
            "🌐 Web Research": [
                "What's the latest news on AI?",
                "Current developments in quantum computing"
            ],
            "📚 Company Info": [
                "What was TechNova's Q1 2024 revenue?",
                "What products does TechNova offer?",
                "Summarize TechNova's risk factors"
            ]
        }
        
        for category, queries in examples.items():
            with st.expander(category):
                for query in queries:
                    if st.button(query, key=f"ex_{query}", use_container_width=True):
                        st.session_state.example_query = query
                        st.rerun()
        
        st.divider()
        
        # Graph visualization
        if st.session_state.workflow:
            with st.expander("🔍 System Architecture"):
                st.code(st.session_state.workflow.get_graph_visualization())
        
        # About
        with st.expander("ℹ️ About"):
            st.markdown("""
            **Multi-Agent System Components:**
            - 🧭 Router Agent: Routes queries intelligently
            - 💡 LLM Agent: General knowledge
            - 🌐 Web Agent: Current information
            - 📚 RAG Agent: Company knowledge base
            - 📝 Summarization Agent: Final synthesis
            
            **Powered by:**
            - Groq (Llama 4 Scout)
            - LangGraph
            - ChromaDB
            - Tavily Search
            """)
    
    # Main chat interface
    if not st.session_state.initialized:
        st.info("👈 Please initialize the system using the sidebar to get started!")
        
        # Show system overview
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### 💡 LLM Agent
            Handles general knowledge questions using the language model's training.
            
            **Examples:**
            - "What is blockchain?"
            - "Explain neural networks"
            """)
        
        with col2:
            st.markdown("""
            ### 🌐 Web Research Agent
            Fetches current information from the web using Tavily Search.
            
            **Examples:**
            - "Latest AI developments"
            - "Current Bitcoin price"
            """)
        
        with col3:
            st.markdown("""
            ### 📚 RAG Agent
            Retrieves information from TechNova's financial documents.
            
            **Examples:**
            - "Q1 2024 revenue?"
            - "TechNova's products?"
            """)
        
        return
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            if message["role"] == "user":
                st.markdown(message["content"])
            else:
                # Display agent badge
                st.markdown(display_agent_badge(message.get("agent", "llm")), unsafe_allow_html=True)
                st.markdown(message["content"])
                
                # Display sources if available
                if message.get("sources"):
                    display_sources(message["sources"], message.get("agent", "llm"))
                
                # Display metadata in expander
                if message.get("show_details"):
                    with st.expander("🔍 Details"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Route", message.get("route", "N/A"))
                        with col2:
                            st.metric("Confidence", f"{message.get('confidence', 0):.0%}")
                        with col3:
                            st.metric("Sources", len(message.get("sources", [])))
                        
                        if message.get("reasoning"):
                            st.write(f"**Reasoning:** {message['reasoning']}")
    
    # Handle example query
    if hasattr(st.session_state, 'example_query'):
        query = st.session_state.example_query
        del st.session_state.example_query
    else:
        # Chat input
        query = st.chat_input("Ask me anything about TechNova or general topics...")
    
    if query:
        # Add user message to chat
        st.session_state.chat_history.append({
            "role": "user",
            "content": query
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(query)
        
        # Process query
        with st.chat_message("assistant"):
            with st.spinner("Processing your query..."):
                try:
                    result = st.session_state.workflow.process_query(query)
                    
                    # Display agent badge
                    st.markdown(display_agent_badge(result["agent_used"]), unsafe_allow_html=True)
                    
                    # Display response
                    st.markdown(result["response"])
                    
                    # Display sources
                    display_sources(result.get("sources", []), result["agent_used"])
                    
                    # Display details
                    with st.expander("🔍 Details"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Route", result["route"])
                        with col2:
                            st.metric("Confidence", f"{result['route_confidence']:.0%}")
                        with col3:
                            st.metric("Sources", len(result.get("sources", [])))
                        
                        st.write(f"**Reasoning:** {result.get('route_reasoning', 'N/A')}")
                        
                        if result.get("execution_path"):
                            st.write("**Execution Path:**")
                            for step in result["execution_path"]:
                                st.write(f"• {step}")
                    
                    # Add to chat history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": result["response"],
                        "agent": result["agent_used"],
                        "route": result["route"],
                        "confidence": result["route_confidence"],
                        "reasoning": result.get("route_reasoning", ""),
                        "sources": result.get("sources", []),
                        "show_details": True
                    })
                    
                except Exception as e:
                    st.error(f"❌ Error processing query: {str(e)}")
                    st.exception(e)

if __name__ == "__main__":
    main()