CREATE OR ALTER PROCEDURE [dbo].[LaneCostWeightBreakLevel_Create]
	@AddedCostWeightBreakLevelTableType_Create CostWeightBreakLevelTableType_Create READONLY,
	@ServiceOfferingID BIGINT
AS

SET NOCOUNT ON;

BEGIN TRAN

DECLARE @ERROR1 INT, @ERROR2 INT;

-- insert new weight break levels

--DECLARE @InsertedCostWeightBreakLevel CostWeightBreakLevelTableType_ID;
--DECLARE @DeletedCostWeightBreakLevel CostWeightBreakLevelTableType_ID;

DECLARE @LaneCostWeightBreakLevel table 
( 
    [WeightBreakLevelID]    BIGINT       NOT NULL,
    [WeightBreakLevelName]  NVARCHAR (50) NOT NULL,
    [WeightBreakLowerBound] INT           NOT NULL,
    [ServiceOfferingID]     BIGINT        NOT NULL
)

DECLARE @ServiceOfferingVersionID table 
( 
	[ServiceOfferingID] [bigint] NOT NULL,
	[ServiceOfferingVersionID] [bigint] NOT NULL
)

INSERT INTO @ServiceOfferingVersionID
(
	[ServiceOfferingID],
	[ServiceOfferingVersionID]
)
SELECT [ServiceOfferingID],
	[ServiceOfferingVersionID]
FROM [dbo].[ServiceOffering_History] SLH
WHERE SLH.[IsLatestVersion] = 1
AND [ServiceOfferingID] IN (SELECT DISTINCT [ServiceOfferingID] FROM @AddedCostWeightBreakLevelTableType_Create)

INSERT INTO [dbo].[LaneCostWeightBreakLevel]
(
    [WeightBreakLevelName],
    [WeightBreakLowerBound],
    [ServiceOfferingID],
	[IsActive],
	[IsInactiveViewable]
)
OUTPUT INSERTED.[WeightBreakLevelID],
	 INSERTED.[WeightBreakLevelName],
	 INSERTED.[WeightBreakLowerBound],
	 INSERTED.[ServiceOfferingID]
INTO @LaneCostWeightBreakLevel
(
	[WeightBreakLevelID],
    [WeightBreakLevelName],
    [WeightBreakLowerBound],
    [ServiceOfferingID]
)
SELECT [WeightBreakLevelName],
    [WeightBreakLowerBound],
    [ServiceOfferingID],
	1,
	1
FROM @AddedCostWeightBreakLevelTableType_Create 

SELECT @ERROR1 = @@ERROR;

INSERT INTO [dbo].[LaneCostWeightBreakLevel_History]
(
	[WeightBreakLevelID],
	[WeightBreakLevelName],
    [WeightBreakLowerBound],
    [ServiceOfferingVersionID],
	[IsActive],
	[VersionNum],
	[IsLatestVersion],
	[IsInactiveViewable],
	[UpdatedOn],
	[UpdatedBy],
	[Comments]
)
SELECT WB.[WeightBreakLevelID],
	WB.[WeightBreakLevelName],
    WB.[WeightBreakLowerBound],
    SO.[ServiceOfferingVersionID],
	 1,
	 1,
	 1,
	 1,
	 GETUTCDATE(),
	'P&C System',
	'Added new Weight break levels'
FROM @LaneCostWeightBreakLevel WB 
INNER JOIN @ServiceOfferingVersionID SO ON WB.[ServiceOfferingID] = SO.[ServiceOfferingID]

SELECT @ERROR2 = @@ERROR;

--INSERT INTO @InsertedCostWeightBreakLevel
--(
--	[WeightBreakLevelID],
--	[ServiceOfferingID]
--)
--SELECT [WeightBreakLevelID],
--	[ServiceOfferingID]
--FROM @LaneCostWeightBreakLevel

---- Update The Lane Cost table

--DECLARE @LaneNewCost LaneCostTableType_Update;

--INSERT INTO @LaneNewCost
--(
--	[LaneCostID],
--	[MinimumCost],
--	[Cost]
--)
--SELECT LC.LaneCostID, 
--	LC.[MinimumCost],
--	dbo.LaneCostWeightBreakLevel_Modify(LC.Cost, @InsertedCostWeightBreakLevel, @DeletedCostWeightBreakLevel, SL.ServiceOfferingID) AS NewCost
--FROM dbo.LaneCost LC
--INNER JOIN dbo.Lane L ON LC.LaneID = L.LaneID
--INNER JOIN dbo.ServiceLevel SL ON L.ServiceLevelID = SL.ServiceLevelID
--WHERE SL.ServiceOfferingID = @ServiceOfferingID

--EXEC [dbo].[LaneCost_Update] @LaneNewCost;

IF (@ERROR1 <> 0) OR (@ERROR2 <> 0)

	BEGIN
	ROLLBACK TRAN
	RAISERROR('Insert Procedure Failed!', 16, 1)
	RETURN 0
	END


COMMIT TRAN

RETURN 1
GO
