CREATE OR ALTER PROCEDURE [dbo].[BrokerContractCost_Insert_Bulk]
	@BrokerContractCostTableType BrokerContractCostTableType READONLY,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ROWCOUNT1 INT, @ROWCOUNT2 INT, @InputCount INT;

SELECT @InputCount = Count(*) FROM @BrokerContractCostTableType;

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

DECLARE @BrokerContractCost table 
( 
	[BrokerContractCostID] [bigint] NOT NULL,
	[TerminalID] [bigint] NOT NULL,
	[ServiceLevelID] [bigint] NOT NULL,
	[Cost] [nvarchar] (MAX) NOT NULL
)

BEGIN TRAN

DECLARE @BrokerContractCostWithTerminalIDServiceLevelID table 
( 
	[TerminalID] [bigint] NOT NULL,
	[ServiceLevelID] [bigint] NOT NULL,
	[Cost] [nvarchar] (MAX) NOT NULL
)

DECLARE @TerminalVersionID table 
( 
	[TerminalID] [bigint] NOT NULL,
	[TerminalVersionID] [bigint] NOT NULL
)

DECLARE @ServiceLevelVersionID table 
( 
	[ServiceLevelID] [bigint] NOT NULL,
	[ServiceLevelVersionID] [bigint] NOT NULL
)

INSERT INTO @BrokerContractCostWithTerminalIDServiceLevelID 
( 
	[TerminalID],
	[ServiceLevelID],
	[Cost]
)
SELECT T.[TerminalID],
	SL.[ServiceLevelID],
	dbo.FormatJsonField(BCTT.[Cost])
FROM @BrokerContractCostTableType BCTT
INNER JOIN [dbo].[Terminal] T ON BCTT.[TerminalCode] = T.[TerminalCode] 
INNER JOIN [dbo].[ServiceOffering] SO ON BCTT.[ServiceOfferingName] = SO.[ServiceOfferingName] 
INNER JOIN [dbo].[ServiceLevel] SL ON SO.[ServiceOfferingID] = SL.[ServiceOfferingID] AND SL.[ServiceLevelCode] = BCTT.[ServiceLevelCode]

INSERT INTO @TerminalVersionID 
( 
	[TerminalID],
	[TerminalVersionID]
)
SELECT [TerminalID],
	[TerminalVersionID]
FROM [dbo].[Terminal_History]
WHERE [IsLatestVersion] = 1
AND [TerminalID] IN (SELECT DISTINCT [TerminalID] FROM @BrokerContractCostWithTerminalIDServiceLevelID)

INSERT INTO @ServiceLevelVersionID 
( 
	[ServiceLevelID],
	[ServiceLevelVersionID]
)
SELECT [ServiceLevelID],
	[ServiceLevelVersionID]
FROM [dbo].[ServiceLevel_History]
WHERE [IsLatestVersion] = 1
AND [ServiceLevelID] IN (SELECT DISTINCT [ServiceLevelID] FROM @BrokerContractCostWithTerminalIDServiceLevelID)

INSERT INTO [dbo].[BrokerContractCost]
(
	[TerminalID],
	[ServiceLevelID],
	[Cost],
	[IsActive],
	[IsInactiveViewable]
)
OUTPUT INSERTED.BrokerContractCostID,
	 INSERTED.TerminalID,
	 INSERTED.ServiceLevelID,
	 INSERTED.Cost
INTO @BrokerContractCost
(
	[BrokerContractCostID],
	[TerminalID],
	[ServiceLevelID],
	[Cost]
)
SELECT [TerminalID],
	[ServiceLevelID],
	[Cost],
	1,
	1
FROM @BrokerContractCostWithTerminalIDServiceLevelID

SELECT @ERROR1 = @@ERROR, @ROWCOUNT1 = @@ROWCOUNT  

INSERT INTO [dbo].[BrokerContractCost_History]
(
	[BrokerContractCostID],
	[TerminalVersionID],
	[ServiceLevelVersionID],
	[Cost],
	[IsActive],
	[VersionNum],
	[IsLatestVersion],
	[IsInactiveViewable],
	[UpdatedOn],
	[UpdatedBy],
	[Comments]
)
SELECT BC.[BrokerContractCostID],
	 TVID.[TerminalVersionID],
	 SLVID.[ServiceLevelVersionID],
	 BC.[Cost],
	 1,
	 1,
	 1,
	 1,
	 GETUTCDATE(),
	 @UpdatedBy,
	 @Comments
FROM @BrokerContractCost BC
INNER JOIN @TerminalVersionID TVID ON BC.[TerminalID] = TVID.[TerminalID]
INNER JOIN @ServiceLevelVersionID SLVID ON BC.[ServiceLevelID] = SLVID.[ServiceLevelID]

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
