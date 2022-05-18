IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'TerminalTableType')
BEGIN
CREATE TYPE [dbo].[TerminalTableType] AS TABLE
(
	[TerminalName] [nvarchar](50) NOT NULL,
	[TerminalCode] [nvarchar](3) NOT NULL,
	[CityName] [nvarchar](50) NOT NULL,
	[ProvinceCode] [nvarchar](2) NOT NULL,
	[CountryCode] [nvarchar](2) NOT NULL,
	[RegionCode] [nvarchar](4) NOT NULL,
	INDEX IX NONCLUSTERED(CountryCode, ProvinceCode, CityName, RegionCode, TerminalCode)
)
END