CREATE OR ALTER PROCEDURE [dbo].[PostalCode_Insert_Bulk]
	@PostalCodeTableType PostalCodeTableType READONLY,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ROWCOUNT1 INT, @ROWCOUNT2 INT, @InputCount INT;

SELECT @InputCount = Count(*) FROM @PostalCodeTableType;

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

BEGIN TRAN

DECLARE @PostalCode table 
( 
	[PostalCodeID] [bigint] NOT NULL,
	[PostalCodeName] [varchar](50) NOT NULL,
	[ServicePointID] [bigint] NOT NULL
)

DECLARE @ServicePointVersionID table 
( 
	[ServicePointID] [bigint] NOT NULL,
	[ServicePointVersionID] [bigint] NOT NULL
)

INSERT INTO [dbo].[PostalCode]
(
	[PostalCodeName],
	[ServicePointID],
	[IsActive],
	[IsInactiveViewable]
)
OUTPUT INSERTED.PostalCodeID,
	 INSERTED.PostalCodeName,
	 INSERTED.[ServicePointID]
INTO @PostalCode
(
	[PostalCodeID],
	[PostalCodeName],
	[ServicePointID]
)
SELECT [PostalCodeName],
	[ServicePointID],
	1,
	1
FROM @PostalCodeTableType PC
INNER JOIN dbo.ServicePoint SP ON PC.ServicePointName = SP.ServicePointName
INNER JOIN dbo.Province P ON P.ProvinceID = SP.ProvinceID AND P.ProvinceCode = PC.ProvinceCode


SELECT @ERROR1 = @@ERROR, @ROWCOUNT1 = @@ROWCOUNT  

INSERT INTO @ServicePointVersionID 
( 
	[ServicePointID],
	[ServicePointVersionID]
)
SELECT [ServicePointID],
	[ServicePointVersionID]
FROM [dbo].[ServicePoint_History]
WHERE [IsLatestVersion] = 1
AND [ServicePointID] IN (SELECT DISTINCT [ServicePointID] FROM @PostalCode)

INSERT INTO [dbo].[PostalCode_History]
(
	[PostalCodeID],
	[PostalCodeName],
	[ServicePointVersionID],
	[IsActive],
	[VersionNum],
	[IsLatestVersion],
	[IsInactiveViewable],
	[UpdatedOn],
	[UpdatedBy],
	[Comments]
)
SELECT SP.[PostalCodeID],
	 SP.[PostalCodeName],
	 BVID.[ServicePointVersionID],
	 1,
	 1,
	 1,
	 1,
	 GETUTCDATE(),
	 @UpdatedBy,
	 @Comments
FROM @PostalCode SP
LEFT JOIN @ServicePointVersionID BVID ON SP.[ServicePointID] = BVID.[ServicePointID]

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
