# 🤖 AI Customer Support Agent

A production-ready AI-powered customer support system with **Hybrid RAG (Retrieval Augmented Generation)** architecture. Built to handle order tracking, product inquiries, and context-aware conversations using SQL and Vector databases.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 🌟 Features

### **🎯 Core Capabilities**
- **Intent Classification**: LLM-based query routing (ORDER, PRODUCT, HYBRID)
- **Hybrid RAG Architecture**: Combines SQL + Vector DB for intelligent responses
- **Conversation Memory**: Context-aware responses using session history
- **Real-time Chat Interface**: Beautiful ChatGPT-style dark theme UI
- **Multi-Model Support**: Works with Ollama (local), OpenAI, Anthropic, or Google Gemini

### **💾 Data Architecture**
- **SQL Database**: Stores orders, users, and conversation history
- **Vector Database**: FAISS-powered semantic search over 20+ products
- **Session Management**: Browser-based localStorage for conversation persistence

### **🧠 AI Features**
- Semantic product search using sentence transformers
- Context-aware response generation
- Handles complex queries like *"What's the current price of the laptop I bought last month?"*
- Prevents hallucinations by grounding responses in retrieved data

---

## 🏗️ Architecture
```
User Query
    ↓
Intent Classifier (LLM)
    ↓
┌─────────────┬─────────────┬──────────────────┐
│  ORDER      │  PRODUCT    │  ORDER_PRODUCT   │
│  DETAILS    │  DETAILS    │  DETAILS         │
└──────┬──────┴──────┬──────┴─────────┬────────┘
       ↓              ↓                ↓
   SQL Query    Vector Search    SQL + Vector
       ↓              ↓                ↓
   Retrieved Context (Orders, Products, Both)
                     ↓
              RAG Engine (LLM)
                     ↓
           Natural Language Response
```

---

## 🛠️ Tech Stack

### **Backend**
- **FastAPI**: Modern async web framework
- **SQLAlchemy**: ORM for SQL database operations
- **FAISS**: Facebook's vector similarity search
- **Sentence Transformers**: Generate text embeddings
- **Ollama/OpenAI/Anthropic/Gemini**: LLM providers

### **Frontend**
- **HTML5**: Semantic markup with form-controlled submission
- **CSS3**: Modern dark theme with animations & responsive design
- **Vanilla JavaScript**: No framework dependencies
- **Marked.js**: Markdown rendering for AI responses
- **LocalStorage**: Session-based conversation persistence

### **Database**
- **SQLite**: Order and conversation storage
- **FAISS**: Vector embeddings for products

---

## 📦 Installation

### **Prerequisites**
- Python 3.11 or higher
- Ollama (for local LLM) OR API keys for OpenAI/Anthropic/Gemini

### **1. Clone the Repository**
```bash
git clone https://github.com/YOUR_USERNAME/ai-support-agent.git
cd ai-support-agent
```

### **2. Create Virtual Environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4. Setup Environment Variables**
Create `.env` file in project root:
```env
# Choose ONE LLM Provider

# Option 1: Local LLM (Ollama - Free, Recommended)
LLM_PROVIDER=local
LOCAL_LLM_URL=http://localhost:11434

# Option 2: OpenAI
# LLM_PROVIDER=openai
# OPENAI_API_KEY=sk-proj-xxxxx

# Option 3: Anthropic Claude
# LLM_PROVIDER=anthropic
# ANTHROPIC_API_KEY=sk-ant-xxxxx

# Option 4: Google Gemini
# LLM_PROVIDER=gemini
# GEMINI_API_KEY=xxxxx
```

### **5. Install Ollama (For Local LLM)**
If using local LLM:

**Windows/Mac/Linux:**
1. Download from: https://ollama.com/download
2. Install and run Ollama
3. Pull the model:
```bash
   ollama pull llama3.2
```

---

## 🚀 Running the Application

### **Start Backend Server**
```bash
python main.py
```

Backend will start on: http://localhost:8000

API Documentation available at: http://localhost:8000/docs

### **Start Frontend**
The frontend is a single-page application built with vanilla HTML, CSS, and JavaScript.
**Option 1: Python HTTP Server (Recommended)**
```bash
cd frontend
python -m http.server 8080
```
Open: http://localhost:8080

**Option 2: Direct File**
Simply double-click `frontend/index.html`

---

## 📖 Usage Examples

### **Query Types**

**1. Order Tracking:**
```
"Where is my order?"
"Track order TRACK123456"
"When will my package arrive?"
```
→ Retrieves from SQL database

**2. Product Information:**
```
"Tell me about Samsung Galaxy S23 Ultra"
"Do you have wireless headphones with noise cancellation?"
"Compare Dell XPS 15 and MacBook Pro"
```
→ Semantic search in vector database

**3. Hybrid Queries (Past Purchases):**
```
"What's the current price of the laptop I bought last month?"
"Does the phone I ordered support fast charging?"
"Tell me about the headphones from my recent order"
```
→ SQL (order history) + Vector DB (product info) + RAG

---

## 🧪 Testing

### **Test Backend API**
```bash
# Run all tests
python test_api.py

# Test specific components
python test_db.py          # SQL database
python test_vector_db.py   # Vector database
python test_intent.py      # Intent classification
python test_rag.py         # End-to-end RAG pipeline
```

### **Test via Swagger UI**
1. Start backend: `python main.py`
2. Open: http://localhost:8000/docs
3. Try the `/api/v1/chat` endpoint

---

## 📁 Project Structure
```
ai-support-agent/
├── api/
│   ├── __init__.py
│   └── routes.py              # FastAPI endpoints
├── database/
│   ├── __init__.py
│   ├── sql_db.py             # SQL operations
│   └── vector_db.py          # Vector DB operations
├── services/
│   ├── __init__.py
│   ├── intent_classifier.py  # LLM-based intent detection
│   ├── retriever.py          # Data retrieval logic
│   └── rag_engine.py         # RAG response generation
├── models/
│   ├── __init__.py
│   └── schemas.py            # Pydantic models
├── frontend/
│   ├── index.html            # Chat interface
│   ├── css/
│   │   └── style.css         # Dark theme styles & animations
│   └── js/
│       ├── api.js            # Backend communication
│       ├── ui.js             # UI management & animations
│       └── app.js            # Main application logic & event handlers
├── data/
│   ├── products.json         # Product catalog
│   ├── ecommerce.db          # SQLite database
│   └── faiss_index.bin       # Vector embeddings
├── main.py                   # Application entry point
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
└── README.md                 # This file
```

---

## 🎯 Key Technical Highlights

### **1. Intent Classification**
Uses LLM to classify queries into:
- `ORDER_DETAILS` → SQL
- `PRODUCT_DETAILS` → Vector DB
- `ORDER_PRODUCT_DETAILS` → Hybrid (SQL + Vector)

### **2. Hybrid RAG Pipeline**
For queries like *"What's the price of the laptop I bought?"*:
1. SQL: Fetch user's order → "User bought Dell XPS 15"
2. Vector DB: Semantic search → Current Dell XPS 15 info
3. RAG: LLM combines both → "You bought Dell XPS 15 for $1799. Current price: $1699."

### **3. Conversation Memory**
- Stores all messages in SQL
- Passes last 10 messages to LLM as context
- Enables follow-up questions like *"Tell me more about that"*

### **4. Semantic Search**
Uses `sentence-transformers` to understand query meaning:
- "affordable laptops" matches "budget-friendly computers"
- "noise-canceling earbuds" matches "ANC headphones"

---

## 🌐 Deployment

### **Backend Deployment (Railway, Render, Fly.io)**
```bash
# Example for Railway
railway init
railway up
```

### **Frontend Deployment (Vercel, Netlify)**
```bash
# Deploy frontend folder
cd frontend
vercel deploy
```

### **Environment Variables**
Remember to set environment variables in your deployment platform.

---

## 🎤 Key Technical Highlights

Use this project to demonstrate:

1. **RAG Architecture**: "I built a hybrid RAG system combining structured (SQL) and unstructured (vector) data for accurate, grounded responses."

2. **System Design**: "I designed a modular architecture with clear separation: intent classification → data retrieval → response generation."

3. **AI/ML Integration**: "I integrated LLMs for intent detection and response generation, with fallback options for different providers."

4. **Full-Stack Skills**: "I implemented both backend (FastAPI, databases) and frontend (vanilla JS, modern UI) from scratch."

5. **Production Readiness**: "I implemented conversation memory, error handling, session management, and comprehensive testing."

---

## 🔮 Future Enhancements

- [ ] User authentication and authorization
- [ ] Multi-language support
- [ ] Voice input/output
- [ ] Admin dashboard for analytics
- [ ] Product recommendation engine
- [ ] Email notifications for order updates
- [ ] Integration with real e-commerce APIs

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is licensed under the MIT License.

---

## 👤 Author

**Sujal Gowda J M**
- GitHub: [Mr-Suj](https://github.com/Mr-Suj)
- LinkedIn: [sujalgowda007](https://www.linkedin.com/in/sujalgowda007)
- Email: sujalgowda42@gmail.com

---

##  Acknowledgments

- FastAPI for the excellent web framework
- OpenAI for GPT models
- Anthropic for Claude models
- Google for Gemini API
- Ollama for local LLM support
- FAISS for efficient vector similarity search
- Sentence Transformers for text embeddings

---

## ⭐ Show Your Support

Give a ⭐ if this project helped you!

---

**Built with ❤️ as a demonstration of production-ready AI engineering**
