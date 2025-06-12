"""Base transformer classes for ETL pipeline."""

import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseTransformer(ABC):
    """Abstract base class for data transformers."""
    
    @abstractmethod
    def transform(self, raw_data: Any) -> List[Dict[str, Any]]:
        """Transform raw data into database-ready format."""
        pass
    
    def safe_get(self, data: Dict[str, Any], key: str, default: Any = None) -> Any:
        """Safely get value from dictionary."""
        return data.get(key, default)
    
    def transform_timestamp(self, timestamp: int) -> Optional[datetime]:
        """Convert Unix timestamp to datetime object."""
        try:
            if timestamp:
                return datetime.fromtimestamp(timestamp)
        except (ValueError, TypeError, OverflowError) as e:
            logger.warning(f"Invalid timestamp {timestamp}: {e}")
        return None
    
    def safe_json_dumps(self, data: Any) -> str:
        """Safely serialize data to JSON string."""
        try:
            return json.dumps(data) if data is not None else json.dumps([])
        except (TypeError, ValueError) as e:
            logger.warning(f"JSON serialization failed: {e}")
            return json.dumps([])
    
    def safe_bool(self, value: Any) -> Optional[bool]:
        """Safely convert value to boolean."""
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return bool(value)
    
    def safe_int(self, value: Any) -> Optional[int]:
        """Safely convert value to integer."""
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    
    def safe_float(self, value: Any) -> Optional[float]:
        """Safely convert value to float."""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def validate_required_fields(self, data: Dict[str, Any], required_fields: List[str]) -> bool:
        """Validate that required fields are present and not None."""
        for field in required_fields:
            if field not in data or data[field] is None:
                logger.warning(f"Missing required field: {field}")
                return False
        return True


class BatchTransformer:
    """Utility for processing data in batches."""
    
    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size
    
    def process_in_batches(self, data: List[Any], transformer: BaseTransformer) -> List[List[Dict[str, Any]]]:
        """Process data in batches using the given transformer."""
        batches = []
        for i in range(0, len(data), self.batch_size):
            batch = data[i:i + self.batch_size]
            transformed_batch = []
            
            for item in batch:
                try:
                    transformed_items = transformer.transform(item)
                    transformed_batch.extend(transformed_items)
                except Exception as e:
                    logger.error(f"Error transforming item: {e}")
                    continue
            
            if transformed_batch:
                batches.append(transformed_batch)
        
        return batches