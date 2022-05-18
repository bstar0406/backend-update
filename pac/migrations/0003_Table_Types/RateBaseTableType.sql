IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'RateBaseTableType')
BEGIN
CREATE TYPE [dbo].[RateBaseTableType] AS TABLE
(
    [RateBaseName]        NVARCHAR (50) NOT NULL,
	INDEX IX NONCLUSTERED([RateBaseName])
)
END