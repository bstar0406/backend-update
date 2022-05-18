CREATE OR ALTER PROCEDURE [dbo].[RequestSectionLane_Staging_Update]
	@RequestSectionID BIGINT,
	@ContextID NVARCHAR(32),
	@OrigPointTypeName NVARCHAR(50),
	@OrigPointID BIGINT,
	@DestPointTypeName NVARCHAR(50),
	@DestPointID BIGINT,
	@LaneStatusName NVARCHAR(50),
	@RequestSectionLaneTableType_ID NVARCHAR(MAX) = NULL,
	@IsBetween BIT = NULL,
	@OperationName  CHAR(1) = NULL,
	@Multiplier DECIMAL(19,6) = NULL,
	@RateTable NVARCHAR(50),
	@WeightBreakLowerBound NVARCHAR(MAX) = NULL,
	@MicroSave BIT = NULL,
	@MacroSave BIT = NULL,
	@IsActive BIT = NULL,
	@IsInactiveViewable BIT = NULL
AS

SET NOCOUNT ON;

BEGIN TRAN

DECLARE @RequestLaneID BIGINT;
SELECT @RequestLaneID = RequestLaneID FROM dbo.RequestSection WHERE RequestSectionID = @RequestSectionID;

DECLARE @RequestSectionLaneTableType IDTableType;
INSERT INTO @RequestSectionLaneTableType
(
	ID
)
SELECT [value]
FROM OPENJSON(@RequestSectionLaneTableType_ID)

DECLARE @FilterCount INT;
SELECT @FilterCount = COUNT(*) FROM @RequestSectionLaneTableType;

DECLARE @WeightBreak IDTableType;
INSERT INTO @WeightBreak
(
	ID
)
SELECT [value]
FROM OPENJSON(@WeightBreakLowerBound)

IF NOT EXISTS (SELECT TOP 1 ContextID FROM dbo.RequestSectionLane_Staging WHERE [RequestLaneID] = @RequestLaneID AND ContextID = @ContextID)
BEGIN
	INSERT INTO dbo.RequestSectionLane_Staging
	(	
	[RequestSectionLaneID],
	[RequestSectionID],
	[RequestLaneID],
    [LaneNumber],
	[IsPublished],
	[IsEdited],
	[IsDuplicate],
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
	[NewCost],
	[IsActive],
	[NewIsActive],
    [IsInactiveViewable],
	[NewIsInactiveViewable],
	[IsBetween],
	[NewIsBetween],
	[IsUpdated],
	[ContextID],
	[ContextCreatedOn],
	[DoNotMeetCommitment],
	[NewDoNotMeetCommitment],
	[Commitment],
	[NewCommitment],
	[CustomerRate],
	[NewCustomerRate],
	[CustomerDiscount],
	[NewCustomerDiscount],
	[DrRate],
	[NewDrRate],
	[PartnerRate],
	[NewPartnerRate],
	[PartnerDiscount],
	[NewPartnerDiscount],
	[Profitability],
	[NewProfitability],
	[PickupCount],
	[NewPickupCount],
	[DeliveryCount],
	[NewDeliveryCount],
	[DockAdjustment],
	[NewDockAdjustment],
	[Margin],
	[NewMargin],
	[Density],
	[NewDensity],
	[PickupCost],
	[NewPickupCost],
	[DeliveryCost],
	[NewDeliveryCost],
	[AccessorialsValue],
	[NewAccessorialsValue],
	[AccessorialsPercentage],
	[NewAccessorialsPercentage]
	)
	SELECT 
	[RequestSectionLaneID],
	RSL.[RequestSectionID],
	RS.[RequestLaneID],
    [LaneNumber],
	[IsPublished],
	[IsEdited],
	[IsDuplicate],
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
	RSL.[Cost],
	RSL.[Cost],
	RSL.[IsActive],
	RSL.[IsActive],
    RSL.[IsInactiveViewable],
	RSL.[IsInactiveViewable],
	RSL.[IsBetween],
	RSL.[IsBetween],
	0,
	@ContextID,
	GETUTCDATE(),
	[DoNotMeetCommitment],
	[DoNotMeetCommitment],
	[Commitment],
	[Commitment],
	[CustomerRate],
	[CustomerRate],
	[CustomerDiscount],
	[CustomerDiscount],
	[DrRate],
	[DrRate],
	[PartnerRate],
	[PartnerRate],
	[PartnerDiscount],
	[PartnerDiscount],
	[Profitability],
	[Profitability],
	[PickupCount],
	[PickupCount],
	[DeliveryCount],
	[DeliveryCount],
	[DockAdjustment],
	[DockAdjustment],
	[Margin],
	[Margin],
	[Density],
	[Density],
	[PickupCost],
	[PickupCost],
	[DeliveryCost],
	[DeliveryCost],
	[AccessorialsValue],
	[AccessorialsValue],
	[AccessorialsPercentage],
	[AccessorialsPercentage]
	FROM dbo.RequestSectionLane RSL
	INNER JOIN dbo.RequestSection RS ON RSL.RequestSectionID = RS.RequestSectionID
	WHERE RS.RequestLaneID = @RequestLaneID
END;

IF NOT EXISTS (SELECT TOP 1 ContextID FROM dbo.RequestSectionLanePricingPoint_Staging WHERE [RequestLaneID] = @RequestLaneID AND ContextID = @ContextID)
BEGIN
	INSERT INTO dbo.RequestSectionLanePricingPoint_Staging
	(	
		[IsActive],
		[NewIsActive],
		[IsInactiveViewable],
		[NewIsInactiveViewable],
		[RequestSectionLanePricingPointID],
		[RequestSectionLaneID],
		[RequestLaneID],
		[PricingPointNumber],
		[OriginPostalCodeID],
		[OriginPostalCodeName],
		[DestinationPostalCodeID],
		[DestinationPostalCodeName],
		[PricingPointHashCode],
		[Cost],
		[NewCost],
		[DrRate],
		[NewDrRate],
		[FakRate],
		[NewFakRate],
		[Profitability],
		[NewProfitability],
		[SplitsAll],
		[NewSplitsAll],
		[SplitsAllUsagePercentage],
		[NewSplitsAllUsagePercentage],
		[PickupCount],
		[NewPickupCount],
		[DeliveryCount],
		[NewDeliveryCount],
		[DockAdjustment],
		[NewDockAdjustment],
		[Margin],
		[NewMargin],
		[Density],
		[NewDensity],
		[PickupCost],
		[NewPickupCost],
		[DeliveryCost],
		[NewDeliveryCost],
		[AccessorialsValue],
		[NewAccessorialsValue],
		[AccessorialsPercentage],
		[NewAccessorialsPercentage],
		[IsUpdated],
		[ContextID],
		[ContextCreatedOn]
	)
	SELECT RSLPP.[IsActive],
		RSLPP.[IsActive],
		RSLPP.[IsInactiveViewable],
		RSLPP.[IsInactiveViewable],
		RSLPP.[RequestSectionLanePricingPointID],
		RSLPP.[RequestSectionLaneID],
		@RequestLaneID,
		RSLPP.[PricingPointNumber],
		RSLPP.[OriginPostalCodeID],
		RSLPP.[OriginPostalCodeName],
		RSLPP.[DestinationPostalCodeID],
		RSLPP.[DestinationPostalCodeName],
		RSLPP.[PricingPointHashCode],
		RSLPP.[Cost],
		RSLPP.[Cost],
		RSLPP.[DrRate],
		RSLPP.[DrRate],
		RSLPP.[FakRate],
		RSLPP.[FakRate],
		RSLPP.[Profitability],
		RSLPP.[Profitability],
		RSLPP.[SplitsAll],
		RSLPP.[SplitsAll],
		RSLPP.[SplitsAllUsagePercentage],
		RSLPP.[SplitsAllUsagePercentage],
		RSLPP.[PickupCount],
		RSLPP.[PickupCount],
		RSLPP.[DeliveryCount],
		RSLPP.[DeliveryCount],
		RSLPP.[DockAdjustment],
		RSLPP.[DockAdjustment],
		RSLPP.[Margin],
		RSLPP.[Margin],
		RSLPP.[Density],
		RSLPP.[Density],
		RSLPP.[PickupCost],
		RSLPP.[PickupCost],
		RSLPP.[DeliveryCost],
		RSLPP.[DeliveryCost],
		RSLPP.[AccessorialsValue],
		RSLPP.[AccessorialsValue],
		RSLPP.[AccessorialsPercentage],
		RSLPP.[AccessorialsPercentage],
		0,
		@ContextID,
		GETUTCDATE()
		FROM dbo.RequestSectionLanePricingPoint RSLPP
		INNER JOIN 	dbo.RequestSectionLane RSL ON RSLPP.RequestSectionLaneID = RSL.RequestSectionLaneID
		INNER JOIN dbo.RequestSection RS ON RSL.RequestSectionID = RS.RequestSectionID
		WHERE RS.RequestLaneID = @RequestLaneID
END;


WITH A AS 
(
	SELECT *
	FROM dbo.RequestSectionLane_Staging RSLS
	WHERE RSLS.RequestLaneID = @RequestLaneID AND RSLS.RequestSectionID = @RequestSectionID AND RSLS.ContextID = @ContextID
	AND (
		( (@LaneStatusName = 'None') OR (@LaneStatusName = 'New' AND [IsPublished] = 0) OR (@LaneStatusName = 'Changed' AND [IsEdited] = 1) OR (@LaneStatusName = 'Duplicated' AND [IsDuplicate] = 1) OR (@LaneStatusName = 'DoNotMeetCommitment' AND [DoNotMeetCommitment] = 1))
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
	AND ((@FilterCount = 0) OR (@FilterCount > 0 AND RSLS.RequestSectionLaneID IN (SELECT ID FROM @RequestSectionLaneTableType)))
)

UPDATE dbo.RequestSectionLane_Staging
SET IsUpdated = 1,
	NewIsActive = CASE WHEN @IsActive IS NOT NULL THEN @IsActive ELSE A.NewIsActive END,
	NewIsInactiveViewable = CASE WHEN @IsInactiveViewable IS NOT NULL THEN @IsInactiveViewable ELSE A.NewIsInactiveViewable END,
	NewIsBetween = CASE WHEN @IsBetween IS NOT NULL THEN @IsBetween ELSE A.NewIsBetween END,
	NewCost = CASE WHEN @RateTable IS NOT NULL AND @RateTable = 'cost' AND @OperationName IS NOT NULL AND @Multiplier IS NOT NULL AND @WeightBreakLowerBound IS NOT NULL THEN dbo.RequestSectionLane_Modify_RateTable(A.NewCost, @WeightBreak, @OperationName, @Multiplier) ELSE A.NewCost END,
	NewCommitment = CASE WHEN @RateTable IS NOT NULL AND @RateTable = 'commitment' AND @OperationName IS NOT NULL AND @Multiplier IS NOT NULL AND @WeightBreakLowerBound IS NOT NULL THEN dbo.RequestSectionLane_Modify_RateTable(A.NewCommitment, @WeightBreak, @OperationName, @Multiplier) ELSE A.NewCommitment END,
	NewCustomerRate = CASE WHEN @RateTable IS NOT NULL AND @RateTable = 'customer_rate' AND @OperationName IS NOT NULL AND @Multiplier IS NOT NULL AND @WeightBreakLowerBound IS NOT NULL THEN dbo.RequestSectionLane_Modify_RateTable(A.NewCustomerRate, @WeightBreak, @OperationName, @Multiplier) ELSE A.NewCustomerRate END,
	NewCustomerDiscount = CASE WHEN @RateTable IS NOT NULL AND @RateTable = 'customer_discount' AND @OperationName IS NOT NULL AND @Multiplier IS NOT NULL AND @WeightBreakLowerBound IS NOT NULL THEN dbo.RequestSectionLane_Modify_RateTable(A.NewCustomerDiscount, @WeightBreak, @OperationName, @Multiplier) ELSE A.NewCustomerDiscount END,
	NewDrRate = CASE WHEN @RateTable IS NOT NULL AND @RateTable = 'dr_rate' AND @OperationName IS NOT NULL AND @Multiplier IS NOT NULL AND @WeightBreakLowerBound IS NOT NULL THEN dbo.RequestSectionLane_Modify_RateTable(A.NewDrRate, @WeightBreak, @OperationName, @Multiplier) ELSE A.NewDrRate END,
	NewPartnerRate = CASE WHEN @RateTable IS NOT NULL AND @RateTable = 'partner_rate' AND @OperationName IS NOT NULL AND @Multiplier IS NOT NULL AND @WeightBreakLowerBound IS NOT NULL THEN dbo.RequestSectionLane_Modify_RateTable(A.NewPartnerRate, @WeightBreak, @OperationName, @Multiplier) ELSE A.NewPartnerRate END,
	NewPartnerDiscount = CASE WHEN @RateTable IS NOT NULL AND @RateTable = 'partner_discount' AND @OperationName IS NOT NULL AND @Multiplier IS NOT NULL AND @WeightBreakLowerBound IS NOT NULL THEN dbo.RequestSectionLane_Modify_RateTable(A.NewPartnerDiscount, @WeightBreak, @OperationName, @Multiplier) ELSE A.NewPartnerDiscount END,
	NewProfitability = CASE WHEN @RateTable IS NOT NULL AND @RateTable = 'profitability' AND @OperationName IS NOT NULL AND @Multiplier IS NOT NULL AND @WeightBreakLowerBound IS NOT NULL THEN dbo.RequestSectionLane_Modify_RateTable(A.NewProfitability, @WeightBreak, @OperationName, @Multiplier) ELSE A.NewProfitability END,
	NewMargin = CASE WHEN @RateTable IS NOT NULL AND @RateTable = 'margin' AND @OperationName IS NOT NULL AND @Multiplier IS NOT NULL AND @WeightBreakLowerBound IS NOT NULL THEN dbo.RequestSectionLane_Modify_RateTable(A.NewMargin, @WeightBreak, @OperationName, @Multiplier) ELSE A.NewMargin END,
	NewDensity = CASE WHEN @RateTable IS NOT NULL AND @RateTable = 'density' AND @OperationName IS NOT NULL AND @Multiplier IS NOT NULL AND @WeightBreakLowerBound IS NOT NULL THEN dbo.RequestSectionLane_Modify_RateTable(A.NewDensity, @WeightBreak, @OperationName, @Multiplier) ELSE A.NewDensity END,
	NewPickupCost = CASE WHEN @RateTable IS NOT NULL AND @RateTable = 'pickup_cost' AND @OperationName IS NOT NULL AND @Multiplier IS NOT NULL AND @WeightBreakLowerBound IS NOT NULL THEN dbo.RequestSectionLane_Modify_RateTable(A.NewPickupCost, @WeightBreak, @OperationName, @Multiplier) ELSE A.NewPickupCost END,
	NewDeliveryCost = CASE WHEN @RateTable IS NOT NULL AND @RateTable = 'delivery_cost' AND @OperationName IS NOT NULL AND @Multiplier IS NOT NULL AND @WeightBreakLowerBound IS NOT NULL THEN dbo.RequestSectionLane_Modify_RateTable(A.NewDeliveryCost, @WeightBreak, @OperationName, @Multiplier) ELSE A.NewDeliveryCost END,
	NewAccessorialsValue = CASE WHEN @RateTable IS NOT NULL AND @RateTable = 'accessorials_value' AND @OperationName IS NOT NULL AND @Multiplier IS NOT NULL AND @WeightBreakLowerBound IS NOT NULL THEN dbo.RequestSectionLane_Modify_RateTable(A.NewAccessorialsValue, @WeightBreak, @OperationName, @Multiplier) ELSE A.NewAccessorialsValue END,
	NewAccessorialsPercentage = CASE WHEN @RateTable IS NOT NULL AND @RateTable = 'accessorials_percentage' AND @OperationName IS NOT NULL AND @Multiplier IS NOT NULL AND @WeightBreakLowerBound IS NOT NULL THEN dbo.RequestSectionLane_Modify_RateTable(A.NewAccessorialsPercentage, @WeightBreak, @OperationName, @Multiplier) ELSE A.NewAccessorialsPercentage END,
	NewPickupCount = CASE WHEN @RateTable IS NOT NULL AND @RateTable = 'pickup_count' AND @OperationName IS NOT NULL AND @Multiplier IS NOT NULL THEN dbo.RequestSectionLane_Modify_Rate(A.NewPickupCount, @OperationName, @Multiplier) ELSE A.NewPickupCount END,
	NewDeliveryCount = CASE WHEN @RateTable IS NOT NULL AND @RateTable = 'delivery_count' AND @OperationName IS NOT NULL AND @Multiplier IS NOT NULL THEN dbo.RequestSectionLane_Modify_Rate(A.NewDeliveryCount, @OperationName, @Multiplier) ELSE A.NewDeliveryCount END,
	NewDockAdjustment = CASE WHEN @RateTable IS NOT NULL AND @RateTable = 'dock_adjustment' AND @OperationName IS NOT NULL AND @Multiplier IS NOT NULL THEN dbo.RequestSectionLane_Modify_Rate(A.NewDockAdjustment, @OperationName, @Multiplier) ELSE A.NewDockAdjustment END
FROM A
WHERE dbo.RequestSectionLane_Staging.RequestLaneID = A.RequestLaneID 
	AND dbo.RequestSectionLane_Staging.RequestSectionID = A.RequestSectionID
	AND dbo.RequestSectionLane_Staging.ContextID = A.ContextID
	AND dbo.RequestSectionLane_Staging.RequestSectionLaneID = A.RequestSectionLaneID

IF (@MicroSave IS NOT NULL AND @MicroSave = 1) OR (@MacroSave IS NOT NULL AND @MacroSave = 1)
BEGIN;

	WITH B AS 
	(	
		SELECT *
		FROM dbo.RequestSectionLane_Staging
		WHERE ContextID = @ContextID AND IsUpdated = 1
	)

	Update dbo.RequestSectionLane
	SET Cost = B.NewCost,
		[DoNotMeetCommitment] = 0,
		[Commitment] = B.[NewCommitment],
		[CustomerRate] = B.[NewCustomerRate],
		[CustomerDiscount] = B.[NewCustomerDiscount],
		[DrRate] = B.[NewDrRate],
		[PartnerRate] = B.[NewPartnerRate],
		[PartnerDiscount] = B.[NewPartnerDiscount],
		[Profitability] = B.[NewProfitability],
		[PickupCount] = B.[NewPickupCount],
		[DeliveryCount] = B.[NewDeliveryCount],
		[DockAdjustment] = B.[NewDockAdjustment],
		[Margin] = B.[NewMargin],
		[Density] = B.[NewDensity],
		[PickupCost] = B.[NewPickupCost],
		[DeliveryCost] = B.[NewDeliveryCost],
		[AccessorialsValue] = B.[NewAccessorialsValue],
		[AccessorialsPercentage] = B.[NewAccessorialsPercentage],
		IsActive = B.NewIsActive,
		IsInactiveViewable = B.NewIsInactiveViewable,
		IsBetween = B.NewIsBetween,
		IsEdited = 1
	FROM B
	WHERE dbo.RequestSectionLane.RequestSectionID = B.RequestSectionID
	AND dbo.RequestSectionLane.RequestSectionLaneID = B.RequestSectionLaneID;

	WITH C AS 
	(	
		SELECT DISTINCT RequestSectionLaneID
		FROM dbo.RequestSectionLanePricingPoint_Staging
		WHERE ContextID = @ContextID AND IsUpdated = 1
	)

	UPDATE dbo.RequestSectionLane
	SET IsEdited = 1
	WHERE dbo.RequestSectionLane.RequestSectionLaneID IN (SELECT RequestSectionLaneID FROM C)

	EXEC [dbo].[RequestSectionLanePricingPoint_Staging_Update] @RequestSectionID, @ContextID, 'None', 0, 'None', 0, 'None', '[]', '[]', NULL, NULL, 'None', NULL, @MicroSave, @MacroSave

	DECLARE @RequestSectionLaneTableTypeID  IDTableType;

	INSERT INTO @RequestSectionLaneTableTypeID
	(
		ID
	)
	SELECT DISTINCT RequestSectionLaneID
	FROM
	(SELECT RequestSectionLaneID
	FROM dbo.RequestSectionLane_Staging
	WHERE ContextID = @ContextID AND IsUpdated = 1 
	UNION
	SELECT DISTINCT RequestSectionLaneID
	FROM dbo.RequestSectionLanePricingPoint_Staging
	WHERE ContextID = @ContextID AND IsUpdated = 1) AS D

	--EXEC [dbo].[RequestSectionLane_History_Update] @RequestSectionLaneTableTypeID
	EXEC dbo.RequestLane_Count @RequestLaneID

	IF (@MacroSave IS NOT NULL AND @MacroSave = 1)
	BEGIN
		DECLARE @RequestLaneVersionID BIGINT;

		SELECT @RequestLaneVersionID = RequestLaneVersionID
		FROM dbo.RequestLane_History RLH
		WHERE RLH.RequestLaneID = @RequestLaneID AND RLH.IsLatestVersion = 1

		DECLARE @RequestHistory TABLE
		(
			[VersionNum]                   INT             NOT NULL,
			[BaseVersion]		  INT				  NULL,
			[IsLatestVersion]              BIT             NOT NULL,
			[UpdatedOn]                    DATETIME2 (7)   NOT NULL,
			[UpdatedBy]                    NVARCHAR (50)   NOT NULL,
			[Comments]                     NVARCHAR (4000) NOT NULL,
			[IsActive]                     BIT             NOT NULL,
			[IsInactiveViewable]           BIT             NOT NULL,
			[RequestVersionID]             BIGINT          NOT NULL,
			[RequestNumber]                NVARCHAR (32)   NOT NULL,
			[RequestCode]                NVARCHAR (32)   NOT NULL,
			[InitiatedOn]                  DATETIME2 (7)   NOT NULL,
			[SubmittedOn]                  DATETIME2 (7)   NULL,
			[IsValidData]                  BIT             NOT NULL,
			[InitiatedByVersion]           BIGINT          NOT NULL,
			[RequestID]                    BIGINT          NOT NULL,
			[RequestAccessorialsVersionID] BIGINT          NULL,
			[RequestInformationVersionID]  BIGINT          NULL,
			[RequestLaneVersionID]        BIGINT          NULL,
			[RequestProfileVersionID]      BIGINT          NULL,
			[SubmittedByVersion]           BIGINT          NULL,
			[IsReview] BIT NOT NULL
		)
		INSERT INTO @RequestHistory
		(
			[VersionNum],
			[BaseVersion],
			[IsLatestVersion],
			[UpdatedOn],
			[UpdatedBy],
			[Comments],
			[IsActive],
			[IsInactiveViewable],
			[RequestVersionID],
			[RequestNumber],
			[RequestCode],
			[InitiatedOn],
			[SubmittedOn],
			[IsValidData],
			[InitiatedByVersion],
			[RequestID],
			[RequestAccessorialsVersionID],
			[RequestInformationVersionID],
			[RequestLaneVersionID],
			[RequestProfileVersionID],
			[SubmittedByVersion],
			[IsReview]
		)
		SELECT [VersionNum],
			[BaseVersion],
			[IsLatestVersion],
			[UpdatedOn],
			[UpdatedBy],
			[Comments],
			RH.[IsActive],
			RH.[IsInactiveViewable],
			[RequestVersionID],
			RH.[RequestNumber],
			RH.[RequestCode],
			RH.[InitiatedOn],
			RH.[SubmittedOn],
			RH.[IsValidData],
			[InitiatedByVersion],
			RH.[RequestID],
			RH.[RequestAccessorialsVersionID],
			[RequestInformationVersionID],
			[RequestLaneVersionID],
			[RequestProfileVersionID],
			[SubmittedByVersion],
			RH.[IsReview]
		FROM dbo.Request_History RH
		INNER JOIN dbo.Request R ON RH.[RequestID] = R.[RequestID] AND RH.[IsLatestVersion] = 1 AND R.RequestLaneID = @RequestLaneID

		UPDATE dbo.Request_History
		SET [IsLatestVersion] = 0
		WHERE dbo.Request_History.[RequestVersionID] IN (SELECT [RequestVersionID] FROM @RequestHistory)

		INSERT INTO dbo.Request_History
		(
			[VersionNum],
			[IsLatestVersion],
			[UpdatedOn],
			[UpdatedBy],
			[Comments],
			[IsActive],
			[IsInactiveViewable],
			[RequestNumber],
			[RequestCode],
			[InitiatedOn],
			[SubmittedOn],
			[IsValidData],
			[InitiatedByVersion],
			[RequestID],
			[RequestAccessorialsVersionID],
			[RequestInformationVersionID],
			[RequestLaneVersionID],
			[RequestProfileVersionID],
			[SubmittedByVersion],
			[IsReview]
		)
		SELECT [VersionNum]+1,
			1,
			GETUTCDATE(),
			'',
			'',
			[IsActive],
			[IsInactiveViewable],
			[RequestNumber],
			[RequestCode],
			[InitiatedOn],
			[SubmittedOn],
			[IsValidData],
			[InitiatedByVersion],
			[RequestID],
			[RequestAccessorialsVersionID],
			[RequestInformationVersionID],
			@RequestLaneVersionID,
			[RequestProfileVersionID],
			[SubmittedByVersion],
			[IsReview]
		FROM @RequestHistory
	END

	DELETE FROM dbo.RequestSectionLane_Staging
	WHERE RequestLaneID = @RequestLaneID AND ContextID = @ContextID 

	--DELETE FROM dbo.RequestSectionLanePricingPoint_Staging
	--WHERE RequestLaneID = @RequestLaneID AND ContextID = @ContextID 

END

COMMIT TRAN

RETURN 1

GO
