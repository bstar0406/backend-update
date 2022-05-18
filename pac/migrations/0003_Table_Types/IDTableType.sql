IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'IDTableType')
BEGIN
CREATE TYPE [dbo].[IDTableType] AS TABLE
(
	[ID]               BIGINT        NOT NULL,
	INDEX IX NONCLUSTERED([ID])
)
END