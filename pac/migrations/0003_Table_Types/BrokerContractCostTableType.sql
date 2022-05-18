IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'BrokerContractCostTableType')
BEGIN
CREATE TYPE [dbo].[BrokerContractCostTableType] AS TABLE
(
	[ServiceOfferingName] [nvarchar](50) NOT NULL,
	[TerminalCode] [nvarchar](3) NOT NULL,
	[ServiceLevelCode] [nvarchar](2) NOT NULL,
	[Cost] [nvarchar](MAX) NOT NULL,
	INDEX IX NONCLUSTERED(ServiceOfferingName, TerminalCode, ServiceLevelCode)
)
END