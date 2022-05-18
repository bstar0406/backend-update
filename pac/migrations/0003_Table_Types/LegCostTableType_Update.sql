IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'LegCostTableType_Update')
BEGIN
CREATE TYPE [dbo].[LegCostTableType_Update] AS TABLE
(
	[LegCostID] [bigint] NOT NULL,
	[Cost] [nvarchar](MAX) NOT NULL,
	INDEX IX NONCLUSTERED([LegCostID])
)
END