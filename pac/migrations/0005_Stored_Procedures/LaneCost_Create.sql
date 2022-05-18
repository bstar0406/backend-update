CREATE OR ALTER PROCEDURE [dbo].[LaneCost_Create]
	@LaneCostTableType_Create LaneCostTableType_Create READONLY
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ROWCOUNT1 INT, @ROWCOUNT2 INT, @InputCount INT;

SELECT @InputCount = Count(*) FROM @LaneCostTableType_Create;

BEGIN TRAN

DECLARE @ExistingDeleted AS TABLE
(
	[LaneID] [bigint] NOT NULL,
	[IsHeadhaul] [bit] NOT NULL,
	[MinimumCost] [decimal](19,6) NOT NULL,
	[Cost] [nvarchar](MAX) NOT NULL
)

INSERT INTO @ExistingDeleted
(
	[LaneID],
	[IsHeadhaul],
	[MinimumCost],
	[Cost]
)
SELECT L.LaneID, 
	LC.[IsHeadhaul], 
	LC.[MinimumCost], 
	LC.[Cost]
FROM dbo.Lane L
INNER JOIN @LaneCostTableType_Create LC ON L.[OriginTerminalID] = LC.[OriginTerminalID]
	AND L.[DestinationTerminalID] = LC.[DestinationTerminalID] 
	AND L.[SubServiceLevelID] = LC.[SubServiceLevelID]
WHERE L.[IsActive] = 0 OR L.[IsInactiveViewable] = 0

DECLARE @ExistingDeletedLanes LaneTableType_Update;

INSERT INTO @ExistingDeletedLanes
(
	[LaneID],
	[IsHeadhaul],
	[IsActive],
	[IsInactiveViewable]
)
SELECT L.[LaneID], L.[IsHeadhaul], 1, 1
FROM @ExistingDeleted L

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
	SSL.[SubServiceLevelCode],
	LC.[OriginTerminalID],
	LC.[DestinationTerminalID],
	LC.[SubServiceLevelID]
FROM @LaneCostTableType_Create LC
INNER JOIN dbo.Terminal O ON LC.[OriginTerminalID] = O.TerminalID
INNER JOIN dbo.Terminal D ON LC.[DestinationTerminalID] = D.TerminalID
INNER JOIN dbo.SubServiceLevel SSL ON LC.SubServiceLevelID = SSL.SubServiceLevelID
INNER JOIN dbo.ServiceLevel SL ON SL.ServiceLevelID = SSL.ServiceLevelID
INNER JOIN dbo.ServiceOffering SO ON SL.ServiceOfferingID = SO.ServiceOfferingID
EXCEPT 
SELECT SO.[ServiceOfferingName],
	O.TerminalCode,
	D.TerminalCode,
	SSL.[SubServiceLevelCode],
	L.[OriginTerminalID],
	L.[DestinationTerminalID],
	L.[SubServiceLevelID]
FROM dbo.Lane L 
INNER JOIN dbo.Terminal O ON L.[OriginTerminalID] = O.TerminalID
INNER JOIN dbo.Terminal D ON L.[DestinationTerminalID] = D.TerminalID
INNER JOIN dbo.SubServiceLevel SSL ON L.SubServiceLevelID = SSL.SubServiceLevelID
INNER JOIN dbo.ServiceLevel SL ON SSL.ServiceLevelID = SL.ServiceLevelID
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
INNER JOIN @LaneCostTableType_Create LC ON LC.[OriginTerminalID] = T.[OriginTerminalID]
AND LC.[DestinationTerminalID] = T.[DestinationTerminalID]
AND LC.SubServiceLevelID = T.SubServiceLevelID

EXEC [dbo].[Lane_Insert_Bulk] @LaneTableType

DECLARE @LaneCostTableType_Create_ID TABLE
(
	[LaneID] BIGINT NOT NULL,
	[MinimumCost] DECIMAL(19,6) NOT NULL,
	[Cost] NVARCHAR(MAX) NOT NULL
)

INSERT INTO  @LaneCostTableType_Create_ID
(
	[LaneID],
	[MinimumCost],
	[Cost]
)

SELECT L.[LaneID],
	LC.[MinimumCost],
	LC.[Cost]
FROM dbo.Lane L
INNER JOIN @LaneCostTableType_Create LC ON L.[OriginTerminalID] = LC.[OriginTerminalID]
	AND L.[DestinationTerminalID] = LC.[DestinationTerminalID] 
	AND L.[SubServiceLevelID] = LC.[SubServiceLevelID]

DECLARE @ExistingDeletedLaneCosts LaneCostTableType_Update;

INSERT INTO @ExistingDeletedLaneCosts
(
	[LaneCostID],
	[MinimumCost],
	[Cost]
)
SELECT LC.[LaneCostID], 
	LCT.[MinimumCost], 
	LCT.[Cost]
FROM @LaneCostTableType_Create_ID LCT 
INNER JOIN dbo.LaneCost LC ON LCT.[LaneID] = LC.[LaneID]

EXEC [dbo].[LaneCost_Update] @ExistingDeletedLaneCosts

DECLARE @LaneCost table 
( 
	[LaneCostID] [bigint] NOT NULL,
	[LaneID] [bigint] NOT NULL,
	[MinimumCost] [decimal](19,6) NOT NULL,
	[Cost] [nvarchar] (MAX) NOT NULL
)

DECLARE @LaneCostID table 
( 
	[LaneID] [bigint] NOT NULL,
	[MinimumCost] [decimal](19,6) NOT NULL,
	[Cost] [nvarchar] (MAX) NOT NULL
)

INSERT INTO @LaneCostID
(
	[LaneID],
	[MinimumCost],
	[Cost]
)
SELECT LC.[LaneID],
	LC.[MinimumCost],
	LC.[Cost]
FROM @LaneCostTableType_Create_ID LC
WHERE LC.[LaneID] NOT IN (SELECT NC.LaneID FROM dbo.LaneCost NC INNER JOIN @ExistingDeletedLaneCosts ENC ON NC.LaneCostID = ENC.LaneCostID)

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
AND [LaneID] IN (SELECT DISTINCT [LaneID] FROM @LaneCostID)

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
FROM @LaneCostID

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
	 'P&C System',
	 ''
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
