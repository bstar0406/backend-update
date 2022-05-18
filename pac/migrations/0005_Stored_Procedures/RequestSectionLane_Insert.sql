CREATE OR ALTER PROCEDURE [dbo].[RequestSectionLane_Insert]
	@RequestSectionID BIGINT,
	@OriginGroupTypeID BIGINT,
	@OriginGroupID BIGINT,
	@OriginPointTypeID BIGINT,
	@OriginPointID BIGINT,
	@DestinationGroupTypeID BIGINT,
	@DestinationGroupID BIGINT,
	@DestinationPointTypeID BIGINT,
	@DestinationPointID BIGINT,
	@IsBetween BIT,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL
AS

SET NOCOUNT ON;

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

BEGIN TRAN

DECLARE @OriginPointTypeName NVARCHAR(50);
DECLARE @DestinationPointTypeName NVARCHAR(50);

SELECT @OriginPointTypeName = RequestSectionLanePointTypeName FROM dbo.RequestSectionLanePointType WHERE RequestSectionLanePointTypeID = @OriginPointTypeID;
SELECT @DestinationPointTypeName = RequestSectionLanePointTypeName FROM dbo.RequestSectionLanePointType WHERE RequestSectionLanePointTypeID = @DestinationPointTypeID;


DECLARE @Origin RequestSectionLanePointTableType;
DECLARE @Destination RequestSectionLanePointTableType;

DECLARE @Cost NVARCHAR(MAX);
SELECT @Cost = dbo.GetRequestSectionLaneDefaultCost(@RequestSectionID);

INSERT INTO @Origin
(
	[ProvinceID],
	[ProvinceCode],
	[RegionID],
	[RegionCode],
	[CountryID],
	[CountryCode],
	[TerminalID],
	[TerminalCode],
	[ZoneID],
	[ZoneName],
	[BasingPointID],
	[BasingPointName],
	[ServicePointID],
	[ServicePointName],
	[PostalCodeID],
	[PostalCodeName],
	[PointCode]
)
SELECT [ProvinceID],
	[ProvinceCode],
	[RegionID],
	[RegionCode],
	[CountryID],
	[CountryCode],
	[TerminalID],
	[TerminalCode],
	[ZoneID],
	[ZoneName],
	[BasingPointID],
	[BasingPointName],
	[ServicePointID],
	[ServicePointName],
	[PostalCodeID],
	[PostalCodeName],
	[PointCode]
FROM dbo.GetRequestSectionLanePoints(@OriginGroupTypeID, @OriginGroupID, @OriginPointTypeID, @OriginPointID)

INSERT INTO @Destination
(
	[ProvinceID],
	[ProvinceCode],
	[RegionID],
	[RegionCode],
	[CountryID],
	[CountryCode],
	[TerminalID],
	[TerminalCode],
	[ZoneID],
	[ZoneName],
	[BasingPointID],
	[BasingPointName],
	[ServicePointID],
	[ServicePointName],
	[PostalCodeID],
	[PostalCodeName],
	[PointCode]
)
SELECT [ProvinceID],
	[ProvinceCode],
	[RegionID],
	[RegionCode],
	[CountryID],
	[CountryCode],
	[TerminalID],
	[TerminalCode],
	[ZoneID],
	[ZoneName],
	[BasingPointID],
	[BasingPointName],
	[ServicePointID],
	[ServicePointName],
	[PostalCodeID],
	[PostalCodeName],
	[PointCode]
FROM dbo.GetRequestSectionLanePoints(@DestinationGroupTypeID, @DestinationGroupID, @DestinationPointTypeID, @DestinationPointID)

DECLARE @OriginCount INT, @DestinationCount INT;

SELECT @OriginCount = COUNT(*) FROM @Origin
SELECT @DestinationCount = COUNT(*) FROM @Destination

IF @OriginCount > 0 AND @DestinationCount > 0
BEGIN
	DECLARE @RequestSectionLaneTableType RequestSectionLaneTableType;

	INSERT INTO @RequestSectionLaneTableType
	(
		[IsActive],
		[IsInactiveViewable],
		[RequestSectionID],
		[LaneNumber],
		[IsPublished],
		[IsEdited],
		[IsDuplicate],
		[IsBetween],
		[IsLaneGroup],
		[OriginProvinceID],
		[OriginProvinceCode],
		[OriginRegionID],
		[OriginRegionCode],
		[OriginCountryID],
		[OriginCountryCode],
		[OriginTerminalID],
		[OriginTerminalCode],
		[OriginZoneID],
		[OriginZoneName],
		[OriginBasingPointID],
		[OriginBasingPointName],
		[OriginServicePointID],
		[OriginServicePointName],
		[OriginPostalCodeID],
		[OriginPostalCodeName],
		[OriginPointTypeID],
		[OriginPointTypeName],
		[OriginCode],
		[DestinationProvinceID],
		[DestinationProvinceCode],
		[DestinationRegionID],
		[DestinationRegionCode],
		[DestinationCountryID],
		[DestinationCountryCode],
		[DestinationTerminalID],
		[DestinationTerminalCode],
		[DestinationZoneID],
		[DestinationZoneName],
		[DestinationBasingPointID],
		[DestinationBasingPointName],
		[DestinationServicePointID],
		[DestinationServicePointName],
		[DestinationPostalCodeID],
		[DestinationPostalCodeName],
		[DestinationPointTypeID],
		[DestinationPointTypeName],
		[DestinationCode],
		[LaneHashCode],
		[BasingPointHashCode],
		[Cost],
		[DoNotMeetCommitment],
		[Commitment],
		[CustomerRate],
		[CustomerDiscount],
		[DrRate],
		[PartnerRate],
		[PartnerDiscount],
		[Profitability],
		[PickupCount],
		[DeliveryCount],
		[DockAdjustment],
		[Margin],
		[Density],
		[PickupCost],
		[DeliveryCost],
		[AccessorialsValue],
		[AccessorialsPercentage]
	)
	SELECT 1,
	1,
	@RequestSectionID,
	REPLACE(NEWID(), '-', ''),
	0,
    0,
    0,
    @IsBetween,
	0,
	O.[ProvinceID],
	O.[ProvinceCode],
	O.[RegionID],
	O.[RegionCode],
	O.[CountryID],
	O.[CountryCode],
	O.[TerminalID],
	O.[TerminalCode],
	O.[ZoneID],
	O.[ZoneName],
	O.[BasingPointID],
	O.[BasingPointName],
	O.[ServicePointID],
	O.[ServicePointName],
	O.[PostalCodeID],
	O.[PostalCodeName],
	@OriginPointTypeID,
	@OriginPointTypeName,
	O.[PointCode],
	D.[ProvinceID],
	D.[ProvinceCode],
	D.[RegionID],
	D.[RegionCode],
	D.[CountryID],
	D.[CountryCode],
	D.[TerminalID],
	D.[TerminalCode],
	D.[ZoneID],
	D.[ZoneName],
	D.[BasingPointID],
	D.[BasingPointName],
	D.[ServicePointID],
	D.[ServicePointName],
	D.[PostalCodeID],
	D.[PostalCodeName],
	@DestinationPointTypeID,
	@DestinationPointTypeName,
	D.[PointCode],
    (SELECT HASHBYTES('SHA2_512', (SELECT O.[ProvinceID] AS OProvince, D.[ProvinceID] AS DProvince, O.[RegionID] AS ORegion, D.[RegionID] AS DRegion, O.[CountryID] AS OCountry, D.[CountryID] AS DCountry, O.[TerminalID] AS OTerminal, D.[TerminalID] AS DTerminal, O.[ZoneID] AS OZone, D.[ZoneID] AS DZone, O.[BasingPointID] AS OBasingPoint, D.[BasingPointID] AS DBasingPoint, O.[ServicePointID] AS OServicePoint, D.[ServicePointID] AS DServicePoint, O.[PostalCodeID] AS OPostalCode, D.[PostalCodeID] AS DPostalCode FOR JSON PATH, WITHOUT_ARRAY_WRAPPER))) AS LaneHashCode,
	CASE WHEN O.[BasingPointID] IS NOT NULL AND D.[BasingPointID] IS NOT NULL THEN (SELECT HASHBYTES('SHA2_512', (SELECT O.[BasingPointID] AS OBasingPoint, D.[BasingPointID] AS DBasingPoint FOR JSON PATH, WITHOUT_ARRAY_WRAPPER))) ELSE NULL END AS BasingPointHashCode,
    @Cost,
	0,
	@Cost,
	@Cost,
	@Cost,
	@Cost,
	@Cost,
	@Cost,
	@Cost,
	NULL,
	NULL,
	NULL,
	@Cost,
	@Cost,
	@Cost,
	@Cost,
	@Cost,
	@Cost
	FROM @Origin O, @Destination D

	DECLARE @RequestLaneID BIGINT;
	SELECT @RequestLaneID = RequestLaneID
	FROM dbo.RequestSection WHERE RequestSectionID = @RequestSectionID

	EXEC dbo.RequestSectionLane_Insert_Bulk @RequestSectionLaneTableType, @RequestLaneID

END

COMMIT TRAN
RETURN 1

