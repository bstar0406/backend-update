IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'LaneCostTableType_Create')
BEGIN
CREATE TYPE [dbo].[LaneCostTableType_Create] AS TABLE
(
	[OriginTerminalID] [bigint] NOT NULL,
	[DestinationTerminalID] [bigint] NOT NULL,
	[SubServiceLevelID] [bigint] NOT NULL,
	[IsHeadhaul] [bit] NOT NULL,
	[MinimumCost] [decimal](19,6) NOT NULL,
	[Cost] [nvarchar](MAX) NOT NULL,
	INDEX IX NONCLUSTERED([OriginTerminalID], [DestinationTerminalID], [SubServiceLevelID])
)
END