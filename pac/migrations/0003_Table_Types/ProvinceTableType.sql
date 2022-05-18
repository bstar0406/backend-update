IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'ProvinceTableType')
BEGIN
CREATE TYPE [dbo].[ProvinceTableType] AS TABLE
(
	[ProvinceName] [nvarchar](50) NOT NULL,
	[ProvinceCode] [nvarchar](2) NOT NULL,
	[CountryCode] [nvarchar](2) NOT NULL,
	[RegionCode] [nvarchar](4) NOT NULL,
	INDEX IX NONCLUSTERED(CountryCode ASC, ProvinceCode ASC, RegionCode ASC)
)
END