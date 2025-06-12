"""Response Explanation Service for generating detailed insights about query results."""

from typing import Dict, Any, List, Optional
from datetime import datetime
from app.agent.llm_client import get_llm_client, BaseLLMClient
import logging

logger = logging.getLogger(__name__)


class InsightGenerator:
    """Generate insights from query results data."""
    
    @staticmethod
    def generate_data_insights(query_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate statistical and contextual insights from query results."""
        
        if not query_result.get("success") or not query_result.get("data"):
            return {"insights": [], "summary": "No data available for analysis"}
        
        data = query_result["data"]
        columns = query_result["columns"]
        insights = []
        
        # Basic data insights
        insights.append(f"Query returned {len(data)} records")
        
        if query_result.get("metadata", {}).get("has_aggregation"):
            insights.append("This is an aggregated query showing summary statistics")
        
        if query_result.get("metadata", {}).get("has_joins"):
            insights.append("Query combines data from multiple tables")
        
        # Column-specific insights
        column_stats = query_result.get("summary", {}).get("column_statistics", {})
        
        for col, stats in column_stats.items():
            if stats.get("type") == "numeric":
                if stats.get("count", 0) > 0:
                    insights.append(f"{col}: ranges from {stats['min']} to {stats['max']}, average {stats['avg']}")
            elif stats.get("type") == "string":
                unique_count = stats.get("unique_values", 0)
                total_count = stats.get("count", 0)
                if unique_count == total_count:
                    insights.append(f"{col}: all values are unique")
                elif unique_count == 1:
                    insights.append(f"{col}: all values are the same")
                else:
                    insights.append(f"{col}: {unique_count} unique values out of {total_count} records")
        
        # Performance insights
        execution_time = query_result.get("execution_time", 0)
        if execution_time > 2.0:
            insights.append(f"Query took {execution_time:.2f} seconds - consider optimization for better performance")
        elif execution_time < 0.1:
            insights.append("Query executed very quickly - efficient data access")
        
        # Data quality insights
        for col, stats in column_stats.items():
            null_count = stats.get("null_count", 0)
            total_count = stats.get("count", 0) + null_count
            if null_count > 0:
                null_percentage = (null_count / total_count) * 100
                insights.append(f"{col}: {null_percentage:.1f}% of values are missing/null")
        
        return {
            "insights": insights,
            "summary": f"Analysis of {len(data)} records across {len(columns)} columns",
            "data_quality": {
                "completeness": InsightGenerator._calculate_completeness(column_stats),
                "complexity": query_result.get("metadata", {}).get("estimated_complexity", "unknown")
            }
        }
    
    @staticmethod
    def _calculate_completeness(column_stats: Dict[str, Any]) -> float:
        """Calculate overall data completeness percentage."""
        
        if not column_stats:
            return 100.0
        
        total_values = 0
        null_values = 0
        
        for stats in column_stats.values():
            count = stats.get("count", 0)
            null_count = stats.get("null_count", 0)
            total_values += count + null_count
            null_values += null_count
        
        if total_values == 0:
            return 100.0
        
        return round((1 - null_values / total_values) * 100, 1)


class ContextualExplainer:
    """Generate contextual explanations based on domain knowledge."""
    
    SPORTS_CONTEXT = {
        "velocity": {
            "unit": "m/s",
            "typical_ranges": {"walking": (0, 2), "jogging": (2, 4), "running": (4, 7), "sprinting": (7, 12)},
            "description": "Speed of movement in meters per second"
        },
        "acceleration": {
            "unit": "m/s²",
            "typical_ranges": {"low": (0, 2), "moderate": (2, 4), "high": (4, 8)},
            "description": "Rate of change in velocity"
        },
        "distance": {
            "unit": "meters",
            "description": "Distance covered during the effort or activity"
        },
        "intensity": {
            "values": {"low": "Light activity", "medium": "Moderate activity", "high": "Intense activity"},
            "description": "Activity intensity level based on physiological markers"
        },
        "effort_bands": {
            "zone_1": "Recovery/Easy (50-60% max heart rate)",
            "zone_2": "Base/Aerobic (60-70% max heart rate)", 
            "zone_3": "Tempo (70-80% max heart rate)",
            "zone_4": "Lactate Threshold (80-90% max heart rate)",
            "zone_5": "VO2 Max/Neuromuscular (90-100% max heart rate)"
        }
    }
    
    @classmethod
    def add_sports_context(cls, query_result: Dict[str, Any], question: str) -> Dict[str, Any]:
        """Add sports-specific context to explain the results."""
        
        if not query_result.get("success"):
            return {"context": [], "domain_insights": []}
        
        context = []
        domain_insights = []
        data = query_result.get("data", [])
        columns = query_result.get("columns", [])
        
        # Add context for sports performance metrics
        for col in columns:
            col_lower = col.lower()
            
            if "velocity" in col_lower and data:
                velocities = [row.get(col) for row in data if row.get(col) is not None]
                if velocities:
                    avg_velocity = sum(velocities) / len(velocities)
                    speed_category = cls._categorize_velocity(avg_velocity)
                    context.append(f"Average velocity of {avg_velocity:.1f} m/s indicates {speed_category} activity")
                    
                    context.append("💡 Velocity represents running speed - higher values indicate faster movement")
            
            elif "acceleration" in col_lower and data:
                accelerations = [row.get(col) for row in data if row.get(col) is not None]
                if accelerations:
                    avg_accel = sum(accelerations) / len(accelerations)
                    accel_category = cls._categorize_acceleration(avg_accel)
                    context.append(f"Average acceleration of {avg_accel:.1f} m/s² shows {accel_category} intensity changes")
                    
                    context.append("💡 Acceleration measures how quickly athletes change speed - important for explosive movements")
            
            elif "distance" in col_lower and data:
                distances = [row.get(col) for row in data if row.get(col) is not None]
                if distances:
                    total_distance = sum(distances)
                    context.append(f"Total distance covered: {total_distance:.0f} meters ({total_distance/1000:.1f} km)")
                    
                    context.append("💡 Distance tracking helps monitor training load and work rate")
            
            elif "intensity" in col_lower and data:
                intensities = [row.get(col) for row in data if row.get(col)]
                if intensities:
                    intensity_distribution = {}
                    for intensity in intensities:
                        intensity_distribution[intensity] = intensity_distribution.get(intensity, 0) + 1
                    
                    most_common = max(intensity_distribution.items(), key=lambda x: x[1])
                    context.append(f"Most common intensity level: {most_common[0]} ({most_common[1]} occurrences)")
                    
                    context.append("💡 Intensity levels help coaches understand training stress and recovery needs")
            
            elif "band" in col_lower and data:
                bands = [row.get(col) for row in data if row.get(col)]
                if bands:
                    for band in set(bands):
                        if band in cls.SPORTS_CONTEXT["effort_bands"]:
                            context.append(f"{band}: {cls.SPORTS_CONTEXT['effort_bands'][band]}")
        
        # Add insights based on the question
        question_lower = question.lower()
        
        if "fastest" in question_lower or "top" in question_lower:
            domain_insights.append("🏃 These results show peak performance - useful for identifying talented athletes or tracking improvements")
        
        if "average" in question_lower or "mean" in question_lower:
            domain_insights.append("📊 Average values provide baseline performance indicators for team or individual assessment")
        
        if "compare" in question_lower or "vs" in question_lower:
            domain_insights.append("⚖️ Comparative analysis helps identify performance gaps and training opportunities")
        
        if any(time_word in question_lower for time_word in ["week", "month", "day", "recent"]):
            domain_insights.append("📅 Time-based analysis reveals trends, seasonal patterns, and training adaptation")
        
        return {
            "context": context,
            "domain_insights": domain_insights
        }
    
    @classmethod
    def _categorize_velocity(cls, velocity: float) -> str:
        """Categorize velocity into human-readable terms."""
        
        ranges = cls.SPORTS_CONTEXT["velocity"]["typical_ranges"]
        
        if velocity <= ranges["walking"][1]:
            return "walking/recovery pace"
        elif velocity <= ranges["jogging"][1]:
            return "jogging/easy pace"
        elif velocity <= ranges["running"][1]:
            return "moderate running pace"
        else:
            return "high-speed running/sprinting"
    
    @classmethod
    def _categorize_acceleration(cls, acceleration: float) -> str:
        """Categorize acceleration into human-readable terms."""
        
        ranges = cls.SPORTS_CONTEXT["acceleration"]["typical_ranges"]
        
        if acceleration <= ranges["low"][1]:
            return "low"
        elif acceleration <= ranges["moderate"][1]:
            return "moderate"
        else:
            return "high"


class ResponseExplainer:
    """Main service for generating comprehensive explanations of query results."""
    
    def __init__(self, llm_client: Optional[BaseLLMClient] = None):
        self.llm_client = llm_client
        self.insight_generator = InsightGenerator()
        self.contextual_explainer = ContextualExplainer()
    
    async def explain_results(
        self, 
        question: str, 
        query_result: Dict[str, Any],
        include_llm_explanation: bool = True
    ) -> Dict[str, Any]:
        """Generate comprehensive explanation of query results."""
        
        explanation = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "query_success": query_result.get("success", False)
        }
        
        if not query_result.get("success"):
            explanation.update({
                "error_explanation": self._explain_error(query_result),
                "suggestions": self._get_error_suggestions(query_result)
            })
            return explanation
        
        # Generate data insights
        data_insights = self.insight_generator.generate_data_insights(query_result)
        
        # Add sports context
        sports_context = self.contextual_explainer.add_sports_context(query_result, question)
        
        # Generate LLM explanation if requested
        llm_explanation = None
        if include_llm_explanation:
            llm_explanation = await self._generate_llm_explanation(question, query_result)
        
        explanation.update({
            "summary": self._generate_summary(question, query_result),
            "data_insights": data_insights,
            "sports_context": sports_context,
            "technical_details": {
                "execution_time": query_result.get("execution_time"),
                "row_count": query_result.get("row_count"),
                "query_complexity": query_result.get("metadata", {}).get("estimated_complexity"),
                "sql_query": query_result.get("sql")
            },
            "llm_explanation": llm_explanation,
            "recommendations": self._generate_recommendations(question, query_result)
        })
        
        return explanation
    
    def _generate_summary(self, question: str, query_result: Dict[str, Any]) -> str:
        """Generate a concise summary of the results."""
        
        data = query_result.get("data", [])
        row_count = len(data)
        
        if row_count == 0:
            return f"Your question '{question}' returned no results. This might mean no data matches your criteria."
        elif row_count == 1:
            return f"Found exactly 1 record matching your question about {self._extract_subject(question)}."
        else:
            return f"Found {row_count} records providing insights about {self._extract_subject(question)}."
    
    def _extract_subject(self, question: str) -> str:
        """Extract the main subject from the question."""
        
        question_lower = question.lower()
        
        if "athlete" in question_lower:
            return "athletes"
        elif "activity" in question_lower or "training" in question_lower:
            return "training activities"
        elif "velocity" in question_lower or "speed" in question_lower:
            return "movement velocity"
        elif "acceleration" in question_lower:
            return "acceleration patterns"
        elif "distance" in question_lower:
            return "distance metrics"
        elif "performance" in question_lower:
            return "performance metrics"
        else:
            return "sports data"
    
    async def _generate_llm_explanation(self, question: str, query_result: Dict[str, Any]) -> Optional[str]:
        """Generate natural language explanation using LLM."""
        
        if not self.llm_client:
            self.llm_client = await get_llm_client()
        
        try:
            # Prepare context for LLM
            data_summary = query_result.get("summary", {})
            row_count = query_result.get("row_count", 0)
            sample_data = data_summary.get("sample_data", [])
            
            prompt = f"""
Explain these sports analytics query results in simple, conversational language:

Question: "{question}"
Results: {row_count} records found
Sample data: {sample_data[:2] if sample_data else "No data"}

Provide a brief, friendly explanation focusing on:
1. What the data shows
2. Key patterns or notable findings
3. What this means for sports performance

Keep it conversational and avoid technical jargon.
"""
            
            explanation = await self.llm_client.generate_response(
                prompt=prompt,
                system_message="You are a sports analytics expert explaining data insights to coaches and athletes. Be conversational, insightful, and avoid technical database terminology.",
                max_tokens=300,
                temperature=0.3
            )
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating LLM explanation: {e}")
            return None
    
    def _explain_error(self, query_result: Dict[str, Any]) -> str:
        """Explain what went wrong with the query."""
        
        error_type = query_result.get("error_type", "unknown")
        error_message = query_result.get("error", "Unknown error occurred")
        
        if error_type == "timeout":
            return "The query took too long to execute. Try simplifying your question or being more specific."
        elif error_type == "database_error":
            return f"Database error occurred: {error_message}. The query might be malformed or reference non-existent data."
        else:
            return f"An error occurred while processing your question: {error_message}"
    
    def _get_error_suggestions(self, query_result: Dict[str, Any]) -> List[str]:
        """Provide suggestions for fixing errors."""
        
        suggestions = []
        error_type = query_result.get("error_type", "unknown")
        
        if error_type == "timeout":
            suggestions.extend([
                "Try asking for a smaller date range",
                "Be more specific in your question",
                "Ask for summary statistics instead of detailed records"
            ])
        elif error_type == "database_error":
            suggestions.extend([
                "Check if you're asking about data that exists",
                "Try rephrasing your question",
                "Use simpler terms in your question"
            ])
        else:
            suggestions.extend([
                "Try rephrasing your question",
                "Be more specific about what you want to know",
                "Ask about a smaller subset of data"
            ])
        
        return suggestions
    
    def _generate_recommendations(self, question: str, query_result: Dict[str, Any]) -> List[str]:
        """Generate recommendations for further analysis."""
        
        recommendations = []
        data = query_result.get("data", [])
        
        if not data:
            recommendations.append("Try expanding your search criteria or date range")
            return recommendations
        
        # Query-specific recommendations
        question_lower = question.lower()
        
        if "average" in question_lower:
            recommendations.append("Compare with individual records to see the full distribution")
            recommendations.append("Look at trends over time to see if averages are changing")
        
        if "top" in question_lower or "best" in question_lower:
            recommendations.append("Analyze what training factors contribute to top performance")
            recommendations.append("Compare top performers across different time periods")
        
        if len(data) > 10:
            recommendations.append("Consider filtering by specific time periods for deeper insights")
            recommendations.append("Look for patterns by grouping results differently")
        
        if any("velocity" in col.lower() for col in query_result.get("columns", [])):
            recommendations.append("Correlate velocity data with training intensity and recovery")
            recommendations.append("Analyze velocity patterns across different activities")
        
        recommendations.append("Export this data for further analysis in your preferred tools")
        
        return recommendations[:4]  # Limit to top 4 recommendations


# Convenience function
async def explain_query_results(
    question: str, 
    query_result: Dict[str, Any],
    include_llm_explanation: bool = True
) -> Dict[str, Any]:
    """Generate comprehensive explanation for query results."""
    
    explainer = ResponseExplainer()
    return await explainer.explain_results(question, query_result, include_llm_explanation)