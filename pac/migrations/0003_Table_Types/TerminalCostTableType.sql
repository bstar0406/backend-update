IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'TerminalCostTableType')
BEGIN
CREATE TYPE [dbo].[TerminalCostTableType] AS TABLE
(
	[ServiceOfferingName] [nvarchar](50) NOT NULL,
	[TerminalCode] [nvarchar](3) NOT NULL,
	[Cost] [nvarchar](MAX) NOT NULL,
	[IsIntraRegionMovementEnabled] [bit] NOT NULL,
	[IntraRegionMovementFactor] [decimal](19,6) NOT NULL,
	INDEX IX NONCLUSTERED(ServiceOfferingName, TerminalCode)
)
END
