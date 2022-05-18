IF EXISTS (SELECT *
FROM sys.objects
WHERE  object_id = OBJECT_ID(N'[dbo].[TerminalCostWeightBreakLevel_Modify]')
	AND type IN ( N'FN', N'IF', N'TF', N'FS', N'FT' ))
  DROP FUNCTION [dbo].[TerminalCostWeightBreakLevel_Modify]
GO

CREATE FUNCTION dbo.TerminalCostWeightBreakLevel_Modify
(
	@Cost NVARCHAR(MAX), 
	@NewCostWeightBreakLevel CostWeightBreakLevelTableType_ID READONLY, 
	@DeletedCostWeightBreakLevel CostWeightBreakLevelTableType_ID READONLY,
	@ServiceOfferingID BIGINT
)

RETURNS NVARCHAR(MAX)
AS
BEGIN

	DECLARE @NewCost NVARCHAR(MAX);

	SELECT @NewCost = '{' +
STUFF((
    SELECT ', ' + '\"' +  CAST([key] AS VARCHAR(MAX)) + '\"' + ':' + CAST([value] AS VARCHAR(MAX))
		FROM
			(
						SELECT [key] , CAST([value] AS NUMERIC(19,6)) AS [value]
				FROM OPENJSON(@Cost)
				WHERE [key] NOT IN (SELECT [WeightBreakLevelID]
				FROM @DeletedCostWeightBreakLevel
				WHERE ServiceOfferingID = @ServiceOfferingID)
			UNION
				SELECT [WeightBreakLevelID], 0.0
				FROM @NewCostWeightBreakLevel
				WHERE ServiceOfferingID = @ServiceOfferingID) AS A
		FOR XML PATH(''),TYPE).value('(./text())[1]','VARCHAR(MAX)')
	,1,2,'') + '}';

	RETURN @NewCost

END
GO

