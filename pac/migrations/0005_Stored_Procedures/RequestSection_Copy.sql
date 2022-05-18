CREATE OR ALTER PROCEDURE [dbo].[RequestSection_Copy]
	@RequestSectionTableType_Pair     RequestSectionTableType_Pair READONLY,
	@RequestID BIGINT,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL

AS

SET NOCOUNT ON;

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Duplicating lanes.';

BEGIN TRAN

	DECLARE @RequestSectionLaneCost TABLE
	(
		[RequestSectionID] BIGINT NOT NULL,
		[Cost] NVARCHAR(MAX) NOT NULL
	)

	INSERT INTO @RequestSectionLaneCost
	(
		[RequestSectionID],
		[Cost]
	)
	SELECT RS.[SourceRequestSectionID],
		dbo.GetRequestSectionLaneDefaultCost(RS.[DestinationRequestSectionID])
	FROM @RequestSectionTableType_Pair RS 
	
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
		[RequestSectionLaneID],
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
	SELECT [IsActive],
		[IsInactiveViewable],
		RS.[DestinationRequestSectionID],
		REPLACE(NEWID(), '-', ''),
		0,
		0,
		0,
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
		RSLC.Cost,
		[RequestSectionLaneID],
		0,
		RSLC.Cost,
		RSLC.Cost,
		RSLC.Cost,
		RSLC.Cost,
		RSLC.Cost,
		RSLC.Cost,
		RSLC.Cost,
		NULL,
		NULL,
		NULL,
		RSLC.Cost,
		RSLC.Cost,
		RSLC.Cost,
		RSLC.Cost,
		RSLC.Cost,
		RSLC.Cost
	FROM dbo.RequestSectionLane RSL
	INNER JOIN @RequestSectionTableType_Pair RS ON RSL.RequestSectionID = RS.[SourceRequestSectionID]
	INNER JOIN @RequestSectionLaneCost RSLC ON RS.[SourceRequestSectionID] = RSLC.RequestSectionID
	WHERE RSL.IsActive = 1 AND RSL.IsInactiveViewable = 1

	DECLARE @RequestLaneID BIGINT;
	SELECT @RequestLaneID = RequestLaneID FROM dbo.Request WHERE RequestID = @RequestID
	EXEC dbo.RequestSectionLane_Insert_Bulk @RequestSectionLaneTableType, @RequestLaneID

COMMIT TRAN
RETURN 1

