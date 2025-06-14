-- Database purge script for clean development environment
-- This will remove all sports data while preserving table structure

-- Disable foreign key checks temporarily for faster deletion
SET session_replication_role = replica;

-- Delete data in correct order (child tables first to avoid FK violations)
TRUNCATE TABLE efforts RESTART IDENTITY CASCADE;
TRUNCATE TABLE events RESTART IDENTITY CASCADE;
TRUNCATE TABLE periods RESTART IDENTITY CASCADE;
TRUNCATE TABLE athletes RESTART IDENTITY CASCADE;
TRUNCATE TABLE activities RESTART IDENTITY CASCADE;
TRUNCATE TABLE owners RESTART IDENTITY CASCADE;
TRUNCATE TABLE positions RESTART IDENTITY CASCADE;
TRUNCATE TABLE parameters RESTART IDENTITY CASCADE;

-- Re-enable foreign key checks
SET session_replication_role = DEFAULT;

-- Verify all tables are empty
SELECT 
    'activities' as table_name, COUNT(*) as records FROM activities
UNION ALL SELECT 'athletes', COUNT(*) FROM athletes
UNION ALL SELECT 'events', COUNT(*) FROM events  
UNION ALL SELECT 'efforts', COUNT(*) FROM efforts
UNION ALL SELECT 'owners', COUNT(*) FROM owners
UNION ALL SELECT 'positions', COUNT(*) FROM positions
UNION ALL SELECT 'parameters', COUNT(*) FROM parameters
UNION ALL SELECT 'periods', COUNT(*) FROM periods;

-- Show completion message
SELECT 'Database purged successfully - all tables are now empty' as status;