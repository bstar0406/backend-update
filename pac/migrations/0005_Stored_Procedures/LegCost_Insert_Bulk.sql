CREATE OR ALTER PROCEDURE [dbo].[LegCost_Insert_Bulk]
	@LegCostTableType LegCostTableType READONLY,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ROWCOUNT1 INT, @ROWCOUNT2 INT, @InputCount INT;

SELECT @InputCount = Count(*) FROM @LegCostTableType;

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

BEGIN TRAN

DECLARE @LegCost table 
( 
	[LegCostID] [bigint] NOT NULL,
	[LaneID] [bigint] NOT NULL,
	[ServiceModeID] [bigint] NOT NULL,
	[Cost] [nvarchar] (MAX) NOT NULL
)

DECLARE @LegCostWithLaneIDServiceLevelID table 
( 
	[LaneID] [bigint] NOT NULL,
	[ServiceModeID] [bigint] NOT NULL,
	[Cost] [nvarchar] (MAX) NOT NULL
)

DECLARE @LaneVersionID table 
( 
	[LaneID] [bigint] NOT NULL,
	[LaneVersionID] [bigint] NOT NULL
)

DECLARE @ServiceModeVersionID table 
( 
	[ServiceModeID] [bigint] NOT NULL,
	[ServiceModeVersionID] [bigint] NOT NULL
)

INSERT INTO @LegCostWithLaneIDServiceLevelID 
( 
	[LaneID],
	[ServiceModeID],
	[Cost]
)
SELECT L.[LaneID],
	SM.[ServiceModeID],
	LCTT.[Cost]
FROM @LegCostTableType LCTT
INNER JOIN [dbo].[Terminal] O ON LCTT.[OriginTerminalCode] = O.[TerminalCode] 
INNER JOIN [dbo].[Terminal] D ON LCTT.[DestinationTerminalCode] = D.[TerminalCode] 
INNER JOIN [dbo].[ServiceOffering] SO ON LCTT.[ServiceOfferingName] = SO.[ServiceOfferingName] 
INNER JOIN [dbo].[ServiceLevel] SL ON SO.[ServiceOfferingID] = SL.[ServiceOfferingID] AND SL.[ServiceLevelCode] = LCTT.[ServiceLevelCode]
INNER JOIN [dbo].[Lane] L ON L.[OriginTerminalID] = O.[TerminalID] AND L.[DestinationTerminalID] = D.[TerminalID] AND L.[ServiceLevelID] = SL.[ServiceLevelID]
INNER JOIN [dbo].[ServiceMode] SM ON SO.[ServiceOfferingID] = SM.[ServiceOfferingID] AND SM.[ServiceModeCode] = LCTT.[ServiceModeCode]

INSERT INTO @LaneVersionID 
( 
	[LaneID],
	[LaneVersionID]
)
SELECT [LaneID],
	[LaneVersionID]
FROM [dbo].[Lane_History]
WHERE [IsLatestVersion] = 1
AND [LaneID] IN (SELECT DISTINCT [LaneID] FROM @LegCostWithLaneIDServiceLevelID)

INSERT INTO @ServiceModeVersionID 
( 
	[ServiceModeID],
	[ServiceModeVersionID]
)
SELECT [ServiceModeID],
	[ServiceModeVersionID]
FROM [dbo].[ServiceMode_History]
WHERE [IsLatestVersion] = 1
AND [ServiceModeID] IN (SELECT DISTINCT [ServiceModeID] FROM @LegCostWithLaneIDServiceLevelID)

INSERT INTO [dbo].[LegCost]
(
	[LaneID],
	[ServiceModeID],
	[Cost],
	[IsActive],
	[IsInactiveViewable]
)
OUTPUT INSERTED.LegCostID,
	 INSERTED.LaneID,
	 INSERTED.[ServiceModeID],
	 INSERTED.Cost
INTO @LegCost
(
	[LegCostID],
	[LaneID],
	[ServiceModeID],
	[Cost]
)
SELECT [LaneID],
	[ServiceModeID],
	[Cost],
	1,
	1
FROM @LegCostWithLaneIDServiceLevelID

SELECT @ERROR1 = @@ERROR, @ROWCOUNT1 = @@ROWCOUNT  

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
	 LVID.[LaneVersionID],
	 SMVID.[ServiceModeVersionID],
	 LC.[Cost],
	 1,
	 1,
	 1,
	 1,
	 GETUTCDATE(),
	 @UpdatedBy,
	 @Comments
FROM @LegCost LC
INNER JOIN @LaneVersionID LVID ON LC.[LaneID] = LVID.[LaneID]
INNER JOIN @ServiceModeVersionID SMVID ON LC.[ServiceModeID] = SMVID.[ServiceModeID]

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
