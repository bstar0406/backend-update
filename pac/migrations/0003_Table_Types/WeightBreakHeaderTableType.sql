IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'WeightBreakHeaderTableType')
BEGIN
CREATE TYPE [dbo].[WeightBreakHeaderTableType] AS TABLE
(
	[ServiceOfferingName] [nvarchar](50) NOT NULL,
    [WeightBreakHeaderName] NVARCHAR (50)   NOT NULL,
    [UnitFactor]            NUMERIC (19, 6) NOT NULL,
    [MaximumValue]          NUMERIC (19, 6) NOT NULL,
    [AsRating]       BIT             NOT NULL,
	[HasMin]       BIT             NOT NULL,
	[HasMax]       BIT             NOT NULL,
    [BaseRate]              BIT             NOT NULL,
    [Levels]                NVARCHAR (MAX)  NOT NULL,
    [ServiceLevelCode]   NVARCHAR (2)  NOT NULL,
    [UnitSymbol]         NVARCHAR (50) NOT NULL,
	INDEX IX NONCLUSTERED([WeightBreakHeaderName], [ServiceLevelCode], [UnitSymbol])
)
END