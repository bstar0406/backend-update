IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'LaneCostTableType_Update')
BEGIN
CREATE TYPE [dbo].[LaneCostTableType_Update] AS TABLE
(
	[LaneCostID] [bigint] NOT NULL,
	[MinimumCost] [decimal](19,6) NOT NULL,
	[Cost] [nvarchar](MAX) NOT NULL,
	INDEX IX NONCLUSTERED([LaneCostID])
)
END