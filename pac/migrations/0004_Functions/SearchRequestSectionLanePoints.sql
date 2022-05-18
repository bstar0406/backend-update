IF EXISTS (SELECT *
FROM sys.objects
WHERE  object_id = OBJECT_ID(N'[dbo].[SearchRequestSectionLanePoints]')
	AND type IN ( N'FN', N'IF', N'TF', N'FS', N'FT' ))
  DROP FUNCTION [dbo].[SearchRequestSectionLanePoints]
GO

CREATE FUNCTION SearchRequestSectionLanePoints
(
	@GroupTypeName NVARCHAR(50),
	@GroupID BIGINT = NULL,
	@PointTypeName NVARCHAR(50),
	@PointName NVARCHAR(50) = NULL
)
RETURNS 
@Points TABLE 
(
	[point_id] BIGINT NULL,
	[point_name] NVARCHAR(50) NULL
)
AS
BEGIN

	IF (@GroupID IS NOT NULL AND @GroupID <= 0)
		SELECT @GroupID = NULL;

	DECLARE @CountryLocationHierarchy INT;
	DECLARE @RegionLocationHierarchy INT;
	DECLARE @ProvinceLocationHierarchy INT;
	DECLARE @TerminalLocationHierarchy INT;
	DECLARE @BasingPointLocationHierarchy INT;
	DECLARE @ServicePointLocationHierarchy INT;
	DECLARE @PostalCodeLocationHierarchy INT;

	SELECT @CountryLocationHierarchy = dbo.GetLocationHierarchy('Country')
	SELECT @RegionLocationHierarchy = dbo.GetLocationHierarchy('Region')
	SELECT @ProvinceLocationHierarchy = dbo.GetLocationHierarchy('Province')
	SELECT @TerminalLocationHierarchy = dbo.GetLocationHierarchy('Terminal')
	SELECT @BasingPointLocationHierarchy = dbo.GetLocationHierarchy('Basing Point')
	SELECT @ServicePointLocationHierarchy = dbo.GetLocationHierarchy('Service Point')
	SELECT @PostalCodeLocationHierarchy = dbo.GetLocationHierarchy('Postal Code')

	DECLARE @GroupLocationHierarchy INT;
	DECLARE @PointLocationHierarchy INT;

	SELECT @GroupLocationHierarchy = LocationHierarchy
	FROM dbo.RequestSectionLanePointType
	WHERE RequestSectionLanePointTypeName = @GroupTypeName
	SELECT @PointLocationHierarchy = LocationHierarchy
	FROM dbo.RequestSectionLanePointType
	WHERE RequestSectionLanePointTypeName = @PointTypeName

	DECLARE @Count INT;

	IF @PointName IS NOT NULL AND LEN(@PointName)>0 AND @PointName <> '$None$'
		SELECT @Count = 100
	ELSE
		BEGIN
		SELECT @PointName = NULL;
		SELECT @Count = 1E9
	END

	IF @PointLocationHierarchy = @RegionLocationHierarchy
	BEGIN
		INSERT INTO @Points
			(
			[point_id],
			[point_name]
			)
		SELECT DISTINCT TOP (@Count)
			R.RegionID, R.RegionCode
		FROM dbo.Country C
			INNER JOIN dbo.Region R ON C.CountryID = R.CountryID
		WHERE (
			(@GroupID IS NULL OR (@GroupID IS NOT NULL AND @GroupLocationHierarchy = @CountryLocationHierarchy AND C.CountryID = @GroupID))
		)
			AND (@PointName IS NULL OR R.RegionCode LIKE @PointName +'%')
	END

	IF @PointLocationHierarchy = @ProvinceLocationHierarchy
	BEGIN
		INSERT INTO @Points
			(
			[point_id],
			[point_name]
			)
		SELECT DISTINCT TOP (@Count)
			P.ProvinceID, P.ProvinceCode
		FROM dbo.Country C
			INNER JOIN dbo.Region R ON C.CountryID = R.CountryID
			INNER JOIN dbo.Province P ON R.RegionID = P.RegionID
		WHERE (
			(@GroupID IS NULL)
			OR (@GroupID IS NOT NULL AND (
			(@GroupLocationHierarchy = @CountryLocationHierarchy AND C.CountryID = @GroupID)
			OR (@GroupLocationHierarchy = @RegionLocationHierarchy AND R.RegionID = @GroupID)
			))
		)
			AND (@PointName IS NULL OR P.ProvinceCode LIKE @PointName +'%')
	END

	IF @PointLocationHierarchy = @TerminalLocationHierarchy
	BEGIN
		INSERT INTO @Points
			(
			[point_id],
			[point_name]
			)
		SELECT DISTINCT TOP (@Count)
			T.TerminalID, T.TerminalCode
		FROM dbo.Country C
			INNER JOIN dbo.Region R ON C.CountryID = R.CountryID
			INNER JOIN dbo.Province P ON R.RegionID = P.RegionID
			INNER JOIN dbo.City Y ON P.ProvinceID = Y.ProvinceID
			INNER JOIN dbo.Terminal T ON T.CityID = Y.CityID
		WHERE (
			(@GroupID IS NULL)
			OR (@GroupID IS NOT NULL AND (
			(@GroupLocationHierarchy = @CountryLocationHierarchy AND C.CountryID = @GroupID)
			OR (@GroupLocationHierarchy = @RegionLocationHierarchy AND R.RegionID = @GroupID)
			OR (@GroupLocationHierarchy = @ProvinceLocationHierarchy AND P.ProvinceID = @GroupID)
			))
		)
			AND (@PointName IS NULL OR T.TerminalCode LIKE @PointName +'%')
	END

	IF @PointLocationHierarchy = @BasingPointLocationHierarchy
	BEGIN
		INSERT INTO @Points
			(
			[point_id],
			[point_name]
			)
		SELECT DISTINCT TOP (@Count)
			BP.BasingPointID, BP.BasingPointName
		FROM dbo.Country C
			INNER JOIN dbo.Region R ON C.CountryID = R.CountryID
			INNER JOIN dbo.Province P ON R.RegionID = P.RegionID
			INNER JOIN dbo.BasingPoint BP ON BP.ProvinceID = P.ProvinceID
		WHERE (
			(@GroupID IS NULL)
			OR (@GroupID IS NOT NULL AND (
			(@GroupLocationHierarchy = @CountryLocationHierarchy AND C.CountryID = @GroupID)
			OR (@GroupLocationHierarchy = @RegionLocationHierarchy AND R.RegionID = @GroupID)
			OR (@GroupLocationHierarchy = @ProvinceLocationHierarchy AND P.ProvinceID = @GroupID)
			))
		)
			AND (@PointName IS NULL OR BP.BasingPointName LIKE @PointName +'%')
	END

	IF @PointLocationHierarchy = @ServicePointLocationHierarchy
	BEGIN
		INSERT INTO @Points
			(
			[point_id],
			[point_name]
			)
		SELECT DISTINCT TOP (@Count)
			SP.ServicePointID, SP.ServicePointName + ', ' + P.ProvinceCode
		FROM dbo.Country C
			INNER JOIN dbo.Region R ON C.CountryID = R.CountryID
			INNER JOIN dbo.Province P ON R.RegionID = P.RegionID
			INNER JOIN dbo.BasingPoint BP ON BP.ProvinceID = P.ProvinceID
			LEFT JOIN dbo.ServicePoint SP ON (SP.BasingPointID IS NULL AND SP.ProvinceID = P.ProvinceID) OR (SP.BasingPointID IS NOT NULL AND SP.BasingPointID = BP.BasingPointID)
			LEFT JOIN dbo.TerminalServicePoint TSP ON SP.ServicePointID = TSP.ServicePointID
		WHERE (
			(@GroupID IS NULL)
			OR (@GroupID IS NOT NULL AND (
			(@GroupLocationHierarchy = @CountryLocationHierarchy AND C.CountryID = @GroupID)
			OR (@GroupLocationHierarchy = @RegionLocationHierarchy AND R.RegionID = @GroupID)
			OR (@GroupLocationHierarchy = @ProvinceLocationHierarchy AND P.ProvinceID = @GroupID)
			OR (@GroupLocationHierarchy = @TerminalLocationHierarchy AND TSP.TerminalID = @GroupID)
			OR (@GroupLocationHierarchy = @BasingPointLocationHierarchy AND BP.BasingPointID = @GroupID)
			))
		)
			AND (@PointName IS NULL OR SP.ServicePointName LIKE @PointName +'%')
	END

	IF @PointLocationHierarchy = @PostalCodeLocationHierarchy
	BEGIN
		INSERT INTO @Points
			(
			[point_id],
			[point_name]
			)
		SELECT DISTINCT TOP (@Count)
			PC.PostalCodeID, PC.PostalCodeName
		FROM dbo.Country C
			INNER JOIN dbo.Region R ON C.CountryID = R.CountryID
			INNER JOIN dbo.Province P ON R.RegionID = P.RegionID
			INNER JOIN dbo.BasingPoint BP ON BP.ProvinceID = P.ProvinceID
			LEFT JOIN dbo.ServicePoint SP ON (SP.BasingPointID IS NULL AND SP.ProvinceID = P.ProvinceID) OR (SP.BasingPointID IS NOT NULL AND SP.BasingPointID = BP.BasingPointID)
			LEFT JOIN dbo.TerminalServicePoint TSP ON SP.ServicePointID = TSP.ServicePointID
			LEFT JOIN dbo.PostalCode PC ON SP.ServicePointID = PC.ServicePointID
		WHERE (
			(@GroupID IS NULL)
			OR (@GroupID IS NOT NULL AND (
			(@GroupLocationHierarchy = @CountryLocationHierarchy AND C.CountryID = @GroupID)
			OR (@GroupLocationHierarchy = @RegionLocationHierarchy AND R.RegionID = @GroupID)
			OR (@GroupLocationHierarchy = @ProvinceLocationHierarchy AND P.ProvinceID = @GroupID)
			OR (@GroupLocationHierarchy = @TerminalLocationHierarchy AND TSP.TerminalID = @GroupID)
			OR (@GroupLocationHierarchy = @BasingPointLocationHierarchy AND BP.BasingPointID = @GroupID)
			OR (@GroupLocationHierarchy = @ServicePointLocationHierarchy AND SP.ServicePointID = @GroupID)
			))
		)
			AND (@PointName IS NULL OR PC.PostalCodeName LIKE @PointName +'%')
	END

	RETURN
END
GO