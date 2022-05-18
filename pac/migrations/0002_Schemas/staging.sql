IF NOT EXISTS (
SELECT schema_name
FROM information_schema.schemata
WHERE   schema_name = 'staging' )

BEGIN
    EXEC sp_executesql N'CREATE SCHEMA staging'
END

