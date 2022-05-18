IF EXISTS (SELECT *
FROM sys.objects
WHERE  object_id = OBJECT_ID(N'[dbo].[GetRequestSectionLaneDefaultCost]')
	AND type IN ( N'FN', N'IF', N'TF', N'FS', N'FT' ))
  DROP FUNCTION [dbo].[GetRequestSectionLaneDefaultCost]
GO

CREATE FUNCTION dbo.GetRequestSectionLaneDefaultCost
(
	@RequestSectionID BIGINT
)

RETURNS NVARCHAR(MAX)
AS
BEGIN

	DECLARE @Cost NVARCHAR(MAX);

	DECLARE @WeightBreak NVARCHAR(MAX);

	SELECT @WeightBreak = WeightBreak
	FROM dbo.RequestSection
	WHERE RequestSectionID = @RequestSectionID

	SELECT @Cost = '{' +
  STUFF((
	SELECT ', ' + '"' +  CAST(E.value AS VARCHAR(MAX)) + '"' + ':' + CAST(0 AS VARCHAR(MAX))
		FROM
			(
		SELECT C.value
			FROM
				(
			SELECT A.value
				FROM OPENJSON(@WeightBreak) AS A
				WHERE A.value LIKE '%:true%'
		) AS B
		OUTER APPLY STRING_SPLIT(B.value, ' ') AS C
			WHERE C.value LIKE '%:true%'
	) AS D
	OUTER APPLY STRING_SPLIT(D.value, ':') AS E
		WHERE E.value NOT LIKE 'true'

		FOR XML PATH(''),TYPE).value('(./text())[1]','VARCHAR(MAX)')
  ,1,2,'') + '}'

	RETURN @Cost

END
GO

