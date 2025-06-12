"""Base extractor classes for ETL pipeline."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.etl.client import CatapultAPIClient
import logging

logger = logging.getLogger(__name__)


class BaseExtractor(ABC):
    """Abstract base class for data extractors."""
    
    def __init__(self, client: CatapultAPIClient):
        self.client = client
    
    @abstractmethod
    async def extract(self, **kwargs) -> List[Dict[str, Any]]:
        """Extract data from the source."""
        pass
    
    def validate_response(self, response: Any, expected_type: type = list) -> bool:
        """Validate API response format."""
        if response is None:
            logger.warning("Received None response from API")
            return False
        
        if not isinstance(response, expected_type):
            logger.warning(f"Expected {expected_type}, got {type(response)}")
            return False
        
        return True


class BatchExtractor:
    """Utility for extracting data in batches with rate limiting."""
    
    def __init__(self, batch_size: int = 50, delay_seconds: float = 0.1):
        self.batch_size = batch_size
        self.delay_seconds = delay_seconds
    
    async def extract_in_batches(self, extractor: BaseExtractor, items: List[Any], **kwargs) -> List[Dict[str, Any]]:
        """Extract data in batches with delays to respect rate limits."""
        import asyncio
        
        all_data = []
        
        for i in range(0, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]
            
            batch_tasks = []
            for item in batch:
                # Create extraction task for each item
                task = extractor.extract(item=item, **kwargs)
                batch_tasks.append(task)
            
            # Execute batch concurrently
            try:
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                for result in batch_results:
                    if isinstance(result, Exception):
                        logger.error(f"Extraction error: {result}")
                        continue
                    
                    if isinstance(result, list):
                        all_data.extend(result)
                    else:
                        all_data.append(result)
                
                # Rate limiting delay
                if self.delay_seconds > 0:
                    await asyncio.sleep(self.delay_seconds)
                
                logger.debug(f"Processed batch {i//self.batch_size + 1}, extracted {len(batch_results)} items")
                
            except Exception as e:
                logger.error(f"Error processing batch {i//self.batch_size + 1}: {e}")
                continue
        
        return all_data