CREATE OR ALTER PROCEDURE [dbo].[Lane_Update]
	@LaneTableType_Update LaneTableType_Update READONLY
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ROWCOUNT1 INT, @InputCount INT;

SELECT @InputCount = Count(*) FROM @LaneTableType_Update;

BEGIN TRAN

DECLARE @Lane table 
( 
	[LaneVersionID] [bigint] NOT NULL,
	[LaneID] [bigint] NOT NULL,
	[OriginTerminalVersionID] [bigint] NOT NULL,
	[DestinationTerminalVersionID] [bigint] NOT NULL,
	[ServiceLevelVersionID] [bigint] NOT NULL,
	[IsHeadhaul]           BIT           NOT NULL,
	[IsActive]           BIT           NOT NULL,
    [IsInactiveViewable] BIT           NOT NULL,
	[VersionNum] [int] NOT NULL
)

INSERT INTO @Lane 
(	
	[LaneVersionID],
	[LaneID],
	[OriginTerminalVersionID],
	[DestinationTerminalVersionID],
	[ServiceLevelVersionID],
	[IsHeadhaul],
	[IsActive],
	[IsInactiveViewable],
	[VersionNum]
)
SELECT LH.[LaneVersionID],
	L.[LaneID],
	LH.[OriginTerminalVersionID],
	LH.[DestinationTerminalVersionID],
	LH.[ServiceLevelVersionID],
	L.[IsHeadhaul],
	L.[IsActive],
	L.[IsInactiveViewable],
	LH.[VersionNum]
FROM [dbo].[Lane_History] LH
INNER JOIN @LaneTableType_Update L ON LH.[LaneID] = L.[LaneID] AND LH.[IsLatestVersion] = 1

UPDATE [dbo].[Lane]
SET [IsHeadhaul] = A.[IsHeadhaul],
	[IsActive] = A.[IsActive],
	[IsInactiveViewable] = A.[IsInactiveViewable]
FROM @LaneTableType_Update AS A
WHERE [dbo].[Lane].[LaneID] = A.[LaneID] 

UPDATE [dbo].[Lane_History]
SET [IsLatestVersion] = 0
FROM @Lane AS A
WHERE [dbo].[Lane_History].[LaneVersionID] = A.[LaneVersionID]


INSERT INTO [dbo].[Lane_History]
(
	[LaneID],
	[OriginTerminalVersionID],
	[DestinationTerminalVersionID],
	[ServiceLevelVersionID],
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
	 L.[OriginTerminalVersionID],
	 L.[DestinationTerminalVersionID],
	 L.[ServiceLevelVersionID],
	 L.[IsHeadhaul],
	 L.[IsActive],
	 L.[VersionNum] + 1,
	 1,
	 L.[IsInactiveViewable],
	 GETUTCDATE(),
	 'P&C System',
	 ''
FROM @Lane L

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
