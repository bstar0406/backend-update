CREATE OR ALTER PROCEDURE [dbo].[LaneCost_Update]
	@LaneCostTableType_Update LaneCostTableType_Update READONLY
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ROWCOUNT1 INT, @InputCount INT;

SELECT @InputCount = Count(*) FROM @LaneCostTableType_Update;

BEGIN TRAN

DECLARE @LaneCost table 
( 
	[LaneCostVersionID] [bigint] NOT NULL,
	[LaneCostID] [bigint] NOT NULL,
	[LaneVersionID] [bigint] NOT NULL,
	[MinimumCost] [decimal](19,6) NOT NULL,
	[Cost] [nvarchar] (MAX) NOT NULL,
	[IsActive]           BIT           NOT NULL,
    [IsInactiveViewable] BIT           NOT NULL,
	[VersionNum] [int] NOT NULL
)

INSERT INTO @LaneCost 
(	
	[LaneCostVersionID],
	[LaneCostID],
	[LaneVersionID],
	[MinimumCost],
	[Cost],
	[IsActive],
	[IsInactiveViewable],
	[VersionNum]
)
SELECT LCH.[LaneCostVersionID],
	LC.[LaneCostID],
	LCH.[LaneVersionID],
	LC.[MinimumCost],
	LC.[Cost],
	LCH.[IsActive],
	LCH.[IsInactiveViewable],
	LCH.[VersionNum]
FROM [dbo].[LaneCost_History] LCH
INNER JOIN @LaneCostTableType_Update LC ON LCH.[LaneCostID] = LC.[LaneCostID] AND LCH.[IsLatestVersion] = 1

UPDATE [dbo].[LaneCost]
SET [MinimumCost] = A.[MinimumCost],
	[Cost] = A.[Cost]
FROM @LaneCostTableType_Update AS A
WHERE [dbo].[LaneCost].[LaneCostID] = A.[LaneCostID]

UPDATE [dbo].[LaneCost_History]
SET [IsLatestVersion] = 0
FROM @LaneCost AS A
WHERE [dbo].[LaneCost_History].[LaneCostVersionID] = A.[LaneCostVersionID]


INSERT INTO [dbo].[LaneCost_History]
(
	[LaneCostID],
	[LaneVersionID],
	[MinimumCost],
	[Cost],
	[IsActive],
	[VersionNum],
	[IsLatestVersion],
	[IsInactiveViewable],
	[UpdatedOn],
	[UpdatedBy],
	[Comments]
)
SELECT LC.[LaneCostID],
	 LC.[LaneVersionID],
	 LC.[MinimumCost],
	 LC.[Cost],
	 LC.[IsActive],
	 LC.[VersionNum] + 1,
	 1,
	 LC.[IsInactiveViewable],
	 GETUTCDATE(),
	 'P&C System',
	 'Updated Lane Cost'
FROM @LaneCost LC

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
