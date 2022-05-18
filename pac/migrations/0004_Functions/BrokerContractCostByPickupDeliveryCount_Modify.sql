IF EXISTS (SELECT *
FROM sys.objects
WHERE  object_id = OBJECT_ID(N'[dbo].[BrokerContractCostByPickupDeliveryCount_Modify]')
	AND type IN ( N'FN', N'IF', N'TF', N'FS', N'FT' ))
  DROP FUNCTION [dbo].[BrokerContractCostByPickupDeliveryCount_Modify]
GO

CREATE FUNCTION dbo.BrokerContractCostByPickupDeliveryCount_Modify
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

	DECLARE @Temp1 TABLE
(
		[PickupDeliveryCount] INT NOT NULL,
		[WeightBreakLevelName] NVARCHAR(50) NOT NULL,
		[WeightBreakLowerBound] INT NOT NULL,
		[Cost] DECIMAL(19,6) NOT NULL
)

	DECLARE @Temp2 TABLE
(
		[PickupDeliveryCount] INT NOT NULL,
		[WeightBreakLevelName] NVARCHAR(50) NOT NULL,
		[WeightBreakLowerBound] INT NOT NULL,
		[Cost] DECIMAL(19,6) NOT NULL
)

	DECLARE @Final TABLE
(
		[PickupDeliveryCount] INT NOT NULL,
		[WeightBreakLevelName] NVARCHAR(50) NOT NULL,
		[WeightBreakLowerBound] INT NOT NULL,
		[Cost] DECIMAL(19,6) NOT NULL
)

	INSERT INTO @Temp1
		(
		PickupDeliveryCount,
		WeightBreakLevelName,
		WeightBreakLowerBound,
		Cost
		)

	SELECT PickupDeliveryCount,
		WeightBreakLevelName,
		WeightBreakLowerBound,
		Cost
	FROM OPENJSON(@Cost,'$')
WITH (
	PickupDeliveryCount INT '$.PickupDeliveryCount', 
	CostByPickupDeliveryCount NVARCHAR(MAX) '$.Cost' AS JSON 
)
CROSS APPLY OPENJSON(CostByPickupDeliveryCount,'$')
WITH (
	WeightBreakLevelName NVARCHAR(50) '$.WeightBreakLevelName',  
	WeightBreakLowerBound INT '$.WeightBreakLowerBound',
	Cost DECIMAL(19,6) '$.Cost' 
)

	INSERT INTO @Temp2
		(
		PickupDeliveryCount,
		WeightBreakLevelName,
		WeightBreakLowerBound,
		Cost
		)
			SELECT PickupDeliveryCount, WeightBreakLevelName, WeightBreakLowerBound, Cost
		FROM @Temp1
		WHERE (WeightBreakLowerBound NOT IN (SELECT WeightBreakLowerBound
			FROM @Deleted) AND WeightBreakLevelName NOT IN (SELECT WeightBreakLevelName
			FROM @Deleted))
	UNION
		SELECT DISTINCT T.PickupDeliveryCount, A.WeightBreakLevelName, A.WeightBreakLowerBound, 0
		FROM @Temp1 T, @Added A

	INSERT INTO @Final
		(
		PickupDeliveryCount,
		WeightBreakLevelName,
		WeightBreakLowerBound,
		Cost
		)
			SELECT A.PickupDeliveryCount, B.WeightBreakLevelName, A.WeightBreakLowerBound, A.Cost
		FROM @Temp2 A
			INNER JOIN @Updated B ON A.WeightBreakLowerBound = B.WeightBreakLowerBound
	UNION
		SELECT PickupDeliveryCount, WeightBreakLevelName, WeightBreakLowerBound, Cost
		FROM @Temp2
		WHERE (WeightBreakLowerBound NOT IN (SELECT WeightBreakLowerBound
			FROM @Updated) AND WeightBreakLevelName NOT IN (SELECT WeightBreakLevelName
			FROM @Updated))

	SELECT @NewCost = (SELECT *
		FROM
			(SELECT DISTINCT PickupDeliveryCount,
				(SELECT WeightBreakLevelName, WeightBreakLowerBound, Cost
				FROM @Final B
				WHERE A.PickupDeliveryCount = B.PickupDeliveryCount
				FOR JSON AUTO) AS Cost
			FROM @Final A) AS C
		FOR JSON AUTO)

	RETURN @NewCost

END
GO

