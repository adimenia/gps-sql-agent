"""Chat API endpoints for SQL Agent interaction."""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from app.core.database import get_db
from app.agent.orchestrator import ask_question, get_agent_stats, get_session_info
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


# Pydantic models for request/response
class ChatRequest(BaseModel):
    question: str = Field(..., description="Natural language question about sports data")
    session_id: str = Field("default", description="Session ID for conversation context")
    include_explanation: bool = Field(True, description="Include detailed explanation in response")
    max_execution_time: int = Field(30, ge=5, le=120, description="Maximum query execution time in seconds")
    max_rows: int = Field(1000, ge=1, le=5000, description="Maximum number of rows to return")


class ChatResponse(BaseModel):
    success: bool
    question: str
    session_id: str = "default"
    timestamp: str
    total_processing_time: float
    summary: str
    sql_generation: Dict[str, Any]
    execution: Dict[str, Any]
    explanation: Optional[Dict[str, Any]] = None
    performance: Dict[str, Any]
    error: Optional[str] = None


class QuickQuestionRequest(BaseModel):
    question: str = Field(..., description="Quick question without session context")


@router.post("/ask", response_model=ChatResponse)
async def ask_sql_agent(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> ChatResponse:
    """Ask a question to the SQL Agent with full conversation context."""
    
    try:
        logger.info(f"Received question: {request.question} (session: {request.session_id})")
        
        # Process the question through the SQL Agent
        result = await ask_question(
            question=request.question,
            session_id=request.session_id,
            include_explanation=request.include_explanation,
            max_execution_time=request.max_execution_time,
            max_rows=request.max_rows,
            db=db
        )
        
        # Log successful processing in background
        if result.get("success"):
            background_tasks.add_task(
                _log_successful_query,
                request.session_id,
                request.question,
                result.get("execution", {}).get("row_count", 0)
            )
        
        return ChatResponse(**result)
        
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process question: {str(e)}"
        )


@router.post("/quick")
async def quick_question(
    request: QuickQuestionRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Ask a quick question without session context or detailed explanation."""
    
    try:
        result = await ask_question(
            question=request.question,
            session_id="quick",
            include_explanation=False,
            max_execution_time=15,
            max_rows=100,
            db=db
        )
        
        # Return simplified response for quick queries
        return {
            "success": result.get("success", False),
            "question": request.question,
            "answer": result.get("summary", "No answer available"),
            "data": result.get("execution", {}).get("data", []),
            "row_count": result.get("execution", {}).get("row_count", 0),
            "processing_time": result.get("total_processing_time", 0),
            "sql_query": result.get("sql_generation", {}).get("sql_query"),
            "error": result.get("error")
        }
        
    except Exception as e:
        logger.error(f"Error processing quick question: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process question: {str(e)}"
        )


@router.get("/sessions/{session_id}")
async def get_session_history(session_id: str) -> Dict[str, Any]:
    """Get conversation history for a specific session."""
    
    try:
        history = get_session_info(session_id)
        
        if "error" in history:
            raise HTTPException(status_code=404, detail=history["error"])
        
        return history
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session history: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get session history: {str(e)}"
        )


@router.get("/stats")
async def get_chat_stats() -> Dict[str, Any]:
    """Get SQL Agent system statistics and performance metrics."""
    
    try:
        return get_agent_stats()
        
    except Exception as e:
        logger.error(f"Error getting agent stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get statistics: {str(e)}"
        )


@router.post("/examples")
async def get_example_questions() -> Dict[str, Any]:
    """Get example questions that users can ask."""
    
    examples = {
        "basic_queries": [
            "How many athletes are in the database?",
            "What's the average velocity for all athletes?",
            "Show me the latest training activities"
        ],
        "performance_analysis": [
            "Who are the top 5 fastest athletes?",
            "What's the total distance covered by athlete ID 1001?",
            "Show me high-intensity events from the last week"
        ],
        "comparative_analysis": [
            "Compare velocity between male and female athletes",
            "Which training session had the most athletes?",
            "Show activities with more than 10 athletes"
        ],
        "time_based_queries": [
            "How many training sessions were there last month?",
            "Show me recent activities by owner",
            "What are the training patterns over the last 30 days?"
        ],
        "aggregated_insights": [
            "What are the different event intensities and their counts?",
            "Show me average acceleration by effort band",
            "What's the distribution of athletes by position?"
        ]
    }
    
    return {
        "examples": examples,
        "tips": [
            "Be specific about time ranges (e.g., 'last week', 'last month')",
            "Use athlete names or IDs when asking about specific players",
            "Ask for 'top N' results to get ranked lists",
            "Combine metrics (e.g., 'velocity and distance for sprinters')",
            "Use comparison words like 'fastest', 'highest', 'most active'"
        ],
        "supported_metrics": [
            "velocity (speed in m/s)",
            "acceleration (m/s²)",
            "distance (meters)",
            "intensity levels (high, medium, low)",
            "effort bands (zone_1 through zone_5)",
            "athlete demographics (position, gender, etc.)",
            "activity information (training sessions, games)"
        ]
    }


@router.post("/test")
async def test_sql_agent(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Test the SQL Agent with a simple question."""
    
    try:
        test_question = "How many athletes are in the database?"
        
        result = await ask_question(
            question=test_question,
            session_id="test",
            include_explanation=False,
            max_execution_time=10,
            max_rows=10,
            db=db
        )
        
        return {
            "test_status": "success" if result.get("success") else "failed",
            "test_question": test_question,
            "result": result,
            "agent_health": "healthy" if result.get("success") else "degraded"
        }
        
    except Exception as e:
        logger.error(f"SQL Agent test failed: {e}")
        return {
            "test_status": "failed",
            "test_question": "How many athletes are in the database?",
            "error": str(e),
            "agent_health": "unhealthy"
        }


async def _log_successful_query(session_id: str, question: str, row_count: int):
    """Background task to log successful queries for analytics."""
    
    try:
        logger.info(f"Successful query in session {session_id}: '{question}' returned {row_count} rows")
        # Here you could add additional logging, metrics collection, etc.
        
    except Exception as e:
        logger.error(f"Error logging query: {e}")


@router.get("/health")
async def chat_health_check() -> Dict[str, Any]:
    """Health check specifically for the chat/SQL Agent service."""
    
    try:
        # Test basic agent functionality
        from app.agent.llm_client import get_llm_client
        
        # Check if LLM client can be created
        llm_client = await get_llm_client()
        llm_available = llm_client is not None
        
        # Get agent stats
        stats = get_agent_stats()
        
        return {
            "status": "healthy" if llm_available else "degraded",
            "timestamp": "2024-01-01T00:00:00",  # Will be replaced with actual timestamp
            "llm_client_available": llm_available,
            "agent_stats": stats,
            "components": {
                "nl_to_sql_parser": "available",
                "sql_executor": "available", 
                "result_explainer": "available",
                "orchestrator": "available"
            }
        }
        
    except Exception as e:
        logger.error(f"Chat health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": "2024-01-01T00:00:00",
            "error": str(e),
            "llm_client_available": False
        }