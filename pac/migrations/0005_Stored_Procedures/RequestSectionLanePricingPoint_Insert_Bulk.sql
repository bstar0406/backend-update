CREATE OR ALTER PROCEDURE [dbo].[RequestSectionLanePricingPoint_Insert_Bulk]
	@RequestSectionLanePricingPointTableType RequestSectionLanePricingPointTableType READONLY,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ERROR3 INT;

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

BEGIN TRAN

DECLARE @RequestSectionLaneTableTypeID IDTableType;

INSERT INTO @RequestSectionLaneTableTypeID
(
	ID
)
SELECT DISTINCT [RequestSectionLaneID] FROM @RequestSectionLanePricingPointTableType

DECLARE @RequestSectionLaneVersion TABLE
(
	[RequestSectionLaneID] BIGINT NOT NULL,
	[RequestSectionLaneVersionID] BIGINT NOT NULL
)
INSERT INTO @RequestSectionLaneVersion
(
	[RequestSectionLaneID],
	[RequestSectionLaneVersionID]
)
SELECT RSLH.[RequestSectionLaneID],
	RSLH.[RequestSectionLaneVersionID]
FROM dbo.RequestSectionLane_History RSLH
INNER JOIN @RequestSectionLaneTableTypeID RSL ON RSLH.[RequestSectionLaneID] = RSL.ID AND RSLH.IsLatestVersion = 1

DECLARE @AllRequestSectionLanePricingPoint TABLE
(
	[RequestSectionLaneID] BIGINT NOT NULL,
	[PricingPointNumber] NVARCHAR(32) NOT NULL,
	[PricingPointHashCode] VARBINARY(8000) NOT NULL
)
INSERT INTO @AllRequestSectionLanePricingPoint
(
	[RequestSectionLaneID],
	[PricingPointNumber],
	[PricingPointHashCode]
)
SELECT RSLPP.[RequestSectionLaneID], RSLPP.[PricingPointNumber], RSLPP.[PricingPointHashCode]
FROM dbo.RequestSectionLanePricingPoint RSLPP
INNER JOIN @RequestSectionLaneTableTypeID RSL ON RSLPP.[RequestSectionLaneID] = RSL.ID
UNION
SELECT [RequestSectionLaneID], [PricingPointNumber], [PricingPointHashCode]
FROM @RequestSectionLanePricingPointTableType

DECLARE @IdenticalPricingPointHashCode TABLE
(
	[RequestSectionLaneID] BIGINT NOT NULL,
	[PricingPointHashCode] VARBINARY(8000) NOT NULL
)
INSERT INTO @IdenticalPricingPointHashCode
(
	[RequestSectionLaneID],
	[PricingPointHashCode]
)
SELECT [RequestSectionLaneID], [PricingPointHashCode]
FROM @AllRequestSectionLanePricingPoint
GROUP BY [RequestSectionLaneID], [PricingPointHashCode]
HAVING COUNT(*) > 1

DECLARE @IdenticalRequestSectionLanePricingPoint TABLE
(
	[RequestSectionLaneID] BIGINT NOT NULL,
	[PricingPointNumber] NVARCHAR(32) NOT NULL
)
INSERT INTO @IdenticalRequestSectionLanePricingPoint
(
	[RequestSectionLaneID],
	[PricingPointNumber]
)
SELECT A.[RequestSectionLaneID], A.[PricingPointNumber]
FROM @AllRequestSectionLanePricingPoint A
INNER JOIN @IdenticalPricingPointHashCode B ON A.[RequestSectionLaneID] = B.[RequestSectionLaneID] AND A.[PricingPointHashCode] = B.[PricingPointHashCode]

DECLARE @ToBeUpDatedRequestSectionLanePricingPoint TABLE
(
	RequestSectionLanePricingPointID BIGINT NOT NULL,
	Cost NVARCHAR(MAX) NOT NULL
)

INSERT INTO @ToBeUpDatedRequestSectionLanePricingPoint
(
	RequestSectionLanePricingPointID,
	Cost
)
SELECT A.[RequestSectionLanePricingPointID],
	dbo.GetRequestSectionLaneDefaultCost(RSL.RequestSectionID)
FROM dbo.RequestSectionLanePricingPoint A
INNER JOIN @IdenticalRequestSectionLanePricingPoint B ON A.[RequestSectionLaneID] = B.[RequestSectionLaneID] AND A.[PricingPointNumber] = B.[PricingPointNumber]
INNER JOIN dbo.RequestSectionLane RSL ON B.[RequestSectionLaneID] = RSL.[RequestSectionLaneID]
WHERE (A.[IsActive] = 0 OR A.[IsInactiveViewable] = 0)

DECLARE @NewRequestSectionLanePricingPointTableType RequestSectionLanePricingPointTableType;

INSERT INTO [dbo].[RequestSectionLanePricingPoint]
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
OUTPUT INSERTED.[IsActive],
	INSERTED.[IsInactiveViewable],
	INSERTED.[RequestSectionLanePricingPointID],
	INSERTED.[RequestSectionLaneID],
	INSERTED.[PricingPointNumber],
	INSERTED.[OriginPostalCodeID],
	INSERTED.[OriginPostalCodeName],
	INSERTED.[DestinationPostalCodeID],
	INSERTED.[DestinationPostalCodeName],
	INSERTED.[PricingPointHashCode],
	INSERTED.[Cost],
	INSERTED.[DrRate],
	INSERTED.[FakRate],
	INSERTED.[Profitability],
	INSERTED.[SplitsAll],
	INSERTED.[SplitsAllUsagePercentage],
	INSERTED.[PickupCount],
	INSERTED.[DeliveryCount],
	INSERTED.[DockAdjustment],
	INSERTED.[Margin],
	INSERTED.[Density],
	INSERTED.[PickupCost],
	INSERTED.[DeliveryCost],
	INSERTED.[AccessorialsValue],
	INSERTED.[AccessorialsPercentage]
INTO @NewRequestSectionLanePricingPointTableType
(	
	[IsActive],
	[IsInactiveViewable],
	[RequestSectionLanePricingPointID],
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
SELECT [IsActive],
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
FROM @RequestSectionLanePricingPointTableType RSLPP
WHERE RSLPP.[PricingPointNumber] NOT IN (SELECT [PricingPointNumber] FROM @IdenticalRequestSectionLanePricingPoint)

SELECT @ERROR1 = @@ERROR

DECLARE @PostalCodeVersionID table 
( 
	[PostalCodeID] [bigint] NOT NULL,
	[PostalCodeVersionID] [bigint] NOT NULL
)
INSERT INTO @PostalCodeVersionID 
( 
	[PostalCodeID],
	[PostalCodeVersionID]
)
SELECT [PostalCodeID],
	[PostalCodeVersionID]
FROM [dbo].[PostalCode_History]
WHERE [IsLatestVersion] = 1
AND [PostalCodeID] IN 
(SELECT DISTINCT PostalCodeID FROM 
(SELECT [OriginPostalCodeID] AS PostalCodeID FROM @NewRequestSectionLanePricingPointTableType
UNION 
SELECT [DestinationPostalCodeID] AS PostalCodeID FROM @NewRequestSectionLanePricingPointTableType) AS A)

INSERT INTO dbo.RequestSectionLanePricingPoint_History
(
	[VersionNum],
	[IsActive],
    [IsInactiveViewable],
	[RequestSectionLanePricingPointID],
	[RequestSectionLaneVersionID],
    [PricingPointNumber],
	[OriginPostalCodeVersionID],
	[OriginPostalCodeName],
	[DestinationPostalCodeVersionID],
	[DestinationPostalCodeName],
	[PricingPointHashCode],
	Cost,
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
	[AccessorialsPercentage],
	UpdatedOn,
	UpdatedBy,
	Comments,
	IsLatestVersion
)
SELECT 1,
	[IsActive],
    [IsInactiveViewable],
	[RequestSectionLanePricingPointID],
	B.[RequestSectionLaneVersionID],
    [PricingPointNumber],
	O_PC.[PostalCodeVersionID],
	[OriginPostalCodeName],
	D_PC.[PostalCodeVersionID],
	[DestinationPostalCodeName],
	[PricingPointHashCode],
	Cost,
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
	[AccessorialsPercentage],
	GETUTCDATE(),
	@UpdatedBy,
	@Comments,
	1
FROM @NewRequestSectionLanePricingPointTableType A
INNER JOIN @RequestSectionLaneVersion B ON A.[RequestSectionLaneID] = B.[RequestSectionLaneID]
LEFT JOIN @PostalCodeVersionID O_PC ON A.OriginPostalCodeID = O_PC.PostalCodeID
LEFT JOIN @PostalCodeVersionID D_PC ON A.DestinationPostalCodeID = D_PC.PostalCodeID

SELECT @ERROR2 = @@ERROR

UPDATE dbo.RequestSectionLanePricingPoint
SET [IsActive] = 1,
	[IsInactiveViewable] = 1,
	[Cost] = A.Cost
FROM @ToBeUpDatedRequestSectionLanePricingPoint A
WHERE dbo.RequestSectionLanePricingPoint.[RequestSectionLanePricingPointID] = A.RequestSectionLanePricingPointID

SELECT @ERROR3 = @@ERROR

IF (@ERROR1 <> 0) OR (@ERROR2 <> 0) OR (@ERROR3 <> 0)
BEGIN
ROLLBACK TRAN
RAISERROR('Insert Procedure Failed!', 16, 1)
RETURN 0
END

DECLARE @RequestSectionLanePricingPointTableTypeID IDTableType;
INSERT INTO @RequestSectionLanePricingPointTableTypeID
(	
	[ID]
)
SELECT RequestSectionLanePricingPointID
FROM @ToBeUpDatedRequestSectionLanePricingPoint

EXEC dbo.RequestSectionLanePricingPoint_History_Update @RequestSectionLanePricingPointTableTypeID, @UpdatedBy, @Comments

COMMIT TRAN
RETURN 1

