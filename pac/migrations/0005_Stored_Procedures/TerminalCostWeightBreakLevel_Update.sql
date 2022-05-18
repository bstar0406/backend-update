CREATE OR ALTER PROCEDURE [dbo].[TerminalCostWeightBreakLevel_Update]
	@UpdatedCostWeightBreakLevel CostWeightBreakLevelTableType_Update READONLY,
	@ServiceOfferingID BIGINT
AS

SET NOCOUNT ON;

BEGIN TRAN

DECLARE @ERROR1 INT, @ERROR2 INT, @ERROR3 INT;

--DECLARE @InsertedCostWeightBreakLevel CostWeightBreakLevelTableType_ID;
--DECLARE @DeletedCostWeightBreakLevel CostWeightBreakLevelTableType_ID;

--INSERT INTO @InsertedCostWeightBreakLevel
--(
--	[WeightBreakLevelID],
--	[ServiceOfferingID]
--)
--SELECT LC.[WeightBreakLevelID],
--	LC.[ServiceOfferingID]
--FROM dbo.TerminalCostWeightBreakLevel LC 
--INNER JOIN @UpdatedCostWeightBreakLevel N ON LC.[WeightBreakLevelID] = N.[WeightBreakLevelID] 
--WHERE LC.[IsActive] = 0 AND N.[IsActive] = 1

--INSERT INTO @DeletedCostWeightBreakLevel
--(
--	[WeightBreakLevelID],
--	[ServiceOfferingID]
--)
--SELECT LC.[WeightBreakLevelID],
--	LC.[ServiceOfferingID]
--FROM dbo.TerminalCostWeightBreakLevel LC 
--INNER JOIN @UpdatedCostWeightBreakLevel N ON LC.[WeightBreakLevelID] = N.[WeightBreakLevelID] 
--WHERE LC.[IsActive] = 1 AND N.[IsActive] = 0

--DECLARE @InsertedCount INT, @DeletedCount INT;

--SELECT @InsertedCount = COUNT(*) FROM @InsertedCostWeightBreakLevel;
--SELECT @DeletedCount = COUNT(*) FROM @DeletedCostWeightBreakLevel;

--IF @InsertedCount > 0 OR @DeletedCount > 0
--BEGIN
--	DECLARE @TerminalNewCost1 TerminalCostTableType_Update;

--	INSERT INTO @TerminalNewCost1
--	(
--		[TerminalCostID],
--		[Cost],
--		[IsIntraRegionMovementEnabled],
--		[IntraRegionMovementFactor]
--	)
--	SELECT [TerminalCostID], 
--		dbo.TerminalCost_Select(LC.Cost) AS Cost, 
--		LC.[IsIntraRegionMovementEnabled],
--		[IntraRegionMovementFactor]
--	FROM dbo.TerminalCost LC
--	WHERE LC.ServiceOfferingID = @ServiceOfferingID

--	DECLARE @TerminalNewCost2 TerminalCostTableType_Update;

--	INSERT INTO @TerminalNewCost2
--	(
--		[TerminalCostID],
--		[Cost],
--		[IsIntraRegionMovementEnabled],
--		[IntraRegionMovementFactor]
--	)
--	SELECT LC.TerminalCostID, 
--		'{"CostComponents":{"CostByWeightBreak":"' + dbo.LaneCostWeightBreakLevel_Modify(LC.Cost, @InsertedCostWeightBreakLevel, @DeletedCostWeightBreakLevel, @ServiceOfferingID) + '","CrossDockCost":""}}' AS NewCost,
--		[IsIntraRegionMovementEnabled],
--		[IntraRegionMovementFactor]
--	FROM @TerminalNewCost1 LC

--	EXEC [dbo].[TerminalCost_Update] @TerminalNewCost2
--END

-- Update the dbo table with the latest values

UPDATE dbo.TerminalCostWeightBreakLevel
SET [WeightBreakLevelName] = A.[WeightBreakLevelName],
[WeightBreakLowerBound] = A.[WeightBreakLowerBound],
[IsActive] = A.[IsActive]
FROM @UpdatedCostWeightBreakLevel AS A
WHERE dbo.TerminalCostWeightBreakLevel.[WeightBreakLevelID] = A.[WeightBreakLevelID]

SELECT @ERROR1 = @@ERROR;

DECLARE @UpdateIDTableType table 
( 
	[WeightBreakLevelID] [bigint] NOT NULL,
	[WeightBreakLevelVersionID] [bigint] NOT NULL,
	[VersionNum] [int] NOT NULL,
	[IsInactiveViewable] [bit] NOT NULL,
	[ServiceOfferingVersionID] [bigint] NOT NULL
)

INSERT INTO @UpdateIDTableType
(
	[WeightBreakLevelID],
	[WeightBreakLevelVersionID],
	[VersionNum],
	[IsInactiveViewable],
	[ServiceOfferingVersionID]
)
SELECT WBH.[WeightBreakLevelID],
	WBH.[WeightBreakLevelVersionID],
	WBH.[VersionNum],
	WBH.[IsInactiveViewable],
	WBH.[ServiceOfferingVersionID]
FROM dbo.TerminalCostWeightBreakLevel_History WBH
INNER JOIN @UpdatedCostWeightBreakLevel WB ON WBH.[WeightBreakLevelID] = WB.[WeightBreakLevelID] AND WBH.IsLatestVersion = 1

-- Set the history.IsLatestVersion to zero

UPDATE dbo.TerminalCostWeightBreakLevel_History
SET IsLatestVersion = 0
FROM @UpdateIDTableType AS U
WHERE dbo.TerminalCostWeightBreakLevel_History.[WeightBreakLevelVersionID] = U.[WeightBreakLevelVersionID]

SELECT @ERROR2 = @@ERROR;

-- Insert new records in the history table.

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
	WBH.[ServiceOfferingVersionID],
	WB.[IsActive],
	WBH.[VersionNum] + 1,
	1,
	WBH.[IsInactiveViewable],
	GETUTCDATE(),
	'P&C System',
	'Updated Weight break levels'
FROM @UpdateIDTableType WBH
INNER JOIN @UpdatedCostWeightBreakLevel WB ON WBH.[WeightBreakLevelID] = WB.[WeightBreakLevelID]

SELECT @ERROR3 = @@ERROR;

IF (@ERROR1 <> 0) OR (@ERROR2 <> 0) OR (@ERROR3 <> 0)

	BEGIN
	ROLLBACK TRAN
	RAISERROR('Insert Procedure Failed!', 16, 1)
	RETURN 0
	END


COMMIT TRAN

RETURN 1
GO
