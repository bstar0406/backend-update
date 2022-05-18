CREATE OR ALTER PROCEDURE [dbo].[WeightBreakHeader_Insert_Bulk]
	@WeightBreakHeaderTableType WeightBreakHeaderTableType READONLY,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ROWCOUNT1 INT, @ROWCOUNT2 INT, @InputCount INT;

SELECT @InputCount = Count(*) FROM @WeightBreakHeaderTableType;

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

BEGIN TRAN

DECLARE @WeightBreakHeader table 
( 
    [WeightBreakHeaderID]   BIGINT          NOT NULL,
    [WeightBreakHeaderName] NVARCHAR (50)   NOT NULL,
    [UnitFactor]            NUMERIC (19, 6) NOT NULL,
    [MaximumValue]          NUMERIC (19, 6) NOT NULL,
    [AsRating]       BIT             NOT NULL,
	[HasMin]       BIT             NOT NULL,
	[HasMax]       BIT             NOT NULL,
    [BaseRate]              BIT             NOT NULL,
    [Levels]                NVARCHAR (MAX)  NOT NULL,
    [ServiceLevelID]        BIGINT          NOT NULL,
    [UnitID]                BIGINT          NOT NULL
)

DECLARE @WeightBreakHeaderID table 
( 
    [WeightBreakHeaderName] NVARCHAR (50)   NOT NULL,
    [UnitFactor]            NUMERIC (19, 6) NOT NULL,
    [MaximumValue]          NUMERIC (19, 6) NOT NULL,
    [AsRating]       BIT             NOT NULL,
	[HasMin]       BIT             NOT NULL,
	[HasMax]       BIT             NOT NULL,
    [BaseRate]              BIT             NOT NULL,
    [Levels]                NVARCHAR (MAX)  NOT NULL,
    [ServiceLevelID]        BIGINT          NOT NULL,
    [UnitID]                BIGINT          NOT NULL
)

DECLARE @ServiceLevelVersionID table 
( 
	[ServiceLevelID] [bigint] NOT NULL,
	[ServiceLevelVersionID] [bigint] NOT NULL
)

DECLARE @UnitVersionID table 
( 
	[UnitID] [bigint] NOT NULL,
	[UnitVersionID] [bigint] NOT NULL
)

INSERT INTO @WeightBreakHeaderID
(
    [WeightBreakHeaderName],
    [UnitFactor],
    [MaximumValue],
    [AsRating],
	[HasMin],
	[HasMax],
    [BaseRate],
    [Levels],
    [ServiceLevelID],
    [UnitID]
)
SELECT WB.[WeightBreakHeaderName],
    WB.[UnitFactor],
    WB.[MaximumValue],
    WB.[AsRating],
	WB.[HasMin],
	WB.[HasMax],
    WB.[BaseRate],
    WB.[Levels],
    SL.[ServiceLevelID],
    U.[UnitID]
FROM @WeightBreakHeaderTableType WB
INNER JOIN dbo.[ServiceOffering] SO ON WB.[ServiceOfferingName] = SO.[ServiceOfferingName]
INNER JOIN dbo.ServiceLevel SL ON SO.[ServiceOfferingID] = SL.[ServiceOfferingID] AND WB.ServiceLevelCode = SL.ServiceLevelCode
INNER JOIN dbo.Unit U ON WB.UnitSymbol = U.UnitSymbol


INSERT INTO @ServiceLevelVersionID
(
	[ServiceLevelID],
	[ServiceLevelVersionID]
)
SELECT [ServiceLevelID],
	[ServiceLevelVersionID]
FROM [dbo].[ServiceLevel_History] SLH
WHERE SLH.[IsLatestVersion] = 1
AND [ServiceLevelID] IN (SELECT DISTINCT [ServiceLevelID] FROM @WeightBreakHeaderID)

INSERT INTO @UnitVersionID
(
	[UnitID],
	[UnitVersionID]
)
SELECT [UnitID],
	[UnitVersionID]
FROM [dbo].[Unit_History] UH
WHERE UH.[IsLatestVersion] = 1
AND [UnitID] IN (SELECT DISTINCT [UnitID] FROM @WeightBreakHeaderID)

INSERT INTO [dbo].[WeightBreakHeader]
(
    [WeightBreakHeaderName],
    [UnitFactor],
    [MaximumValue],
    [AsRating],
	[HasMin],
	[HasMax],
    [BaseRate],
    [Levels],
    [ServiceLevelID],
    [UnitID],
	[IsActive],
	[IsInactiveViewable]
)
OUTPUT INSERTED.[WeightBreakHeaderID],
	 INSERTED.[WeightBreakHeaderName],
	 INSERTED.[UnitFactor],
	 INSERTED.[MaximumValue],
	 INSERTED.[AsRating],
	 INSERTED.[HasMin],
	 INSERTED.[HasMax],
	 INSERTED.[BaseRate],
	 INSERTED.[Levels],
	 INSERTED.[ServiceLevelID],
	 INSERTED.[UnitID]
INTO @WeightBreakHeader
(
	[WeightBreakHeaderID],
    [WeightBreakHeaderName],
    [UnitFactor],
    [MaximumValue],
    [AsRating],
	[HasMin],
	[HasMax],
    [BaseRate],
    [Levels],
    [ServiceLevelID],
    [UnitID]
)
SELECT [WeightBreakHeaderName],
    [UnitFactor],
    [MaximumValue],
    [AsRating],
	[HasMin],
	[HasMax],
    [BaseRate],
    [Levels],
    [ServiceLevelID],
    [UnitID],
	1,
	1
FROM @WeightBreakHeaderID 

SELECT @ERROR1 = @@ERROR, @ROWCOUNT1 = @@ROWCOUNT  

INSERT INTO [dbo].[WeightBreakHeader_History]
(
	[WeightBreakHeaderID],
	[WeightBreakHeaderName],
    [UnitFactor],
    [MaximumValue],
    [AsRating],
	[HasMin],
	[HasMax],
    [BaseRate],
    [Levels],
    [ServiceLevelVersionID],
    [UnitVersionID],
	[IsActive],
	[VersionNum],
	[IsLatestVersion],
	[IsInactiveViewable],
	[UpdatedOn],
	[UpdatedBy],
	[Comments]
)
SELECT WB.[WeightBreakHeaderID],
	WB.[WeightBreakHeaderName],
    WB.[UnitFactor],
    WB.[MaximumValue],
    WB.[AsRating],
	WB.[HasMin],
	WB.[HasMax],
    WB.[BaseRate],
    WB.[Levels],
    SL.[ServiceLevelVersionID],
    U.[UnitVersionID],
	 1,
	 1,
	 1,
	 1,
	 GETUTCDATE(),
	 @UpdatedBy,
	 @Comments
FROM @WeightBreakHeader WB 
INNER JOIN @ServiceLevelVersionID SL ON WB.[ServiceLevelID] = SL.[ServiceLevelID]
INNER JOIN @UnitVersionID U ON WB.[UnitID] = U.[UnitID]

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
