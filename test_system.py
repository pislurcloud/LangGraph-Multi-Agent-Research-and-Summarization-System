"""
Comprehensive Test Script for Multi-Agent System
Tests all agents and workflows
"""
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_environment():
    """Test environment setup"""
    print("=" * 60)
    print("1. TESTING ENVIRONMENT SETUP")
    print("=" * 60)
    
    from dotenv import load_dotenv
    load_dotenv()
    
    groq_key = os.getenv("GROQ_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    
    print(f"✓ GROQ_API_KEY: {'Set' if groq_key else 'NOT SET'}")
    print(f"✓ TAVILY_API_KEY: {'Set' if tavily_key else 'NOT SET'}")
    
    if not groq_key or not tavily_key:
        print("\n⚠️  Warning: Some API keys are missing!")
        print("Please set them in .env file")
        return False
    
    print("\n✅ Environment setup complete!\n")
    return True

def test_llm_config():
    """Test LLM configuration"""
    print("=" * 60)
    print("2. TESTING LLM CONFIGURATION")
    print("=" * 60)
    
    from src.utils.llm_config import get_llm
    
    try:
        llm = get_llm()
        response = llm.invoke("Say 'Hello World'")
        print(f"✓ LLM Response: {response.content[:50]}...")
        print("\n✅ LLM configuration working!\n")
        return True
    except Exception as e:
        print(f"❌ LLM Error: {e}\n")
        return False

def test_vector_store():
    """Test vector store setup"""
    print("=" * 60)
    print("3. TESTING VECTOR STORE")
    print("=" * 60)
    
    from src.utils.vector_store import initialize_vectorstore
    
    try:
        data_path = os.path.join(os.path.dirname(__file__), "src", "data", "financial_reports")
        manager = initialize_vectorstore(data_path, force_recreate=False)
        
        # Test search
        results = manager.similarity_search("TechNova revenue", k=2)
        print(f"✓ Vector store initialized")
        print(f"✓ Test search returned {len(results)} results")
        print(f"✓ Sample result: {results[0].page_content[:100]}...")
        print("\n✅ Vector store working!\n")
        return True
    except Exception as e:
        print(f"❌ Vector Store Error: {e}\n")
        return False

def test_router_agent():
    """Test router agent"""
    print("=" * 60)
    print("4. TESTING ROUTER AGENT")
    print("=" * 60)
    
    from src.agents.router_agent import RouterAgent
    from src.utils.llm_config import get_router_llm
    
    try:
        llm = get_router_llm()
        router = RouterAgent(llm)
        
        test_queries = [
            ("What is AI?", "llm"),
            ("Latest AI news", "web_research"),
            ("TechNova revenue", "rag")
        ]
        
        passed = 0
        for query, expected_route in test_queries:
            result = router.route_query(query)
            actual_route = result["route"]
            status = "✓" if actual_route == expected_route else "✗"
            print(f"{status} Query: '{query}'")
            print(f"  Expected: {expected_route}, Got: {actual_route}")
            print(f"  Confidence: {result['confidence']:.2f}")
            if actual_route == expected_route:
                passed += 1
        
        print(f"\nPassed: {passed}/{len(test_queries)}")
        print("✅ Router agent working!\n" if passed >= 2 else "⚠️  Router needs tuning\n")
        return passed >= 2
    except Exception as e:
        print(f"❌ Router Error: {e}\n")
        return False

def test_llm_agent():
    """Test LLM agent"""
    print("=" * 60)
    print("5. TESTING LLM AGENT")
    print("=" * 60)
    
    from src.agents.llm_agent import LLMAgent
    from src.utils.llm_config import get_general_llm
    
    try:
        llm = get_general_llm()
        agent = LLMAgent(llm)
        
        result = agent.process_query("What is machine learning in one sentence?")
        print(f"✓ Query processed")
        print(f"✓ Response: {result['response'][:150]}...")
        print(f"✓ Agent: {result['agent']}")
        print("\n✅ LLM agent working!\n")
        return True
    except Exception as e:
        print(f"❌ LLM Agent Error: {e}\n")
        return False

def test_web_research_agent():
    """Test web research agent"""
    print("=" * 60)
    print("6. TESTING WEB RESEARCH AGENT")
    print("=" * 60)
    
    from src.agents.web_research_agent import WebResearchAgent
    from src.utils.llm_config import get_general_llm
    
    try:
        llm = get_general_llm()
        agent = WebResearchAgent(llm)
        
        result = agent.process_query("Latest developments in AI 2025")
        print(f"✓ Query processed")
        print(f"✓ Response: {result['response'][:150]}...")
        print(f"✓ Sources found: {len(result.get('sources', []))}")
        print(f"✓ Agent: {result['agent']}")
        print("\n✅ Web research agent working!\n")
        return True
    except Exception as e:
        print(f"❌ Web Research Error: {e}\n")
        return False

def test_rag_agent():
    """Test RAG agent"""
    print("=" * 60)
    print("7. TESTING RAG AGENT")
    print("=" * 60)
    
    from src.agents.rag_agent import RAGAgent
    from src.utils.llm_config import get_general_llm
    from src.utils.vector_store import initialize_vectorstore
    
    try:
        llm = get_general_llm()
        data_path = os.path.join(os.path.dirname(__file__), "src", "data", "financial_reports")
        vector_store_manager = initialize_vectorstore(data_path)
        agent = RAGAgent(llm, vector_store_manager)
        
        result = agent.process_query("What was TechNova's Q1 2024 revenue?")
        print(f"✓ Query processed")
        print(f"✓ Response: {result['response'][:150]}...")
        print(f"✓ Sources found: {len(result.get('sources', []))}")
        print(f"✓ Agent: {result['agent']}")
        print("\n✅ RAG agent working!\n")
        return True
    except Exception as e:
        print(f"❌ RAG Agent Error: {e}\n")
        return False

def test_workflow():
    """Test complete workflow"""
    print("=" * 60)
    print("8. TESTING COMPLETE WORKFLOW")
    print("=" * 60)
    
    from src.graph.workflow import create_workflow
    
    try:
        data_path = os.path.join(os.path.dirname(__file__), "src", "data", "financial_reports")
        workflow = create_workflow(data_path=data_path)
        
        test_queries = [
            "What is artificial intelligence?",
            "TechNova Q1 2024 revenue?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\nTest {i}: {query}")
            result = workflow.process_query(query, use_memory=True)
            print(f"✓ Route: {result['route']}")
            print(f"✓ Agent: {result['agent_used']}")
            print(f"✓ Confidence: {result['route_confidence']:.2f}")
            print(f"✓ Response: {result['response'][:100]}...")
        
        # Test memory
        stats = workflow.get_memory_stats()
        print(f"\n✓ Memory: {stats['total_messages']} messages stored")
        
        print("\n✅ Complete workflow working!\n")
        return True
    except Exception as e:
        print(f"❌ Workflow Error: {e}\n")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("LANGGRAPH MULTI-AGENT SYSTEM - COMPREHENSIVE TEST")
    print("=" * 60 + "\n")
    
    results = []
    
    # Run tests
    results.append(("Environment", test_environment()))
    results.append(("LLM Config", test_llm_config()))
    results.append(("Vector Store", test_vector_store()))
    results.append(("Router Agent", test_router_agent()))
    results.append(("LLM Agent", test_llm_agent()))
    results.append(("Web Research", test_web_research_agent()))
    results.append(("RAG Agent", test_rag_agent()))
    results.append(("Complete Workflow", test_workflow()))
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! System is ready to use.")
        print("\nNext steps:")
        print("1. Run 'streamlit run app.py' to start the UI")
        print("2. Try different types of queries")
        print("3. Explore the conversation memory")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("Common issues:")
        print("- Missing API keys in .env file")
        print("- Network connectivity for web search")
        print("- Vector store not initialized")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)