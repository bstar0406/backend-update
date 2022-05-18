CREATE OR ALTER PROCEDURE [dbo].[ServiceLevel_Insert_Bulk]
	@ServiceLevelTableType ServiceLevelTableType READONLY,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ROWCOUNT1 INT, @ROWCOUNT2 INT, @InputCount INT;

SELECT @InputCount = Count(*) FROM @ServiceLevelTableType;

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

DECLARE @ServiceLevel table 
( 
	[ServiceLevelID] [bigint] NOT NULL,
	[ServiceLevelName] [nvarchar](50) NOT NULL,
	[ServiceLevelCode] [nvarchar](3) NOT NULL,
	[ServiceOfferingID] [bigint] NOT NULL,
	[PricingType] NVARCHAR (50) NOT NULL
)

BEGIN TRAN

DECLARE @ServiceLevelWithServiceOfferingID table 
( 
	[ServiceLevelName] [nvarchar](50) NOT NULL,
	[ServiceLevelCode] [nvarchar](3) NOT NULL,
	[ServiceOfferingID] [bigint] NOT NULL,
	[PricingType] NVARCHAR (50) NOT NULL
)

DECLARE @ServiceOfferingVersionID table 
( 
	[ServiceOfferingID] [bigint] NOT NULL,
	[ServiceOfferingVersionID] [bigint] NOT NULL
)

INSERT INTO @ServiceLevelWithServiceOfferingID 
( 
	[ServiceLevelName],
	[ServiceLevelCode],
	[PricingType],
	[ServiceOfferingID]
)
SELECT SLTT.[ServiceLevelName],
	SLTT.[ServiceLevelCode],
	S.[ServiceOfferingID],
	SLTT.[PricingType]
FROM @ServiceLevelTableType SLTT
INNER JOIN [dbo].[ServiceOffering] S ON SLTT.[ServiceOfferingName] = S.[ServiceOfferingName]

INSERT INTO @ServiceOfferingVersionID 
( 
	[ServiceOfferingID],
	[ServiceOfferingVersionID]
)
SELECT [ServiceOfferingID],
	[ServiceOfferingVersionID]
FROM [dbo].[ServiceOffering_History]
WHERE [IsLatestVersion] = 1
AND [ServiceOfferingID] IN (SELECT DISTINCT [ServiceOfferingID] FROM @ServiceLevelWithServiceOfferingID)


INSERT INTO [dbo].[ServiceLevel]
(
	[ServiceLevelName],
	[ServiceLevelCode],
	[PricingType],
	[ServiceOfferingID],
	[IsActive],
	[IsInactiveViewable]
)
OUTPUT INSERTED.ServiceLevelID,
	 INSERTED.ServiceLevelName,
	 INSERTED.ServiceLevelCode,
	 INSERTED.[PricingType],
	 INSERTED.ServiceOfferingID
INTO @ServiceLevel
(
	[ServiceLevelID],
	[ServiceLevelName],
	[ServiceLevelCode],
	[PricingType],
	[ServiceOfferingID]
)
SELECT [ServiceLevelName],
	[ServiceLevelCode],
	[PricingType],
	[ServiceOfferingID],
	1,
	1
FROM @ServiceLevelWithServiceOfferingID

SELECT @ERROR1 = @@ERROR, @ROWCOUNT1 = @@ROWCOUNT  

INSERT INTO [dbo].[ServiceLevel_History]
(
	[ServiceLevelID],
	[ServiceLevelName],
	[ServiceLevelCode],
	[PricingType],
	[ServiceOfferingVersionID],
	[IsActive],
	[VersionNum],
	[IsLatestVersion],
	[IsInactiveViewable],
	[UpdatedOn],
	[UpdatedBy],
	[Comments]
)
SELECT S.[ServiceLevelID],
	 S.[ServiceLevelName],
	 S.[ServiceLevelCode],
	 S.[PricingType],
	 SVID.[ServiceOfferingVersionID],
	 1,
	 1,
	 1,
	 1,
	 GETUTCDATE(),
	 @UpdatedBy,
	 @Comments
FROM @ServiceLevel S
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
