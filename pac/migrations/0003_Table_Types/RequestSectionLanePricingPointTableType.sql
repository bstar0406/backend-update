IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'RequestSectionLanePricingPointTableType')
BEGIN
CREATE TYPE [dbo].[RequestSectionLanePricingPointTableType] AS TABLE
(
	[RequestSectionLanePricingPointID] [bigint] NULL,
	[IsActive] [bit] NOT NULL,
	[IsInactiveViewable] [bit] NOT NULL,
	[RequestSectionLaneID] [bigint] NOT NULL,
	[PricingPointNumber] [nvarchar](32) NOT NULL,
	[OriginPostalCodeID] [bigint] NULL,
	[OriginPostalCodeName] [nvarchar](10) NULL,
	[DestinationPostalCodeID] [bigint] NULL,
	[DestinationPostalCodeName] [nvarchar](10) NULL,
	[PricingPointHashCode] [varbinary](8000) NOT NULL,
	[Cost] [nvarchar](MAX) NULL,
	[DrRate] NVARCHAR(MAX) NOT NULL,
	[FakRate] NVARCHAR(MAX) NOT NULL,
	[Profitability] NVARCHAR(MAX) NOT NULL,
	[SplitsAll] NVARCHAR(MAX) NOT NULL,
	[SplitsAllUsagePercentage] DECIMAL(19,6) NOT NULL,
	[PickupCount] INT NULL,
	[DeliveryCount] INT NULL,
	[DockAdjustment] DECIMAL(19,6) NULL,
	[Margin] NVARCHAR(MAX) NOT NULL,
	[Density] NVARCHAR(MAX) NOT NULL,
	[PickupCost] NVARCHAR(MAX) NOT NULL,
	[DeliveryCost] NVARCHAR(MAX) NOT NULL,
	[AccessorialsValue] NVARCHAR(MAX) NOT NULL,
	[AccessorialsPercentage] NVARCHAR(MAX) NOT NULL,
	INDEX IX1 NONCLUSTERED([RequestSectionLaneID] ASC),
	INDEX IX2 NONCLUSTERED([PricingPointNumber] ASC),
	INDEX IX3 NONCLUSTERED([OriginPostalCodeID] ASC),
	INDEX IX4 NONCLUSTERED([DestinationPostalCodeID] ASC),
	INDEX IX5 NONCLUSTERED([PricingPointHashCode] ASC),
	INDEX IX6 NONCLUSTERED([RequestSectionLanePricingPointID] ASC)
)
END




