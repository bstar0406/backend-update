CREATE OR ALTER PROCEDURE [dbo].[LegCost_Create]
	@LegCostTableType_Create LegCostTableType_Create READONLY
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ROWCOUNT1 INT, @ROWCOUNT2 INT, @InputCount INT;

SELECT @InputCount = Count(*) FROM @LegCostTableType_Create;

BEGIN TRAN

DECLARE @ExistingDeletedLanes LaneTableType_Update;

INSERT INTO @ExistingDeletedLanes
(
	[LaneID],
	[IsHeadhaul],
	[IsActive],
	[IsInactiveViewable]
)
SELECT DISTINCT L.LaneID, L.[IsHeadhaul], 1, 1
FROM dbo.Lane L
INNER JOIN @LegCostTableType_Create LC ON L.[OriginTerminalID] = LC.[OriginTerminalID]
	AND L.[DestinationTerminalID] = LC.[DestinationTerminalID] 
	AND L.[ServiceLevelID] = LC.[ServiceLevelID]
WHERE L.[IsActive] = 0 OR L.[IsInactiveViewable] = 0

EXEC [dbo].[Lane_Update] @ExistingDeletedLanes

DECLARE @LaneTableType LaneTableType;

DECLARE @TempLaneTableType AS table
(
	[ServiceOfferingName] [nvarchar](50) NOT NULL,
	[OriginTerminalCode]    NVARCHAR (3)  NOT NULL,
	[DestinationTerminalCode]    NVARCHAR (3) NOT NULL,
	[SubServiceLevelCode]  NVARCHAR (2) NOT NULL,
	[OriginTerminalID] BIGINT NOT NULL,
	[DestinationTerminalID] BIGINT NOT NULL,
	[SubServiceLevelID] BIGINT NOT NULL
)

INSERT INTO @TempLaneTableType
(
	[ServiceOfferingName],
	[OriginTerminalCode],
	[DestinationTerminalCode],
	[SubServiceLevelCode],
	[OriginTerminalID],
	[DestinationTerminalID],
	[SubServiceLevelID]
)
SELECT SO.[ServiceOfferingName],
	O.TerminalCode,
	D.TerminalCode,
	ssl.[SubServiceLevelCode],
	LC.[OriginTerminalID],
	LC.[DestinationTerminalID],
	LC.[SubServiceLevelID]
FROM @LegCostTableType_Create LC
INNER JOIN dbo.Terminal O ON LC.[OriginTerminalID] = O.TerminalID
INNER JOIN dbo.Terminal D ON LC.[DestinationTerminalID] = D.TerminalID
INNER JOIN dbo.SubServiceLevel ssl ON ssl.SubServiceLevelID = lc.SubServiceLevelID
INNER JOIN dbo.ServiceLevel SL ON ssl.ServiceLevelID = SL.ServiceLevelID
INNER JOIN dbo.ServiceOffering SO ON SL.ServiceOfferingID = SO.ServiceOfferingID
EXCEPT 
SELECT SO.[ServiceOfferingName],
	O.TerminalCode,
	D.TerminalCode,
	ssl.[SubServiceLevelCode],
	L.[OriginTerminalID],
	L.[DestinationTerminalID],
	L.[SubServiceLevelID]
FROM dbo.Lane L 
INNER JOIN dbo.Terminal O ON L.[OriginTerminalID] = O.TerminalID
INNER JOIN dbo.Terminal D ON L.[DestinationTerminalID] = D.TerminalID
INNER JOIN dbo.SubServiceLevel ssl ON ssl.SubServiceLevelID = l.SubServiceLevelID
INNER JOIN dbo.ServiceLevel SL ON ssl.ServiceLevelID = SL.ServiceLevelID
INNER JOIN dbo.ServiceOffering SO ON SL.ServiceOfferingID = SO.ServiceOfferingID

INSERT INTO @LaneTableType
(
	[ServiceOfferingName],
	[OriginTerminalCode],
	[DestinationTerminalCode],
	[SubServiceLevelCode],
	[IsHeadhaul]
)
SELECT T.[ServiceOfferingName],
	T.[OriginTerminalCode],
	T.[DestinationTerminalCode],
	T.[SubServiceLevelCode],
	LC.[IsHeadhaul]
FROM @TempLaneTableType T
INNER JOIN @LegCostTableType_Create LC ON LC.[OriginTerminalID] = T.[OriginTerminalID]
AND LC.[DestinationTerminalID] = T.[DestinationTerminalID]
AND LC.SubServiceLevelID = T.SubServiceLevelID

EXEC [dbo].[Lane_Insert_Bulk] @LaneTableType

DECLARE @LegCostTableType_Create_ID TABLE
(
	[LaneID] BIGINT NOT NULL,
	[ServiceModeID] BIGINT NOT NULL,
	[Cost] NVARCHAR(MAX)
)

INSERT INTO @LegCostTableType_Create_ID
(
	[LaneID],
	[ServiceModeID],
	[Cost]
)
SELECT L.[LaneID],
	LC.[ServiceModeID],
	LC.[Cost]
FROM @LegCostTableType_Create LC
INNER JOIN dbo.Lane L ON L.[OriginTerminalID] = LC.[OriginTerminalID]
	AND L.[DestinationTerminalID] = LC.[DestinationTerminalID] 
	AND L.[SubServiceLevelID] = LC.[SubServiceLevelID]

DECLARE @ExistingDeletedLegCosts TABLE
(
	[LegCostID] BIGINT NOT NULL,
	[LaneID] BIGINT NOT NULL,
	[ServiceModeID] BIGINT NOT NULL,
	[Cost] NVARCHAR(MAX)
)

INSERT INTO @ExistingDeletedLegCosts
(
	[LegCostID],
	[LaneID],
	[ServiceModeID],
	[Cost]
)
SELECT LC.[LegCostID], 
	LC.[LaneID],
	LC.[ServiceModeID],
	LCT.[Cost]
FROM @LegCostTableType_Create_ID LCT
INNER JOIN dbo.LegCost LC ON LCT.LaneID = LC.LaneID AND LCT.ServiceModeID = LC.ServiceModeID

DECLARE @LegCostTableType_Update LegCostTableType_Update;

INSERT INTO @LegCostTableType_Update
(
	[LegCostID],
	[Cost]
)
SELECT [LegCostID],
	[Cost]
FROM @ExistingDeletedLegCosts

EXEC [dbo].[LegCost_Update] @ExistingDeletedLegCosts;

DECLARE @LegCost table 
( 
	[LegCostID] [bigint] NOT NULL,
	[LaneID] [bigint] NOT NULL,
	[ServiceModeID] [bigint] NOT NULL,
	[Cost] [nvarchar] (MAX) NOT NULL
)

DECLARE @LegCostID table 
( 
	[LaneID] [bigint] NOT NULL,
	[ServiceModeID] [bigint] NOT NULL,
	[Cost] [nvarchar] (MAX) NOT NULL
)

DECLARE @NewRecords table
(
	[LaneID] [bigint] NOT NULL,
	[ServiceModeID] [bigint] NOT NULL
)

INSERT INTO @NewRecords
(
	[LaneID],
	[ServiceModeID]
)
SELECT [LaneID], [ServiceModeID] FROM @LegCostTableType_Create_ID
EXCEPT
SELECT [LaneID], [ServiceModeID] FROM @ExistingDeletedLegCosts

INSERT INTO @LegCostID
(
	[LaneID],
	[ServiceModeID],
	[Cost]
)
SELECT LC.[LaneID],
	LC.[ServiceModeID],
	LC.[Cost]
FROM @LegCostTableType_Create_ID LC
INNER JOIN @NewRecords N ON LC.[LaneID] = N.[LaneID] 
	AND LC.[ServiceModeID] = N.[ServiceModeID] 

DECLARE @LaneVersionID table 
( 
	[LaneID] [bigint] NOT NULL,
	[LaneVersionID] [bigint] NOT NULL
)

INSERT INTO @LaneVersionID 
( 
	[LaneID],
	[LaneVersionID]
)
SELECT [LaneID],
	[LaneVersionID]
FROM [dbo].[Lane_History]
WHERE [IsLatestVersion] = 1
AND [LaneID] IN (SELECT DISTINCT [LaneID] FROM @LegCostID)

DECLARE @ServiceModeVersionID table 
( 
	[ServiceModeID] [bigint] NOT NULL,
	[ServiceModeVersionID] [bigint] NOT NULL
)

INSERT INTO @ServiceModeVersionID 
( 
	[ServiceModeID],
	[ServiceModeVersionID]
)
SELECT [ServiceModeID],
	[ServiceModeVersionID]
FROM [dbo].[ServiceMode_History]
WHERE [IsLatestVersion] = 1
AND [ServiceModeID] IN (SELECT DISTINCT [ServiceModeID] FROM @LegCostID)

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
FROM @LegCostID

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
	 'P&C System',
	 ''
FROM @LegCost LC
INNER JOIN @LaneVersionID LVID ON LC.[LaneID] = LVID.[LaneID]
INNER JOIN @ServiceModeVersionID SMVID ON LC.ServiceModeID = SMVID.ServiceModeID

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
