CREATE OR ALTER PROCEDURE [dbo].[RequestSectionLanePricingPoint_History_Update]
	@RequestSectionLanePricingPointTableTypeID IDTableType READONLY,
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

DECLARE @RequestSectionLaneTableTypeID IDTableType;

INSERT INTO @RequestSectionLaneTableTypeID
(
	ID
)
SELECT DISTINCT RSLPP.RequestSectionLaneID
FROM dbo.RequestSectionLanePricingPoint RSLPP
WHERE RSLPP.RequestSectionLanePricingPointID IN (SELECT ID FROM @RequestSectionLanePricingPointTableTypeID)

DECLARE @RequestSectionLaneVersion TABLE
(
	RequestSectionLaneID BIGINT NOT NULL,
	RequestSectionLaneVersionID BIGINT NOT NULL
)

INSERT INTO @RequestSectionLaneVersion
(
	RequestSectionLaneID,
	RequestSectionLaneVersionID
)
SELECT RSLH.RequestSectionLaneID,
	RSLH.RequestSectionLaneVersionID
FROM dbo.RequestSectionLane_History RSLH
INNER JOIN @RequestSectionLaneTableTypeID RSL ON RSLH.RequestSectionLaneID = RSL.ID AND RSLH.IsLatestVersion = 1

DECLARE @RequestSectionLanePricingPointHistory TABLE
(
	[VersionNum]          INT             NOT NULL,
	[IsActive]           BIT           NOT NULL,
    [IsInactiveViewable] BIT           NOT NULL,
	[RequestSectionLanePricingPointVersionID]          BIGINT     NOT NULL,
	[RequestSectionLanePricingPointID]          BIGINT     NOT NULL,
	[RequestSectionLaneVersionID]          BIGINT     NOT NULL,
    [PricingPointNumber]        NVARCHAR(32) NOT NULL,
	[OriginPostalCodeVersionID] BIGINT NULL,
	[OriginPostalCodeName] NVARCHAR(10) NULL,
	[DestinationPostalCodeVersionID] BIGINT NULL,
	[DestinationPostalCodeName] NVARCHAR(10) NULL,
	[PricingPointHashCode] VARBINARY(8000) NOT NULL,
	[Cost]        NVARCHAR(MAX) NULL,
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
	[AccessorialsPercentage] NVARCHAR(MAX) NOT NULL
)
INSERT INTO @RequestSectionLanePricingPointHistory
(
	[VersionNum],
	[IsActive],
    [IsInactiveViewable],
	[RequestSectionLanePricingPointVersionID],
	[RequestSectionLanePricingPointID],
	[RequestSectionLaneVersionID],
    [PricingPointNumber],
	[OriginPostalCodeVersionID],
	[OriginPostalCodeName],
	[DestinationPostalCodeVersionID],
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
SELECT  [VersionNum],
	PP.[IsActive],
    PP.[IsInactiveViewable],
	[RequestSectionLanePricingPointVersionID],
	PPH.[RequestSectionLanePricingPointID],
	[RequestSectionLaneVersionID],
    PP.[PricingPointNumber],
	[OriginPostalCodeVersionID],
	PP.[OriginPostalCodeName],
	[DestinationPostalCodeVersionID],
	PP.[DestinationPostalCodeName],
	PP.[PricingPointHashCode],
	PP.[Cost],
	PP.[DrRate],
	PP.[FakRate],
	PP.[Profitability],
	PP.[SplitsAll],
	PP.[SplitsAllUsagePercentage],
	PP.[PickupCount],
	PP.[DeliveryCount],
	PP.[DockAdjustment],
	PP.[Margin],
	PP.[Density],
	PP.[PickupCost],
	PP.[DeliveryCost],
	PP.[AccessorialsValue],
	PP.[AccessorialsPercentage]
FROM dbo.RequestSectionLanePricingPoint_History PPH
INNER JOIN dbo.RequestSectionLanePricingPoint PP ON PPH.RequestSectionLanePricingPointID = PP.RequestSectionLanePricingPointID AND PPH.IsLatestVersion = 1
WHERE PP.RequestSectionLanePricingPointID IN (SELECT ID FROM @RequestSectionLanePricingPointTableTypeID) 

UPDATE dbo.RequestSectionLanePricingPoint_History
SET IsLatestVersion = 0
WHERE dbo.RequestSectionLanePricingPoint_History.[RequestSectionLanePricingPointVersionID] IN (SELECT [RequestSectionLanePricingPointVersionID] FROM @RequestSectionLanePricingPointHistory)

SELECT @ERROR1 = @@ERROR

INSERT INTO RequestSectionLanePricingPoint_History
(
	[VersionNum],
    [IsLatestVersion],
    [UpdatedOn],
    [UpdatedBy],
    [Comments],
	[IsActive],
    [IsInactiveViewable],
	PPH.[RequestSectionLanePricingPointID],
	[RequestSectionLaneVersionID],
    [PricingPointNumber],
	[OriginPostalCodeVersionID],
	[OriginPostalCodeName],
	[DestinationPostalCodeVersionID],
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
SELECT [VersionNum]+1,
	1,
	GETUTCDATE(),
	@UpdatedBy,
	@Comments,
	PPH.[IsActive],
    PPH.[IsInactiveViewable],
	PPH.[RequestSectionLanePricingPointID],
	RSL.[RequestSectionLaneVersionID],
    PPH.[PricingPointNumber],
	[OriginPostalCodeVersionID],
	PPH.[OriginPostalCodeName],
	[DestinationPostalCodeVersionID],
	PPH.[DestinationPostalCodeName],
	PPH.[PricingPointHashCode],
	PPH.[Cost],
	PPH.[DrRate],
	PPH.[FakRate],
	PPH.[Profitability],
	PPH.[SplitsAll],
	PPH.[SplitsAllUsagePercentage],
	PPH.[PickupCount],
	PPH.[DeliveryCount],
	PPH.[DockAdjustment],
	PPH.[Margin],
	PPH.[Density],
	PPH.[PickupCost],
	PPH.[DeliveryCost],
	PPH.[AccessorialsValue],
	PPH.[AccessorialsPercentage]
FROM @RequestSectionLanePricingPointHistory PPH
INNER JOIN dbo.RequestSectionLanePricingPoint PP ON PPH.RequestSectionLanePricingPointID = PP.RequestSectionLanePricingPointID
INNER JOIN @RequestSectionLaneVersion RSL ON PP.RequestSectionLaneID = RSL.RequestSectionLaneID
WHERE PP.RequestSectionLanePricingPointID IN (SELECT ID FROM @RequestSectionLanePricingPointTableTypeID)

SELECT @ERROR2 = @@ERROR


IF (@ERROR1 <> 0) OR (@ERROR2 <> 0)
BEGIN
ROLLBACK TRAN
RAISERROR('Insert Procedure Failed!', 16, 1)
RETURN 0
END

COMMIT TRAN
RETURN 1

