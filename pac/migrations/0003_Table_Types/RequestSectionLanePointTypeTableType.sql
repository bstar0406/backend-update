IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'RequestSectionLanePointTypeTableType')
BEGIN
CREATE TYPE [dbo].[RequestSectionLanePointTypeTableType] AS TABLE
(
	[ServiceOfferingName] [nvarchar](50) NOT NULL,
	[IsDensityPricing] [bit] NOT NULL,
	[RequestSectionLanePointTypeName]        NVARCHAR (50) NOT NULL,
	[LocationHierarchy] [int] NOT NULL,
	[IsGroupType] [bit] NOT NULL,
	[IsPointType] [bit] NOT NULL,
	INDEX IX NONCLUSTERED([ServiceOfferingName], [IsDensityPricing])
)
END