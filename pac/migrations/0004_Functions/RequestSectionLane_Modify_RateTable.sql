IF EXISTS (SELECT *
FROM sys.objects
WHERE  object_id = OBJECT_ID(N'[dbo].[RequestSectionLane_Modify_RateTable]')
	AND type IN ( N'FN', N'IF', N'TF', N'FS', N'FT' ))
  DROP FUNCTION [dbo].[RequestSectionLane_Modify_RateTable]
GO

CREATE FUNCTION dbo.RequestSectionLane_Modify_RateTable
(
	@Cost NVARCHAR(MAX),
	@WeightBreak IDTableType READONLY,
	@Operation NVARCHAR(1),
	@Multiplier DECIMAL(19,6)
)

RETURNS NVARCHAR(MAX)
AS
BEGIN

	DECLARE @NewCost NVARCHAR(MAX);

	DECLARE @Count INT;
	SELECT @Count = COUNT(*)
	FROM @WeightBreak;

	With
		A
		AS
		(
			SELECT [key], [value]
			FROM OPENJSON(@Cost)
		)

	SELECT @NewCost = '{' +
 STUFF((
SELECT ', ' + '"' +  CAST(C.[key] AS VARCHAR(MAX)) + '"' + ':' + CAST(C.[value] AS VARCHAR(MAX))
		FROM
			(
				SELECT A.[key], CASE 
	WHEN @Operation = '+' THEN A.[value] + @Multiplier
	WHEN @Operation = '-' THEN A.[value] - @Multiplier
	WHEN @Operation = '*' THEN A.[value] * @Multiplier
	WHEN @Operation = '/' THEN A.[value] / @Multiplier
	WHEN @Operation = '=' THEN  @Multiplier
	END AS [value]
				FROM A
				WHERE @Count = 0 OR A.[key] IN (SELECT ID
					FROM @WeightBreak)
			UNION
				SELECT A.[key], A.[value]
				FROM A
				WHERE @Count > 0 AND A.[key] NOT IN (SELECT ID
					FROM @WeightBreak)
) AS C
		FOR XML PATH(''),TYPE).value('(./text())[1]','VARCHAR(MAX)')
,1,2,'') + '}'

	RETURN @NewCost

END
GO

