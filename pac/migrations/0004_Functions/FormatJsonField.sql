IF EXISTS (SELECT *
FROM sys.objects
WHERE  object_id = OBJECT_ID(N'[dbo].[FormatJsonField]')
	AND type IN ( N'FN', N'IF', N'TF', N'FS', N'FT' ))
  DROP FUNCTION [dbo].[FormatJsonField]
GO

CREATE FUNCTION dbo.FormatJsonField
(
	@JSON NVARCHAR(MAX)
)

RETURNS NVARCHAR(MAX)
AS
BEGIN

	DECLARE @NewJSON NVARCHAR(MAX);

	SELECT @NewJSON = REPLACE(REPLACE(REPLACE(REPLACE(REPLACE (@JSON, '\', ''), '}",','},'), ':"{', ':{'), '""', '{}'), '}"', '}');

	RETURN @NewJSON

END
GO

