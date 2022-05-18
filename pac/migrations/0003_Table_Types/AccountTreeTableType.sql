IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'AccountTreeTableType')
BEGIN
CREATE TYPE [dbo].[AccountTreeTableType] AS TABLE
(
    [AccountID]        BIGINT NOT NULL,
	[ParentAccountNumber]        NVARCHAR (50) NULL,
	INDEX IX NONCLUSTERED([AccountID])
)
END