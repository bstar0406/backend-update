CREATE OR ALTER PROCEDURE [dbo].[City_Insert_Bulk]
	@CityTableType CityTableType READONLY,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ROWCOUNT1 INT, @ROWCOUNT2 INT, @InputCount INT;

SELECT @InputCount = Count(*) FROM @CityTableType;

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

DECLARE @City table 
( 
	[CityID] [bigint] NOT NULL,
	[CityName] [nvarchar](50) NOT NULL,
	[ProvinceID] [bigint] NOT NULL
)

BEGIN TRAN

DECLARE @CityWithProvinceID table 
( 
	[CityName] [nvarchar](50) NOT NULL,
	[ProvinceID] [bigint] NOT NULL
)

DECLARE @ProvinceVersionID table 
( 
	[ProvinceID] [bigint] NOT NULL,
	[ProvinceVersionID] [bigint] NOT NULL
)

INSERT INTO @CityWithProvinceID 
( 
	[CityName],
	[ProvinceID]
)
SELECT CTT.[CityName],
	P.[ProvinceID]
FROM @CityTableType CTT
INNER JOIN [dbo].[Province] P ON CTT.[ProvinceCode] = P.[ProvinceCode]
INNER JOIN [dbo].[Region] R ON P.[RegionID] = R.[RegionID]
INNER JOIN [dbo].[Country] C ON R.[CountryID] = C.[CountryID] AND CTT.[CountryCode] = C.[CountryCode]

INSERT INTO @ProvinceVersionID 
( 
	[ProvinceID],
	[ProvinceVersionID]
)
SELECT [ProvinceID],
	[ProvinceVersionID]
FROM [dbo].[Province_History]
WHERE [IsLatestVersion] = 1
AND [ProvinceID] IN (SELECT DISTINCT [ProvinceID] FROM @CityWithProvinceID)


INSERT INTO [dbo].[City]
(
	[CityName],
	[ProvinceID],
	[IsActive],
	[IsInactiveViewable]
)
OUTPUT INSERTED.CityID,
	 INSERTED.CityName,
	 INSERTED.ProvinceID
INTO @City
(
	[CityID],
	[CityName],
	[ProvinceID]
)
SELECT [CityName],
	[ProvinceID],
	1,
	1
FROM @CityWithProvinceID

SELECT @ERROR1 = @@ERROR, @ROWCOUNT1 = @@ROWCOUNT  

INSERT INTO [dbo].[City_History]
(
	[CityID],
	[CityName],
	[ProvinceVersionID],
	[IsActive],
	[VersionNum],
	[IsLatestVersion],
	[IsInactiveViewable],
	[UpdatedOn],
	[UpdatedBy],
	[Comments]
)
SELECT C.[CityID],
	 C.[CityName],
	 PVID.[ProvinceVersionID],
	 1,
	 1,
	 1,
	 1,
	 GETUTCDATE(),
	 @UpdatedBy,
	 @Comments
FROM @City C
INNER JOIN @ProvinceVersionID PVID ON C.[ProvinceID] = PVID.[ProvinceID]

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
