IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'LegCostTableType_Create')
BEGIN
CREATE TYPE [dbo].[LegCostTableType_Create] AS TABLE
(
	[OriginTerminalID] [bigint] NOT NULL,
	[DestinationTerminalID] [bigint] NOT NULL,
	[SubServiceLevelID] [bigint] NOT NULL,
	[ServiceModeID] [bigint] NOT NULL,
	[IsHeadhaul] [bit] NOT NULL,
	[Cost] [nvarchar](MAX) NOT NULL,
	INDEX IX NONCLUSTERED([OriginTerminalID], [DestinationTerminalID], [SubServiceLevelID], [ServiceModeID])
)
END