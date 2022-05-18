CREATE OR ALTER PROCEDURE [dbo].[TerminalCost_Insert_Bulk]
	@TerminalCostTableType TerminalCostTableType READONLY,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ROWCOUNT1 INT, @ROWCOUNT2 INT, @InputCount INT;

SELECT @InputCount = Count(*) FROM @TerminalCostTableType;

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

DECLARE @TerminalCost table 
( 
	[TerminalCostID] [bigint] NOT NULL,
	[TerminalID] [bigint] NOT NULL,
	[ServiceOfferingID] [bigint] NOT NULL,
	[Cost] [nvarchar] (MAX) NOT NULL,
	[IsIntraRegionMovementEnabled] [bit] NOT NULL,
	[IntraRegionMovementFactor] [decimal](19,6) NOT NULL
)

BEGIN TRAN

DECLARE @TerminalCostWithTerminalIDServiceOfferingID table 
( 
	[TerminalID] [bigint] NOT NULL,
	[ServiceOfferingID] [bigint] NOT NULL,
	[Cost] [nvarchar] (MAX) NOT NULL,
	[IsIntraRegionMovementEnabled] [bit] NOT NULL,
	[IntraRegionMovementFactor] [decimal](19,6) NOT NULL
)

DECLARE @TerminalVersionID table 
( 
	[TerminalID] [bigint] NOT NULL,
	[TerminalVersionID] [bigint] NOT NULL
)

DECLARE @ServiceOfferingVersionID table 
( 
	[ServiceOfferingID] [bigint] NOT NULL,
	[ServiceOfferingVersionID] [bigint] NOT NULL
)

INSERT INTO @TerminalCostWithTerminalIDServiceOfferingID 
( 
	[TerminalID],
	[ServiceOfferingID],
	[Cost],
	[IsIntraRegionMovementEnabled],
	[IntraRegionMovementFactor]
)
SELECT T.[TerminalID],
	SO.[ServiceOfferingID],
	TCTT.[Cost],
	TCTT.[IsIntraRegionMovementEnabled],
	TCTT.[IntraRegionMovementFactor]
FROM @TerminalCostTableType TCTT
INNER JOIN [dbo].[Terminal] T ON TCTT.[TerminalCode] = T.[TerminalCode] 
INNER JOIN [dbo].[ServiceOffering] SO ON TCTT.[ServiceOfferingName] = SO.[ServiceOfferingName] 

INSERT INTO @TerminalVersionID 
( 
	[TerminalID],
	[TerminalVersionID]
)
SELECT [TerminalID],
	[TerminalVersionID]
FROM [dbo].[Terminal_History]
WHERE [IsLatestVersion] = 1
AND [TerminalID] IN (SELECT DISTINCT [TerminalID] FROM @TerminalCostWithTerminalIDServiceOfferingID)

INSERT INTO @ServiceOfferingVersionID 
( 
	[ServiceOfferingID],
	[ServiceOfferingVersionID]
)
SELECT [ServiceOfferingID],
	[ServiceOfferingVersionID]
FROM [dbo].[ServiceOffering_History]
WHERE [IsLatestVersion] = 1
AND [ServiceOfferingID] IN (SELECT DISTINCT [ServiceOfferingID] FROM @TerminalCostWithTerminalIDServiceOfferingID)

INSERT INTO [dbo].[TerminalCost]
(
	[TerminalID],
	[ServiceOfferingID],
	[Cost],
	[IsIntraRegionMovementEnabled],
	[IntraRegionMovementFactor],
	[IsActive],
	[IsInactiveViewable]
)
OUTPUT INSERTED.TerminalCostID,
	 INSERTED.TerminalID,
	 INSERTED.ServiceOfferingID,
	 INSERTED.Cost,
	 INSERTED.IsIntraRegionMovementEnabled,
	 INSERTED.IntraRegionMovementFactor
INTO @TerminalCost
(
	[TerminalCostID],
	[TerminalID],
	[ServiceOfferingID],
	[Cost],
	[IsIntraRegionMovementEnabled],
	[IntraRegionMovementFactor]
)
SELECT [TerminalID],
	[ServiceOfferingID],
	dbo.FormatJsonField(Cost),
	[IsIntraRegionMovementEnabled],
	[IntraRegionMovementFactor],
	1,
	1
FROM @TerminalCostWithTerminalIDServiceOfferingID

SELECT @ERROR1 = @@ERROR, @ROWCOUNT1 = @@ROWCOUNT  

INSERT INTO [dbo].[TerminalCost_History]
(
	[TerminalCostID],
	[TerminalVersionID],
	[ServiceOfferingVersionID],
	[Cost],
	[IsIntraRegionMovementEnabled],
	[IntraRegionMovementFactor],
	[IsActive],
	[VersionNum],
	[IsLatestVersion],
	[IsInactiveViewable],
	[UpdatedOn],
	[UpdatedBy],
	[Comments]
)
SELECT TC.[TerminalCostID],
	 TVID.[TerminalVersionID],
	 SOVID.[ServiceOfferingVersionID],
	 TC.[Cost],
	 TC.[IsIntraRegionMovementEnabled],
	 TC.[IntraRegionMovementFactor],
	 1,
	 1,
	 1,
	 1,
	 GETUTCDATE(),
	 @UpdatedBy,
	 @Comments
FROM @TerminalCost TC
INNER JOIN @TerminalVersionID TVID ON TC.[TerminalID] = TVID.[TerminalID]
INNER JOIN @ServiceOfferingVersionID SOVID ON TC.[ServiceOfferingID] = SOVID.[ServiceOfferingID]

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
