"""SQL Agent Orchestrator - coordinates the complete NL → SQL → Execution → Explanation workflow."""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.agent.llm_client import get_llm_client, BaseLLMClient
from app.agent.nl_to_sql import parse_natural_language_to_sql, NLToSQLParser
from app.agent.sql_executor import execute_sql_query, get_query_performance_stats
from app.agent.explainer import explain_query_results, ResponseExplainer
import logging

logger = logging.getLogger(__name__)


class QuerySession:
    """Manages context and history for a query session."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.created_at = datetime.now()
        self.query_history = []
        self.context = {}
    
    def add_query(self, query_data: Dict[str, Any]):
        """Add a query to the session history."""
        query_data["timestamp"] = datetime.now().isoformat()
        self.query_history.append(query_data)
        
        # Keep only recent queries for context
        if len(self.query_history) > 10:
            self.query_history = self.query_history[-10:]
    
    def get_recent_queries(self, limit: int = 3) -> List[Dict[str, str]]:
        """Get recent successful queries for context."""
        recent = []
        for query in reversed(self.query_history):
            if query.get("sql_success") and query.get("sql_query"):
                recent.append({
                    "question": query["question"],
                    "sql": query["sql_query"]
                })
                if len(recent) >= limit:
                    break
        return recent
    
    def update_context(self, key: str, value: Any):
        """Update session context."""
        self.context[key] = value


class SQLAgent:
    """Main SQL Agent that orchestrates the complete workflow."""
    
    def __init__(self, llm_client: Optional[BaseLLMClient] = None):
        self.llm_client = llm_client
        self.sessions = {}  # Session management
        self.parser = None
        self.explainer = None
    
    async def process_question(
        self,
        question: str,
        session_id: str = "default",
        include_explanation: bool = True,
        max_execution_time: int = 30,
        max_rows: int = 1000,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """Process a natural language question through the complete SQL Agent workflow."""
        
        start_time = datetime.now()
        
        # Get or create session
        session = self._get_or_create_session(session_id)
        
        logger.info(f"Processing question: {question}")
        
        try:
            # Initialize components if needed
            if not self.llm_client:
                self.llm_client = await get_llm_client()
            
            if not self.parser:
                self.parser = NLToSQLParser(self.llm_client)
            
            if not self.explainer:
                self.explainer = ResponseExplainer(self.llm_client)
            
            # Step 1: Parse natural language to SQL
            parse_result = await self._parse_question(question, session)
            
            # Step 2: Execute SQL if valid
            execution_result = None
            if parse_result["is_valid"] and parse_result["sql_query"]:
                execution_result = await self._execute_query(
                    parse_result["sql_query"], 
                    max_execution_time, 
                    max_rows,
                    db
                )
            
            # Step 3: Generate explanation
            explanation = None
            if include_explanation:
                explanation = await self._generate_explanation(
                    question, 
                    execution_result or parse_result, 
                    include_explanation
                )
            
            # Compile final response
            response = self._compile_response(
                question, parse_result, execution_result, explanation, start_time
            )
            
            # Update session history
            session.add_query({
                "question": question,
                "sql_query": parse_result.get("sql_query"),
                "sql_success": execution_result.get("success") if execution_result else False,
                "row_count": execution_result.get("row_count") if execution_result else 0,
                "execution_time": execution_result.get("execution_time") if execution_result else 0
            })
            
            logger.info(f"Question processed successfully in {response['total_processing_time']:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"Error processing question '{question}': {e}")
            
            error_response = {
                "success": False,
                "question": question,
                "session_id": session_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "total_processing_time": (datetime.now() - start_time).total_seconds()
            }
            
            session.add_query({
                "question": question,
                "error": str(e),
                "sql_success": False
            })
            
            return error_response
    
    async def _parse_question(self, question: str, session: QuerySession) -> Dict[str, Any]:
        """Parse natural language question to SQL."""
        
        # Get recent queries for context
        context = {
            "recent_queries": session.get_recent_queries()
        }
        
        return await self.parser.parse_question(question, context)
    
    async def _execute_query(
        self, 
        sql: str, 
        max_execution_time: int, 
        max_rows: int,
        db: Optional[Session]
    ) -> Dict[str, Any]:
        """Execute SQL query safely."""
        
        return await execute_sql_query(
            sql=sql,
            timeout_seconds=max_execution_time,
            max_rows=max_rows,
            db=db
        )
    
    async def _generate_explanation(
        self, 
        question: str, 
        query_result: Dict[str, Any],
        include_llm_explanation: bool
    ) -> Dict[str, Any]:
        """Generate comprehensive explanation."""
        
        return await self.explainer.explain_results(
            question, 
            query_result, 
            include_llm_explanation
        )
    
    def _compile_response(
        self,
        question: str,
        parse_result: Dict[str, Any],
        execution_result: Optional[Dict[str, Any]],
        explanation: Optional[Dict[str, Any]],
        start_time: datetime
    ) -> Dict[str, Any]:
        """Compile the final comprehensive response."""
        
        total_time = (datetime.now() - start_time).total_seconds()
        
        response = {
            "success": execution_result.get("success", False) if execution_result else parse_result["is_valid"],
            "question": question,
            "timestamp": datetime.now().isoformat(),
            "total_processing_time": round(total_time, 3),
            
            # SQL Generation Phase
            "sql_generation": {
                "sql_query": parse_result.get("sql_query"),
                "is_valid": parse_result["is_valid"],
                "confidence": parse_result.get("confidence", 0.0),
                "errors": parse_result.get("errors", []),
                "warnings": parse_result.get("warnings", [])
            },
            
            # Query Execution Phase
            "execution": execution_result if execution_result else {
                "success": False,
                "error": "SQL generation failed - cannot execute query"
            },
            
            # Explanation Phase
            "explanation": explanation if explanation else None,
            
            # Performance Metrics
            "performance": {
                "sql_generation_confidence": parse_result.get("confidence", 0.0),
                "execution_time": execution_result.get("execution_time") if execution_result else None,
                "row_count": execution_result.get("row_count") if execution_result else 0,
                "query_complexity": execution_result.get("metadata", {}).get("estimated_complexity") if execution_result else "unknown"
            }
        }
        
        # Add user-friendly summary
        response["summary"] = self._generate_user_summary(response)
        
        return response
    
    def _generate_user_summary(self, response: Dict[str, Any]) -> str:
        """Generate a user-friendly summary of the response."""
        
        if not response["success"]:
            errors = response["sql_generation"]["errors"]
            if errors:
                return f"I couldn't process your question: {errors[0]}"
            else:
                return "I encountered an issue processing your question. Please try rephrasing it."
        
        execution = response["execution"]
        row_count = execution.get("row_count", 0)
        
        if row_count == 0:
            return "Your question was processed successfully, but no matching data was found."
        elif row_count == 1:
            return "Found 1 record that answers your question."
        else:
            return f"Found {row_count} records that answer your question."
    
    def _get_or_create_session(self, session_id: str) -> QuerySession:
        """Get existing session or create new one."""
        
        if session_id not in self.sessions:
            self.sessions[session_id] = QuerySession(session_id)
        
        return self.sessions[session_id]
    
    def get_session_history(self, session_id: str) -> Dict[str, Any]:
        """Get session history and statistics."""
        
        if session_id not in self.sessions:
            return {"error": "Session not found"}
        
        session = self.sessions[session_id]
        
        return {
            "session_id": session_id,
            "created_at": session.created_at.isoformat(),
            "total_queries": len(session.query_history),
            "successful_queries": len([q for q in session.query_history if q.get("sql_success", False)]),
            "recent_queries": session.query_history[-5:],  # Last 5 queries
            "context": session.context
        }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system-wide statistics."""
        
        total_sessions = len(self.sessions)
        total_queries = sum(len(s.query_history) for s in self.sessions.values())
        successful_queries = sum(
            len([q for q in s.query_history if q.get("sql_success", False)]) 
            for s in self.sessions.values()
        )
        
        # Get query performance stats
        performance_stats = get_query_performance_stats()
        
        return {
            "total_sessions": total_sessions,
            "total_queries": total_queries,
            "successful_queries": successful_queries,
            "success_rate": round((successful_queries / total_queries * 100) if total_queries > 0 else 0, 1),
            "active_sessions": len([s for s in self.sessions.values() if len(s.query_history) > 0]),
            "performance": performance_stats
        }


# Global agent instance
sql_agent = SQLAgent()


# Convenience functions
async def ask_question(
    question: str,
    session_id: str = "default",
    include_explanation: bool = True,
    max_execution_time: int = 30,
    max_rows: int = 1000,
    db: Optional[Session] = None
) -> Dict[str, Any]:
    """Ask a natural language question to the SQL Agent."""
    
    return await sql_agent.process_question(
        question=question,
        session_id=session_id,
        include_explanation=include_explanation,
        max_execution_time=max_execution_time,
        max_rows=max_rows,
        db=db
    )


def get_agent_stats() -> Dict[str, Any]:
    """Get SQL Agent system statistics."""
    return sql_agent.get_system_stats()


def get_session_info(session_id: str) -> Dict[str, Any]:
    """Get information about a specific session."""
    return sql_agent.get_session_history(session_id)