"""
LangGraph Workflow - Multi-Agent Orchestration
"""
import os
from typing import TypedDict, List, Dict, Any, Annotated
from langgraph.graph import StateGraph, END
import operator

# Import agents
from src.agents.router_agent import RouterAgent
from src.agents.llm_agent import LLMAgent
from src.agents.web_research_agent import WebResearchAgent
from src.agents.rag_agent import RAGAgent
from src.agents.summarization_agent import SummarizationAgent

# Import utilities
from src.utils.llm_config import get_router_llm, get_general_llm, get_summarization_llm
from src.utils.vector_store import initialize_vectorstore
from src.utils.memory import get_memory

class AgentState(TypedDict):
    """State definition for the agent workflow"""
    query: str
    conversation_context: str
    route: str
    route_reasoning: str
    route_confidence: float
    llm_response: str
    web_results: List[Dict]
    rag_context: List[Dict]
    agent_response: str
    agent_type: str
    sources: List[Dict]
    final_summary: str
    metadata: Dict[str, Any]
    messages: Annotated[List[str], operator.add]

class MultiAgentWorkflow:
    """LangGraph workflow for multi-agent system"""
    
    def __init__(self, data_path: str, persist_dir: str = "./chroma_db"):
        """
        Initialize the multi-agent workflow
        
        Args:
            data_path: Path to data directory for RAG
            persist_dir: Directory for vector store persistence
        """
        # Initialize LLMs
        self.router_llm = get_router_llm()
        self.general_llm = get_general_llm()
        self.summary_llm = get_summarization_llm()
        
        # Initialize vector store
        self.vector_store_manager = initialize_vectorstore(data_path, persist_dir)
        
        # Initialize agents
        self.router_agent = RouterAgent(self.router_llm)
        self.llm_agent = LLMAgent(self.general_llm)
        self.web_agent = WebResearchAgent(self.general_llm)
        self.rag_agent = RAGAgent(self.general_llm, self.vector_store_manager)
        self.summary_agent = SummarizationAgent(self.summary_llm)
        
        # Initialize memory
        self.memory = get_memory()
        
        # Build graph
        self.graph = self._build_graph()
        self.app = self.graph.compile()
    
    def _build_graph(self) -> StateGraph:
        """Build the state graph"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("router", self.route_query)
        workflow.add_node("llm", self.process_with_llm)
        workflow.add_node("web_research", self.process_with_web)
        workflow.add_node("rag", self.process_with_rag)
        workflow.add_node("summarize", self.summarize_response)
        
        # Set entry point
        workflow.set_entry_point("router")
        
        # Add conditional edges from router
        workflow.add_conditional_edges(
            "router",
            self.decide_route,
            {
                "llm": "llm",
                "web_research": "web_research",
                "rag": "rag"
            }
        )
        
        # All agents flow to summarization
        workflow.add_edge("llm", "summarize")
        workflow.add_edge("web_research", "summarize")
        workflow.add_edge("rag", "summarize")
        
        # Summarization flows to END
        workflow.add_edge("summarize", END)
        
        return workflow
    
    def route_query(self, state: AgentState) -> AgentState:
        """Router node - determines which agent to use"""
        query = state["query"]
        context = state.get("conversation_context", "")
        
        # Get routing decision
        routing = self.router_agent.route_query(query, context)
        
        state["route"] = routing["route"]
        state["route_reasoning"] = routing["reasoning"]
        state["route_confidence"] = routing["confidence"]
        state["messages"] = [f"Router: Query routed to {routing['route']} agent"]
        
        return state
    
    def decide_route(self, state: AgentState) -> str:
        """Conditional edge function"""
        return state["route"]
    
    def process_with_llm(self, state: AgentState) -> AgentState:
        """LLM node - process with general LLM"""
        query = state["query"]
        context = state.get("conversation_context", "")
        
        result = self.llm_agent.process_query(query, context)
        
        state["agent_response"] = result["response"]
        state["agent_type"] = "llm"
        state["sources"] = []
        state["metadata"] = result.get("metadata", {})
        state["messages"] = [f"LLM: Generated response"]
        
        return state
    
    def process_with_web(self, state: AgentState) -> AgentState:
        """Web research node"""
        query = state["query"]
        context = state.get("conversation_context", "")
        
        result = self.web_agent.process_query(query, context)
        
        state["agent_response"] = result["response"]
        state["agent_type"] = "web_research"
        state["sources"] = result.get("sources", [])
        state["web_results"] = result.get("search_results", [])
        state["metadata"] = result.get("metadata", {})
        state["messages"] = [f"Web Research: Found {len(result.get('sources', []))} sources"]
        
        return state
    
    def process_with_rag(self, state: AgentState) -> AgentState:
        """RAG node"""
        query = state["query"]
        context = state.get("conversation_context", "")
        
        result = self.rag_agent.process_query(query, context, k=3)
        
        state["agent_response"] = result["response"]
        state["agent_type"] = "rag"
        state["sources"] = result.get("sources", [])
        state["rag_context"] = result.get("retrieved_docs", [])
        state["metadata"] = result.get("metadata", {})
        state["messages"] = [f"RAG: Retrieved {len(result.get('sources', []))} documents"]
        
        return state
    
    def summarize_response(self, state: AgentState) -> AgentState:
        """Summarization node"""
        query = state["query"]
        agent_response = state["agent_response"]
        agent_type = state["agent_type"]
        sources = state.get("sources", [])
        context = state.get("conversation_context", "")
        metadata = state.get("metadata", {})
        
        result = self.summary_agent.summarize(
            query=query,
            agent_response=agent_response,
            agent_type=agent_type,
            sources=sources,
            conversation_context=context,
            metadata=metadata
        )
        
        state["final_summary"] = result["final_response"]
        state["messages"] = [f"Summarization: Final response generated"]
        
        return state
    
    def process_query(self, query: str, use_memory: bool = True) -> Dict[str, Any]:
        """
        Process a user query through the workflow
        
        Args:
            query: User query
            use_memory: Whether to use conversation memory
        
        Returns:
            Dictionary with final response and metadata
        """
        # Get conversation context
        context = ""
        if use_memory:
            context = self.memory.get_formatted_history(last_n=3)
        
        # Create initial state
        initial_state = {
            "query": query,
            "conversation_context": context,
            "route": "",
            "route_reasoning": "",
            "route_confidence": 0.0,
            "llm_response": "",
            "web_results": [],
            "rag_context": [],
            "agent_response": "",
            "agent_type": "",
            "sources": [],
            "final_summary": "",
            "metadata": {},
            "messages": []
        }
        
        # Run the workflow
        final_state = self.app.invoke(initial_state)
        
        # Update memory
        if use_memory:
            self.memory.add_user_message(query)
            self.memory.add_assistant_message(
                message=final_state["final_summary"],
                route=final_state["agent_type"],
                sources=[s.get("title") or s.get("document") for s in final_state.get("sources", [])]
            )
        
        return {
            "response": final_state["final_summary"],
            "agent_used": final_state["agent_type"],
            "route": final_state["route"],
            "route_reasoning": final_state["route_reasoning"],
            "route_confidence": final_state["route_confidence"],
            "sources": final_state.get("sources", []),
            "metadata": final_state.get("metadata", {}),
            "execution_path": final_state.get("messages", [])
        }
    
    def get_graph_visualization(self) -> str:
        """Get a text representation of the graph"""
        return """
Multi-Agent Workflow Graph:

    ┌─────────┐
    │  START  │
    └────┬────┘
         │
         ▼
    ┌─────────┐
    │ ROUTER  │
    └────┬────┘
         │
    ┌────┴────┬────────────┬────────┐
    │         │            │        │
    ▼         ▼            ▼        │
┌─────┐  ┌──────┐     ┌──────┐    │
│ LLM │  │ WEB  │     │ RAG  │    │
└──┬──┘  └───┬──┘     └───┬──┘    │
   │         │            │        │
   └────┬────┴────────────┘        │
        │                          │
        ▼                          │
  ┌──────────────┐                │
  │ SUMMARIZATION│                │
  └──────┬───────┘                │
         │                          │
         ▼                          │
    ┌────────┐                     │
    │  END   │◄────────────────────┘
    └────────┘

Routing Logic:
- LLM: General knowledge questions
- WEB: Current/recent information (keywords: latest, current, 2025)
- RAG: TechNova company information (keywords: TechNova, our, revenue)
"""
    
    def reset_memory(self):
        """Reset conversation memory"""
        self.memory.clear_history()
    
    def get_memory_stats(self) -> Dict:
        """Get memory statistics"""
        return self.memory.get_summary_stats()

def create_workflow(data_path: str = None, persist_dir: str = "./chroma_db") -> MultiAgentWorkflow:
    """
    Factory function to create a workflow instance
    
    Args:
        data_path: Path to data directory
        persist_dir: Vector store persistence directory
    
    Returns:
        MultiAgentWorkflow instance
    """
    if data_path is None:
        # Default to project data path
        data_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "data",
            "financial_reports"
        )
    
    return MultiAgentWorkflow(data_path, persist_dir)

if __name__ == "__main__":
    # Test the workflow
    import sys
    
    try:
        print("🔧 Initializing Multi-Agent Workflow...\n")
        
        # Create workflow
        workflow = create_workflow()
        
        # Print graph visualization
        print(workflow.get_graph_visualization())
        
        # Test queries
        test_queries = [
            "What is machine learning?",
            "What's the latest news on AI?",
            "What was TechNova's revenue in Q1 2024?"
        ]
        
        print("\n🧪 Testing Workflow\n")
        
        for query in test_queries:
            print(f"Query: {query}")
            result = workflow.process_query(query)
            print(f"Route: {result['route']} ({result['agent_used']})")
            print(f"Response: {result['response'][:200]}...")
            print(f"Sources: {len(result['sources'])}")
            print()
        
        # Memory stats
        stats = workflow.get_memory_stats()
        print(f"Memory Stats: {stats}")
        
        print("\n✅ Workflow test successful!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)