IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'RequestSectionLanePointTableType')
BEGIN
CREATE TYPE [dbo].[RequestSectionLanePointTableType] AS TABLE
(
	[ProvinceID] BIGINT NULL,
	[ProvinceCode] NVARCHAR(2) NULL,
	[RegionID] BIGINT NULL,
	[RegionCode] NVARCHAR(4) NULL,
	[CountryID] BIGINT NULL,
	[CountryCode] NVARCHAR(2) NULL,
	[TerminalID] BIGINT NULL,
	[TerminalCode] NVARCHAR(3) NULL,
	[ZoneID] BIGINT NULL,
	[ZoneName] NVARCHAR(50) NULL,
	[BasingPointID] BIGINT NULL,
	[BasingPointName] NVARCHAR(50) NULL,
	[ServicePointID] BIGINT NULL,
	[ServicePointName] NVARCHAR(50) NULL,
	[PostalCodeID] BIGINT NULL,
	[PostalCodeName] NVARCHAR(10) NULL,
	[PointCode] NVARCHAR(50) NULL
)
END