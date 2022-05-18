IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'RegionTableType')
BEGIN
CREATE TYPE [dbo].[RegionTableType] AS TABLE
(
	[RegionName] [nvarchar](50) NOT NULL,
	[RegionCode] [nvarchar](4) NOT NULL,
	[CountryCode] [nvarchar](2) NOT NULL,
	INDEX IX NONCLUSTERED([CountryCode] ASC, RegionCode ASC)
)
END