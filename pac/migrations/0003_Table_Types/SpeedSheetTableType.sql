IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'SpeedSheetTableType')
BEGIN
CREATE TYPE [dbo].[SpeedSheetTableType] AS TABLE
(
	[ServiceOfferingName] [nvarchar](50) NOT NULL,
    [Margin]             NUMERIC (19, 6) NOT NULL,
    [MaxDensity]         NUMERIC (19, 6) NOT NULL,
    [MinDensity]         NUMERIC (19, 6) NOT NULL,
	INDEX IX NONCLUSTERED(ServiceOfferingName, Margin)
)
END