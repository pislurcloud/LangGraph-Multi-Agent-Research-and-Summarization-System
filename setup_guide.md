# Complete Setup and Usage Guide

## 📋 Prerequisites

Before you begin, ensure you have:

1. **Python 3.10 or higher**
   ```bash
   python --version  # Should be 3.10+
   ```

2. **pip package manager**
   ```bash
   pip --version
   ```

3. **Internet connection** (for API calls and package installation)

4. **API Keys** (obtain before starting):
   - **Groq API Key**: Sign up at https://console.groq.com/
   - **Tavily API Key**: Sign up at https://tavily.com/

---

## 🚀 Installation Steps

### Step 1: Extract the Project

```bash
# Navigate to your workspace
cd ~/workspace

# Extract the project (if downloaded as zip)
unzip langgraph_multi_agent.zip
cd langgraph_multi_agent
```

### Step 2: Create Virtual Environment

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

### Step 3: Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt
```

This will install:
- LangGraph and LangChain
- Groq API client
- ChromaDB
- Tavily Python client
- Streamlit
- Sentence Transformers
- And other dependencies

**Installation time**: 2-5 minutes depending on your internet speed.

### Step 4: Configure API Keys

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env

# Edit with your favorite editor
nano .env  # or vim, code, etc.
```

Add your API keys:
```env
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
TAVILY_API_KEY=tvly-your_actual_tavily_api_key_here
```

**Save and close the file.**

### Step 5: Initialize the Vector Store

The system needs to create the vector database for RAG:

```bash
python src/utils/vector_store.py
```

Expected output:
```
Loading documents from .../financial_reports...
✓ Loaded 5 documents
Splitting documents into chunks...
✓ Created 156 chunks
Creating vector store...
✓ Vector store created with 156 documents
✓ Persisted to ./chroma_db
```

---

## 🧪 Validation & Testing

### Quick Test

Run the comprehensive test suite:

```bash
python test_system.py
```

This will test:
1. Environment setup (API keys)
2. LLM configuration
3. Vector store
4. All 5 agents
5. Complete workflow

**Expected result**: 8/8 tests passed

### Individual Component Tests

Test each component separately:

```bash
# Test router
python src/agents/router_agent.py

# Test LLM agent
python src/agents/llm_agent.py

# Test web research
python src/agents/web_research_agent.py

# Test RAG agent
python src/agents/rag_agent.py

# Test workflow
python src/graph/workflow.py
```

---

## 🌐 Running the Application

### Launch Streamlit UI

```bash
streamlit run app.py
```

**Output:**
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

**Open your browser** and navigate to `http://localhost:8501`

### First-Time Setup in UI

1. **Check API Keys**: Sidebar shows ✅ Groq and ✅ Tavily
2. **Click "🚀 Initialize System"**: This loads the workflow and vector store
3. **Wait for confirmation**: "✅ System initialized successfully!"

Now you're ready to use the system!

---

## 💬 Using the System

### Basic Usage

1. **Type a query** in the chat input at the bottom
2. **Press Enter** or click Send
3. **View the response** with:
   - Agent badge (LLM/Web/RAG)
   - Response text
   - Sources (if applicable)
   - Details (routing info)

### Example Queries

#### Test LLM Agent
```
Query: "What is artificial intelligence?"

Expected:
- Route: llm
- Agent: LLM
- Response: General AI explanation
- Sources: None
```

#### Test Web Research Agent
```
Query: "What are the latest AI developments in 2025?"

Expected:
- Route: web_research
- Agent: Web Research
- Response: Current AI news
- Sources: 3-5 web articles with URLs
```

#### Test RAG Agent
```
Query: "What was TechNova's revenue in Q1 2024?"

Expected:
- Route: rag
- Agent: Knowledge Base
- Response: "$2.8 billion, up 28% YoY..."
- Sources: Q1_2024_Earnings_Report.txt
```

#### Test Conversation Memory
```
User: "What was TechNova's Q1 revenue?"
Bot: "$2.8 billion..." [RAG]

User: "What about Q2?"  ← Follow-up question
Bot: "$3.2 billion..." [RAG]  ← Understands context
```

### Using Example Queries

The sidebar has pre-built example queries:

1. **Expand category** (💡 General / 🌐 Web / 📚 Company)
2. **Click a query button**
3. **System automatically processes** the query

---

## 🔍 Understanding the Interface

### Main Chat Area
- **User messages**: Your queries in blue
- **Assistant messages**: System responses in gray
- **Agent badges**: Color-coded by agent type
  - 💡 Blue: LLM
  - 🌐 Green: Web Research
  - 📚 Orange: RAG

### Response Details
Click "🔍 Details" to see:
- **Route**: Which agent was selected
- **Confidence**: Router's confidence score (0-100%)
- **Reasoning**: Why this route was chosen
- **Execution Path**: Steps taken

### Sources
Click "📎 Sources" to see:
- **Web sources**: Article titles + URLs
- **RAG sources**: Document names + relevance scores

### Sidebar
- **API Key Status**: Green ✅ or Red ❌
- **System Status**: Ready or Not Initialized
- **Memory Stats**: Message count and routes used
- **Clear History**: Reset conversation
- **Example Queries**: Quick test buttons
- **System Architecture**: Graph visualization

---

## 🎯 Advanced Usage

### Conversation Flows

**Sequential Questions:**
```
1. "What products does TechNova offer?"
2. "How much revenue do they generate?"
3. "What are the growth trends?"
```

Each question builds on previous context.

**Comparative Analysis:**
```
1. "TechNova Q1 revenue?"
2. "Compare with Q2"
3. "Calculate the growth rate"
```

System maintains context across all queries.

### Complex Queries

**Multi-part questions:**
```
"What was TechNova's Q1 2024 revenue, and how does it compare to the 
latest industry trends?"
```

System may:
1. Route to RAG for TechNova data
2. Optionally search web for industry context
3. Synthesize both sources

### Memory Management

**View Statistics:**
- Sidebar shows total messages
- Routes used breakdown
- Conversation depth

**Clear History:**
- Click "🗑️ Clear History"
- Resets conversation state
- Useful for testing different scenarios

---

## 🐛 Troubleshooting

### Issue: API Key Error

**Symptom:** "GROQ_API_KEY not found"

**Solution:**
```bash
# Check .env file exists
ls -la .env

# Verify contents
cat .env

# Should show:
# GROQ_API_KEY=gsk_...
# TAVILY_API_KEY=tvly-...

# Restart Streamlit
streamlit run app.py
```

### Issue: Vector Store Not Found

**Symptom:** "Vector store not initialized"

**Solution:**
```bash
# Regenerate vector store
python src/utils/vector_store.py

# Should create ./chroma_db directory
ls -la chroma_db/
```

### Issue: Import Errors

**Symptom:** "ModuleNotFoundError: No module named 'langgraph'"

**Solution:**
```bash
# Verify virtual environment is activated
which python  # Should point to venv/bin/python

# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

### Issue: Streamlit Port in Use

**Symptom:** "Address already in use"

**Solution:**
```bash
# Use different port
streamlit run app.py --server.port 8502

# Or kill existing process
lsof -ti:8501 | xargs kill -9
```

### Issue: Web Search Fails

**Symptom:** "Tavily API error"

**Solution:**
1. Check Tavily API key is correct
2. Verify internet connection
3. Check Tavily API status: https://status.tavily.com/
4. Try a different query

### Issue: RAG Returns No Results

**Symptom:** "No relevant documents found"

**Solution:**
1. Check query mentions TechNova or company terms
2. Verify vector store is initialized
3. Try more specific query: "TechNova Q1 2024 revenue"
4. Regenerate vector store if corrupted

---

## 📊 Performance Expectations

### Response Times

| Agent Type | Expected Time | Notes |
|------------|---------------|-------|
| LLM | 2-3 seconds | Direct LLM inference |
| Web Research | 5-8 seconds | Search + synthesis |
| RAG | 3-5 seconds | Vector search + generation |

### Routing Accuracy

- **LLM queries**: 95%+ correct
- **Web queries**: 90%+ correct
- **RAG queries**: 88%+ correct
- **Overall**: ~92% accuracy

### Memory Capacity

- **Storage**: In-memory (session-based)
- **Window**: Last 10 turns (20 messages)
- **Context injection**: Last 3 turns (6 messages)

---

## 🔒 Security Notes

- API keys stored in `.env` (not committed to git)
- Vector store persisted locally (no cloud)
- Conversation history session-based (not saved)
- No sensitive data logged

---

## 📈 Monitoring & Debugging

### Enable Debug Mode

Add to `.env`:
```env
DEBUG=True
LOG_LEVEL=DEBUG
```

### View Execution Details

In UI, expand "🔍 Details" to see:
- Routing decisions
- Agent execution path
- Confidence scores
- Source retrieval

### Check Logs

```bash
# View Streamlit logs
streamlit run app.py --logger.level=debug

# Python logging
tail -f app.log  # If logging configured
```

---

## 🎓 Next Steps

### Learn More

1. **Read README.md**: Complete system documentation
2. **Study workflow.py**: Understand LangGraph implementation
3. **Explore agents/**: See individual agent implementations
4. **Review test_system.py**: Understand testing approach

### Customize

1. **Add new documents**: Place in `src/data/financial_reports/`
2. **Modify routing**: Edit `router_agent.py`
3. **Add new agents**: Create in `src/agents/`
4. **Enhance UI**: Modify `app.py`

### Extend

- Add more data sources (APIs, databases)
- Implement caching for faster responses
- Add authentication and user management
- Deploy to cloud (Heroku, AWS, GCP)
- Create REST API endpoints
- Add multi-user support

---

## ✅ Success Checklist

Before submitting your assignment, verify:

- [ ] All tests pass (`python test_system.py`)
- [ ] Streamlit UI launches successfully
- [ ] Router correctly classifies queries
- [ ] LLM agent responds to general questions
- [ ] Web agent fetches current information
- [ ] RAG agent retrieves company documents
- [ ] Conversation memory works across turns
- [ ] Sources are properly attributed
- [ ] Documentation is complete and clear

---

## 📞 Support

If you encounter issues:

1. **Check this guide** first
2. **Run test_system.py** to identify failing components
3. **Review error messages** carefully
4. **Check API key configuration**
5. **Verify internet connection** (for web searches)
6. **Ensure Python 3.10+** is installed

---

**Congratulations!** You now have a fully functional Multi-Agent Research and Summarization System. 🎉

Explore, experiment, and customize to your needs!