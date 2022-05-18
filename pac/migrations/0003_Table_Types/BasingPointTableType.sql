IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'BasingPointTableType')
BEGIN
CREATE TYPE [dbo].[BasingPointTableType] AS TABLE
(
	[BasingPointName] [nvarchar](50) NOT NULL,
	[ProvinceCode] [nvarchar](2) NOT NULL,
	[CountryCode] [nvarchar](2) NOT NULL,
	INDEX IX NONCLUSTERED([BasingPointName])
)
END