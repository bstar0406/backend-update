IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'LaneTableType')
BEGIN
CREATE TYPE [dbo].[LaneTableType] AS TABLE
(
	[ServiceOfferingName] [nvarchar](50) NOT NULL,
	[OriginTerminalCode]    NVARCHAR (3)  NOT NULL,
	[DestinationTerminalCode]    NVARCHAR (3) NOT NULL,
	[SubServiceLevelCode]  NVARCHAR (2) NOT NULL,
	[IsHeadhaul] BIT NOT NULL,
    INDEX IX NONCLUSTERED(ServiceOfferingName, OriginTerminalCode, DestinationTerminalCode)
)
END