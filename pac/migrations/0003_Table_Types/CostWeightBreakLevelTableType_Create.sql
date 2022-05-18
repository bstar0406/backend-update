IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'CostWeightBreakLevelTableType_Create')
BEGIN
CREATE TYPE [dbo].[CostWeightBreakLevelTableType_Create] AS TABLE
(
	[ServiceOfferingID] BIGINT NOT NULL,
    [WeightBreakLevelName]  NVARCHAR (50) NOT NULL,
    [WeightBreakLowerBound] INT           NOT NULL,
	INDEX IX NONCLUSTERED([ServiceOfferingID], [WeightBreakLowerBound])
)
END