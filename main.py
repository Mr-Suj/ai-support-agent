from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="AI Customer Support Agent",
    description="""
    Production-ready AI customer support backend with:
    - LLM-based intent classification
    - Hybrid retrieval (SQL + Vector DB)
    - RAG for accurate responses
    
    Built with: FastAPI, Ollama/LLaMA, SQLAlchemy, FAISS
    """,
    version="1.0.0",
    docs_url="/docs",  # Swagger UI at /docs
    redoc_url="/redoc"  # ReDoc at /redoc
)

# Add CORS middleware (allows frontend to call API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1", tags=["Chat"])


@app.on_event("startup")
async def startup_event():
    """Run on app startup"""
    print("="*70)
    print("🚀 AI Customer Support Agent Starting...")
    print("="*70)
    print("📊 Initializing databases...")
    
    # Initialize databases (create tables if needed)
    from database.sql_db import init_db, populate_sample_data
    from database.vector_db import load_vector_db
    
    init_db()
    populate_sample_data()
    load_vector_db()
    
    print("✅ Databases initialized!")
    print("="*70)
    print("📡 API is ready!")
    print("📝 Docs available at: http://localhost:8000/docs")
    print("="*70)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Customer Support Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
        "chat": "/api/v1/chat"
    }


if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload on code changes
    )