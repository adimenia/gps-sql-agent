-- Add unique constraints to prevent duplicates
-- This script adds composite unique constraints based on natural business keys

-- 1. Add unique constraint for efforts table
-- Natural key: activity_id + athlete_id + start_time + end_time + effort_type + band
-- Note: PostgreSQL unique constraints handle NULLs differently, so we create a partial unique index
CREATE UNIQUE INDEX IF NOT EXISTS efforts_unique_natural_key 
ON efforts (activity_id, athlete_id, start_time, end_time, effort_type, band);

-- 2. Add unique constraint for events table  
-- Natural key: activity_id + athlete_id + start_time + end_time + device_id
CREATE UNIQUE INDEX IF NOT EXISTS events_unique_natural_key 
ON events (activity_id, athlete_id, start_time, end_time, device_id);

-- 3. Verify indexes were added successfully
SELECT indexname, tablename, indexdef 
FROM pg_indexes 
WHERE indexname IN ('efforts_unique_natural_key', 'events_unique_natural_key');