IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'CostWeightBreakLevelTableType_Update')
BEGIN
CREATE TYPE [dbo].[CostWeightBreakLevelTableType_Update] AS TABLE
(
	[WeightBreakLevelID] BIGINT NOT NULL,
    [WeightBreakLevelName]  NVARCHAR (50) NOT NULL,
    [WeightBreakLowerBound] INT           NOT NULL,
	[IsActive] BIT						  NOT NULL,
	INDEX IX NONCLUSTERED([WeightBreakLevelID], [WeightBreakLowerBound])
)
END