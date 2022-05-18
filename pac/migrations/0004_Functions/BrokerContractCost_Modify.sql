IF EXISTS (SELECT *
FROM sys.objects
WHERE  object_id = OBJECT_ID(N'[dbo].[BrokerContractCost_Modify]')
	AND type IN ( N'FN', N'IF', N'TF', N'FS', N'FT' ))
  DROP FUNCTION [dbo].[BrokerContractCost_Modify]
GO

CREATE FUNCTION dbo.BrokerContractCost_Modify
(
	@Cost NVARCHAR(MAX),
	@Added BrokerContractCostWeightBreakLevelTableType READONLY, 
	@Updated BrokerContractCostWeightBreakLevelTableType READONLY,
	@Deleted BrokerContractCostWeightBreakLevelTableType READONLY
)

RETURNS NVARCHAR(MAX)
AS
BEGIN

	DECLARE @NewCost NVARCHAR(MAX);

	DECLARE @CostByWeightBreakByPickupDeliveryCount NVARCHAR(MAX);
	DECLARE @CostByWeightBreak NVARCHAR(MAX);

	Select @CostByWeightBreakByPickupDeliveryCount = [value]
	FROM OPENJSON(@Cost, '$.CostComponents')
	WHERE [key] = 'CostByWeightBreakByPickupDeliveryCount'

	Select @CostByWeightBreak = [value]
	FROM OPENJSON(@Cost, '$.CostComponents')
	WHERE [key] = 'CostByWeightBreak'

	IF @CostByWeightBreakByPickupDeliveryCount IS NOT NULL AND LEN(REPLACE(@CostByWeightBreakByPickupDeliveryCount, '{}','')) > 0
BEGIN
		SELECT @NewCost = '{"CostComponents":{"CostByWeightBreakByPickupDeliveryCount":' + dbo.BrokerContractCostByPickupDeliveryCount_Modify(@CostByWeightBreakByPickupDeliveryCount, @Added, @Updated, @Deleted) + ',"CostByWeightBreak":""}}'
	END

	IF @CostByWeightBreak IS NOT NULL AND LEN(REPLACE(@CostByWeightBreak, '{}','')) > 0
BEGIN
		SELECT @NewCost = '{"CostComponents":{"CostByWeightBreakByPickupDeliveryCount":"","CostByWeightBreak":' + dbo.BrokerContractCostByWeightBreak_Modify(@CostByWeightBreak, @Added, @Updated, @Deleted) + '}}'
	END

	RETURN @NewCost;

END