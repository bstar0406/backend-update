IF EXISTS (SELECT *
FROM sys.objects
WHERE  object_id = OBJECT_ID(N'[dbo].[TerminalCost_Select]')
	AND type IN ( N'FN', N'IF', N'TF', N'FS', N'FT' ))
  DROP FUNCTION [dbo].[TerminalCost_Select]
GO

CREATE FUNCTION dbo.TerminalCost_Select
(
	@Cost NVARCHAR(MAX)
)

RETURNS NVARCHAR(MAX)
AS
BEGIN

	DECLARE @NewCost NVARCHAR(MAX);

	SELECT @NewCost = [value]
	FROM OPENJSON(@Cost,'$.CostComponents')
	WHERE [key] = 'CostByWeightBreak'

	RETURN @NewCost

END
GO

