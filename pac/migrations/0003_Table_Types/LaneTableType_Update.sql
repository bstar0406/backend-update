IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'LaneTableType_Update')
BEGIN
CREATE TYPE [dbo].[LaneTableType_Update] AS TABLE
(
	[LaneID] [bigint] NOT NULL,
	[IsHeadhaul] [bit] NOT NULL,
	[IsActive]           BIT           NOT NULL,
    [IsInactiveViewable] BIT           NOT NULL,
	INDEX IX NONCLUSTERED([LaneID])
)
END