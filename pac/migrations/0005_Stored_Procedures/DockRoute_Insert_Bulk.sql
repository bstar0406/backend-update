CREATE OR ALTER PROCEDURE [dbo].[DockRoute_Insert_Bulk]
	@DockRouteTableType DockRouteTableType READONLY,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ROWCOUNT1 INT, @ROWCOUNT2 INT, @InputCount INT;

SELECT @InputCount = Count(*) FROM 
(
SELECT [ServiceOfferingName], [OriginTerminalCode], [DestinationTerminalCode], [ServiceLevelCode], COUNT(*) AS NumLegs
FROM @DockRouteTableType DR
GROUP BY [ServiceOfferingName], [OriginTerminalCode], [DestinationTerminalCode], [ServiceLevelCode]
) AS A

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

BEGIN TRAN

DECLARE @DockRoute table 
( 
	[DockRouteID] [bigint] NOT NULL,
	[LaneID]      BIGINT NOT NULL,
	[RouteLegs]          NVARCHAR (MAX) NOT NULL
)

DECLARE @DockRouteJson table 
( 
	[LaneID]      BIGINT NOT NULL,
	[LaneVersionID]      BIGINT NOT NULL,
	[RouteLegs]          NVARCHAR (MAX) NOT NULL,
	[RouteLegsVersion]          NVARCHAR (MAX) NOT NULL
)

DECLARE @DockRouteTableVersion table 
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
	[LegDestinationTerminalCode]    NVARCHAR (3) NOT NULL
)

DECLARE @DockRouteTable table 
( 
	[LaneID]      BIGINT NOT NULL,
	[SeqNum] INT NOT NULL,
	[LegLaneID]      BIGINT NOT NULL,
	[LegOriginTerminalID]    BIGINT  NOT NULL,
	[LegDestinationTerminalID]    BIGINT NOT NULL,
	[LegOriginTerminalCode]    NVARCHAR (3)  NOT NULL,
	[LegDestinationTerminalCode]    NVARCHAR (3) NOT NULL
)

DECLARE @DockRouteTableTypeID table
(
	[OriginTerminalID]   BIGINT  NOT NULL,
	[DestinationTerminalID]    BIGINT NOT NULL,
	[ServiceLevelID]  BIGINT NOT NULL,
	[SeqNum] INT NOT NULL,
	[LegOriginTerminalID]    BIGINT  NOT NULL,
	[LegDestinationTerminalID]    BIGINT NOT NULL,
	[LegOriginTerminalCode]    NVARCHAR (3)  NOT NULL,
	[LegDestinationTerminalCode]    NVARCHAR (3) NOT NULL
)

INSERT INTO @DockRouteTableTypeID
(
	[OriginTerminalID],
	[DestinationTerminalID],
	[ServiceLevelID],
	[SeqNum],
	[LegOriginTerminalID],
	[LegDestinationTerminalID],
	[LegOriginTerminalCode],
	[LegDestinationTerminalCode]
)
SELECT O.[TerminalID], 
	D.[TerminalID], 
	SL.ServiceLevelID, 
	DR.[SeqNum], 
	LO.[TerminalID], 
	LD.[TerminalID],
	DR.[LegOriginTerminalCode],
	DR.[LegDestinationTerminalCode]
FROM @DockRouteTableType DR
INNER JOIN [dbo].[ServiceLevel] SL ON DR.[ServiceLevelCode] = SL.[ServiceLevelCode]
INNER JOIN [dbo].[ServiceOffering] SO ON SL.[ServiceOfferingID] = SO.[ServiceOfferingID] AND DR.[ServiceOfferingName] = SO.[ServiceOfferingName]
INNER JOIN [dbo].[Terminal] O ON DR.[OriginTerminalCode] = O.[TerminalCode]
INNER JOIN [dbo].[Terminal] D ON DR.[DestinationTerminalCode] = D.[TerminalCode]
INNER JOIN [dbo].[Terminal] LO ON DR.[LegOriginTerminalCode] = LO.[TerminalCode]
INNER JOIN [dbo].[Terminal] LD ON DR.[LegDestinationTerminalCode] = LD.[TerminalCode]

INSERT INTO @DockRouteTable 
( 
	[LaneID],
	[SeqNum],
	[LegLaneID],
	[LegOriginTerminalID],
	[LegDestinationTerminalID],
	[LegOriginTerminalCode],
	[LegDestinationTerminalCode]
)
SELECT L.LaneID,
	DR.[SeqNum],
	LL.[LaneID],
	DR.[LegOriginTerminalID],
	DR.[LegDestinationTerminalID],
	DR.[LegOriginTerminalCode],
	DR.[LegDestinationTerminalCode]
FROM @DockRouteTableTypeID DR
INNER JOIN [dbo].[Lane] L ON DR.[OriginTerminalID] = L.[OriginTerminalID] AND DR.[DestinationTerminalID] = L.[DestinationTerminalID] AND DR.[ServiceLevelID] = L.[ServiceLevelID]
INNER JOIN [dbo].[Lane] LL ON DR.[LegOriginTerminalID] = LL.[OriginTerminalID] AND DR.[LegDestinationTerminalID] = LL.[DestinationTerminalID] AND DR.[ServiceLevelID] = LL.[ServiceLevelID]

INSERT INTO @DockRouteTableVersion 
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
	[LegDestinationTerminalCode]
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
	DR.[LegDestinationTerminalCode]
FROM @DockRouteTable DR
INNER JOIN [dbo].[Lane_History] L ON DR.[LaneID] = L.[LaneID] AND L.[IsLatestVersion] = 1
INNER JOIN [dbo].[Lane_History] LL ON DR.[LegLaneID] = LL.[LaneID] AND LL.[IsLatestVersion] = 1


INSERT INTO @DockRouteJson 
( 
	[LaneID],
	[LaneVersionID],
	[RouteLegs],
	[RouteLegsVersion]
)
SELECT A.[LaneID], A.[LaneVersionID], MAX(A.RouteLegs) AS RouteLegs, MAX(A.RouteLegsVersion) AS RouteLegsVersion
FROM
(SELECT DR.[LaneID],
	DR.[LaneVersionID],
	(SELECT D.[SeqNum], D.[LegLaneID], D.[LegOriginTerminalID], D.[LegDestinationTerminalID], D.[LegOriginTerminalCode], D.[LegDestinationTerminalCode] FROM @DockRouteTableVersion D WHERE D.[LaneID] = DR.[LaneID] FOR JSON AUTO) As RouteLegs,
	(SELECT D.[SeqNum], D.[LegLaneVersionID], D.[LegOriginTerminalVersionID], D.[LegDestinationTerminalVersionID], D.[LegOriginTerminalCode], D.[LegDestinationTerminalCode] FROM @DockRouteTableVersion D WHERE D.[LaneID] = DR.[LaneID] FOR JSON AUTO) As RouteLegsVersion
FROM @DockRouteTableVersion DR) AS A
GROUP BY A.[LaneID], A.[LaneVersionID]

INSERT INTO [dbo].[DockRoute]
(
	[LaneID],
	[RouteLegs],
	[IsActive],
	[IsInactiveViewable]
)
OUTPUT INSERTED.DockRouteID, 
	 INSERTED.LaneID,
	 INSERTED.RouteLegs
INTO @DockRoute
(
	[DockRouteID],
	[LaneID],
	[RouteLegs]
)
SELECT [LaneID],
	[RouteLegs],
	1,
	1
FROM @DockRouteJson

SELECT @ERROR1 = @@ERROR, @ROWCOUNT1 = @@ROWCOUNT

INSERT INTO [dbo].[DockRoute_History]
(
	[DockRouteID],
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
SELECT DR.[DockRouteID],
	 J.[LaneVersionID],
	 J.[RouteLegsVersion],
	 1,
	 1,
	 1,
	 1,
	 GETUTCDATE(),
	 @UpdatedBy,
	 @Comments
FROM @DockRoute DR
INNER JOIN @DockRouteJson J ON DR.[LaneID] = J.[LaneID]

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
