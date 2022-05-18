CREATE OR ALTER PROCEDURE [dbo].[Terminal_Insert_Bulk]
	@TerminalTableType TerminalTableType READONLY,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ROWCOUNT1 INT, @ROWCOUNT2 INT, @InputCount INT;

SELECT @InputCount = Count(*) FROM @TerminalTableType;

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

DECLARE @Terminal table 
( 
	[TerminalID] [bigint] NOT NULL,
	[TerminalName] [nvarchar](50) NOT NULL,
	[TerminalCode] [nvarchar] (3) NOT NULL,
	[CityID] [bigint] NOT NULL,
	[RegionID] [bigint] NOT NULL
)

BEGIN TRAN

DECLARE @TerminalWithCityIDRegionID table 
( 
	[TerminalName] [nvarchar](50) NOT NULL,
	[TerminalCode] [nvarchar] (3) NOT NULL,
	[CityID] [bigint] NOT NULL,
	[RegionID] [bigint] NOT NULL
)

DECLARE @CityVersionID table 
( 
	[CityID] [bigint] NOT NULL,
	[CityVersionID] [bigint] NOT NULL
)

DECLARE @RegionVersionID table 
( 
	[RegionID] [bigint] NOT NULL,
	[RegionVersionID] [bigint] NOT NULL
)

INSERT INTO @TerminalWithCityIDRegionID 
( 
	[TerminalName],
	[TerminalCode],
	[CityID],
	[RegionID]
)
SELECT TTT.[TerminalName],
	TTT.[TerminalCode],
	Y.[CityID],
	O.[RegionID]
FROM @TerminalTableType TTT
INNER JOIN [dbo].[City] Y ON TTT.[CityName] = Y.[CityName] 
INNER JOIN [dbo].[Province] P ON Y.[ProvinceID] = P.[ProvinceID] AND TTT.[ProvinceCode] = P.[ProvinceCode]
INNER JOIN [dbo].[Region] R ON P.[RegionID] = R.[RegionID]
INNER JOIN [dbo].[Country] C ON R.[CountryID] = C.[CountryID] AND TTT.[CountryCode] = C.[CountryCode]
INNER JOIN [dbo].[Region] O ON TTT.[RegionCode] = O.[RegionCode] AND TTT.[RegionCode] = O.[RegionCode]

INSERT INTO @CityVersionID 
( 
	[CityID],
	[CityVersionID]
)
SELECT [CityID],
	[CityVersionID]
FROM [dbo].[City_History]
WHERE [IsLatestVersion] = 1
AND [CityID] IN (SELECT DISTINCT [CityID] FROM @TerminalWithCityIDRegionID)

INSERT INTO @RegionVersionID 
( 
	[RegionID],
	[RegionVersionID]
)
SELECT [RegionID],
	[RegionVersionID]
FROM [dbo].[Region_History]
WHERE [IsLatestVersion] = 1
AND [RegionID] IN (SELECT DISTINCT [RegionID] FROM @TerminalWithCityIDRegionID)


INSERT INTO [dbo].[Terminal]
(
	[TerminalName],
	[TerminalCode],
	[CityID],
	[RegionID],
	[IsActive],
	[IsInactiveViewable]
)
OUTPUT INSERTED.TerminalID,
	 INSERTED.TerminalName,
	 INSERTED.TerminalCode,
	 INSERTED.CityID,
	 INSERTED.RegionID
INTO @Terminal
(
	[TerminalID],
	[TerminalName],
	[TerminalCode],
	[CityID],
	[RegionID]
)
SELECT [TerminalName],
	[TerminalCode],
	[CityID],
	[RegionID],
	1,
	1
FROM @TerminalWithCityIDRegionID

SELECT @ERROR1 = @@ERROR, @ROWCOUNT1 = @@ROWCOUNT  

INSERT INTO [dbo].[Terminal_History]
(
	[TerminalID],
	[TerminalName],
	[TerminalCode],
	[CityVersionID],
	[RegionVersionID],
	[IsActive],
	[VersionNum],
	[IsLatestVersion],
	[IsInactiveViewable],
	[UpdatedOn],
	[UpdatedBy],
	[Comments]
)
SELECT T.[TerminalID],
	 T.[TerminalName],
	 T.[TerminalCode],
	 CVID.[CityVersionID],
	 RVID.[RegionVersionID],
	 1,
	 1,
	 1,
	 1,
	 GETUTCDATE(),
	 @UpdatedBy,
	 @Comments
FROM @Terminal T
INNER JOIN @CityVersionID CVID ON T.[CityID] = CVID.[CityID]
INNER JOIN @RegionVersionID RVID ON T.[RegionID] = RVID.[RegionID]

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
