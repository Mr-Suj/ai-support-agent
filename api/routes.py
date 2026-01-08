from fastapi import APIRouter, HTTPException, status
from models.schemas import ChatRequest, ChatResponse, ErrorResponse
from services.intent_classifier import classify_intent
from services.retriever import retrieve
from services.rag_engine import generate_response
import traceback

router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        200: {"description": "Successful response"},
        400: {"model": ErrorResponse, "description": "Bad request"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="Chat with AI Customer Support Agent",
    description="""
    Send a customer support query and receive an AI-generated response.
    
    The system:
    1. Classifies the intent (ORDER, PRODUCT, or HYBRID query)
    2. Retrieves relevant data from SQL and/or Vector databases
    3. Uses conversation history for context-aware responses
    4. Generates a natural language response using RAG
    
    Example queries:
    - "Where is my order?"
    - "Tell me about Samsung Galaxy S23"
    - "What's the current price of the laptop I bought?"
    """
)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - handles all customer support queries with conversation memory.
    """
    try:
        from database.sql_db import add_message, get_conversation_history, create_conversation
        
        # Validate input
        if not request.query or not request.query.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query cannot be empty"
            )
        
        query = request.query.strip()
        user_email = request.user_email
        
        # Get or generate session_id
        session_id = request.session_id if request.session_id else None
        if not session_id:
            import uuid
            session_id = f"session_{uuid.uuid4().hex[:16]}"
            create_conversation(session_id, user_email)
        
        # Get conversation history
        conversation_history = get_conversation_history(session_id, limit=10)
        
        # Store user message
        add_message(session_id, "user", query)
        
        # Step 1: Classify intent
        try:
            intent_result = classify_intent(query)
            intent = intent_result['intent']
            entities = intent_result.get('entities', {})
            reasoning = intent_result.get('reasoning', '')
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Intent classification failed: {str(e)}"
            )
        
        # Step 2: Retrieve relevant data
        try:
            retrieval_result = retrieve(
                intent=intent,
                query=query,
                entities=entities,
                user_email=user_email
            )
            context = retrieval_result['context']
            data_source = retrieval_result['data_source']
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Data retrieval failed: {str(e)}"
            )
        
        # Step 3: Generate response using RAG with conversation history
        try:
            ai_response = generate_response(
                query=query,
                context=context,
                intent=intent,
                conversation_history=conversation_history
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Response generation failed: {str(e)}"
            )
        
        # Store assistant message
        add_message(session_id, "assistant", ai_response, intent, data_source)
        
        # Return successful response
        return ChatResponse(
            success=True,
            query=query,
            intent=intent,
            data_source=data_source,
            response=ai_response,
            metadata={
                "session_id": session_id,
                "entities": entities,
                "reasoning": reasoning,
                "context_length": len(context),
                "conversation_length": len(conversation_history)
            }
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"❌ Unexpected error: {error_details}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get(
    "/conversation/{session_id}",
    summary="Get Conversation History",
    description="Retrieve all messages from a conversation session"
)
async def get_conversation(session_id: str):
    """Get conversation history by session ID"""
    from database.sql_db import get_conversation_history
    
    messages = get_conversation_history(session_id, limit=50)
    
    if not messages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {session_id} not found"
        )
    
    return {
        "session_id": session_id,
        "message_count": len(messages),
        "messages": messages
    }


@router.delete(
    "/conversation/{session_id}",
    summary="Delete Conversation",
    description="Delete a conversation and all its messages"
)
async def delete_conversation_endpoint(session_id: str):
    """Delete conversation by session ID"""
    from database.sql_db import delete_conversation
    
    success = delete_conversation(session_id)
    
    return {
        "success": success,
        "message": f"Conversation {session_id} deleted successfully"
    }


@router.get(
    "/health",
    summary="Health Check",
    description="Check if the API is running"
)
async def health_check():
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "message": "AI Customer Support Agent is running"
    }