"""SQL Execution Service with safety validation and result formatting."""

import asyncio
import time
from typing import Dict, Any, List, Optional, Union
from decimal import Decimal
from datetime import datetime, date
from sqlalchemy import text, create_engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.core.database import get_db, engine
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class QueryExecutionError(Exception):
    """Custom exception for query execution errors."""
    pass


class QueryTimeout(Exception):
    """Custom exception for query timeouts."""
    pass


class SQLExecutor:
    """Safe SQL query executor with result formatting and performance monitoring."""
    
    def __init__(self, timeout_seconds: int = 30, max_rows: int = 1000):
        self.timeout_seconds = timeout_seconds
        self.max_rows = max_rows
    
    async def execute_query(self, sql: str, db: Optional[Session] = None) -> Dict[str, Any]:
        """Execute SQL query safely with comprehensive result formatting."""
        
        execution_start = time.time()
        
        try:
            # Use provided session or get new one
            session = db if db else next(get_db())
            
            # Execute query with timeout
            result = await self._execute_with_timeout(sql, session)
            
            execution_time = time.time() - execution_start
            
            return {
                "success": True,
                "sql": sql,
                "execution_time": round(execution_time, 3),
                "row_count": result["row_count"],
                "columns": result["columns"],
                "data": result["data"],
                "summary": result["summary"],
                "metadata": {
                    "query_type": self._detect_query_type(sql),
                    "has_aggregation": self._has_aggregation(sql),
                    "has_joins": self._has_joins(sql),
                    "estimated_complexity": self._estimate_complexity(sql)
                }
            }
            
        except QueryTimeout:
            return {
                "success": False,
                "sql": sql,
                "execution_time": self.timeout_seconds,
                "error": f"Query timed out after {self.timeout_seconds} seconds",
                "error_type": "timeout"
            }
        except SQLAlchemyError as e:
            return {
                "success": False,
                "sql": sql,
                "execution_time": time.time() - execution_start,
                "error": f"Database error: {str(e)}",
                "error_type": "database_error"
            }
        except Exception as e:
            logger.error(f"Unexpected error executing query: {e}")
            return {
                "success": False,
                "sql": sql,
                "execution_time": time.time() - execution_start,
                "error": f"Execution error: {str(e)}",
                "error_type": "execution_error"
            }
        finally:
            # Clean up session if we created it
            if not db and 'session' in locals():
                session.close()
    
    async def _execute_with_timeout(self, sql: str, session: Session) -> Dict[str, Any]:
        """Execute query with timeout protection."""
        
        # Create asyncio task for query execution
        task = asyncio.create_task(self._execute_query_task(sql, session))
        
        try:
            # Wait for task completion or timeout
            result = await asyncio.wait_for(task, timeout=self.timeout_seconds)
            return result
        except asyncio.TimeoutError:
            task.cancel()
            raise QueryTimeout(f"Query exceeded {self.timeout_seconds} second timeout")
    
    async def _execute_query_task(self, sql: str, session: Session) -> Dict[str, Any]:
        """Execute the actual SQL query."""
        
        # Execute query
        result = session.execute(text(sql))
        
        # Fetch results
        if result.returns_rows:
            rows = result.fetchall()
            columns = list(result.keys())
            
            # Apply row limit
            if len(rows) > self.max_rows:
                logger.warning(f"Query returned {len(rows)} rows, limiting to {self.max_rows}")
                rows = rows[:self.max_rows]
            
            # Convert to serializable format
            data = []
            for row in rows:
                row_data = {}
                for i, value in enumerate(row):
                    row_data[columns[i]] = self._serialize_value(value)
                data.append(row_data)
            
            # Generate summary
            summary = self._generate_summary(data, columns)
            
            return {
                "row_count": len(data),
                "columns": columns,
                "data": data,
                "summary": summary
            }
        else:
            # Non-SELECT query (shouldn't happen with our validation, but just in case)
            return {
                "row_count": 0,
                "columns": [],
                "data": [],
                "summary": {"message": "Query executed successfully but returned no data"}
            }
    
    def _serialize_value(self, value: Any) -> Any:
        """Convert database values to JSON-serializable format."""
        
        if value is None:
            return None
        elif isinstance(value, (datetime, date)):
            return value.isoformat()
        elif isinstance(value, Decimal):
            return float(value)
        elif isinstance(value, (dict, list)):
            return value  # Already JSON-serializable
        else:
            return str(value)
    
    def _generate_summary(self, data: List[Dict[str, Any]], columns: List[str]) -> Dict[str, Any]:
        """Generate summary statistics for the query results."""
        
        if not data:
            return {"message": "No data returned"}
        
        summary = {
            "total_rows": len(data),
            "columns_count": len(columns),
            "sample_data": data[:3] if len(data) > 3 else data  # First 3 rows as sample
        }
        
        # Analyze column types and generate statistics
        column_stats = {}
        for col in columns:
            col_values = [row[col] for row in data if row[col] is not None]
            
            if not col_values:
                column_stats[col] = {"type": "null", "null_count": len(data)}
                continue
            
            # Detect column type and generate appropriate stats
            sample_value = col_values[0]
            
            if isinstance(sample_value, (int, float)):
                # Numeric column
                numeric_values = [v for v in col_values if isinstance(v, (int, float))]
                if numeric_values:
                    column_stats[col] = {
                        "type": "numeric",
                        "count": len(numeric_values),
                        "min": min(numeric_values),
                        "max": max(numeric_values),
                        "avg": round(sum(numeric_values) / len(numeric_values), 2)
                    }
            elif isinstance(sample_value, str):
                # String column
                unique_values = set(col_values)
                column_stats[col] = {
                    "type": "string",
                    "count": len(col_values),
                    "unique_values": len(unique_values),
                    "sample_values": list(unique_values)[:5]  # First 5 unique values
                }
            else:
                # Other type
                column_stats[col] = {
                    "type": type(sample_value).__name__,
                    "count": len(col_values)
                }
        
        summary["column_statistics"] = column_stats
        return summary
    
    def _detect_query_type(self, sql: str) -> str:
        """Detect the type of SQL query."""
        
        sql_lower = sql.lower().strip()
        
        if sql_lower.startswith('select'):
            if 'group by' in sql_lower:
                return "aggregation"
            elif 'join' in sql_lower:
                return "join"
            else:
                return "select"
        else:
            return "unknown"
    
    def _has_aggregation(self, sql: str) -> bool:
        """Check if query contains aggregation functions."""
        
        aggregation_functions = ['count(', 'sum(', 'avg(', 'max(', 'min(', 'group by']
        sql_lower = sql.lower()
        
        return any(func in sql_lower for func in aggregation_functions)
    
    def _has_joins(self, sql: str) -> bool:
        """Check if query contains joins."""
        
        join_keywords = ['join', 'inner join', 'left join', 'right join', 'outer join']
        sql_lower = sql.lower()
        
        return any(keyword in sql_lower for keyword in join_keywords)
    
    def _estimate_complexity(self, sql: str) -> str:
        """Estimate query complexity based on various factors."""
        
        sql_lower = sql.lower()
        complexity_score = 0
        
        # Basic SELECT gets 1 point
        if 'select' in sql_lower:
            complexity_score += 1
        
        # Joins add complexity
        join_count = sql_lower.count('join')
        complexity_score += join_count * 2
        
        # Aggregations add complexity
        aggregation_functions = ['count(', 'sum(', 'avg(', 'max(', 'min(']
        for func in aggregation_functions:
            complexity_score += sql_lower.count(func)
        
        # Subqueries add complexity
        complexity_score += sql_lower.count('select') - 1  # Subqueries
        
        # GROUP BY, ORDER BY add complexity
        if 'group by' in sql_lower:
            complexity_score += 1
        if 'order by' in sql_lower:
            complexity_score += 1
        
        # WHERE conditions add complexity
        complexity_score += sql_lower.count('where')
        complexity_score += sql_lower.count('and')
        complexity_score += sql_lower.count('or')
        
        # Classify complexity
        if complexity_score <= 2:
            return "simple"
        elif complexity_score <= 5:
            return "moderate"
        else:
            return "complex"


class QueryPerformanceMonitor:
    """Monitor and log query performance for optimization."""
    
    def __init__(self):
        self.query_history = []
        self.max_history = 100
    
    def log_query_execution(self, query_result: Dict[str, Any]):
        """Log query execution for performance monitoring."""
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "sql": query_result.get("sql", ""),
            "execution_time": query_result.get("execution_time", 0),
            "row_count": query_result.get("row_count", 0),
            "success": query_result.get("success", False),
            "complexity": query_result.get("metadata", {}).get("estimated_complexity", "unknown")
        }
        
        self.query_history.append(log_entry)
        
        # Keep only recent queries
        if len(self.query_history) > self.max_history:
            self.query_history = self.query_history[-self.max_history:]
        
        # Log slow queries
        if log_entry["execution_time"] > 5.0:  # 5 second threshold
            logger.warning(f"Slow query detected: {log_entry['execution_time']}s - {log_entry['sql'][:100]}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get aggregated performance statistics."""
        
        if not self.query_history:
            return {"message": "No query history available"}
        
        successful_queries = [q for q in self.query_history if q["success"]]
        
        if not successful_queries:
            return {"message": "No successful queries in history"}
        
        execution_times = [q["execution_time"] for q in successful_queries]
        row_counts = [q["row_count"] for q in successful_queries]
        
        return {
            "total_queries": len(self.query_history),
            "successful_queries": len(successful_queries),
            "success_rate": round(len(successful_queries) / len(self.query_history) * 100, 1),
            "avg_execution_time": round(sum(execution_times) / len(execution_times), 3),
            "max_execution_time": max(execution_times),
            "avg_row_count": round(sum(row_counts) / len(row_counts), 1),
            "max_row_count": max(row_counts),
            "recent_queries": self.query_history[-5:]  # Last 5 queries
        }


# Global performance monitor instance
performance_monitor = QueryPerformanceMonitor()


async def execute_sql_query(
    sql: str, 
    timeout_seconds: int = 30, 
    max_rows: int = 1000,
    db: Optional[Session] = None
) -> Dict[str, Any]:
    """Execute SQL query safely with monitoring."""
    
    executor = SQLExecutor(timeout_seconds=timeout_seconds, max_rows=max_rows)
    result = await executor.execute_query(sql, db)
    
    # Log execution for monitoring
    performance_monitor.log_query_execution(result)
    
    return result


def get_query_performance_stats() -> Dict[str, Any]:
    """Get query performance statistics."""
    return performance_monitor.get_performance_stats()