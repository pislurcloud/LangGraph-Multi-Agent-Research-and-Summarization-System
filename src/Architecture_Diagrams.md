# System Architecture Diagrams

## 1. High-Level System Flow

```mermaid
graph TD
    A[User Query] --> B[Router Agent]
    B -->|LLM-based Classification| C{Route Decision}
    C -->|General Knowledge| D[LLM Agent]
    C -->|Current Info| E[Web Research Agent]
    C -->|Company Data| F[RAG Agent]
    D --> G[Summarization Agent]
    E --> G
    F --> G
    G --> H[Final Response with Sources]
    H --> I[Update Memory]
    I --> J[Display to User]
```

## 2. LangGraph State Machine

```mermaid
stateDiagram-v2
    [*] --> Router
    Router --> LLM : route=llm
    Router --> WebResearch : route=web_research
    Router --> RAG : route=rag
    LLM --> Summarization
    WebResearch --> Summarization
    RAG --> Summarization
    Summarization --> [*]
```

## 3. Component Architecture

```mermaid
graph LR
    subgraph "User Interface"
        A[Streamlit UI]
    end
    
    subgraph "Orchestration Layer"
        B[LangGraph Workflow]
        C[State Management]
        D[Memory Manager]
    end
    
    subgraph "Agent Layer"
        E[Router Agent]
        F[LLM Agent]
        G[Web Agent]
        H[RAG Agent]
        I[Summary Agent]
    end
    
    subgraph "Data Layer"
        J[Groq API]
        K[Tavily API]
        L[ChromaDB]
        M[TechNova Docs]
    end
    
    A --> B
    B --> C
    B --> D
    C --> E
    E --> F
    E --> G
    E --> H
    F --> I
    G --> I
    H --> I
    F --> J
    G --> K
    H --> L
    L --> M
```

## 4. Data Flow

```mermaid
sequenceDiagram
    participant U as User
    participant R as Router
    participant A as Agent (LLM/Web/RAG)
    participant S as Summarizer
    participant M as Memory
    
    U->>R: Submit Query
    R->>R: Classify Query
    R->>A: Route to Agent
    A->>A: Process Query
    A->>S: Send Results
    S->>S: Synthesize Response
    S->>M: Update History
    S->>U: Return Response
```

## 5. Router Decision Logic

```mermaid
flowchart TD
    A[Receive Query] --> B{Contains time keywords?}
    B -->|Yes: latest, current, 2025| C[Route to Web]
    B -->|No| D{Contains company keywords?}
    D -->|Yes: TechNova, revenue, our| E[Route to RAG]
    D -->|No| F{LLM Classification}
    F -->|General Knowledge| G[Route to LLM]
    F -->|Uncertain| H[Keyword Fallback]
    H --> I[Default to LLM]
```

## 6. RAG System Architecture

```mermaid
graph TB
    A[Financial Documents] -->|Text Splitting| B[Document Chunks]
    B -->|Embedding| C[Sentence Transformers]
    C -->|Store| D[ChromaDB Vector Store]
    E[User Query] -->|Embed| F[Query Embedding]
    F -->|Similarity Search| D
    D -->|Top-k Results| G[Relevant Contexts]
    G -->|Inject into Prompt| H[LLM]
    H -->|Generate| I[Contextualized Answer]
```

## 7. Web Research Flow

```mermaid
graph LR
    A[Query] --> B[Tavily Search API]
    B --> C[Multiple Web Sources]
    C --> D[Extract Content]
    D --> E[Rank by Relevance]
    E --> F[LLM Synthesis]
    F --> G[Cited Response]
```

## 8. Memory Management

```mermaid
graph TD
    A[User Message] --> B[Memory Manager]
    C[Assistant Response] --> B
    B --> D[Conversation Buffer]
    D -->|Last 3 Turns| E[Context Window]
    E -->|Next Query| F[Context Injection]
    F --> G[Enhanced Understanding]
```

## Routing Examples

### Example 1: General Knowledge
```
Input: "What is machine learning?"
Router: Analyzes → No time words, no company words → LLM
Flow: Router → LLM Agent → Summarizer → Response
```

### Example 2: Current Information
```
Input: "What's the latest AI news?"
Router: Detects "latest" → Web Research
Flow: Router → Web Agent (Tavily) → Summarizer → Response
```

### Example 3: Company Data
```
Input: "TechNova's Q1 revenue?"
Router: Detects "TechNova" → RAG
Flow: Router → RAG Agent (ChromaDB) → Summarizer → Response
```

### Example 4: Follow-up with Memory
```
Query 1: "TechNova Q1 revenue?"
Response 1: "$2.8B" [RAG Agent, stored in memory]

Query 2: "What about Q2?"
Memory: Injects context "Previous: Q1 revenue query"
Router: Detects follow-up pattern → RAG
Flow: Router → RAG Agent (with context) → Summarizer → Response: "$3.2B"
```

## Technology Stack Diagram

```mermaid
graph TB
    subgraph "Frontend"
        A[Streamlit UI]
    end
    
    subgraph "Backend"
        B[Python 3.10+]
        C[LangChain/LangGraph]
    end
    
    subgraph "LLM Provider"
        D[Groq API]
        E[Llama 4 Scout]
    end
    
    subgraph "Search"
        F[Tavily API]
    end
    
    subgraph "Storage"
        G[ChromaDB]
        H[Sentence Transformers]
    end
    
    A --> B
    B --> C
    C --> D
    C --> F
    C --> G
    D --> E
    G --> H
```

---

These diagrams illustrate the complete system architecture, data flow, and decision-making processes implemented in the LangGraph Multi-Agent System.