CREATE OR ALTER PROCEDURE [dbo].[TerminalCostWeightBreakLevel_Create]
	@AddedCostWeightBreakLevelTableType_Create CostWeightBreakLevelTableType_Create READONLY,
	@ServiceOfferingID BIGINT
AS

SET NOCOUNT ON;

BEGIN TRAN

DECLARE @ERROR1 INT, @ERROR2 INT, @ERROR3 INT, @ERROR4 INT, @ERROR5 INT;

-- insert new weight break levels

--DECLARE @InsertedCostWeightBreakLevel CostWeightBreakLevelTableType_ID;
--DECLARE @DeletedCostWeightBreakLevel CostWeightBreakLevelTableType_ID;

DECLARE @TerminalCostWeightBreakLevel table 
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

INSERT INTO [dbo].[TerminalCostWeightBreakLevel]
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
INTO @TerminalCostWeightBreakLevel
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

INSERT INTO [dbo].[TerminalCostWeightBreakLevel_History]
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
FROM @TerminalCostWeightBreakLevel WB 
INNER JOIN @ServiceOfferingVersionID SO ON WB.[ServiceOfferingID] = SO.[ServiceOfferingID]

--INSERT INTO @InsertedCostWeightBreakLevel
--(
--	[WeightBreakLevelID],
--	[ServiceOfferingID]
--)
--SELECT [WeightBreakLevelID],
--	[ServiceOfferingID]
--FROM @TerminalCostWeightBreakLevel

--SELECT @ERROR2 = @@ERROR;

---- Update The Cost table

--DECLARE @TerminalNewCost1 TerminalCostTableType_Update;

--INSERT INTO @TerminalNewCost1
--(
--	[TerminalCostID],
--	[Cost],
--	[IsIntraRegionMovementEnabled],
--	[IntraRegionMovementFactor]
--)
--SELECT [TerminalCostID], 
--	dbo.TerminalCost_Select(LC.Cost) AS Cost, 
--	LC.[IsIntraRegionMovementEnabled],
--	[IntraRegionMovementFactor]
--FROM dbo.TerminalCost LC
--WHERE LC.ServiceOfferingID = @ServiceOfferingID

--DECLARE @TerminalNewCost2 TerminalCostTableType_Update;

--INSERT INTO @TerminalNewCost2
--(
--	[TerminalCostID],
--	[Cost],
--	[IsIntraRegionMovementEnabled],
--	[IntraRegionMovementFactor]
--)
--SELECT LC.TerminalCostID, 
--	'{"CostComponents":{"CostByWeightBreak":"' + dbo.LaneCostWeightBreakLevel_Modify(LC.Cost, @InsertedCostWeightBreakLevel, @DeletedCostWeightBreakLevel, @ServiceOfferingID) + '","CrossDockCost":""}}' AS NewCost,
--	[IsIntraRegionMovementEnabled],
--	[IntraRegionMovementFactor]
--FROM @TerminalNewCost1 LC

--EXEC [dbo].[TerminalCost_Update] @TerminalNewCost2

IF (@ERROR1 <> 0) OR (@ERROR2 <> 0) 

	BEGIN
	ROLLBACK TRAN
	RAISERROR('Insert Procedure Failed!', 16, 1)
	RETURN 0
	END


COMMIT TRAN

RETURN 1
GO
