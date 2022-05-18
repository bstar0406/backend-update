CREATE OR ALTER PROCEDURE [dbo].[ServicePoint_Insert_Bulk]
	@ServicePointTableType ServicePointTableType READONLY,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ROWCOUNT1 INT, @ROWCOUNT2 INT, @InputCount INT;

SELECT @InputCount = Count(*) FROM @ServicePointTableType;

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

BEGIN TRAN

DECLARE @ServicePoint table 
( 
	[ServicePointID] [bigint] NOT NULL,
	[ServicePointName] [varchar](50) NOT NULL,
	[ProvinceID] [bigint] NOT NULL,
	[BasingPointID] [bigint] NULL
)

DECLARE @BasingPointVersionID table 
( 
	[BasingPointID] [bigint] NOT NULL,
	[BasingPointVersionID] [bigint] NOT NULL
)

DECLARE @ProvinceVersionID table 
( 
	[ProvinceID] [bigint] NOT NULL,
	[ProvinceVersionID] [bigint] NOT NULL
)

INSERT INTO [dbo].[ServicePoint]
(
	[ServicePointName],
	[BasingPointID],
	[ProvinceID],
	[IsActive],
	[IsInactiveViewable]
)
OUTPUT INSERTED.ServicePointID,
	 INSERTED.ServicePointName,
	 INSERTED.[BasingPointID],
	 INSERTED.[ProvinceID]
INTO @ServicePoint
(
	[ServicePointID],
	[ServicePointName],
	[BasingPointID],
	[ProvinceID]
)
SELECT [ServicePointName],
	[BasingPointID],
	P.[ProvinceID],
	1,
	1
FROM @ServicePointTableType SP
INNER JOIN dbo.Province P ON SP.ProvinceCode = P.ProvinceCode
LEFT JOIN dbo.BasingPoint BP ON P.ProvinceID = BP.ProvinceID AND SP.BasingPointName = BP.BasingPointName


SELECT @ERROR1 = @@ERROR, @ROWCOUNT1 = @@ROWCOUNT  

INSERT INTO @BasingPointVersionID 
( 
	[BasingPointID],
	[BasingPointVersionID]
)
SELECT [BasingPointID],
	[BasingPointVersionID]
FROM [dbo].[BasingPoint_History]
WHERE [IsLatestVersion] = 1
AND [BasingPointID] IN (SELECT DISTINCT [BasingPointID] FROM @ServicePoint)

INSERT INTO @ProvinceVersionID 
( 
	[ProvinceID],
	[ProvinceVersionID]
)
SELECT [ProvinceID],
	[ProvinceVersionID]
FROM [dbo].[Province_History]
WHERE [IsLatestVersion] = 1
AND [ProvinceID] IN (SELECT DISTINCT [ProvinceID] FROM @ServicePoint)

INSERT INTO [dbo].[ServicePoint_History]
(
	[ServicePointID],
	[ServicePointName],
	[BasingPointVersionID],
	[ProvinceVersionID],
	[IsActive],
	[VersionNum],
	[IsLatestVersion],
	[IsInactiveViewable],
	[UpdatedOn],
	[UpdatedBy],
	[Comments]
)
SELECT SP.[ServicePointID],
	 SP.[ServicePointName],
	 BVID.[BasingPointVersionID],
	 PVID.[ProvinceVersionID],
	 1,
	 1,
	 1,
	 1,
	 GETUTCDATE(),
	 @UpdatedBy,
	 @Comments
FROM @ServicePoint SP
INNER JOIN @ProvinceVersionID PVID ON SP.[ProvinceID] = PVID.[ProvinceID]
LEFT JOIN @BasingPointVersionID BVID ON SP.[BasingPointID] = BVID.[BasingPointID]

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
