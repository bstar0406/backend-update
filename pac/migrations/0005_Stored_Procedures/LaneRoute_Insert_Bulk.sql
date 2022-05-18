CREATE OR ALTER PROCEDURE [dbo].[LaneRoute_Insert_Bulk]
	@LaneRouteTableType LaneRouteTableType READONLY,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ROWCOUNT1 INT, @ROWCOUNT2 INT, @InputCount INT;

SELECT @InputCount = Count(*) FROM 
(
SELECT [ServiceOfferingName], [OriginTerminalCode], [DestinationTerminalCode], [ServiceLevelCode], COUNT(*) AS NumLegs
FROM @LaneRouteTableType LR
GROUP BY [ServiceOfferingName], [OriginTerminalCode], [DestinationTerminalCode], [ServiceLevelCode]
) AS A

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

BEGIN TRAN

DECLARE @LaneRoute table 
( 
	[LaneRouteID] [bigint] NOT NULL,
	[LaneID]      BIGINT NOT NULL,
	[RouteLegs]          NVARCHAR (MAX) NOT NULL
)

DECLARE @LaneRouteJson table 
( 
	[LaneID]      BIGINT NOT NULL,
	[LaneVersionID]      BIGINT NOT NULL,
	[RouteLegs]          NVARCHAR (MAX) NOT NULL,
	[RouteLegsVersion]          NVARCHAR (MAX) NOT NULL
)

DECLARE @LaneRouteTableVersion table 
( 
	[LaneID]      BIGINT NOT NULL,
	[LaneVersionID]      BIGINT NOT NULL,
	[SeqNum] INT NOT NULL,
	[LegLaneID]      BIGINT NOT NULL,
	[LegOriginTerminalID]    BIGINT  NOT NULL,
	[LegDestinationTerminalID]    BIGINT NOT NULL,
	[LegLaneVersionID]      BIGINT NOT NULL,
	[LegOriginTerminalVersionID]    BIGINT  NOT NULL,
	[LegDestinationTerminalVersionID]    BIGINT NOT NULL,
	[LegOriginTerminalCode]    NVARCHAR (3)  NOT NULL,
	[LegDestinationTerminalCode]    NVARCHAR (3) NOT NULL,
	[LegServiceModeCode] NVARCHAR (1) NOT NULL,
	[LegServiceModeID] BIGINT NOT NULL,
	[LegServiceModeVersionID] BIGINT NOT NULL
)

DECLARE @LaneRouteTable table 
( 
	[LaneID]      BIGINT NOT NULL,
	[SeqNum] INT NOT NULL,
	[LegLaneID]      BIGINT NOT NULL,
	[LegOriginTerminalID]    BIGINT  NOT NULL,
	[LegDestinationTerminalID]    BIGINT NOT NULL,
	[LegOriginTerminalCode]    NVARCHAR (3)  NOT NULL,
	[LegDestinationTerminalCode]    NVARCHAR (3) NOT NULL,
	[LegServiceModeCode] NVARCHAR (1) NOT NULL,
	[LegServiceModeID] BIGINT NOT NULL
)

DECLARE @LaneRouteTableTypeID table
(
	[OriginTerminalID]   BIGINT  NOT NULL,
	[DestinationTerminalID]    BIGINT NOT NULL,
	[ServiceLevelID]  BIGINT NOT NULL,
	[SeqNum] INT NOT NULL,
	[LegOriginTerminalID]    BIGINT  NOT NULL,
	[LegDestinationTerminalID]    BIGINT NOT NULL,
	[LegOriginTerminalCode]    NVARCHAR (3)  NOT NULL,
	[LegDestinationTerminalCode]    NVARCHAR (3) NOT NULL,
	[LegServiceModeCode] NVARCHAR (1) NOT NULL,
	[LegServiceModeID] BIGINT NOT NULL
)

INSERT INTO @LaneRouteTableTypeID
(
	[OriginTerminalID],
	[DestinationTerminalID],
	[ServiceLevelID],
	[SeqNum],
	[LegOriginTerminalID],
	[LegDestinationTerminalID],
	[LegOriginTerminalCode],
	[LegDestinationTerminalCode],
	[LegServiceModeCode],
	[LegServiceModeID]
)
SELECT O.[TerminalID], 
	D.[TerminalID], 
	SL.ServiceLevelID, 
	DR.[SeqNum], 
	LO.[TerminalID], 
	LD.[TerminalID],
	DR.[LegOriginTerminalCode],
	DR.[LegDestinationTerminalCode],
	DR.[LegServiceModeCode],
	SM.[ServiceModeID]
FROM @LaneRouteTableType DR
INNER JOIN [dbo].[ServiceOffering] SO ON DR.[ServiceOfferingName] = SO.[ServiceOfferingName]
INNER JOIN [dbo].[ServiceLevel] SL ON SO.[ServiceOfferingID] = SL.[ServiceOfferingID] AND DR.[ServiceLevelCode] = SL.[ServiceLevelCode]
INNER JOIN [dbo].[Terminal] O ON DR.[OriginTerminalCode] = O.[TerminalCode]
INNER JOIN [dbo].[Terminal] D ON DR.[DestinationTerminalCode] = D.[TerminalCode]
INNER JOIN [dbo].[Terminal] LO ON DR.[LegOriginTerminalCode] = LO.[TerminalCode]
INNER JOIN [dbo].[Terminal] LD ON DR.[LegDestinationTerminalCode] = LD.[TerminalCode]
INNER JOIN [dbo].[ServiceMode] SM ON SO.[ServiceOfferingID] = SM.[ServiceOfferingID] AND DR.[LegServiceModeCode] = SM.[ServiceModeCode]

INSERT INTO @LaneRouteTable 
( 
	[LaneID],
	[SeqNum],
	[LegLaneID],
	[LegOriginTerminalID],
	[LegDestinationTerminalID],
	[LegOriginTerminalCode],
	[LegDestinationTerminalCode],
	[LegServiceModeCode],
	[LegServiceModeID]
)
SELECT L.LaneID,
	DR.[SeqNum],
	LL.[LaneID],
	DR.[LegOriginTerminalID],
	DR.[LegDestinationTerminalID],
	DR.[LegOriginTerminalCode],
	DR.[LegDestinationTerminalCode],
	DR.[LegServiceModeCode],
	DR.[LegServiceModeID]
FROM @LaneRouteTableTypeID DR
INNER JOIN [dbo].[Lane] L ON DR.[OriginTerminalID] = L.[OriginTerminalID] AND DR.[DestinationTerminalID] = L.[DestinationTerminalID] AND DR.[ServiceLevelID] = L.[ServiceLevelID]
INNER JOIN [dbo].[Lane] LL ON DR.[LegOriginTerminalID] = LL.[OriginTerminalID] AND DR.[LegDestinationTerminalID] = LL.[DestinationTerminalID] AND DR.[ServiceLevelID] = LL.[ServiceLevelID]

INSERT INTO @LaneRouteTableVersion 
( 
	[LaneID],
	[LaneVersionID],
	[SeqNum],
	[LegLaneID],
	[LegOriginTerminalID],
	[LegDestinationTerminalID],
	[LegLaneVersionID],
	[LegOriginTerminalVersionID],
	[LegDestinationTerminalVersionID],
	[LegOriginTerminalCode],
	[LegDestinationTerminalCode],
	[LegServiceModeCode],
	[LegServiceModeID],
	[LegServiceModeVersionID] 
)
SELECT	DR.[LaneID],
	L.[LaneVersionID],
	DR.[SeqNum],
	DR.[LegLaneID],
	DR.[LegOriginTerminalID],
	DR.[LegDestinationTerminalID],
	LL.[LaneVersionID],
	LL.[OriginTerminalVersionID],
	LL.[DestinationTerminalVersionID],
	DR.[LegOriginTerminalCode],
	DR.[LegDestinationTerminalCode],
	DR.[LegServiceModeCode],
	DR.[LegServiceModeID],
	SM.[ServiceModeVersionID] 
FROM @LaneRouteTable DR
INNER JOIN [dbo].[Lane_History] L ON DR.[LaneID] = L.[LaneID] AND L.[IsLatestVersion] = 1
INNER JOIN [dbo].[Lane_History] LL ON DR.[LegLaneID] = LL.[LaneID] AND LL.[IsLatestVersion] = 1
INNER JOIN [dbo].[ServiceMode_History] SM ON DR.[LegServiceModeID] = SM.[ServiceModeID] AND SM.[IsLatestVersion] = 1

INSERT INTO @LaneRouteJson 
( 
	[LaneID],
	[LaneVersionID],
	[RouteLegs],
	[RouteLegsVersion]
)
SELECT DISTINCT DR.[LaneID],
	DR.[LaneVersionID],
	(SELECT D.[SeqNum], D.[LegLaneID], D.[LegOriginTerminalID], D.[LegDestinationTerminalID], D.[LegOriginTerminalCode], D.[LegDestinationTerminalCode], D.[LegServiceModeCode], D.[LegServiceModeID] FROM @LaneRouteTableVersion D WHERE D.[LaneID] = DR.[LaneID] ORDER BY D.[SeqNum] FOR JSON AUTO) As RouteLegs,
	(SELECT D.[SeqNum], D.[LegLaneVersionID], D.[LegOriginTerminalVersionID], D.[LegDestinationTerminalVersionID], D.[LegOriginTerminalCode], D.[LegDestinationTerminalCode], D.[LegServiceModeCode], D.[LegServiceModeVersionID] FROM @LaneRouteTableVersion D WHERE D.[LaneID] = DR.[LaneID] ORDER BY D.[SeqNum] FOR JSON AUTO) As RouteLegsVersion
FROM @LaneRouteTableVersion DR

INSERT INTO [dbo].[LaneRoute]
(
	[LaneID],
	[RouteLegs],
	[IsActive],
	[IsInactiveViewable]
)
OUTPUT INSERTED.LaneRouteID, 
	 INSERTED.LaneID,
	 INSERTED.RouteLegs
INTO @LaneRoute
(
	[LaneRouteID],
	[LaneID],
	[RouteLegs]
)
SELECT [LaneID],
	[RouteLegs],
	1,
	1
FROM @LaneRouteJson

SELECT @ERROR1 = @@ERROR, @ROWCOUNT1 = @@ROWCOUNT

INSERT INTO [dbo].[LaneRoute_History]
(
	[LaneRouteID],
	[LaneVersionID],
	[RouteLegs],
	[IsActive],
	[VersionNum],
	[IsLatestVersion],
	[IsInactiveViewable],
	[UpdatedOn],
	[UpdatedBy],
	[Comments]
)
SELECT DR.[LaneRouteID],
	 J.[LaneVersionID],
	 J.[RouteLegsVersion],
	 1,
	 1,
	 1,
	 1,
	 GETUTCDATE(),
	 @UpdatedBy,
	 @Comments
FROM @LaneRoute DR
INNER JOIN @LaneRouteJson J ON DR.[LaneID] = J.[LaneID]

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
