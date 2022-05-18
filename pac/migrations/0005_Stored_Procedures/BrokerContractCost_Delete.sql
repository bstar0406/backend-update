CREATE OR ALTER PROCEDURE [dbo].[BrokerContractCost_Delete]
	@deleted BrokerContractCostWeightBreakLevelTableType READONLY,
	@TerminalID BIGINT,
	@ServiceLevelID BIGINT
AS

SET NOCOUNT ON;

BEGIN TRAN

DECLARE @added BrokerContractCostWeightBreakLevelTableType;
DECLARE @updated BrokerContractCostWeightBreakLevelTableType;

EXEC dbo.[BrokerContractCost_Update_Base] @added, @updated, @deleted, @TerminalID, @ServiceLevelID

COMMIT TRAN

RETURN 1

GO
