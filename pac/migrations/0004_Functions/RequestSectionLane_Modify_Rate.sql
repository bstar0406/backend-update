IF EXISTS (SELECT *
FROM sys.objects
WHERE  object_id = OBJECT_ID(N'[dbo].[RequestSectionLane_Modify_Rate]')
	AND type IN ( N'FN', N'IF', N'TF', N'FS', N'FT' ))
  DROP FUNCTION [dbo].[RequestSectionLane_Modify_Rate]
GO

CREATE FUNCTION dbo.RequestSectionLane_Modify_Rate
(
	@Cost DECIMAL(19,6),
	@Operation NVARCHAR(1),
	@Multiplier DECIMAL(19,6)
)

RETURNS NVARCHAR(MAX)
AS
BEGIN

	DECLARE @NewCost DECIMAL(19,6);

	SELECT @NewCost = CASE 
	WHEN @Operation = '+' THEN @Cost + @Multiplier
	WHEN @Operation = '-' THEN @Cost - @Multiplier
	WHEN @Operation = '*' THEN @Cost * @Multiplier
	WHEN @Operation = '/' THEN @Cost / @Multiplier
	WHEN @Operation = '=' THEN @Multiplier
	END

	RETURN @NewCost

END
GO

