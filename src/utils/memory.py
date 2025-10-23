"""
Conversational Memory Management
"""
from typing import List, Dict, Any, Optional
from datetime import datetime

class ConversationMemoryManager:
    """Manages conversation history with context preservation"""
    
    def __init__(self, max_history: int = 10):
        """
        Initialize memory manager
        
        Args:
            max_history: Maximum number of conversation turns to keep
        """
        self.max_history = max_history
        self.conversation_history: List[Dict[str, Any]] = []
    
    def add_user_message(self, message: str, metadata: Optional[Dict] = None):
        """
        Add user message to history
        
        Args:
            message: User message text
            metadata: Optional metadata
        """
        entry = {
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.conversation_history.append(entry)
        self._trim_history()
    
    def add_assistant_message(
        self,
        message: str,
        route: Optional[str] = None,
        sources: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ):
        """
        Add assistant message to history
        
        Args:
            message: Assistant message text
            route: Which agent handled the query (llm/web/rag)
            sources: List of sources used
            metadata: Optional metadata
        """
        entry = {
            "role": "assistant",
            "content": message,
            "route": route,
            "sources": sources or [],
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.conversation_history.append(entry)
        self._trim_history()
    
    def get_conversation_history(self, last_n: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get conversation history
        
        Args:
            last_n: Get last N messages (None for all)
        
        Returns:
            List of conversation entries
        """
        if last_n is None:
            return self.conversation_history
        return self.conversation_history[-last_n:]
    
    def get_formatted_history(self, last_n: Optional[int] = None) -> str:
        """
        Get formatted conversation history for context
        
        Args:
            last_n: Get last N messages
        
        Returns:
            Formatted string of conversation history
        """
        history = self.get_conversation_history(last_n)
        
        formatted = []
        for entry in history:
            role = entry["role"].capitalize()
            content = entry["content"]
            formatted.append(f"{role}: {content}")
        
        return "\n".join(formatted)
    
    def get_context_for_query(self, current_query: str, context_window: int = 3) -> str:
        """
        Get relevant context for current query
        
        Args:
            current_query: Current user query
            context_window: Number of previous turns to include
        
        Returns:
            Context string
        """
        recent_history = self.get_conversation_history(last_n=context_window * 2)
        
        if not recent_history:
            return current_query
        
        context_parts = ["Previous conversation:"]
        for entry in recent_history:
            role = entry["role"].capitalize()
            content = entry["content"][:200]  # Truncate long messages
            context_parts.append(f"{role}: {content}")
        
        context_parts.append(f"\nCurrent query: {current_query}")
        
        return "\n".join(context_parts)
    
    def clear_history(self):
        """Clear all conversation history"""
        self.conversation_history = []
    
    def _trim_history(self):
        """Trim history to max_history length"""
        if len(self.conversation_history) > self.max_history * 2:  # *2 for user+assistant pairs
            self.conversation_history = self.conversation_history[-(self.max_history * 2):]
    
    def export_history(self) -> List[Dict[str, Any]]:
        """Export conversation history"""
        return self.conversation_history.copy()
    
    def import_history(self, history: List[Dict[str, Any]]):
        """Import conversation history"""
        self.conversation_history = history
        self._trim_history()
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics of conversation"""
        total_messages = len(self.conversation_history)
        user_messages = sum(1 for entry in self.conversation_history if entry["role"] == "user")
        assistant_messages = sum(1 for entry in self.conversation_history if entry["role"] == "assistant")
        
        routes_used = {}
        for entry in self.conversation_history:
            if entry["role"] == "assistant" and entry.get("route"):
                route = entry["route"]
                routes_used[route] = routes_used.get(route, 0) + 1
        
        return {
            "total_messages": total_messages,
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "routes_used": routes_used
        }

# Global memory instance for the application
_global_memory: Optional[ConversationMemoryManager] = None

def get_memory() -> ConversationMemoryManager:
    """Get global memory instance"""
    global _global_memory
    if _global_memory is None:
        _global_memory = ConversationMemoryManager()
    return _global_memory

def reset_memory():
    """Reset global memory"""
    global _global_memory
    _global_memory = ConversationMemoryManager()

if __name__ == "__main__":
    # Test memory management
    memory = ConversationMemoryManager(max_history=5)
    
    # Simulate conversation
    memory.add_user_message("What was TechNova's revenue in Q1?")
    memory.add_assistant_message(
        "TechNova's revenue in Q1 2024 was $2.8 billion.",
        route="rag",
        sources=["Q1_2024_Earnings_Report.txt"]
    )
    
    memory.add_user_message("What about Q2?")
    memory.add_assistant_message(
        "In Q2 2024, TechNova's revenue increased to $3.2 billion.",
        route="rag",
        sources=["Q2_2024_Earnings_Report.txt"]
    )
    
    # Get formatted history
    print("Conversation History:")
    print(memory.get_formatted_history())
    print()
    
    # Get context for new query
    context = memory.get_context_for_query("Tell me about the growth rate")
    print("Context for new query:")
    print(context)
    print()
    
    # Get stats
    stats = memory.get_summary_stats()
    print("Summary Stats:")
    print(stats)
    
    print("\n✅ Memory management test successful!")