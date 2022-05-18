CREATE OR ALTER PROCEDURE [dbo].[SubServiceLevel_Insert_Bulk]
	@SubServiceLevelTableType SubServiceLevelTableType READONLY,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ROWCOUNT1 INT, @ROWCOUNT2 INT, @InputCount INT;

SELECT @InputCount = Count(*) FROM @SubServiceLevelTableType;

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

DECLARE @SubServiceLevel table 
( 
	[SubServiceLevelID] [bigint] NOT NULL,
	[SubServiceLevelName] [nvarchar](50) NOT NULL,
	[SubServiceLevelCode] [nvarchar](2) NOT NULL,
	[ServiceLevelID] [bigint] NOT NULL
)

BEGIN TRAN

DECLARE @ServiceLevelVersionID table 
( 
	[ServiceLevelID] [bigint] NOT NULL,
	[ServiceLevelVersionID] [bigint] NOT NULL
)

INSERT INTO [dbo].[SubServiceLevel]
(
	[SubServiceLevelName],
	[SubServiceLevelCode],
	[ServiceLevelID],
	[IsActive],
	[IsInactiveViewable]
)
OUTPUT INSERTED.SubServiceLevelID,
	 INSERTED.SubServiceLevelName,
	 INSERTED.SubServiceLevelCode,
	 INSERTED.[ServiceLevelID]
INTO @SubServiceLevel
(
	[SubServiceLevelID],
	[SubServiceLevelName],
	[SubServiceLevelCode],
	[ServiceLevelID]
)
SELECT [SubServiceLevelName],
	[SubServiceLevelCode],
	[ServiceLevelID],
	1,
	1
FROM @SubServiceLevelTableType

SELECT @ERROR1 = @@ERROR, @ROWCOUNT1 = @@ROWCOUNT  

INSERT INTO @ServiceLevelVersionID 
( 
	[ServiceLevelID],
	[ServiceLevelVersionID]
)
SELECT [ServiceLevelID],
	[ServiceLevelVersionID]
FROM [dbo].[ServiceLevel_History]
WHERE [IsLatestVersion] = 1
AND [ServiceLevelID] IN (SELECT DISTINCT [ServiceLevelID] FROM @SubServiceLevelTableType)


INSERT INTO [dbo].[SubServiceLevel_History]
(
	[SubServiceLevelID],
	[SubServiceLevelName],
	[SubServiceLevelCode],
	[ServiceLevelVersionID],
	[IsActive],
	[VersionNum],
	[IsLatestVersion],
	[IsInactiveViewable],
	[UpdatedOn],
	[UpdatedBy],
	[Comments]
)
SELECT S.[SubServiceLevelID],
	 S.[SubServiceLevelName],
	 S.[SubServiceLevelCode],
	 SVID.[ServiceLevelVersionID],
	 1,
	 1,
	 1,
	 1,
	 GETUTCDATE(),
	 @UpdatedBy,
	 @Comments
FROM @SubServiceLevel S
INNER JOIN @ServiceLevelVersionID SVID ON S.[ServiceLevelID] = SVID.[ServiceLevelID]

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
