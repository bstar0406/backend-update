IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'CountryTableType')
BEGIN
CREATE TYPE [dbo].[CountryTableType] AS TABLE
(
	[CountryName] [nvarchar](50) NOT NULL,
	[CountryCode] [nvarchar](2) NOT NULL,
	INDEX IX NONCLUSTERED(CountryCode)
)
END