CREATE OR ALTER PROCEDURE [dbo].[SpeedSheet_Insert_Bulk]
	@SpeedSheetTableType SpeedSheetTableType READONLY,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ROWCOUNT1 INT, @ROWCOUNT2 INT, @InputCount INT;

SELECT @InputCount = Count(*) FROM @SpeedSheetTableType;

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

BEGIN TRAN

DECLARE @SpeedSheet table 
( 
	[SpeedSheetID]       BIGINT          NOT NULL,
	[ServiceOfferingID]  BIGINT          NOT NULL,
    [Margin]             NUMERIC (19, 6) NOT NULL,
    [MaxDensity]         NUMERIC (19, 6) NOT NULL,
    [MinDensity]         NUMERIC (19, 6) NOT NULL
)

INSERT INTO [dbo].[SpeedSheet]
(
	[ServiceOfferingID],
    [Margin],
    [MaxDensity],
    [MinDensity],
	[IsActive],
	[IsInactiveViewable]
)
OUTPUT INSERTED.SpeedSheetID,
	 INSERTED.[ServiceOfferingID],
	 INSERTED.[Margin],
	 INSERTED.[MaxDensity],
	 INSERTED.[MinDensity]
INTO @SpeedSheet
(
	[SpeedSheetID],
	[ServiceOfferingID],
    [Margin],
    [MaxDensity],
    [MinDensity]
)
SELECT SO.[ServiceOfferingID],
	SS.[Margin],
	SS.[MaxDensity],
	SS.[MinDensity],
	1,
	1
FROM @SpeedSheetTableType SS
INNER JOIN [dbo].[ServiceOffering] SO ON SS.[ServiceOfferingName] = SO.[ServiceOfferingName]

SELECT @ERROR1 = @@ERROR, @ROWCOUNT1 = @@ROWCOUNT  

INSERT INTO [dbo].[SpeedSheet_History]
(
	[SpeedSheetID],
	[ServiceOfferingVersionID],
    [Margin],
    [MaxDensity],
    [MinDensity],
	[IsActive],
	[VersionNum],
	[IsLatestVersion],
	[IsInactiveViewable],
	[UpdatedOn],
	[UpdatedBy],
	[Comments]
)
SELECT SS.[SpeedSheetID],
	 SO.[ServiceOfferingVersionID],
     SS.[Margin],
     SS.[MaxDensity],
     SS.[MinDensity],
	 1,
	 1,
	 1,
	 1,
	 GETUTCDATE(),
	 @UpdatedBy,
	 @Comments
FROM @SpeedSheet SS
INNER JOIN [dbo].[ServiceOffering_History] SO ON SS.[ServiceOfferingID] = SO.[ServiceOfferingID] AND SO.[IsLatestVersion] = 1

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
