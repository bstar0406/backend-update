CREATE OR ALTER PROCEDURE [dbo].[BrokerContractCost_Create]
	@added BrokerContractCostWeightBreakLevelTableType READONLY,
	@TerminalID BIGINT,
	@ServiceLevelID BIGINT
AS

SET NOCOUNT ON;

BEGIN TRAN

DECLARE @updated BrokerContractCostWeightBreakLevelTableType;
DECLARE @deleted BrokerContractCostWeightBreakLevelTableType;

EXEC dbo.[BrokerContractCost_Update_Base] @added, @updated, @deleted, @TerminalID, @ServiceLevelID

COMMIT TRAN

RETURN 1

GO
