IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'LaneCostTableType')
BEGIN
	CREATE TYPE [dbo].[LaneCostTableType] AS TABLE
(
		[ServiceOfferingName] [nvarchar](50) NOT NULL,
		[OriginTerminalCode] [nvarchar](3) NOT NULL,
		[DestinationTerminalCode] [nvarchar](3) NOT NULL,
		[ServiceLevelCode] [nvarchar](2) NOT NULL,
		[IsHeadhaul] [bit] NOT NULL,
		[MinimumCost] [decimal](19,6) NOT NULL,
		[Cost] [nvarchar](MAX) NOT NULL,
		INDEX IX NONCLUSTERED(ServiceOfferingName, OriginTerminalCode, DestinationTerminalCode, ServiceLevelCode)
)
END