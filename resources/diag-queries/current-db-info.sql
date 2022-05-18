SELECT *
-- SELECT name, is_read_committed_snapshot_on
FROM sys.databases
WHERE name = DB_NAME();

