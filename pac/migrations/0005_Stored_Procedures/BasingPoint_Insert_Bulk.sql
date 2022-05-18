CREATE OR ALTER PROCEDURE [dbo].[BasingPoint_Insert_Bulk]
	@BasingPointTableType BasingPointTableType READONLY,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ROWCOUNT1 INT, @ROWCOUNT2 INT, @InputCount INT;

SELECT @InputCount = Count(*) FROM @BasingPointTableType;

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

DECLARE @BasingPoint table 
( 
	[BasingPointID] [bigint] NOT NULL,
	[BasingPointName] [nvarchar](50) NOT NULL,
	[ProvinceID] [bigint] NOT NULL
)

BEGIN TRAN

INSERT INTO [dbo].[BasingPoint]
(
	[BasingPointName],
	[ProvinceID],
	[IsActive],
	[IsInactiveViewable]
)
OUTPUT INSERTED.BasingPointID,
	 INSERTED.BasingPointName,
	 INSERTED.ProvinceID
INTO @BasingPoint
(
	[BasingPointID],
	[BasingPointName],
	[ProvinceID]
)
SELECT [BasingPointName],
	P.[ProvinceID],
	1,
	1
FROM @BasingPointTableType BP
INNER JOIN dbo.Country C ON BP.CountryCode = C.CountryCode
INNER JOIN dbo.Region R ON C.CountryID = R.CountryID
INNER JOIN dbo.Province P ON R.RegionID = P.RegionID AND P.ProvinceCode = BP.ProvinceCode

SELECT @ERROR1 = @@ERROR, @ROWCOUNT1 = @@ROWCOUNT  

INSERT INTO [dbo].[BasingPoint_History]
(
	[BasingPointID],
	[BasingPointName],
	[ProvinceVersionID],
	[IsActive],
	[VersionNum],
	[IsLatestVersion],
	[IsInactiveViewable],
	[UpdatedOn],
	[UpdatedBy],
	[Comments]
)
SELECT [BasingPointID],
	 [BasingPointName],
	 [ProvinceVersionID],
	 1,
	 1,
	 1,
	 1,
	 GETUTCDATE(),
	 @UpdatedBy,
	 @Comments
FROM @BasingPoint BP
INNER JOIN dbo.Province_History PH ON BP.ProvinceID = PH.ProvinceID AND PH.IsLatestVersion = 1

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
