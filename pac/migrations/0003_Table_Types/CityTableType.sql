IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'CityTableType')
BEGIN
CREATE TYPE [dbo].[CityTableType] AS TABLE
(
	[CityName] [nvarchar](50) NOT NULL,
	[ProvinceCode] [nvarchar](2) NOT NULL,
	[CountryCode] [nvarchar](2) NOT NULL,
	INDEX IX NONCLUSTERED(CountryCode, ProvinceCode, CityName)
)
END