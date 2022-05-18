CREATE OR ALTER PROCEDURE [dbo].[RequestSectionLanePricingPoint_Copy]
	@RequestSectionLanePricingPointIDs NVARCHAR(MAX),
	@SourceRequestSectionLaneID BIGINT,
	@DestinationRequestSectionID BIGINT,
	@IsMove BIT,
	@DestinationRequestSectionLaneID BIGINT = NULL,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL

AS

SET NOCOUNT ON;

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Duplicating lanes.';

BEGIN TRAN

	DECLARE @RequestSectionLanePricingPoints IDTableType;
	INSERT INTO @RequestSectionLanePricingPoints
	(
		ID
	)
	SELECT [value]
	FROM OPENJSON(@RequestSectionLanePricingPointIDs)

	DECLARE @FilterCount INT;
	SELECT @FilterCount = COUNT(*) FROM @RequestSectionLanePricingPoints;

	IF @FilterCount = 0
	BEGIN
		INSERT INTO @RequestSectionLanePricingPoints
		(
			ID
		)
		SELECT RequestSectionLanePricingPointID
		FROM dbo.RequestSectionLanePricingPoint 
		WHERE RequestSectionLaneID = @SourceRequestSectionLaneID AND [IsActive] = 1 AND [IsInactiveViewable] = 1
	END

	IF @DestinationRequestSectionLaneID IS NOT NULL AND @DestinationRequestSectionLaneID > 0
	BEGIN
		DECLARE @RequestSectionLanePricingPointTableType RequestSectionLanePricingPointTableType;

		INSERT INTO @RequestSectionLanePricingPointTableType
		(	
			[IsActive],
			[IsInactiveViewable],
			[RequestSectionLaneID],
			[PricingPointNumber],
			[OriginPostalCodeID],
			[OriginPostalCodeName],
			[DestinationPostalCodeID],
			[DestinationPostalCodeName],
			[PricingPointHashCode],
			[Cost],
			[DrRate],
			[FakRate],
			[Profitability],
			[SplitsAll],
			[SplitsAllUsagePercentage],
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
			@DestinationRequestSectionLaneID,
			REPLACE(NEWID(), '-', ''),
			[OriginPostalCodeID],
			[OriginPostalCodeName],
			[DestinationPostalCodeID],
			[DestinationPostalCodeName],
			[PricingPointHashCode],
			'{}',
			[DrRate],
			[FakRate],
			[Profitability],
			[SplitsAll],
			[SplitsAllUsagePercentage],
			[PickupCount],
			[DeliveryCount],
			[DockAdjustment],
			[Margin],
			[Density],
			[PickupCost],
			[DeliveryCost],
			[AccessorialsValue],
			[AccessorialsPercentage]
		FROM dbo.RequestSectionLanePricingPoint RSLPP
		WHERE RequestSectionLanePricingPointID IN (SELECT ID FROM @RequestSectionLanePricingPoints)

		EXEC dbo.RequestSectionLanePricingPoint_Insert_Bulk @RequestSectionLanePricingPointTableType, @UpdatedBy, @Comments

		IF @IsMove = 1
		BEGIN
			Update dbo.RequestSectionLanePricingPoint
			SET IsActive = 0
			WHERE dbo.RequestSectionLanePricingPoint.RequestSectionLanePricingPointID IN (SELECT ID FROM @RequestSectionLanePricingPoints)

			DECLARE @RequestSectionLaneTableTypeID  IDTableType;

			DECLARE @SourcePricingPointsCount INT;
			SELECT @SourcePricingPointsCount = COUNT(*) FROM dbo.RequestSectionLanePricingPoint WHERE RequestSectionLaneID = @SourceRequestSectionLaneID AND [IsActive] = 1 AND [IsInactiveViewable] = 1

			IF @SourcePricingPointsCount = 0
			BEGIN
				Update dbo.RequestSectionLane
				SET IsLaneGroup = 0
				WHERE dbo.RequestSectionLane.RequestSectionLaneID = @SourceRequestSectionLaneID

				INSERT INTO @RequestSectionLaneTableTypeID (ID) SELECT @SourceRequestSectionLaneID
			END

			DECLARE @DestinationIsLaneGroup BIT;
			SELECT @DestinationIsLaneGroup = IsLaneGroup FROM dbo.RequestSectionLane WHERE RequestSectionLaneID = @DestinationRequestSectionLaneID

			IF @DestinationIsLaneGroup = 0
			BEGIN
				Update dbo.RequestSectionLane
				SET IsLaneGroup = 1
				WHERE dbo.RequestSectionLane.RequestSectionLaneID = @DestinationRequestSectionLaneID

				INSERT INTO @RequestSectionLaneTableTypeID (ID) SELECT @DestinationRequestSectionLaneID
			END

			DECLARE @Count INT;
			SELECT @Count = COUNT(*) FROM @RequestSectionLaneTableTypeID

			IF @Count > 0
			BEGIN
				EXEC dbo.RequestSectionLane_History_Update @RequestSectionLaneTableTypeID, @UpdatedBy, @Comments
			END
			ELSE
			BEGIN
				EXEC dbo.RequestSectionLanePricingPoint_History_Update @RequestSectionLanePricingPoints, @UpdatedBy, @Comments
			END
		END
	END
	--ELSE
	--BEGIN
		--DECLARE @RequestSectionLaneTableType RequestSectionLaneTableType;

		--INSERT INTO @RequestSectionLaneTableType
		--(
		--	[IsActive],
		--	[IsInactiveViewable],
		--	[RequestSectionID],
		--	[LaneNumber],
		--	[IsPublished],
		--	[IsEdited],
		--	[IsDuplicate],
		--	[IsBetween],
		--	[IsLaneGroup],
		--	[OriginProvinceID],
		--	[OriginProvinceCode],
		--	[OriginRegionID],
		--	[OriginRegionCode],
		--	[OriginCountryID],
		--	[OriginCountryCode],
		--	[OriginTerminalID],
		--	[OriginTerminalCode],
		--	[OriginZoneID],
		--	[OriginZoneName],
		--	[OriginBasingPointID],
		--	[OriginBasingPointName],
		--	[OriginServicePointID],
		--	[OriginServicePointName],
		--	[OriginPostalCodeID],
		--	[OriginPostalCodeName],
		--	[OriginPointTypeID],
		--	[OriginPointTypeName],
		--	[OriginCode],
		--	[DestinationProvinceID],
		--	[DestinationProvinceCode],
		--	[DestinationRegionID],
		--	[DestinationRegionCode],
		--	[DestinationCountryID],
		--	[DestinationCountryCode],
		--	[DestinationTerminalID],
		--	[DestinationTerminalCode],
		--	[DestinationZoneID],
		--	[DestinationZoneName],
		--	[DestinationBasingPointID],
		--	[DestinationBasingPointName],
		--	[DestinationServicePointID],
		--	[DestinationServicePointName],
		--	[DestinationPostalCodeID],
		--	[DestinationPostalCodeName],
		--	[DestinationPointTypeID],
		--	[DestinationPointTypeName],
		--	[DestinationCode],
		--	[LaneHashCode],
		--	[BasingPointHashCode],
		--	[Cost],
		--	[RequestSectionLaneID]
		--)
		--SELECT 1,
		--	1,
		--	@DestinationRequestSectionID,
		--	REPLACE(NEWID(), '-', ''),
		--	0,
		--	0,
		--	0,
		--	0,
		--	0,
		--	[OriginProvinceID],
		--	[OriginProvinceCode],
		--	[OriginRegionID],
		--	[OriginRegionCode],
		--	[OriginCountryID],
		--	[OriginCountryCode],
		--	[OriginTerminalID],
		--	[OriginTerminalCode],
		--	[OriginZoneID],
		--	[OriginZoneName],
		--	[OriginBasingPointID],
		--	[OriginBasingPointName],
		--	[OriginServicePointID],
		--	[OriginServicePointName],
		--	[OriginPostalCodeID],
		--	[OriginPostalCodeName],
		--	[OriginPointTypeID],
		--	[OriginPointTypeName],
		--	[OriginCode],
		--	[DestinationProvinceID],
		--	[DestinationProvinceCode],
		--	[DestinationRegionID],
		--	[DestinationRegionCode],
		--	[DestinationCountryID],
		--	[DestinationCountryCode],
		--	[DestinationTerminalID],
		--	[DestinationTerminalCode],
		--	[DestinationZoneID],
		--	[DestinationZoneName],
		--	[DestinationBasingPointID],
		--	[DestinationBasingPointName],
		--	[DestinationServicePointID],
		--	[DestinationServicePointName],
		--	[DestinationPostalCodeID],
		--	[DestinationPostalCodeName],
		--	[DestinationPointTypeID],
		--	[DestinationPointTypeName],
		--	[DestinationCode],
		--	[LaneHashCode],
		--	[BasingPointHashCode],
		--	@Cost,
		--	[RequestSectionLaneID]
		--FROM dbo.RequestSectionLane RSL

		--IF @IsMove = 1
		--BEGIN
		--	Update dbo.RequestSectionLane
		--	SET IsActive = 0
		--	WHERE dbo.RequestSectionLane.RequestSectionLaneID IN (SELECT RequestSectionLaneID FROM @RequestSectionLaneTableType)

		--	EXEC dbo.RequestLane_Count @RequestLaneID
		--END
	--END

COMMIT TRAN
RETURN 1

