IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'RequestSectionLanePricingPointTableType_Create')
BEGIN
CREATE TYPE [dbo].[RequestSectionLanePricingPointTableType_Create] AS TABLE
(
	[RequestSectionLaneID] [bigint] NOT NULL,
	[OriginPostalCodeID] [bigint] NULL,
	[DestinationPostalCodeID] [bigint] NULL,
	INDEX IX1 NONCLUSTERED([RequestSectionLaneID] ASC),
	INDEX IX2 NONCLUSTERED([OriginPostalCodeID] ASC),
	INDEX IX3 NONCLUSTERED([DestinationPostalCodeID] ASC)
)
END
