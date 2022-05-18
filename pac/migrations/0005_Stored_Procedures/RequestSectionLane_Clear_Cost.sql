CREATE OR ALTER PROCEDURE [dbo].[RequestSectionLane_Clear_Cost]
	@RequestSectionTableType_ID     IDTableType READONLY,
	@RequestID BIGINT,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL

AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT;

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Clearing Invalid Cost.';

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
SELECT ID,
	dbo.GetRequestSectionLaneDefaultCost(ID)
FROM @RequestSectionTableType_ID

DECLARE @RequestSectionLane TABLE
(
	[RequestSectionLaneID] BIGINT NOT NULL,
	[Cost] NVARCHAR(MAX) NOT NULL
)

INSERT INTO @RequestSectionLane
(
	[RequestSectionLaneID],
	[Cost]
)
SELECT RSL.RequestSectionLaneID,
	RS.[Cost]
FROM dbo.RequestSectionLane RSL
INNER JOIN @RequestSectionLaneCost RS ON RSL.RequestSectionID = RS.RequestSectionID

UPDATE dbo.RequestSectionLane
SET [Commitment] = A.Cost,
	[CustomerRate] = A.Cost,
	[CustomerDiscount] = A.Cost,
	[DrRate] = A.Cost,
	[PartnerRate] = A.Cost,
	[PartnerDiscount] = A.Cost,
	[Profitability] = A.Cost,
	[PickupCount] = NULL,
	[DeliveryCount] = NULL,
	[DockAdjustment] = NULL,
	[Margin] = A.Cost,
	[Density] = A.Cost,
	[PickupCost] = A.Cost,
	[DeliveryCost] = A.Cost,
	[AccessorialsValue] = A.Cost,
	[AccessorialsPercentage] = A.Cost,
	IsEdited = 1,
	[DoNotMeetCommitment] = 0
FROM @RequestSectionLane A
WHERE dbo.RequestSectionLane.RequestSectionLaneID = A.RequestSectionLaneID 

UPDATE dbo.RequestSectionLanePricingPoint
SET [DrRate] = A.Cost,
	[FakRate] = A.Cost,
	[Profitability] = A.Cost,
	[SplitsAll] = A.Cost,
	[SplitsAllUsagePercentage] = 0,
	[PickupCount] = NULL,
	[DeliveryCount] = NULL,
	[DockAdjustment] = NULL,
	[Margin] = A.Cost,
	[Density] = A.Cost,
	[PickupCost] = A.Cost,
	[DeliveryCost] = A.Cost,
	[AccessorialsValue] = A.Cost,
	[AccessorialsPercentage] = A.Cost
FROM @RequestSectionLane A
WHERE dbo.RequestSectionLanePricingPoint.RequestSectionLaneID = A.RequestSectionLaneID 

SELECT @ERROR1 = @@ERROR

IF (@ERROR1 <> 0)

	BEGIN
	ROLLBACK TRAN
	RAISERROR('Insert Procedure Failed!', 16, 1)
	RETURN 0
	END

DECLARE @RequestLaneID BIGINT;
SELECT @RequestLaneID = RequestLaneID FROM dbo.Request WHERE RequestID = @RequestID
EXEC dbo.RequestLane_Count @RequestLaneID, @UpdatedBy, @Comments

COMMIT TRAN
RETURN 1

