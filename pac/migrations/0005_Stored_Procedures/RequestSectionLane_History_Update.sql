CREATE OR ALTER PROCEDURE [dbo].[RequestSectionLane_History_Update]
	@RequestSectionLaneTableTypeID  IDTableType READONLY,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL

AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT;

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Saving RequestLane_History.';

BEGIN TRAN

DECLARE @RequestSectionTableTypeID IDTableType;

INSERT INTO @RequestSectionTableTypeID
(
	ID
)
SELECT DISTINCT RSL.RequestSectionID
FROM dbo.RequestSectionLane RSL
WHERE RSL.RequestSectionLaneID IN (SELECT ID FROM @RequestSectionLaneTableTypeID)

DECLARE @RequestSectionVersion TABLE
(
	RequestSectionID BIGINT NOT NULL,
	RequestSectionVersionID BIGINT NOT NULL
)

INSERT INTO @RequestSectionVersion
(
	RequestSectionID,
	RequestSectionVersionID
)
SELECT RSH.RequestSectionID,
	RSH.RequestSectionVersionID
FROM dbo.RequestSection_History RSH
INNER JOIN @RequestSectionTableTypeID RS ON RSH.RequestSectionID = RS.ID AND RSH.IsLatestVersion = 1

DECLARE @RequestSectionLaneID TABLE
(
	[RequestSectionLaneID] BIGINT        NOT NULL,
	[RequestSectionID] BIGINT        NOT NULL
)
INSERT INTO @RequestSectionLaneID
(
	[RequestSectionLaneID],
	[RequestSectionID]
)
SELECT [RequestSectionLaneID], [RequestSectionID]
FROM dbo.RequestSectionLane
WHERE [RequestSectionLaneID] IN (SELECT ID FROM @RequestSectionLaneTableTypeID)

DECLARE @RequestSectionLaneHistory TABLE
(
	[VersionNum]          INT             NOT NULL,
	[IsActive]           BIT           NOT NULL,
    [IsInactiveViewable] BIT           NOT NULL,
	[RequestSectionLaneVersionID]          BIGINT        NOT NULL,
	[RequestSectionLaneID]          BIGINT    NOT NULL,
	[RequestSectionVersionID]          BIGINT        NOT NULL,
    [LaneNumber]        NVARCHAR(32) NOT NULL,
	[IsPublished]        BIT NOT NULL,
	[IsEdited]        BIT NOT NULL,
	[IsDuplicate]        BIT NOT NULL,
	[IsBetween]        BIT NOT NULL,
	[IsLaneGroup]        BIT NOT NULL,
	[OriginProvinceVersionID] BIGINT NULL,
	[OriginProvinceCode] NVARCHAR(2) NULL,
	[OriginRegionVersionID] BIGINT NULL,
	[OriginRegionCode] NVARCHAR(4) NULL,
	[OriginCountryVersionID] BIGINT NULL,
	[OriginCountryCode] NVARCHAR(2) NULL,
	[OriginTerminalVersionID] BIGINT NULL,
	[OriginTerminalCode] NVARCHAR(3) NULL,
	[OriginZoneVersionID] BIGINT NULL,
	[OriginZoneName] NVARCHAR(50) NULL,
	[OriginBasingPointVersionID] BIGINT NULL,
	[OriginBasingPointName] NVARCHAR(50) NULL,
	[OriginServicePointVersionID] BIGINT NULL,
	[OriginServicePointName] NVARCHAR(50) NULL,
	[OriginPostalCodeVersionID] BIGINT NULL,
	[OriginPostalCodeName] NVARCHAR(10) NULL,
	[OriginPointTypeVersionID] BIGINT NOT NULL,
	[OriginPointTypeName] NVARCHAR(50) NOT NULL,
	[OriginCode] NVARCHAR(50) NOT NULL,
	[DestinationProvinceVersionID] BIGINT NULL,
	[DestinationProvinceCode] NVARCHAR(2) NULL,
	[DestinationRegionVersionID] BIGINT NULL,
	[DestinationRegionCode] NVARCHAR(4) NULL,
	[DestinationCountryVersionID] BIGINT NULL,
	[DestinationCountryCode] NVARCHAR(2) NULL,
	[DestinationTerminalVersionID] BIGINT NULL,
	[DestinationTerminalCode] NVARCHAR(3) NULL,
	[DestinationZoneVersionID] BIGINT NULL,
	[DestinationZoneName] NVARCHAR(50) NULL,
	[DestinationBasingPointVersionID] BIGINT NULL,
	[DestinationBasingPointName] NVARCHAR(50) NULL,
	[DestinationServicePointVersionID] BIGINT NULL,
	[DestinationServicePointName] NVARCHAR(50) NULL,
	[DestinationPostalCodeVersionID] BIGINT NULL,
	[DestinationPostalCodeName] NVARCHAR(10) NULL,
	[DestinationPointTypeVersionID] BIGINT NOT NULL,
	[DestinationPointTypeName] NVARCHAR(50) NOT NULL,
	[DestinationCode] NVARCHAR(50) NOT NULL,
	[LaneHashCode] VARBINARY(8000) NOT NULL,
	[BasingPointHashCode] VARBINARY(8000) NULL,
	[Cost]        NVARCHAR(MAX) NULL,
	[DoNotMeetCommitment] BIT NOT NULL,
	[Commitment] NVARCHAR(MAX) NULL,
	[CustomerRate] NVARCHAR(MAX) NOT NULL,
	[CustomerDiscount] NVARCHAR(MAX) NOT NULL,
	[DrRate] NVARCHAR(MAX) NOT NULL,
	[PartnerRate] NVARCHAR(MAX) NOT NULL,
	[PartnerDiscount] NVARCHAR(MAX) NOT NULL,
	[Profitability] NVARCHAR(MAX) NOT NULL,
	[PickupCount] INT NULL,
	[DeliveryCount] INT NULL,
	[DockAdjustment] DECIMAL(19,6) NULL,
	[Margin] NVARCHAR(MAX) NOT NULL,
	[Density] NVARCHAR(MAX) NOT NULL,
	[PickupCost] NVARCHAR(MAX) NOT NULL,
	[DeliveryCost] NVARCHAR(MAX) NOT NULL,
	[AccessorialsValue] NVARCHAR(MAX) NOT NULL,
	[AccessorialsPercentage] NVARCHAR(MAX) NOT NULL
)

INSERT INTO @RequestSectionLaneHistory
(
	[VersionNum],
	[IsActive],
    [IsInactiveViewable],
	[RequestSectionLaneVersionID],
	[RequestSectionLaneID],
	[RequestSectionVersionID],
    [LaneNumber],
	[IsPublished],
	[IsEdited],
	[IsDuplicate],
	[IsBetween],
	[IsLaneGroup],
	[OriginProvinceVersionID],
	[OriginProvinceCode],
	[OriginRegionVersionID],
	[OriginRegionCode],
	[OriginCountryVersionID],
	[OriginCountryCode],
	[OriginTerminalVersionID],
	[OriginTerminalCode],
	[OriginZoneVersionID],
	[OriginZoneName],
	[OriginBasingPointVersionID],
	[OriginBasingPointName],
	[OriginServicePointVersionID],
	[OriginServicePointName],
	[OriginPostalCodeVersionID],
	[OriginPostalCodeName],
	[OriginPointTypeVersionID],
	[OriginPointTypeName],
	[OriginCode],
	[DestinationProvinceVersionID],
	[DestinationProvinceCode],
	[DestinationRegionVersionID],
	[DestinationRegionCode],
	[DestinationCountryVersionID],
	[DestinationCountryCode],
	[DestinationTerminalVersionID],
	[DestinationTerminalCode],
	[DestinationZoneVersionID],
	[DestinationZoneName],
	[DestinationBasingPointVersionID],
	[DestinationBasingPointName],
	[DestinationServicePointVersionID],
	[DestinationServicePointName],
	[DestinationPostalCodeVersionID],
	[DestinationPostalCodeName],
	[DestinationPointTypeVersionID],
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
SELECT [VersionNum],
	RSL.[IsActive],
    RSL.[IsInactiveViewable],
	[RequestSectionLaneVersionID],
	RSLH.[RequestSectionLaneID],
	[RequestSectionVersionID],
    RSL.[LaneNumber],
	RSL.[IsPublished],
	RSL.[IsEdited],
	RSL.[IsDuplicate],
	RSL.[IsBetween],
	RSL.[IsLaneGroup],
	[OriginProvinceVersionID],
	RSL.[OriginProvinceCode],
	[OriginRegionVersionID],
	RSL.[OriginRegionCode],
	[OriginCountryVersionID],
	RSL.[OriginCountryCode],
	[OriginTerminalVersionID],
	RSL.[OriginTerminalCode],
	[OriginZoneVersionID],
	RSL.[OriginZoneName],
	[OriginBasingPointVersionID],
	RSL.[OriginBasingPointName],
	[OriginServicePointVersionID],
	RSL.[OriginServicePointName],
	[OriginPostalCodeVersionID],
	RSL.[OriginPostalCodeName],
	[OriginPointTypeVersionID],
	RSL.[OriginPointTypeName],
	RSL.[OriginCode],
	[DestinationProvinceVersionID],
	RSL.[DestinationProvinceCode],
	[DestinationRegionVersionID],
	RSL.[DestinationRegionCode],
	[DestinationCountryVersionID],
	RSL.[DestinationCountryCode],
	[DestinationTerminalVersionID],
	RSL.[DestinationTerminalCode],
	[DestinationZoneVersionID],
	RSL.[DestinationZoneName],
	[DestinationBasingPointVersionID],
	RSL.[DestinationBasingPointName],
	[DestinationServicePointVersionID],
	RSL.[DestinationServicePointName],
	[DestinationPostalCodeVersionID],
	RSL.[DestinationPostalCodeName],
	[DestinationPointTypeVersionID],
	RSL.[DestinationPointTypeName],
	RSL.[DestinationCode],
	RSL.[LaneHashCode],
	RSL.[BasingPointHashCode],
	RSL.[Cost],
	RSL.[DoNotMeetCommitment],
	RSL.[Commitment],
	RSL.[CustomerRate],
	RSL.[CustomerDiscount],
	RSL.[DrRate],
	RSL.[PartnerRate],
	RSL.[PartnerDiscount],
	RSL.[Profitability],
	RSL.[PickupCount],
	RSL.[DeliveryCount],
	RSL.[DockAdjustment],
	RSL.[Margin],
	RSL.[Density],
	RSL.[PickupCost],
	RSL.[DeliveryCost],
	RSL.[AccessorialsValue],
	RSL.[AccessorialsPercentage]
FROM dbo.RequestSectionLane_History RSLH
INNER JOIN dbo.RequestSectionLane RSL ON RSLH.RequestSectionLaneID = RSL.RequestSectionLaneID AND RSLH.IsLatestVersion = 1
WHERE RSL.RequestSectionLaneID IN (SELECT RequestSectionLaneID FROM @RequestSectionLaneID)

UPDATE dbo.RequestSectionLane_History 
SET IsLatestVersion = 0
WHERE dbo.RequestSectionLane_History.RequestSectionLaneVersionID IN (SELECT RequestSectionLaneVersionID FROM @RequestSectionLaneHistory)

SELECT @ERROR1 = @@ERROR

-- Insert INTO RequestSectionLane_History

INSERT INTO dbo.RequestSectionLane_History
(
	[VersionNum],
    [IsLatestVersion],
    [UpdatedOn],
    [UpdatedBy],
    [Comments],
	[IsActive],
    [IsInactiveViewable],
	[RequestSectionLaneID],
	[RequestSectionVersionID],
    [LaneNumber],
	[IsPublished],
	[IsEdited],
	[IsDuplicate],
	[IsBetween],
	[IsLaneGroup],
	[OriginProvinceVersionID],
	[OriginProvinceCode],
	[OriginRegionVersionID],
	[OriginRegionCode],
	[OriginCountryVersionID],
	[OriginCountryCode],
	[OriginTerminalVersionID],
	[OriginTerminalCode],
	[OriginZoneVersionID],
	[OriginZoneName],
	[OriginBasingPointVersionID],
	[OriginBasingPointName],
	[OriginServicePointVersionID],
	[OriginServicePointName],
	[OriginPostalCodeVersionID],
	[OriginPostalCodeName],
	[OriginPointTypeVersionID],
	[OriginPointTypeName],
	[OriginCode],
	[DestinationProvinceVersionID],
	[DestinationProvinceCode],
	[DestinationRegionVersionID],
	[DestinationRegionCode],
	[DestinationCountryVersionID],
	[DestinationCountryCode],
	[DestinationTerminalVersionID],
	[DestinationTerminalCode],
	[DestinationZoneVersionID],
	[DestinationZoneName],
	[DestinationBasingPointVersionID],
	[DestinationBasingPointName],
	[DestinationServicePointVersionID],
	[DestinationServicePointName],
	[DestinationPostalCodeVersionID],
	[DestinationPostalCodeName],
	[DestinationPointTypeVersionID],
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
SELECT [VersionNum]+1,
	1,
	GETUTCDATE(),
	@UpdatedBy,
	@Comments,
	[IsActive],
    [IsInactiveViewable],
	RSLH.[RequestSectionLaneID],
	RS.[RequestSectionVersionID],
    [LaneNumber],
	[IsPublished],
	[IsEdited],
	[IsDuplicate],
	[IsBetween],
	[IsLaneGroup],
	[OriginProvinceVersionID],
	[OriginProvinceCode],
	[OriginRegionVersionID],
	[OriginRegionCode],
	[OriginCountryVersionID],
	[OriginCountryCode],
	[OriginTerminalVersionID],
	[OriginTerminalCode],
	[OriginZoneVersionID],
	[OriginZoneName],
	[OriginBasingPointVersionID],
	[OriginBasingPointName],
	[OriginServicePointVersionID],
	[OriginServicePointName],
	[OriginPostalCodeVersionID],
	[OriginPostalCodeName],
	[OriginPointTypeVersionID],
	[OriginPointTypeName],
	[OriginCode],
	[DestinationProvinceVersionID],
	[DestinationProvinceCode],
	[DestinationRegionVersionID],
	[DestinationRegionCode],
	[DestinationCountryVersionID],
	[DestinationCountryCode],
	[DestinationTerminalVersionID],
	[DestinationTerminalCode],
	[DestinationZoneVersionID],
	[DestinationZoneName],
	[DestinationBasingPointVersionID],
	[DestinationBasingPointName],
	[DestinationServicePointVersionID],
	[DestinationServicePointName],
	[DestinationPostalCodeVersionID],
	[DestinationPostalCodeName],
	[DestinationPointTypeVersionID],
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
FROM @RequestSectionLaneHistory RSLH
INNER JOIN @RequestSectionLaneID RSL ON RSLH.RequestSectionLaneID = RSL.RequestSectionLaneID
INNER JOIN @RequestSectionVersion RS ON RSL.RequestSectionID = RS.RequestSectionID

DECLARE @RequestSectionLanePricingPointTableTypeID IDTableType;
INSERT INTO @RequestSectionLanePricingPointTableTypeID
(	
	[ID]
)
SELECT RequestSectionLanePricingPointID
FROM dbo.RequestSectionLanePricingPoint
WHERE RequestSectionLaneID IN (SELECT ID FROM @RequestSectionLaneTableTypeID)

EXEC dbo.RequestSectionLanePricingPoint_History_Update @RequestSectionLanePricingPointTableTypeID, @UpdatedBy, @Comments

SELECT @ERROR2 = @@ERROR

	IF (@ERROR1 <> 0) OR (@ERROR2 <> 0)
	BEGIN
	ROLLBACK TRAN
	RAISERROR('Insert Procedure Failed!', 16, 1)
	RETURN 0
	END

COMMIT TRAN
RETURN 1

