CREATE OR ALTER PROCEDURE [dbo].[Province_Insert_Bulk]
	@ProvinceTableType ProvinceTableType READONLY,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ROWCOUNT1 INT, @ROWCOUNT2 INT, @InputCount INT;

SELECT @InputCount = Count(*) FROM @ProvinceTableType;

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

DECLARE @Province table 
( 
	[ProvinceID] [bigint] NOT NULL,
	[ProvinceName] [nvarchar](50) NOT NULL,
	[ProvinceCode] [nvarchar](2) NOT NULL,
	[RegionID] [bigint] NOT NULL
)

BEGIN TRAN

DECLARE @ProvinceWithRegionID table 
( 
	[ProvinceName] [nvarchar](50) NOT NULL,
	[ProvinceCode] [nvarchar](2) NOT NULL,
	[RegionID] [bigint] NOT NULL
)

DECLARE @RegionVersionID table 
( 
	[RegionID] [bigint] NOT NULL,
	[RegionVersionID] [bigint] NOT NULL
)

INSERT INTO @ProvinceWithRegionID 
( 
	[ProvinceName],
	[ProvinceCode],
	[RegionID]
)
SELECT PTT.[ProvinceName],
	PTT.[ProvinceCode],
	C.[RegionID]
FROM @ProvinceTableType PTT
INNER JOIN [dbo].[Region] C ON PTT.[RegionCode] = C.[RegionCode]

INSERT INTO @RegionVersionID 
( 
	[RegionID],
	[RegionVersionID]
)
SELECT [RegionID],
	[RegionVersionID]
FROM [dbo].[Region_History]
WHERE [IsLatestVersion] = 1
AND [RegionID] IN (SELECT DISTINCT [RegionID] FROM @ProvinceWithRegionID)


INSERT INTO [dbo].[Province]
(
	[ProvinceName],
	[ProvinceCode],
	[RegionID],
	[IsActive],
	[IsInactiveViewable]
)
OUTPUT INSERTED.ProvinceID,
	 INSERTED.ProvinceName,
	 INSERTED.ProvinceCode,
	 INSERTED.RegionID
INTO @Province
(
	[ProvinceID],
	[ProvinceName],
	[ProvinceCode],
	[RegionID]
)
SELECT [ProvinceName],
	[ProvinceCode],
	[RegionID],
	1,
	1
FROM @ProvinceWithRegionID

SELECT @ERROR1 = @@ERROR, @ROWCOUNT1 = @@ROWCOUNT  

INSERT INTO [dbo].[Province_History]
(
	[ProvinceID],
	[ProvinceName],
	[ProvinceCode],
	[RegionVersionID],
	[IsActive],
	[VersionNum],
	[IsLatestVersion],
	[IsInactiveViewable],
	[UpdatedOn],
	[UpdatedBy],
	[Comments]
)
SELECT P.[ProvinceID],
	 P.[ProvinceName],
	 P.[ProvinceCode],
	 CVID.[RegionVersionID],
	 1,
	 1,
	 1,
	 1,
	 GETUTCDATE(),
	 @UpdatedBy,
	 @Comments
FROM @Province P
INNER JOIN @RegionVersionID CVID ON P.[RegionID] = CVID.[RegionID]

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
