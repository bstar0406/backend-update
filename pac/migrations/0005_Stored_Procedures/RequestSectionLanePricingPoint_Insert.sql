CREATE OR ALTER PROCEDURE [dbo].[RequestSectionLanePricingPoint_Insert]
	@RequestSectionLanePricingPointTableType_Create RequestSectionLanePricingPointTableType_Create READONLY,
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

DECLARE @RequestSectionTableType_ID IDTableType;

INSERT INTO @RequestSectionTableType_ID
(
	ID
)
SELECT DISTINCT RSL.[RequestSectionID]
FROM dbo.RequestSectionLane RSL
INNER JOIN @RequestSectionLanePricingPointTableType_Create RSLPP ON RSL.RequestSectionLaneID = RSLPP.RequestSectionLaneID

DECLARE @RequestSectionLaneTableType_ID IDTableType;
INSERT INTO @RequestSectionLaneTableType_ID
(
	ID
)
SELECT DISTINCT RSL.[RequestSectionLaneID]
FROM dbo.RequestSectionLane RSL
INNER JOIN @RequestSectionLanePricingPointTableType_Create RSLPP ON RSL.RequestSectionLaneID = RSLPP.RequestSectionLaneID
WHERE RSL.IsLaneGroup = 0

UPDATE dbo.RequestSectionLane
SET IsLaneGroup = 1
WHERE dbo.RequestSectionLane.RequestSectionLaneID IN (SELECT ID FROM @RequestSectionLaneTableType_ID)

EXEC dbo.RequestSectionLane_History_Update @RequestSectionLaneTableType_ID, @UpdatedBy, @Comments

DECLARE @PostalCodes TABLE
(
	[PostalCodeID] BIGINT NOT NULL,
	[PostalCodeName] NVARCHAR(10) NOT NULL
)
INSERT INTO @PostalCodes
(
	[PostalCodeID],
	[PostalCodeName]
)
SELECT DISTINCT [PostalCodeID], [PostalCodeName]
FROM dbo.PostalCode
WHERE [PostalCodeID] IN (SELECT OriginPostalCodeID FROM @RequestSectionLanePricingPointTableType_Create UNION SELECT DestinationPostalCodeID FROM @RequestSectionLanePricingPointTableType_Create)

DECLARE @RequestSectionCost TABLE
(
	[RequestSectionID] BIGINT NOT NULL,
	[Cost] NVARCHAR(MAX) NOT NULL
)

INSERT INTO @RequestSectionCost
(
	[RequestSectionID],
	[Cost]
)
SELECT ID,
	dbo.GetRequestSectionLaneDefaultCost(ID)
FROM @RequestSectionTableType_ID

DECLARE @RequestSectionLaneCost TABLE
(
	[RequestSectionLaneID] BIGINT NOT NULL,
	[Cost] NVARCHAR(MAX) NOT NULL
)

INSERT INTO @RequestSectionLaneCost
(
	[RequestSectionLaneID],
	[Cost]
)
SELECT RSL.RequestSectionLaneID,
	RSC.[Cost]
FROM dbo.RequestSectionLane RSL
INNER JOIN dbo.RequestSection RS ON RSL.RequestSectionID = RS.RequestSectionID
INNER JOIN @RequestSectionCost RSC ON RS.RequestSectionID = RSC.RequestSectionID
WHERE RSL.RequestSectionLaneID IN (SELECT DISTINCT [RequestSectionLaneID] FROM @RequestSectionLanePricingPointTableType_Create)

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
	RSLPP.[RequestSectionLaneID],
	REPLACE(NEWID(), '-', ''),
	RSLPP.[OriginPostalCodeID],
	O_PC.[PostalCodeName],
	RSLPP.[DestinationPostalCodeID],
	D_PC.[PostalCodeName],
	(SELECT HASHBYTES('SHA2_512', (SELECT RSLPP.[OriginPostalCodeID] AS OriginPostalCodeID, RSLPP.[DestinationPostalCodeID] AS DestinationPostalCodeID FOR JSON PATH, WITHOUT_ARRAY_WRAPPER))),
	RSLC.Cost,
	RSLC.Cost,
	RSLC.Cost,
	RSLC.Cost,
	'{"orig": 0.5, "dest": 0.5}',
	0,
	NULL,
	NULL,
	NULL,
	RSLC.Cost,
	RSLC.Cost,
	RSLC.Cost,
	RSLC.Cost,
	RSLC.Cost,
	RSLC.Cost
FROM @RequestSectionLanePricingPointTableType_Create RSLPP
INNER JOIN @PostalCodes O_PC ON RSLPP.[OriginPostalCodeID] = O_PC.PostalCodeID
INNER JOIN @PostalCodes D_PC ON RSLPP.[DestinationPostalCodeID] = D_PC.PostalCodeID
INNER JOIN @RequestSectionLaneCost RSLC ON RSLPP.RequestSectionLaneID = RSLC.RequestSectionLaneID

EXEC dbo.RequestSectionLanePricingPoint_Insert_Bulk @RequestSectionLanePricingPointTableType, @UpdatedBy, @Comments

COMMIT TRAN
RETURN 1

