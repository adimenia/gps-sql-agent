"""Base loader classes for ETL pipeline."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)


class BaseLoader(ABC):
    """Abstract base class for data loaders."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    @abstractmethod
    def load(self, data: List[Dict[str, Any]]) -> int:
        """Load data into database. Returns number of records processed."""
        pass
    
    def bulk_insert_on_conflict_ignore(self, table, data: List[Dict[str, Any]]) -> int:
        """Perform bulk insert with ON CONFLICT DO NOTHING."""
        if not data:
            return 0
        
        try:
            # Check count before insertion
            count_before = self.db.execute(text(f"SELECT COUNT(*) FROM {table.name}")).scalar()
            logger.info(f"🔍 Before insert: {table.name} has {count_before} records")
            
            # Use PostgreSQL's INSERT ... ON CONFLICT DO NOTHING
            stmt = insert(table).values(data)
            stmt = stmt.on_conflict_do_nothing()
            
            result = self.db.execute(stmt)
            self.db.commit()
            
            # Check count after insertion to see actual inserts
            count_after = self.db.execute(text(f"SELECT COUNT(*) FROM {table.name}")).scalar()
            actual_inserted = count_after - count_before
            
            logger.info(f"✅ Successfully inserted {actual_inserted} new records into {table.name} (attempted: {len(data)}, total now: {count_after})")
            
            return actual_inserted
            
        except Exception as e:
            logger.error(f"❌ Error inserting data into {table.name}: {e}")
            self.db.rollback()
            return 0
    
    def bulk_upsert(self, table, data: List[Dict[str, Any]], conflict_columns: List[str], update_columns: List[str] = None) -> int:
        """Perform bulk upsert (INSERT ... ON CONFLICT DO UPDATE)."""
        if not data:
            return 0
        
        try:
            stmt = insert(table).values(data)
            
            # Define what to update on conflict
            if update_columns:
                update_dict = {col: stmt.excluded[col] for col in update_columns}
                stmt = stmt.on_conflict_do_update(
                    index_elements=conflict_columns,
                    set_=update_dict
                )
            else:
                # If no update columns specified, just ignore conflicts
                stmt = stmt.on_conflict_do_nothing(index_elements=conflict_columns)
            
            result = self.db.execute(stmt)
            self.db.commit()
            
            logger.info(f"Upserted {len(data)} records for {table.name}")
            return len(data)
            
        except Exception as e:
            logger.error(f"Error upserting data into {table.name}: {e}")
            self.db.rollback()
            return 0
    
    def execute_raw_sql(self, sql: str, params: Dict[str, Any] = None) -> int:
        """Execute raw SQL query."""
        try:
            result = self.db.execute(text(sql), params or {})
            self.db.commit()
            return result.rowcount
        except Exception as e:
            logger.error(f"Error executing SQL: {e}")
            self.db.rollback()
            return 0
    
    def check_record_exists(self, table, **conditions) -> bool:
        """Check if a record exists with given conditions."""
        try:
            query = self.db.query(table)
            for column, value in conditions.items():
                query = query.filter(getattr(table, column) == value)
            
            return query.first() is not None
        except Exception as e:
            logger.error(f"Error checking record existence: {e}")
            return False


class BatchLoader:
    """Utility for loading data in batches."""
    
    def __init__(self, batch_size: int = 1000):
        self.batch_size = batch_size
    
    def load_in_batches(self, loader: BaseLoader, data: List[Dict[str, Any]]) -> int:
        """Load data in batches using the given loader."""
        total_processed = 0
        
        for i in range(0, len(data), self.batch_size):
            batch = data[i:i + self.batch_size]
            try:
                processed = loader.load(batch)
                total_processed += processed
                logger.debug(f"Processed batch {i//self.batch_size + 1}: {processed} records")
            except Exception as e:
                logger.error(f"Error processing batch {i//self.batch_size + 1}: {e}")
                continue
        
        return total_processed