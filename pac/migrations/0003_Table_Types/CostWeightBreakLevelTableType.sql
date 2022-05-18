IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'CostWeightBreakLevelTableType')
BEGIN
    CREATE TYPE [dbo].[CostWeightBreakLevelTableType] AS TABLE
(
        [ServiceOfferingName] [nvarchar](50) NOT NULL,
        [WeightBreakLevelName] NVARCHAR (50) NOT NULL,
        [WeightBreakLowerBound] INT NOT NULL,
        INDEX IX NONCLUSTERED([ServiceOfferingName], [WeightBreakLowerBound])
)
END