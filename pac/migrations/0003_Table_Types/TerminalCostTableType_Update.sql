IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'TerminalCostTableType_Update')
BEGIN
CREATE TYPE [dbo].[TerminalCostTableType_Update] AS TABLE
(
	[TerminalCostID] [BIGINT] NOT NULL,
	[Cost] [NVARCHAR](MAX) NOT NULL,
	[IsIntraRegionMovementEnabled] BIT             NOT NULL,
    [IntraRegionMovementFactor]    NUMERIC (19, 6) NOT NULL,
	INDEX IX NONCLUSTERED([TerminalCostID])
)
END