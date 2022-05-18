IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'BrokerContractCostWeightBreakLevelTableType')
BEGIN
CREATE TYPE [dbo].[BrokerContractCostWeightBreakLevelTableType] AS TABLE
(
    [WeightBreakLevelName]  NVARCHAR (50) NOT NULL,
    [WeightBreakLowerBound] INT           NOT NULL,
	INDEX IX NONCLUSTERED([WeightBreakLevelName], [WeightBreakLowerBound])
)
END