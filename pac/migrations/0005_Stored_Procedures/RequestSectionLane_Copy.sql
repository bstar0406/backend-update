CREATE OR ALTER PROCEDURE [dbo].[RequestSectionLane_Copy]
	@RequestSectionLaneIDs NVARCHAR(MAX),
	@SourceRequestSectionID BIGINT,
	@DestinationRequestSectionID BIGINT,
	@OrigPointTypeName NVARCHAR(50),
	@OrigPointID BIGINT,
	@DestPointTypeName NVARCHAR(50),
	@DestPointID BIGINT,
	@LaneStatusName NVARCHAR(50),
	@IsMove BIT,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL

AS

SET NOCOUNT ON;

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Duplicating lanes.';

BEGIN TRAN

	DECLARE @RequestSectionLanes IDTableType;
	INSERT INTO @RequestSectionLanes
	(
		ID
	)
	SELECT [value]
	FROM OPENJSON(@RequestSectionLaneIDs)

	DECLARE @FilterCount INT;
	SELECT @FilterCount = COUNT(*) FROM @RequestSectionLanes;

	DECLARE @Cost NVARCHAR(MAX) = dbo.GetRequestSectionLaneDefaultCost(@DestinationRequestSectionID);
	
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
	SELECT 1,
		1,
		@DestinationRequestSectionID,
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
		@Cost,
		[RequestSectionLaneID],
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
	FROM dbo.RequestSectionLane RSL
	WHERE RSL.RequestSectionID = @SourceRequestSectionID
	AND (
		( (@LaneStatusName = 'None') OR (@LaneStatusName = 'New' AND [IsPublished] = 0) OR (@LaneStatusName = 'Changed' AND [IsEdited] = 1) OR (@LaneStatusName = 'Duplicated' AND [IsDuplicate] = 1) OR (@LaneStatusName = 'DoNotMeetCommitment' AND [DoNotMeetCommitment] = 1) )
		AND ( (@OrigPointTypeName = 'None') OR
			(@OrigPointTypeName = 'Country' AND OriginCountryID = @OrigPointID) OR (@OrigPointTypeName = 'Region' AND OriginRegionID = @OrigPointID)
			OR
			(@OrigPointTypeName = 'Province' AND OriginProvinceID = @OrigPointID) OR (@OrigPointTypeName = 'Terminal' AND OriginTerminalID = @OrigPointID)
			OR 
			(@OrigPointTypeName = 'Basing Point' AND OriginBasingPointID = @OrigPointID) OR (@OrigPointTypeName = 'Service Point' AND OriginServicePointID = @OrigPointID)
			OR
			(@OrigPointTypeName = 'Postal Code' AND OriginPostalCodeID = @OrigPointID) OR (@OrigPointTypeName = 'Point Type' AND OriginPointTypeID = @OrigPointID)
			)
		AND ( (@DestPointTypeName = 'None') OR
			(@DestPointTypeName = 'Country' AND DestinationCountryID = @DestPointID) OR (@DestPointTypeName = 'Region' AND DestinationRegionID = @DestPointID)
			OR
			(@DestPointTypeName = 'Province' AND DestinationProvinceID = @DestPointID) OR (@DestPointTypeName = 'Terminal' AND DestinationTerminalID = @DestPointID)
			OR 
			(@DestPointTypeName = 'Basing Point' AND DestinationBasingPointID = @DestPointID) OR (@DestPointTypeName = 'Service Point' AND DestinationServicePointID = @DestPointID)
			OR
			(@DestPointTypeName = 'Postal Code' AND DestinationPostalCodeID = @DestPointID) OR (@DestPointTypeName = 'Point Type' AND DestinationPointTypeID = @DestPointID)
			)
		)
	AND ((@FilterCount = 0) OR (@FilterCount > 0 AND RequestSectionLaneID IN (SELECT ID FROM @RequestSectionLanes)))

	DECLARE @RequestLaneID BIGINT = (SELECT RequestLaneID FROM dbo.RequestSection WHERE RequestSectionID = @SourceRequestSectionID)

	EXEC dbo.RequestSectionLane_Insert_Bulk @RequestSectionLaneTableType, @RequestLaneID

	IF @IsMove = 1
	BEGIN
		Update dbo.RequestSectionLane
		SET IsActive = 0
		WHERE dbo.RequestSectionLane.RequestSectionLaneID IN (SELECT RequestSectionLaneID FROM @RequestSectionLaneTableType)

		EXEC dbo.RequestLane_Count @RequestLaneID
	END

COMMIT TRAN
RETURN 1

