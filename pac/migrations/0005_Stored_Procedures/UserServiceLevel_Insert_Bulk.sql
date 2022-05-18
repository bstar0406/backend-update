CREATE OR ALTER PROCEDURE [dbo].[UserServiceLevel_Insert_Bulk]
	@UserServiceLevelTableType UserServiceLevelTableType READONLY,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ROWCOUNT1 INT, @ROWCOUNT2 INT, @InputCount INT;

SELECT @InputCount = Count(*) FROM @UserServiceLevelTableType;

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

DECLARE @UserServiceLevel table 
( 
	[UserServiceLevelID] [bigint] NOT NULL,
	[UserID] [bigint] NOT NULL,
	[ServiceLevelID] [bigint] NOT NULL
)

BEGIN TRAN

DECLARE @UserVersionID table 
( 
	[UserID] [bigint] NOT NULL,
	[UserVersionID] [bigint] NOT NULL
)

INSERT INTO @UserVersionID 
( 
	[UserID],
	[UserVersionID]
)
SELECT [UserID],
	[UserVersionID]
FROM [dbo].[User_History]
WHERE [IsLatestVersion] = 1
AND [UserID] IN (SELECT DISTINCT [UserID] FROM @UserServiceLevelTableType)


DECLARE @ServiceLevelVersionID table 
( 
	[ServiceLevelID] [bigint] NOT NULL,
	[ServiceLevelVersionID] [bigint] NOT NULL
)

INSERT INTO @ServiceLevelVersionID 
( 
	[ServiceLevelID],
	[ServiceLevelVersionID]
)
SELECT [ServiceLevelID],
	[ServiceLevelVersionID]
FROM [dbo].[ServiceLevel_History]
WHERE [IsLatestVersion] = 1
AND [ServiceLevelID] IN (SELECT DISTINCT [ServiceLevelID] FROM @UserServiceLevelTableType)


INSERT INTO [dbo].[UserServiceLevel]
(
	[UserID],
	[ServiceLevelID],
	[IsActive],
	[IsInactiveViewable]
)
OUTPUT INSERTED.[UserServiceLevelID],
	 INSERTED.[UserID],
	 INSERTED.[ServiceLevelID]
INTO @UserServiceLevel
(
	[UserServiceLevelID],
	[UserID],
	[ServiceLevelID]
)
SELECT [UserID],
	[ServiceLevelID],
	1,
	1
FROM @UserServiceLevelTableType

SELECT @ERROR1 = @@ERROR, @ROWCOUNT1 = @@ROWCOUNT  

INSERT INTO [dbo].[UserServiceLevel_History]
(
	[UserServiceLevelID],
	[UserVersionID],
	[ServiceLevelVersionID],
	[IsActive],
	[VersionNum],
	[IsLatestVersion],
	[IsInactiveViewable],
	[UpdatedOn],
	[UpdatedBy],
	[Comments]
)
SELECT USL.[UserServiceLevelID],
	 UVID.[UserVersionID],
	 SLVID.[ServiceLevelVersionID],
	 1,
	 1,
	 1,
	 1,
	 GETUTCDATE(),
	 @UpdatedBy,
	 @Comments
FROM @UserServiceLevel USL
INNER JOIN @UserVersionID UVID ON USL.[UserID] = UVID.[UserID]
INNER JOIN @ServiceLevelVersionID SLVID ON USL.[ServiceLevelID] = SLVID.[ServiceLevelID]

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
