IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'CostWeightBreakLevelTableType_ID')
BEGIN
CREATE TYPE [dbo].[CostWeightBreakLevelTableType_ID] AS TABLE
(
	[WeightBreakLevelID] BIGINT NOT NULL,
	[ServiceOfferingID] BIGINT NOT NULL,
	INDEX IX NONCLUSTERED([ServiceOfferingID], [WeightBreakLevelID])
)
END