# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Setup (2 minutes)

```bash
# Clone and navigate
cd langgraph_multi_agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys (1 minute)

Create `.env` file:
```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

**Get API Keys:**
- Groq: https://console.groq.com/
- Tavily: https://tavily.com/

### 3. Run (1 minute)

```bash
streamlit run app.py
```

Open browser to `http://localhost:8501`

### 4. Use (1 minute)

1. Click "🚀 Initialize System" in sidebar
2. Try example queries:
   - "What is machine learning?" (LLM)
   - "Latest AI news?" (Web)
   - "TechNova Q1 revenue?" (RAG)

## 🎯 Test Without UI

```bash
# Test complete workflow
python src/graph/workflow.py

# Test individual components
python src/agents/router_agent.py
python src/agents/llm_agent.py
python src/agents/web_research_agent.py
python src/agents/rag_agent.py
```

## ❓ Troubleshooting

### Issue: API Key Error
**Solution**: Verify `.env` file has correct keys

### Issue: Import Errors
**Solution**: 
```bash
pip install -r requirements.txt --upgrade
```

### Issue: Vector Store Not Found
**Solution**: 
```bash
python src/utils/vector_store.py
```

### Issue: Streamlit Port in Use
**Solution**: 
```bash
streamlit run app.py --server.port 8502
```

## 📚 Next Steps

- Read full [README.md](README.md)
- Try different query types
- Explore agent routing decisions
- Check conversation memory
- View system architecture

## 🎓 Learning Path

1. **Understand Routing**: Try various queries, observe routing
2. **Explore Sources**: Check which documents/web pages are used
3. **Test Memory**: Ask follow-up questions
4. **Review Code**: Start with `workflow.py`, then individual agents
5. **Modify System**: Add new documents or change routing logic

## 💡 Pro Tips

- Use example queries in sidebar for quick tests
- Check "Details" expander to see routing decisions
- Clear history when testing different query types
- Monitor confidence scores for routing accuracy

---

**Ready to start? Run `streamlit run app.py` and explore!** 🚀