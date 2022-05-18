CREATE OR ALTER PROCEDURE [dbo].[ServiceMode_Insert_Bulk]
	@ServiceModeTableType ServiceModeTableType READONLY,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ROWCOUNT1 INT, @ROWCOUNT2 INT, @InputCount INT;

SELECT @InputCount = Count(*) FROM @ServiceModeTableType;

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

DECLARE @ServiceMode table 
( 
	[ServiceModeID] [bigint] NOT NULL,
	[ServiceModeName] [nvarchar](50) NOT NULL,
	[ServiceModeCode] [nvarchar](1) NOT NULL,
	[ServiceOfferingID] [bigint] NOT NULL
)

BEGIN TRAN

DECLARE @ServiceModeWithServiceOfferingID table 
( 
	[ServiceModeName] [nvarchar](50) NOT NULL,
	[ServiceModeCode] [nvarchar](1) NOT NULL,
	[ServiceOfferingID] [bigint] NOT NULL
)

DECLARE @ServiceOfferingVersionID table 
( 
	[ServiceOfferingID] [bigint] NOT NULL,
	[ServiceOfferingVersionID] [bigint] NOT NULL
)

INSERT INTO @ServiceModeWithServiceOfferingID 
( 
	[ServiceModeName],
	[ServiceModeCode],
	[ServiceOfferingID]
)
SELECT SMTT.[ServiceModeName],
	SMTT.[ServiceModeCode],
	S.[ServiceOfferingID]
FROM @ServiceModeTableType SMTT
INNER JOIN [dbo].[ServiceOffering] S ON SMTT.[ServiceOfferingName] = S.[ServiceOfferingName]

INSERT INTO @ServiceOfferingVersionID 
( 
	[ServiceOfferingID],
	[ServiceOfferingVersionID]
)
SELECT [ServiceOfferingID],
	[ServiceOfferingVersionID]
FROM [dbo].[ServiceOffering_History]
WHERE [IsLatestVersion] = 1
AND [ServiceOfferingID] IN (SELECT DISTINCT [ServiceOfferingID] FROM @ServiceModeWithServiceOfferingID)


INSERT INTO [dbo].[ServiceMode]
(
	[ServiceModeName],
	[ServiceModeCode],
	[ServiceOfferingID],
	[IsActive],
	[IsInactiveViewable]
)
OUTPUT INSERTED.ServiceModeID,
	 INSERTED.ServiceModeName,
	 INSERTED.ServiceModeCode,
	 INSERTED.ServiceOfferingID
INTO @ServiceMode
(
	[ServiceModeID],
	[ServiceModeName],
	[ServiceModeCode],
	[ServiceOfferingID]
)
SELECT [ServiceModeName],
	[ServiceModeCode],
	[ServiceOfferingID],
	1,
	1
FROM @ServiceModeWithServiceOfferingID

SELECT @ERROR1 = @@ERROR, @ROWCOUNT1 = @@ROWCOUNT  

INSERT INTO [dbo].[ServiceMode_History]
(
	[ServiceModeID],
	[ServiceModeName],
	[ServiceModeCode],
	[ServiceOfferingVersionID],
	[IsActive],
	[VersionNum],
	[IsLatestVersion],
	[IsInactiveViewable],
	[UpdatedOn],
	[UpdatedBy],
	[Comments]
)
SELECT S.[ServiceModeID],
	 S.[ServiceModeName],
	 S.[ServiceModeCode],
	 SVID.[ServiceOfferingVersionID],
	 1,
	 1,
	 1,
	 1,
	 GETUTCDATE(),
	 @UpdatedBy,
	 @Comments
FROM @ServiceMode S
INNER JOIN @ServiceOfferingVersionID SVID ON S.[ServiceOfferingID] = SVID.[ServiceOfferingID]

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
