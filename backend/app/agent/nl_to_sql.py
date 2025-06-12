"""Natural Language to SQL Parser with advanced prompt engineering."""

import re
from typing import Dict, Any, List, Optional
from sqlalchemy import inspect
from sqlalchemy.orm import Session
from app.core.database import get_db, engine
from app.models.sports import Activity, Athlete, Event, Effort, Owner, Period
from app.agent.llm_client import get_llm_client, BaseLLMClient
import logging

logger = logging.getLogger(__name__)


class DatabaseSchemaGenerator:
    """Generate comprehensive database schema context for LLM."""
    
    @staticmethod
    def get_schema_context() -> str:
        """Generate detailed schema context for the LLM."""
        
        schema_context = """
DATABASE SCHEMA FOR SPORTS ANALYTICS PLATFORM:

=== TABLES AND RELATIONSHIPS ===

1. ACTIVITIES (Main training sessions/games)
   - activity_id (Primary Key, BigInteger) - Unique identifier
   - name (String) - Activity name (e.g., "Training Session", "Match")
   - start_time (Timestamp) - When activity started
   - end_time (Timestamp) - When activity ended
   - game_id (BigInteger) - Game identifier if applicable
   - owner_id (BigInteger) - References owners.owner_id
   - owner_name (String) - Owner/team name
   - owner_email (String) - Owner contact
   - athlete_count (Integer) - Number of athletes in activity
   - period_count (Integer) - Number of periods in activity
   - created_at (Timestamp) - Record creation time
   - updated_at (Timestamp) - Record update time

2. ATHLETES (Player information)
   - athlete_id (Primary Key, BigInteger) - Unique identifier
   - first_name (String) - Athlete's first name
   - last_name (String) - Athlete's last name  
   - gender (String) - "Male", "Female", etc.
   - jersey_number (Integer) - Player's jersey/shirt number
   - height (Decimal) - Height in cm
   - weight (Decimal) - Weight in kg
   - position_id (Integer) - Position identifier
   - date_of_birth (Date) - Birth date
   - created_at (Timestamp) - Record creation time

3. EVENTS (Performance events during activities)
   - event_id (Primary Key, BigInteger) - Unique identifier
   - activity_id (BigInteger) - References activities.activity_id
   - athlete_id (BigInteger) - References athletes.athlete_id
   - device_id (BigInteger) - Tracking device ID
   - start_time (Timestamp) - Event start time
   - end_time (Timestamp) - Event end time
   - version (Integer) - Event version/type
   - intensity (String) - "high", "medium", "low"
   - direction (String) - Movement direction if applicable
   - created_at (Timestamp) - Record creation time

4. EFFORTS (Performance efforts/metrics)
   - effort_id (Primary Key, BigInteger) - Unique identifier
   - activity_id (BigInteger) - References activities.activity_id
   - athlete_id (BigInteger) - References athletes.athlete_id
   - device_id (BigInteger) - Tracking device ID
   - start_time (Timestamp) - Effort start time
   - end_time (Timestamp) - Effort end time
   - band (String) - Effort intensity band ("zone_1", "zone_2", etc.)
   - distance (Decimal) - Distance covered in meters
   - velocity (Decimal) - Speed in m/s
   - acceleration (Decimal) - Acceleration in m/s²
   - created_at (Timestamp) - Record creation time

5. OWNERS (Team/organization owners)
   - owner_id (Primary Key, BigInteger) - Unique identifier
   - customer_id (String) - External customer ID
   - name (String) - Owner/team name
   - email (String) - Contact email
   - is_synced (Boolean) - Sync status
   - is_deleted (Boolean) - Deletion status
   - created_at (Timestamp) - Record creation time

6. PERIODS (Training/game periods)
   - period_id (Primary Key, BigInteger) - Unique identifier
   - activity_id (BigInteger) - References activities.activity_id
   - name (String) - Period name (e.g., "1st Half", "Period 1")
   - start_time (Timestamp) - Period start time
   - end_time (Timestamp) - Period end time
   - is_deleted (Boolean) - Deletion status

=== COMMON QUERY PATTERNS ===

Performance Analysis:
- Velocity/speed metrics: SELECT velocity FROM efforts WHERE...
- Acceleration metrics: SELECT acceleration FROM efforts WHERE...
- Distance covered: SELECT SUM(distance) FROM efforts WHERE...
- Intensity analysis: SELECT intensity, COUNT(*) FROM events GROUP BY intensity

Athlete Analysis:
- Player performance: JOIN athletes with efforts/events
- Position-based analysis: GROUP BY position_id
- Individual stats: WHERE athlete_id = X

Activity Analysis:
- Training session data: SELECT * FROM activities WHERE...
- Time-based filtering: WHERE start_time BETWEEN '...' AND '...'
- Owner/team analysis: GROUP BY owner_name

=== IMPORTANT NOTES ===
- Always use proper JOINs when data spans multiple tables
- Use LIMIT clauses for potentially large result sets
- Time filtering is common - use start_time, end_time, created_at
- Common aggregations: COUNT, SUM, AVG, MAX, MIN
- Effort bands are typically: zone_1, zone_2, zone_3, zone_4, zone_5
- Event intensities are typically: high, medium, low
"""
        return schema_context.strip()
    
    @staticmethod
    def get_example_queries() -> List[Dict[str, str]]:
        """Get example natural language to SQL query pairs."""
        
        return [
            {
                "question": "How many athletes are in the database?",
                "sql": "SELECT COUNT(*) FROM athletes;"
            },
            {
                "question": "What's the average velocity for all athletes?", 
                "sql": "SELECT AVG(velocity) FROM efforts WHERE velocity IS NOT NULL;"
            },
            {
                "question": "Show me the top 5 fastest athletes by maximum velocity",
                "sql": "SELECT a.first_name, a.last_name, MAX(e.velocity) as max_velocity FROM athletes a JOIN efforts e ON a.athlete_id = e.athlete_id WHERE e.velocity IS NOT NULL GROUP BY a.athlete_id, a.first_name, a.last_name ORDER BY max_velocity DESC LIMIT 5;"
            },
            {
                "question": "How many training sessions were there last week?",
                "sql": "SELECT COUNT(*) FROM activities WHERE start_time >= NOW() - INTERVAL '7 days';"
            },
            {
                "question": "What's the total distance covered by athlete ID 1001?",
                "sql": "SELECT SUM(distance) FROM efforts WHERE athlete_id = 1001 AND distance IS NOT NULL;"
            },
            {
                "question": "Show activities with more than 10 athletes",
                "sql": "SELECT activity_id, name, athlete_count FROM activities WHERE athlete_count > 10 ORDER BY athlete_count DESC;"
            },
            {
                "question": "What are the different event intensities and their counts?",
                "sql": "SELECT intensity, COUNT(*) as count FROM events WHERE intensity IS NOT NULL GROUP BY intensity ORDER BY count DESC;"
            },
            {
                "question": "Find athletes who played in activities in the last month",
                "sql": "SELECT DISTINCT a.first_name, a.last_name FROM athletes a JOIN events e ON a.athlete_id = e.athlete_id JOIN activities act ON e.activity_id = act.activity_id WHERE act.start_time >= NOW() - INTERVAL '30 days';"
            }
        ]


class QueryValidator:
    """Validate and sanitize SQL queries for safety."""
    
    ALLOWED_KEYWORDS = {
        'select', 'from', 'where', 'join', 'inner', 'left', 'right', 'outer',
        'group', 'by', 'order', 'having', 'limit', 'offset', 'as', 'and', 'or',
        'not', 'in', 'like', 'ilike', 'between', 'is', 'null', 'count', 'sum',
        'avg', 'max', 'min', 'distinct', 'case', 'when', 'then', 'else', 'end',
        'extract', 'date_trunc', 'now', 'interval', 'cast', 'coalesce'
    }
    
    FORBIDDEN_KEYWORDS = {
        'drop', 'delete', 'insert', 'update', 'alter', 'create', 'truncate',
        'grant', 'revoke', 'commit', 'rollback', 'execute', 'exec', 'sp_',
        'xp_', 'pg_', 'information_schema', 'pg_catalog'
    }
    
    ALLOWED_TABLES = {
        'activities', 'athletes', 'events', 'efforts', 'owners', 'periods'
    }
    
    @classmethod
    def validate_query(cls, sql: str) -> Dict[str, Any]:
        """Validate SQL query for safety and correctness."""
        
        sql_lower = sql.lower().strip()
        
        # Remove comments and normalize whitespace
        sql_clean = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
        sql_clean = re.sub(r'/\*.*?\*/', '', sql_clean, flags=re.DOTALL)
        sql_clean = re.sub(r'\s+', ' ', sql_clean).strip()
        
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "cleaned_sql": sql_clean
        }
        
        # Check for forbidden keywords
        for forbidden in cls.FORBIDDEN_KEYWORDS:
            if forbidden in sql_lower:
                validation_result["is_valid"] = False
                validation_result["errors"].append(f"Forbidden keyword detected: {forbidden}")
        
        # Check if query starts with SELECT
        if not sql_lower.strip().startswith('select'):
            validation_result["is_valid"] = False
            validation_result["errors"].append("Only SELECT queries are allowed")
        
        # Check for table references
        found_tables = []
        for table in cls.ALLOWED_TABLES:
            if table in sql_lower:
                found_tables.append(table)
        
        if not found_tables:
            validation_result["warnings"].append("No recognized tables found in query")
        
        # Check for potentially dangerous patterns
        dangerous_patterns = [
            r'\binto\s+outfile\b',
            r'\bload_file\b',
            r'\bselect\s+into\b',
            r';\s*select',  # Multiple statements
            r'\bunion\s+select.*information_schema'
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, sql_lower):
                validation_result["is_valid"] = False
                validation_result["errors"].append(f"Potentially dangerous pattern detected")
        
        # Suggest LIMIT if not present and query might return many rows
        if 'limit' not in sql_lower and any(word in sql_lower for word in ['select *', 'join']):
            validation_result["warnings"].append("Consider adding LIMIT clause for better performance")
        
        return validation_result


class NLToSQLParser:
    """Advanced Natural Language to SQL parser with context awareness."""
    
    def __init__(self, llm_client: Optional[BaseLLMClient] = None):
        self.llm_client = llm_client
        self.schema_generator = DatabaseSchemaGenerator()
        self.validator = QueryValidator()
    
    async def parse_question(self, question: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Parse natural language question into SQL query with validation."""
        
        if not self.llm_client:
            self.llm_client = await get_llm_client()
        
        try:
            # Get schema context
            schema_context = self.schema_generator.get_schema_context()
            
            # Get example queries for few-shot learning
            examples = self.schema_generator.get_example_queries()
            
            # Add context-specific examples if provided
            if context and "recent_queries" in context:
                examples.extend(context["recent_queries"][-3:])  # Last 3 queries
            
            # Generate SQL query
            sql_query = await self.llm_client.generate_sql(
                question=question,
                schema_context=schema_context,
                examples=examples
            )
            
            # Clean up the SQL (remove markdown formatting, etc.)
            sql_query = self._clean_sql_response(sql_query)
            
            # Validate the query
            validation = self.validator.validate_query(sql_query)
            
            result = {
                "question": question,
                "sql_query": validation["cleaned_sql"] if validation["is_valid"] else None,
                "raw_sql": sql_query,
                "is_valid": validation["is_valid"],
                "errors": validation["errors"],
                "warnings": validation["warnings"],
                "confidence": self._calculate_confidence(question, sql_query, validation)
            }
            
            if not validation["is_valid"]:
                logger.warning(f"Invalid SQL generated for question: {question}")
                logger.warning(f"Errors: {validation['errors']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing question '{question}': {e}")
            return {
                "question": question,
                "sql_query": None,
                "raw_sql": None,
                "is_valid": False,
                "errors": [f"Parser error: {str(e)}"],
                "warnings": [],
                "confidence": 0.0
            }
    
    def _clean_sql_response(self, sql_response: str) -> str:
        """Clean up LLM response to extract just the SQL query."""
        
        # Remove markdown code blocks
        sql_response = re.sub(r'```sql\n?', '', sql_response)
        sql_response = re.sub(r'```\n?', '', sql_response)
        
        # Remove common LLM response prefixes
        prefixes_to_remove = [
            "Here's the SQL query:",
            "SQL Query:",
            "Query:",
            "The SQL query is:",
            "SQL:"
        ]
        
        for prefix in prefixes_to_remove:
            if sql_response.strip().lower().startswith(prefix.lower()):
                sql_response = sql_response[len(prefix):].strip()
        
        # Remove trailing explanations (everything after semicolon + text)
        lines = sql_response.split('\n')
        sql_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('--') and not line.lower().startswith('explanation'):
                sql_lines.append(line)
            elif ';' in line:
                # Include line up to semicolon
                sql_lines.append(line[:line.index(';') + 1])
                break
        
        sql_query = ' '.join(sql_lines).strip()
        
        # Ensure it ends with semicolon
        if sql_query and not sql_query.endswith(';'):
            sql_query += ';'
        
        return sql_query
    
    def _calculate_confidence(self, question: str, sql_query: str, validation: Dict[str, Any]) -> float:
        """Calculate confidence score for the generated SQL."""
        
        confidence = 1.0
        
        # Reduce confidence for validation errors
        if not validation["is_valid"]:
            confidence -= 0.5
        
        # Reduce confidence for warnings
        confidence -= len(validation["warnings"]) * 0.1
        
        # Reduce confidence for very short or generic queries
        if len(sql_query.split()) < 5:
            confidence -= 0.2
        
        # Increase confidence for complex queries that match question complexity
        question_words = len(question.split())
        sql_words = len(sql_query.split())
        
        if question_words > 10 and sql_words > 15:  # Complex question with complex SQL
            confidence += 0.1
        elif question_words < 5 and sql_words < 10:  # Simple question with simple SQL
            confidence += 0.1
        
        # Ensure confidence is between 0 and 1
        return max(0.0, min(1.0, confidence))


# Convenience function
async def parse_natural_language_to_sql(question: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Parse natural language question to SQL query."""
    parser = NLToSQLParser()
    return await parser.parse_question(question, context)