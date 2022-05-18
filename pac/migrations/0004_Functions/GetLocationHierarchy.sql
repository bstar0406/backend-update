IF EXISTS (SELECT *
FROM sys.objects
WHERE  object_id = OBJECT_ID(N'[dbo].[GetLocationHierarchy]')
	AND type IN ( N'FN', N'IF', N'TF', N'FS', N'FT' ))
  DROP FUNCTION [dbo].[GetLocationHierarchy]
GO

CREATE FUNCTION dbo.GetLocationHierarchy
(
	@RequestSectionLanePointTypeName NVARCHAR(50)
)

RETURNS INT
AS
BEGIN

	DECLARE @LocationHierarchy INT;

	SELECT @LocationHierarchy = (SELECT DISTINCT LocationHierarchy
		FROM dbo.RequestSectionLanePointType
		WHERE RequestSectionLanePointTypeName = @RequestSectionLanePointTypeName)

	RETURN @LocationHierarchy

END
GO

