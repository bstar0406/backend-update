CREATE OR ALTER PROCEDURE [dbo].[LegCost_Update]
	@LegCostTableType_Update LegCostTableType_Update READONLY
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ROWCOUNT1 INT,@InputCount INT;

SELECT @InputCount = Count(*) FROM @LegCostTableType_Update;

BEGIN TRAN

DECLARE @LegCost table 
( 
	[LegCostVersionID] [bigint] NOT NULL,
	[LegCostID] [bigint] NOT NULL,
	[LaneVersionID] [bigint] NOT NULL,
	[ServiceModeVersionID] [bigint] NOT NULL,
	[Cost] [nvarchar] (MAX) NOT NULL,
	[IsActive]           BIT           NOT NULL,
    [IsInactiveViewable] BIT           NOT NULL,
	[VersionNum] [int] NOT NULL
)

INSERT INTO @LegCost 
(	
	[LegCostVersionID],
	[LegCostID],
	[LaneVersionID],
	[ServiceModeVersionID],
	[Cost],
	[IsActive],
	[IsInactiveViewable],
	[VersionNum]
)
SELECT LCH.[LegCostVersionID],
	LC.[LegCostID],
	LCH.[LaneVersionID],
	LCH.[ServiceModeVersionID],
	LC.[Cost],
	LCH.[IsActive],
	LCH.[IsInactiveViewable],
	LCH.[VersionNum]
FROM [dbo].[LegCost_History] LCH
INNER JOIN @LegCostTableType_Update LC ON LCH.[LegCostID] = LC.[LegCostID] AND LCH.[IsLatestVersion] = 1

UPDATE [dbo].[LegCost]
SET [Cost] = A.[Cost]
FROM @LegCostTableType_Update AS A
WHERE [dbo].[LegCost].[LegCostID] = A.[LegCostID] 

UPDATE [dbo].[LegCost_History]
SET [IsLatestVersion] = 0
FROM @LegCost AS A
WHERE [dbo].[LegCost_History].[LegCostVersionID] = A.[LegCostVersionID]


INSERT INTO [dbo].[LegCost_History]
(
	[LegCostID],
	[LaneVersionID],
	[ServiceModeVersionID],
	[Cost],
	[IsActive],
	[VersionNum],
	[IsLatestVersion],
	[IsInactiveViewable],
	[UpdatedOn],
	[UpdatedBy],
	[Comments]
)
SELECT LC.[LegCostID],
	 LC.[LaneVersionID],
	 LC.[ServiceModeVersionID],
	 LC.[Cost],
	 LC.[IsActive],
	 LC.[VersionNum] + 1,
	 1,
	 LC.[IsInactiveViewable],
	 GETUTCDATE(),
	 'P&C System',
	 ''
FROM @LegCost LC

SELECT @ERROR1 = @@ERROR, @ROWCOUNT1 = @@ROWCOUNT 

IF (@ERROR1 <> 0) 

	BEGIN
	ROLLBACK TRAN
	RAISERROR('Insert Procedure Failed!', 16, 1)
	RETURN 0
	END

IF (@ROWCOUNT1 <> @InputCount) 
	
	BEGIN
	ROLLBACK TRAN
	RAISERROR('%d Records Affected by Insert Procedure while the expected number of record is %d!', 16, 1, @ROWCOUNT1,  @InputCount);
	RETURN 0
	END

COMMIT TRAN

RETURN 1

GO
