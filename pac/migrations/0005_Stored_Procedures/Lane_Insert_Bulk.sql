SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE   PROCEDURE [dbo].[Lane_Insert_Bulk]
	@LaneTableType LaneTableType READONLY,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ROWCOUNT1 INT, @ROWCOUNT2 INT, @InputCount INT;

SELECT @InputCount = Count(*) FROM @LaneTableType;

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

BEGIN TRAN

DECLARE @Lane table
(
	[LaneID] [bigint] NOT NULL,
	[OriginTerminalID]      BIGINT NOT NULL,
    [DestinationTerminalID] BIGINT NOT NULL,
	[SubServiceLevelID]        BIGINT NOT NULL,
	[IsHeadhaul]            BIT    NOT NULL
)

DECLARE @LaneWithOrigDestID table
(
	[OriginTerminalID]      BIGINT NOT NULL,
    [DestinationTerminalID] BIGINT NOT NULL,
	[SubServiceLevelID] BIGINT NOT NULL,
	[IsHeadhaul]            BIT    NOT NULL
)

DECLARE @OriginTerminalVersionID table
(
	[TerminalID] [bigint] NOT NULL,
	[TerminalVersionID] [bigint] NOT NULL
)

DECLARE @DestinationTerminalVersionID table
(
	[TerminalID] [bigint] NOT NULL,
	[TerminalVersionID] [bigint] NOT NULL
)

DECLARE @SubServiceLevelVersionID table
(
	[SubServiceLevelID] [bigint] NOT NULL,
	[SubServiceLevelVersionID] [bigint] NOT NULL
)

INSERT INTO @LaneWithOrigDestID
(
	[OriginTerminalID],
    [DestinationTerminalID],
	[SubServiceLevelID],
	[IsHeadhaul]
)
SELECT O.[TerminalID],
	D.[TerminalID],
	SSL.[SubServiceLevelID],
	LTT.[IsHeadhaul]
FROM @LaneTableType LTT
INNER JOIN [dbo].[Terminal] O ON LTT.[OriginTerminalCode] = O.[TerminalCode]
INNER JOIN [dbo].[Terminal] D ON LTT.[DestinationTerminalCode] = D.[TerminalCode]
INNER JOIN [dbo].[ServiceOffering] SO ON LTT.[ServiceOfferingName] = SO.[ServiceOfferingName]
INNER JOIN [dbo].[ServiceLevel] SL ON SO.[ServiceOfferingID] = SL.[ServiceOfferingID]
INNER JOIN [dbo].[SubServiceLevel] SSL ON SSL.[ServiceLevelID] = SL.[ServiceLevelID] AND LTT.[SubServiceLevelCode] = SSL.[SubServiceLevelCode]

INSERT INTO @OriginTerminalVersionID
(
	[TerminalID],
	[TerminalVersionID]
)
SELECT [TerminalID],
	[TerminalVersionID]
FROM [dbo].[Terminal_History]
WHERE [IsLatestVersion] = 1
AND [TerminalID] IN (SELECT DISTINCT [OriginTerminalID] FROM @LaneWithOrigDestID)

INSERT INTO @DestinationTerminalVersionID
(
	[TerminalID],
	[TerminalVersionID]
)
SELECT [TerminalID],
	[TerminalVersionID]
FROM [dbo].[Terminal_History]
WHERE [IsLatestVersion] = 1
AND [TerminalID] IN (SELECT DISTINCT [DestinationTerminalID] FROM @LaneWithOrigDestID)

INSERT INTO @SubServiceLevelVersionID
(
	[SubServiceLevelID],
	[SubServiceLevelVersionID]
)
SELECT [SubServiceLevelID],
	[SubServiceLevelVersionID]
FROM [dbo].[SubServiceLevel_History] SLH
WHERE SLH.[IsLatestVersion] = 1
AND [SubServiceLevelID] IN (SELECT DISTINCT [SubServiceLevelID] FROM @LaneWithOrigDestID)

INSERT INTO [dbo].[Lane]
(
	[OriginTerminalID],
    [DestinationTerminalID],
	[ServiceLevelID],
	[IsHeadhaul],
	[IsActive],
	[IsInactiveViewable]
)
OUTPUT INSERTED.LaneID,
	 INSERTED.OriginTerminalID,
	 INSERTED.DestinationTerminalID,
	 INSERTED.[ServiceLevelID],
	 INSERTED.[IsHeadhaul]
INTO @Lane
(
	[LaneID],
	[OriginTerminalID],
	[DestinationTerminalID],
	[SubServiceLevelID],
	[IsHeadhaul]
)
SELECT [OriginTerminalID],
	[DestinationTerminalID],
	[SubServiceLevelID],
	[IsHeadhaul],
	1,
	1
FROM @LaneWithOrigDestID

SELECT @ERROR1 = @@ERROR, @ROWCOUNT1 = @@ROWCOUNT

INSERT INTO [dbo].[Lane_History]
(
	[LaneID],
	[OriginTerminalVersionID],
	[DestinationTerminalVersionID],
	[SubServiceLevelVersionID],
	[IsHeadhaul],
	[IsActive],
	[VersionNum],
	[IsLatestVersion],
	[IsInactiveViewable],
	[UpdatedOn],
	[UpdatedBy],
	[Comments]
)
SELECT L.[LaneID],
	 OVID.[TerminalVersionID],
	 DVID.[TerminalVersionID],
	 SLH.[SubServiceLevelVersionID],
	 L.[IsHeadhaul],
	 1,
	 1,
	 1,
	 1,
	 GETUTCDATE(),
	 @UpdatedBy,
	 @Comments
FROM @Lane L
INNER JOIN @OriginTerminalVersionID OVID ON L.[OriginTerminalID] = OVID.[TerminalID]
INNER JOIN @DestinationTerminalVersionID DVID ON L.[DestinationTerminalID] = DVID.[TerminalID]
INNER JOIN @SubServiceLevelVersionID SLH ON SLH.[SubServiceLevelID] = L.[SubServiceLevelID]

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
