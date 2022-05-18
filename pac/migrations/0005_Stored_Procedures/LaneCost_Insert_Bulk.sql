CREATE OR ALTER PROCEDURE [dbo].[LaneCost_Insert_Bulk]
	@LaneCostTableType LaneCostTableType READONLY,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ROWCOUNT1 INT, @ROWCOUNT2 INT, @InputCount INT;

SELECT @InputCount = Count(*) FROM @LaneCostTableType;

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

BEGIN TRAN

DECLARE @LaneCost table 
( 
	[LaneCostID] [bigint] NOT NULL,
	[LaneID] [bigint] NOT NULL,
	[MinimumCost] [decimal](19,6) NOT NULL,
	[Cost] [nvarchar] (MAX) NOT NULL
)

DECLARE @LaneCostWithLaneIDServiceLevelID table 
( 
	[LaneID] [bigint] NOT NULL,
	[MinimumCost] [decimal](19,6) NOT NULL,
	[Cost] [nvarchar] (MAX) NOT NULL
)

DECLARE @LaneVersionID table 
( 
	[LaneID] [bigint] NOT NULL,
	[LaneVersionID] [bigint] NOT NULL
)

INSERT INTO @LaneCostWithLaneIDServiceLevelID 
( 
	[LaneID],
	[MinimumCost],
	[Cost]
)
SELECT L.[LaneID],
	LCTT.[MinimumCost],
	LCTT.[Cost]
FROM @LaneCostTableType LCTT
INNER JOIN [dbo].[Terminal] O ON LCTT.[OriginTerminalCode] = O.[TerminalCode] 
INNER JOIN [dbo].[Terminal] D ON LCTT.[DestinationTerminalCode] = D.[TerminalCode] 
INNER JOIN [dbo].[ServiceOffering] SO ON LCTT.[ServiceOfferingName] = SO.[ServiceOfferingName] 
INNER JOIN [dbo].[ServiceLevel] SL ON SO.[ServiceOfferingID] = SL.[ServiceOfferingID] AND SL.[ServiceLevelCode] = LCTT.[ServiceLevelCode]
INNER JOIN [dbo].[Lane] L ON L.[OriginTerminalID] = O.[TerminalID] AND L.[DestinationTerminalID] = D.[TerminalID] AND L.[ServiceLevelID] = SL.[ServiceLevelID]

INSERT INTO @LaneVersionID 
( 
	[LaneID],
	[LaneVersionID]
)
SELECT [LaneID],
	[LaneVersionID]
FROM [dbo].[Lane_History]
WHERE [IsLatestVersion] = 1
AND [LaneID] IN (SELECT DISTINCT [LaneID] FROM @LaneCostWithLaneIDServiceLevelID)

INSERT INTO [dbo].[LaneCost]
(
	[LaneID],
	[MinimumCost],
	[Cost],
	[IsActive],
	[IsInactiveViewable]
)
OUTPUT INSERTED.LaneCostID,
	 INSERTED.LaneID,
	 INSERTED.[MinimumCost],
	 INSERTED.Cost
INTO @LaneCost
(
	[LaneCostID],
	[LaneID],
	[MinimumCost],
	[Cost]
)
SELECT [LaneID],
	[MinimumCost],
	[Cost],
	1,
	1
FROM @LaneCostWithLaneIDServiceLevelID

SELECT @ERROR1 = @@ERROR, @ROWCOUNT1 = @@ROWCOUNT  

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
	 LVID.[LaneVersionID],
	 LC.[MinimumCost],
	 LC.[Cost],
	 1,
	 1,
	 1,
	 1,
	 GETUTCDATE(),
	 @UpdatedBy,
	 @Comments
FROM @LaneCost LC
INNER JOIN @LaneVersionID LVID ON LC.[LaneID] = LVID.[LaneID]

SELECT @ERROR2 = @@ERROR, @ROWCOUNT2 = @@ROWCOUNT 

IF (@ERROR1 <> 0) OR (@ERROR2 <> 0)

	BEGIN
	ROLLBACK TRAN
	RAISERROR('Insert Procedure Failed!', 16, 1)
	RETURN 0
	END

IF (@ROWCOUNT1 <> @InputCount) OR (@ROWCOUNT2 <> @InputCount)
	
	BEGIN
	ROLLBACK TRAN
	IF (@ROWCOUNT1 <> @InputCount)
		RAISERROR('%d Records Affected by Insert Procedure while the expected number of record is %d!', 16, 1, @ROWCOUNT1,  @InputCount);
	IF (@ROWCOUNT2 <> @InputCount)
		RAISERROR('%d Records Affected by Insert Procedure while the expected number of record is %d!', 16, 1, @ROWCOUNT2, @InputCount);
	RETURN 0
	END

COMMIT TRAN

RETURN 1

GO
