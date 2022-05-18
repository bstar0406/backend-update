CREATE OR ALTER PROCEDURE [dbo].[BrokerContractCost_Update_Base]
	@Added BrokerContractCostWeightBreakLevelTableType READONLY, 
	@Updated BrokerContractCostWeightBreakLevelTableType READONLY,
	@Deleted BrokerContractCostWeightBreakLevelTableType READONLY,
	@TerminalID BIGINT,
	@ServiceLevelID BIGINT
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ROWCOUNT1 INT,@InputCount INT;

BEGIN TRAN

DECLARE @Cost NVARCHAR(MAX);

DECLARE @BrokerContractCost table 
( 
	[BrokerContractCostVersionID] [bigint] NOT NULL,
	[BrokerContractCostID] [bigint] NOT NULL,
	[TerminalVersionID] [bigint] NOT NULL,
	[ServiceLevelVersionID] [bigint] NOT NULL,
	[Cost] [nvarchar] (MAX) NOT NULL,
	[IsActive]           BIT           NOT NULL,
    [IsInactiveViewable] BIT           NOT NULL,
	[VersionNum] [int] NOT NULL
)

INSERT INTO @BrokerContractCost 
(	
	[BrokerContractCostVersionID],
	[BrokerContractCostID],
	[TerminalVersionID],
	[ServiceLevelVersionID],
	[Cost],
	[IsActive],
	[IsInactiveViewable],
	[VersionNum]
)
SELECT BCH.[BrokerContractCostVersionID],
	BC.[BrokerContractCostID],
	BCH.[TerminalVersionID],
	BCH.[ServiceLevelVersionID],
	dbo.FormatJsonField(dbo.BrokerContractCost_Modify(BC.[Cost], @Added, @Updated, @Deleted)),
	BCH.[IsActive],
	BCH.[IsInactiveViewable],
	BCH.[VersionNum]
FROM [dbo].[BrokerContractCost_History] BCH
INNER JOIN [dbo].[BrokerContractCost] BC ON BCH.[BrokerContractCostID] = BC.[BrokerContractCostID] AND BCH.[IsLatestVersion] = 1
WHERE BC.TerminalID = @TerminalID AND BC.ServiceLevelID = @ServiceLevelID


UPDATE [dbo].[BrokerContractCost]
SET [Cost] = A.[Cost]
FROM @BrokerContractCost A
WHERE [dbo].[BrokerContractCost].[BrokerContractCostID] = A.[BrokerContractCostID] 

UPDATE [dbo].[BrokerContractCost_History]
SET [IsLatestVersion] = 0
FROM @BrokerContractCost AS A
WHERE [dbo].[BrokerContractCost_History].[BrokerContractCostVersionID] = A.[BrokerContractCostVersionID]


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
	 BC.[TerminalVersionID],
 	 BC.[ServiceLevelVersionID],
	 BC.[Cost],
	 BC.[IsActive],
	 BC.[VersionNum] + 1,
	 1,
	 BC.[IsInactiveViewable],
	 GETUTCDATE(),
	 'P&C System',
	 ''
FROM @BrokerContractCost BC

SELECT @ERROR1 = @@ERROR, @ROWCOUNT1 = @@ROWCOUNT 

IF (@ERROR1 <> 0) 

	BEGIN
	ROLLBACK TRAN
	RAISERROR('Insert Procedure Failed!', 16, 1)
	RETURN 0
	END

IF (@ROWCOUNT1 <> 1) 
	
	BEGIN
	ROLLBACK TRAN
	RAISERROR('%d Records Affected by Insert Procedure while the expected number of record is %d!', 16, 1, @ROWCOUNT1,  @InputCount);
	RETURN 0
	END

COMMIT TRAN

RETURN 1

GO
