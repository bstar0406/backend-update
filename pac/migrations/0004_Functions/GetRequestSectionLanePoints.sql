IF EXISTS (SELECT *
FROM sys.objects
WHERE  object_id = OBJECT_ID(N'[dbo].[GetRequestSectionLanePoints]')
	AND type IN ( N'FN', N'IF', N'TF', N'FS', N'FT' ))
  DROP FUNCTION [dbo].[GetRequestSectionLanePoints]
GO

CREATE FUNCTION GetRequestSectionLanePoints
(
	@GroupTypeID BIGINT,
	@GroupID BIGINT,
	@PointTypeID BIGINT,
	@PointID BIGINT
)
RETURNS 
@Points TABLE 
(
	[ProvinceID] BIGINT NULL,
	[ProvinceCode] NVARCHAR(2) NULL,
	[RegionID] BIGINT NULL,
	[RegionCode] NVARCHAR(4) NULL,
	[CountryID] BIGINT NULL,
	[CountryCode] NVARCHAR(2) NULL,
	[TerminalID] BIGINT NULL,
	[TerminalCode] NVARCHAR(3) NULL,
	[ZoneID] BIGINT NULL,
	[ZoneName] NVARCHAR(50) NULL,
	[BasingPointID] BIGINT NULL,
	[BasingPointName] NVARCHAR(50) NULL,
	[ServicePointID] BIGINT NULL,
	[ServicePointName] NVARCHAR(50) NULL,
	[PostalCodeID] BIGINT NULL,
	[PostalCodeName] NVARCHAR(10) NULL,
	[PointCode] NVARCHAR(50) NULL
)
AS
BEGIN

	IF @GroupTypeID <= 0
		SELECT @GroupTypeID = NULL

	IF @GroupID <= 0
		SELECT @GroupID = NULL

	IF @PointTypeID <= 0
		SELECT @PointTypeID = NULL

	IF @PointID <= 0
		SELECT @PointID = NULL

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

	IF @GroupTypeID IS NULL
	BEGIN
		SELECT @GroupLocationHierarchy = @CountryLocationHierarchy
	END
	ELSE 
	BEGIN
		SELECT @GroupLocationHierarchy = LocationHierarchy
		FROM dbo.RequestSectionLanePointType
		WHERE RequestSectionLanePointTypeID = @GroupTypeID
	END

	IF @PointTypeID IS NULL
	BEGIN
		SELECT @PointLocationHierarchy = @PostalCodeLocationHierarchy
	END
	ELSE 
	BEGIN
		SELECT @PointLocationHierarchy = LocationHierarchy
		FROM dbo.RequestSectionLanePointType
		WHERE RequestSectionLanePointTypeID = @PointTypeID
	END

	IF @PointLocationHierarchy = @RegionLocationHierarchy
BEGIN
		INSERT INTO @Points
			(
			[ProvinceID],
			[ProvinceCode],
			[RegionID],
			[RegionCode],
			[CountryID],
			[CountryCode],
			[TerminalID],
			[TerminalCode],
			[ZoneID],
			[ZoneName],
			[BasingPointID],
			[BasingPointName],
			[ServicePointID],
			[ServicePointName],
			[PostalCodeID],
			[PostalCodeName],
			[PointCode]
			)
		SELECT DISTINCT NULL,
			NULL,
			R.[RegionID],
			R.[RegionCode],
			C.[CountryID],
			C.[CountryCode],
			NULL,
			NULL,
			NULL,
			NULL,
			NULL,
			NULL,
			NULL,
			NULL,
			NULL,
			NULL,
			R.[RegionCode]
		FROM dbo.Country C
			INNER JOIN dbo.Region R ON C.CountryID = R.CountryID
		WHERE (
		@GroupID IS NULL
			OR (@GroupLocationHierarchy = @CountryLocationHierarchy AND C.CountryID = @GroupID)
	)
			AND @PointID IS NULL OR R.RegionID = @PointID
	END
ELSE
BEGIN
		IF @PointLocationHierarchy = @ProvinceLocationHierarchy
	BEGIN
			INSERT INTO @Points
				(
				[ProvinceID],
				[ProvinceCode],
				[RegionID],
				[RegionCode],
				[CountryID],
				[CountryCode],
				[TerminalID],
				[TerminalCode],
				[ZoneID],
				[ZoneName],
				[BasingPointID],
				[BasingPointName],
				[ServicePointID],
				[ServicePointName],
				[PostalCodeID],
				[PostalCodeName],
				[PointCode]
				)
			SELECT DISTINCT P.[ProvinceID],
				P.[ProvinceCode],
				R.[RegionID],
				R.[RegionCode],
				C.[CountryID],
				C.[CountryCode],
				NULL,
				NULL,
				NULL,
				NULL,
				NULL,
				NULL,
				NULL,
				NULL,
				NULL,
				NULL,
				P.[ProvinceCode]
			FROM dbo.Country C
				INNER JOIN dbo.Region R ON C.CountryID = R.CountryID
				INNER JOIN dbo.Province P ON R.RegionID = P.RegionID
			WHERE (
			@GroupID IS NULL
				OR (@GroupLocationHierarchy = @CountryLocationHierarchy AND C.CountryID = @GroupID)
				OR (@GroupLocationHierarchy = @RegionLocationHierarchy AND R.RegionID = @GroupID)
		)
				AND @PointID IS NULL OR P.ProvinceID = @PointID
		END
	ELSE
	BEGIN
			IF @PointLocationHierarchy = @TerminalLocationHierarchy
		BEGIN
				INSERT INTO @Points
					(
					[ProvinceID],
					[ProvinceCode],
					[RegionID],
					[RegionCode],
					[CountryID],
					[CountryCode],
					[TerminalID],
					[TerminalCode],
					[ZoneID],
					[ZoneName],
					[BasingPointID],
					[BasingPointName],
					[ServicePointID],
					[ServicePointName],
					[PostalCodeID],
					[PostalCodeName],
					[PointCode]
					)
				SELECT DISTINCT P.[ProvinceID],
					P.[ProvinceCode],
					R.[RegionID],
					R.[RegionCode],
					C.[CountryID],
					C.[CountryCode],
					T.[TerminalID],
					T.[TerminalCode],
					NULL,
					NULL,
					NULL,
					NULL,
					NULL,
					NULL,
					NULL,
					NULL,
					T.[TerminalCode]
				FROM dbo.Country C
					INNER JOIN dbo.Region R ON C.CountryID = R.CountryID
					INNER JOIN dbo.Province P ON R.RegionID = P.RegionID
					INNER JOIN dbo.City Y ON P.ProvinceID = Y.ProvinceID
					INNER JOIN dbo.Terminal T ON T.CityID = Y.CityID
				WHERE (
				@GroupID IS NULL
					OR (@GroupLocationHierarchy = @CountryLocationHierarchy AND C.CountryID = @GroupID)
					OR (@GroupLocationHierarchy = @RegionLocationHierarchy AND R.RegionID = @GroupID)
					OR (@GroupLocationHierarchy = @ProvinceLocationHierarchy AND P.ProvinceID = @GroupID)
			)
					AND @PointID IS NULL OR T.TerminalID = @PointID
			END
		ELSE
		BEGIN
				IF @PointLocationHierarchy = @BasingPointLocationHierarchy
			BEGIN
					INSERT INTO @Points
						(
						[ProvinceID],
						[ProvinceCode],
						[RegionID],
						[RegionCode],
						[CountryID],
						[CountryCode],
						[TerminalID],
						[TerminalCode],
						[ZoneID],
						[ZoneName],
						[BasingPointID],
						[BasingPointName],
						[ServicePointID],
						[ServicePointName],
						[PostalCodeID],
						[PostalCodeName],
						[PointCode]
						)
					SELECT DISTINCT P.[ProvinceID],
						P.[ProvinceCode],
						R.[RegionID],
						R.[RegionCode],
						C.[CountryID],
						C.[CountryCode],
						NULL,
						NULL,
						NULL,
						NULL,
						BP.BasingPointID,
						BP.BasingPointName,
						NULL,
						NULL,
						NULL,
						NULL,
						BP.BasingPointName
					FROM dbo.Country C
						INNER JOIN dbo.Region R ON C.CountryID = R.CountryID
						INNER JOIN dbo.Province P ON R.RegionID = P.RegionID
						INNER JOIN dbo.BasingPoint BP ON P.ProvinceID = BP.ProvinceID
					WHERE (
					@GroupID IS NULL
						OR (@GroupLocationHierarchy = @CountryLocationHierarchy AND C.CountryID = @GroupID)
						OR (@GroupLocationHierarchy = @RegionLocationHierarchy AND R.RegionID = @GroupID)
						OR (@GroupLocationHierarchy = @ProvinceLocationHierarchy AND P.ProvinceID = @GroupID)
				)
						AND @PointID IS NULL OR BP.BasingPointID = @PointID
				END
			ELSE
			BEGIN
					IF @PointLocationHierarchy = @ServicePointLocationHierarchy
				BEGIN
						INSERT INTO @Points
							(
							[ProvinceID],
							[ProvinceCode],
							[RegionID],
							[RegionCode],
							[CountryID],
							[CountryCode],
							[TerminalID],
							[TerminalCode],
							[ZoneID],
							[ZoneName],
							[BasingPointID],
							[BasingPointName],
							[ServicePointID],
							[ServicePointName],
							[PostalCodeID],
							[PostalCodeName],
							[PointCode]
							)
						SELECT DISTINCT P.[ProvinceID],
							P.[ProvinceCode],
							R.[RegionID],
							R.[RegionCode],
							C.[CountryID],
							C.[CountryCode],
							T.[TerminalID],
							T.[TerminalCode],
							NULL,
							NULL,
							BP.BasingPointID,
							BP.BasingPointName,
							SP.ServicePointID,
							SP.ServicePointName,
							NULL,
							NULL,
							SP.ServicePointName
						FROM dbo.Country C
							INNER JOIN dbo.Region R ON C.CountryID = R.CountryID
							INNER JOIN dbo.Province P ON R.RegionID = P.RegionID
							INNER JOIN dbo.ServicePoint SP ON P.ProvinceID = SP.ProvinceID
							INNER JOIN dbo.TerminalServicePoint TSP ON SP.ServicePointID = TSP.ServicePointID
							INNER JOIN dbo.Terminal T ON TSP.TerminalID = T.TerminalID
							LEFT JOIN dbo.BasingPoint BP ON SP.BasingPointID = BP.BasingPointID
						WHERE (
						@GroupID IS NULL
							OR (@GroupLocationHierarchy = @CountryLocationHierarchy AND C.CountryID = @GroupID)
							OR (@GroupLocationHierarchy = @RegionLocationHierarchy AND R.RegionID = @GroupID)
							OR (@GroupLocationHierarchy = @ProvinceLocationHierarchy AND P.ProvinceID = @GroupID)
					)
							AND @PointID IS NULL OR SP.ServicePointID = @PointID
					END
				ELSE
				BEGIN
						INSERT INTO @Points
							(
							[ProvinceID],
							[ProvinceCode],
							[RegionID],
							[RegionCode],
							[CountryID],
							[CountryCode],
							[TerminalID],
							[TerminalCode],
							[ZoneID],
							[ZoneName],
							[BasingPointID],
							[BasingPointName],
							[ServicePointID],
							[ServicePointName],
							[PostalCodeID],
							[PostalCodeName],
							[PointCode]
							)
						SELECT DISTINCT P.[ProvinceID],
							P.[ProvinceCode],
							R.[RegionID],
							R.[RegionCode],
							C.[CountryID],
							C.[CountryCode],
							T.[TerminalID],
							T.[TerminalCode],
							NULL,
							NULL,
							BP.BasingPointID,
							BP.BasingPointName,
							SP.ServicePointID,
							SP.ServicePointName,
							PC.PostalCodeID,
							PC.PostalCodeName,
							PC.PostalCodeName
						FROM dbo.Country C
							INNER JOIN dbo.Region R ON C.CountryID = R.CountryID
							INNER JOIN dbo.Province P ON R.RegionID = P.RegionID
							INNER JOIN dbo.ServicePoint SP ON P.ProvinceID = SP.ProvinceID
							INNER JOIN dbo.TerminalServicePoint TSP ON SP.ServicePointID = TSP.ServicePointID
							INNER JOIN dbo.Terminal T ON TSP.TerminalID = T.TerminalID
							INNER JOIN dbo.PostalCode PC ON SP.ServicePointID = PC.ServicePointID
							LEFT JOIN dbo.BasingPoint BP ON SP.BasingPointID = BP.BasingPointID
						WHERE (
						@GroupID IS NULL
							OR (@GroupLocationHierarchy = @CountryLocationHierarchy AND C.CountryID = @GroupID)
							OR (@GroupLocationHierarchy = @RegionLocationHierarchy AND R.RegionID = @GroupID)
							OR (@GroupLocationHierarchy = @ProvinceLocationHierarchy AND P.ProvinceID = @GroupID)
					)
							AND @PointID IS NULL OR PC.PostalCodeID = @PointID
					END
				END
			END
		END
	END
	RETURN
END
GO