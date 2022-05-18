IF EXISTS (SELECT *
FROM sys.objects
WHERE  object_id = OBJECT_ID(N'[dbo].[BrokerContractCostByWeightBreak_Modify]')
	AND type IN ( N'FN', N'IF', N'TF', N'FS', N'FT' ))
  DROP FUNCTION [dbo].[BrokerContractCostByWeightBreak_Modify]
GO

CREATE FUNCTION dbo.BrokerContractCostByWeightBreak_Modify
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

	DECLARE @RateBase DECIMAL(19,6);
	DECLARE @RateMax DECIMAL(19,6);
	DECLARE @CostByWeightBreak NVARCHAR(MAX);

	DECLARE @Temp1 TABLE
(
		[WeightBreakLevelName] NVARCHAR(50) NOT NULL,
		[WeightBreakLowerBound] INT NOT NULL,
		[Cost] DECIMAL(19,6) NOT NULL
)

	DECLARE @Temp2 TABLE
(
		[WeightBreakLevelName] NVARCHAR(50) NOT NULL,
		[WeightBreakLowerBound] INT NOT NULL,
		[Cost] DECIMAL(19,6) NOT NULL
)

	DECLARE @Final TABLE
(
		[WeightBreakLevelName] NVARCHAR(50) NOT NULL,
		[WeightBreakLowerBound] INT NOT NULL,
		[Cost] DECIMAL(19,6) NOT NULL
)

	SELECT @RateBase = RateBase,
		@RateMax = RateMax,
		@CostByWeightBreak = CostByWeightBreak
	FROM OPENJSON(@Cost,'$')
WITH (
	RateBase DECIMAL(19,6) '$.RateBase', 
	RateMax DECIMAL(19,6) '$.RateMax', 
	CostByWeightBreak NVARCHAR(MAX) '$.Cost' AS JSON 
)

	INSERT INTO @Temp1
		(
		WeightBreakLevelName,
		WeightBreakLowerBound,
		Cost
		)
	SELECT WeightBreakLevelName,
		WeightBreakLowerBound,
		Cost
	FROM OPENJSON(@CostByWeightBreak,'$')
WITH (
	WeightBreakLevelName NVARCHAR(50) '$.WeightBreakLevelName',  
	WeightBreakLowerBound INT '$.WeightBreakLowerBound',
	Cost DECIMAL(19,6) '$.Cost' 
)

	INSERT INTO @Temp2
		(
		WeightBreakLevelName,
		WeightBreakLowerBound,
		Cost
		)
			SELECT WeightBreakLevelName, WeightBreakLowerBound, Cost
		FROM @Temp1
		WHERE (WeightBreakLowerBound NOT IN (SELECT WeightBreakLowerBound
			FROM @Deleted) AND WeightBreakLevelName NOT IN (SELECT WeightBreakLevelName
			FROM @Deleted))
	UNION
		SELECT DISTINCT WeightBreakLevelName, WeightBreakLowerBound, 0
		FROM @Added

	INSERT INTO @Final
		(
		WeightBreakLevelName,
		WeightBreakLowerBound,
		Cost
		)
			SELECT B.WeightBreakLevelName, A.WeightBreakLowerBound, A.Cost
		FROM @Temp2 A
			INNER JOIN @Updated B ON A.WeightBreakLowerBound = B.WeightBreakLowerBound
	UNION
		SELECT WeightBreakLevelName, WeightBreakLowerBound, Cost
		FROM @Temp2
		WHERE (WeightBreakLowerBound NOT IN (SELECT WeightBreakLowerBound
			FROM @Updated) AND WeightBreakLevelName NOT IN (SELECT WeightBreakLevelName
			FROM @Updated))

	SELECT @NewCost = (SELECT WeightBreakLevelName, WeightBreakLowerBound, Cost
		FROM @Final B
		FOR JSON AUTO)

	RETURN '{"RateBase":' + CAST(@RateBase AS NVARCHAR(50)) + ', "RateMax":' + CAST(@RateMax AS NVARCHAR(50)) + ', "Cost":' + @NewCost + '}'

END
GO

