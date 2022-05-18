GET_ACCOUNT_HISTORY = """
DECLARE @AccountID BIGINT;
SELECT @AccountID = C.AccountID
FROM dbo.Request R
INNER JOIN dbo.RequestInformation RI ON R.RequestInformationID = RI.RequestInformationID
INNER JOIN dbo.Customer C ON RI.CustomerID = C.CustomerID
WHERE R.RequestID = {0}

SELECT CAST(
(SELECT *
FROM
(
	SELECT R.RequestID AS request_id,
		R.RequestNumber AS request_number,
		R.RequestCode AS request_code,
		CASE WHEN C.AccountID IS NULL THEN 'New' ELSE 'Expanded' END AS business_type_name,
		ISNULL(RS.SalesRepresentativeID, '') AS sales_representative_id,
		ISNULL(SR.UserName, '') AS sales_representative_name,
		ISNULL(RS.PricingAnalystID, '') AS pricing_analyst_id,
		ISNULL(PA.UserName, '') AS pricing_analyst_name,
		ISNULL(R.SubmittedOn, '') AS date_submitted,
		ISNULL(T.PublishedOn, '') AS date_published,
		ISNULL(T.ExpiresOn, '') AS expiration_date,
		ISNULL(T.DocumentUrl, '') AS document_url
	FROM dbo.Account A
		RIGHT JOIN dbo.Customer C ON A.AccountID = C.AccountID
		INNER JOIN dbo.RequestInformation RI ON C.CustomerID = RI.CustomerID
		INNER JOIN dbo.Request R ON RI.RequestInformationID = R.RequestInformationID
		LEFT JOIN dbo.Tariff T ON R.RequestID = T.RequestID
		LEFT JOIN dbo.RequestStatus RS ON R.RequestID = RS.RequestID
		LEFT JOIN dbo.[User] SR ON RS.SalesRepresentativeID = SR.UserID
		LEFT JOIN dbo.[User] PA ON RS.PricingAnalystID = PA.UserID
	WHERE A.AccountID = @AccountID) AS Q
	FOR JSON AUTO)
	AS VARCHAR(MAX))
"""

GET_TARIFF_HISTORY = """
DECLARE @CustomerID BIGINT;
SELECT @CustomerID = C.CustomerID
FROM dbo.Request R
INNER JOIN dbo.RequestInformation RI ON R.RequestInformationID = RI.RequestInformationID
INNER JOIN dbo.Customer C ON RI.CustomerID = C.CustomerID
WHERE R.RequestID = {0}

SELECT CAST(
(SELECT *
FROM
(
	SELECT R.RequestID AS request_id,
		R.RequestNumber AS request_number,
		R.RequestCode AS request_code,
		CASE WHEN C.AccountID IS NULL THEN 'New' ELSE 'Expanded' END AS business_type_name,
		RH.VersionNum AS version_num,
		RH.UpdatedOn AS version_saved_on,
		RH.UpdatedBy AS saved_by,
		RH.Comments AS comments
	FROM Customer C 
		INNER JOIN dbo.RequestInformation RI ON C.CustomerID = RI.CustomerID
		INNER JOIN dbo.Request R ON RI.RequestInformationID = R.RequestInformationID
		INNER JOIN dbo.Request_History RH ON R.RequestID = RH.RequestID AND RH.IsLatestVersion = 1
	WHERE C.CustomerID = @CustomerID) AS Q
	FOR JSON AUTO)
	AS VARCHAR(MAX))
"""

GET_REQUEST_LANE_LOCATION_TREE = """
DECLARE @RequestSectionID BIGINT = {0};
DECLARE @OrigPointTypeName NVARCHAR(50) = '{1}';
DECLARE @OrigPointID BIGINT = {2};
DECLARE @DestPointTypeName NVARCHAR(50) = '{3}';
DECLARE @DestPointID BIGINT = {4};
DECLARE @LaneStatusName NVARCHAR(50) = '{5}';

With RequestSectionLanes AS 
(SELECT RSL.*
FROM dbo.RequestSectionLane{6} RSL
WHERE RSL.RequestSectionID = @RequestSectionID AND RSL.IsActive = 1 AND RSL.IsInactiveViewable = 1
AND	( (@LaneStatusName = 'None') OR (@LaneStatusName = 'New' AND [IsPublished] = 0) OR (@LaneStatusName = 'Changed' AND [IsEdited] = 1) OR (@LaneStatusName = 'Duplicated' AND [IsDuplicate] = 1) OR (@LaneStatusName = 'DoNotMeetCommitment' AND [DoNotMeetCommitment] = 1))
	AND ( (@OrigPointTypeName = 'None') OR
		(@OrigPointTypeName = 'Country' AND OriginCountryID = @OrigPointID) OR (@OrigPointTypeName = 'Region' AND OriginRegionID = @OrigPointID)
		OR
		(@OrigPointTypeName = 'Province' AND OriginProvinceID = @OrigPointID) OR (@OrigPointTypeName = 'Terminal' AND OriginTerminalID = @OrigPointID)
		OR 
		(@OrigPointTypeName = 'Basing Point' AND OriginBasingPointID = @OrigPointID) OR (@OrigPointTypeName = 'Service Point' AND OriginServicePointID = @OrigPointID)
		OR
		(@OrigPointTypeName = 'Postal Code' AND OriginPostalCodeID = @OrigPointID) OR (@OrigPointTypeName = 'Point Type' AND OriginPointTypeID = @OrigPointID)
		)
	AND ( (@DestPointTypeName = 'None') OR
		(@DestPointTypeName = 'Country' AND DestinationCountryID = @DestPointID) OR (@DestPointTypeName = 'Region' AND DestinationRegionID = @DestPointID)
		OR
		(@DestPointTypeName = 'Province' AND DestinationProvinceID = @DestPointID) OR (@DestPointTypeName = 'Terminal' AND DestinationTerminalID = @DestPointID)
		OR 
		(@DestPointTypeName = 'Basing Point' AND DestinationBasingPointID = @DestPointID) OR (@DestPointTypeName = 'Service Point' AND DestinationServicePointID = @DestPointID)
		OR
		(@DestPointTypeName = 'Postal Code' AND DestinationPostalCodeID = @DestPointID) OR (@DestPointTypeName = 'Point Type' AND DestinationPointTypeID = @DestPointID)
		)
),
O_PC AS 
(SELECT DISTINCT OriginPostalCodeID AS postal_code_id, OriginPostalCodeName AS postal_code_name
FROM RequestSectionLanes
WHERE OriginPostalCodeID IS NOT NULL),
D_PC AS 
(SELECT DISTINCT DestinationPostalCodeID AS postal_code_id, DestinationPostalCodeName AS postal_code_name
FROM RequestSectionLanes
WHERE DestinationPostalCodeID IS NOT NULL),
O_SP AS 
(SELECT DISTINCT OriginServicePointID AS service_point_id, OriginServicePointName AS service_point_name
FROM RequestSectionLanes
WHERE OriginServicePointID IS NOT NULL),
D_SP AS 
(SELECT DISTINCT DestinationServicePointID AS service_point_id, DestinationServicePointName AS service_point_name
FROM RequestSectionLanes
WHERE DestinationServicePointID IS NOT NULL),
O_T AS 
(SELECT DISTINCT OriginTerminalID AS terminal_id, OriginTerminalCode AS terminal_code
FROM RequestSectionLanes
WHERE OriginTerminalID IS NOT NULL),
D_T AS 
(SELECT DISTINCT DestinationTerminalID AS terminal_id, DestinationTerminalCode AS terminal_code
FROM RequestSectionLanes 
WHERE DestinationTerminalID IS NOT NULL),
O_BP AS 
(SELECT DISTINCT OriginBasingPointID AS basing_point_id, OriginBasingPointName AS basing_point_name
FROM RequestSectionLanes
WHERE OriginBasingPointID IS NOT NULL),
D_BP AS 
(SELECT DISTINCT DestinationBasingPointID AS basing_point_id, DestinationBasingPointName AS basing_point_name
FROM RequestSectionLanes
WHERE DestinationBasingPointID IS NOT NULL),
O_P AS 
(SELECT DISTINCT OriginProvinceID AS province_id, OriginProvinceCode AS province_code
FROM RequestSectionLanes
WHERE OriginProvinceID IS NOT NULL),
D_P AS 
(SELECT DISTINCT DestinationProvinceID AS province_id, DestinationProvinceCode AS province_code
FROM RequestSectionLanes
WHERE DestinationProvinceID IS NOT NULL),
O_R AS 
(SELECT DISTINCT OriginRegionID AS region_id, OriginRegionCode AS region_code
FROM RequestSectionLanes
WHERE OriginRegionID IS NOT NULL),
D_R AS 
(SELECT DISTINCT DestinationRegionID AS region_id, DestinationRegionCode AS region_code
FROM RequestSectionLanes
WHERE DestinationRegionID IS NOT NULL),
O_C AS 
(SELECT DISTINCT OriginCountryID AS country_id, OriginCountryCode AS country_code
FROM RequestSectionLanes
WHERE OriginCountryID IS NOT NULL),
D_C AS 
(SELECT DISTINCT DestinationCountryID AS country_id, DestinationCountryCode AS country_code
FROM RequestSectionLanes
WHERE DestinationCountryID IS NOT NULL),
O_Z AS 
(SELECT DISTINCT OriginZoneID AS zone_id, OriginZoneName AS zone_name
FROM RequestSectionLanes
WHERE OriginZoneID IS NOT NULL),
D_Z AS 
(SELECT DISTINCT DestinationZoneID AS zone_id, DestinationZoneName AS zone_name
FROM RequestSectionLanes
WHERE DestinationZoneID IS NOT NULL),
O_PT AS 
(SELECT DISTINCT OriginPointTypeID AS point_type_id, OriginPointTypeName AS point_type_name
FROM RequestSectionLanes
WHERE OriginPointTypeID IS NOT NULL),
D_PT AS 
(SELECT DISTINCT DestinationPointTypeID AS point_type_id, DestinationPointTypeName AS point_type_name
FROM RequestSectionLanes
WHERE DestinationPointTypeID IS NOT NULL),
Origin AS 
(SELECT 
	(SELECT * FROM O_PT FOR JSON AUTO) AS point_types,
	(SELECT * FROM O_Z FOR JSON AUTO) AS zones,
	(SELECT * FROM O_C FOR JSON AUTO) AS countries,
	(SELECT * FROM O_R FOR JSON AUTO) AS regions,
	(SELECT * FROM O_P FOR JSON AUTO) AS provinces,
	(SELECT * FROM O_BP FOR JSON AUTO) AS basing_points,
	(SELECT * FROM O_T FOR JSON AUTO) AS terminals,
	(SELECT * FROM O_SP FOR JSON AUTO) AS service_points,
	(SELECT * FROM O_PC FOR JSON AUTO) AS postal_codes
),
Destination AS 
(SELECT
	(SELECT * FROM D_PT FOR JSON AUTO) AS point_types,
	(SELECT * FROM D_Z FOR JSON AUTO) AS zones,
	(SELECT * FROM D_C FOR JSON AUTO) AS countries,
	(SELECT * FROM D_R FOR JSON AUTO) AS regions,
	(SELECT * FROM D_P FOR JSON AUTO) AS provinces,
	(SELECT * FROM D_BP FOR JSON AUTO) AS basing_points,
	(SELECT * FROM D_T FOR JSON AUTO) AS terminals,
	(SELECT * FROM D_SP FOR JSON AUTO) AS service_points,
	(SELECT * FROM D_PC FOR JSON AUTO) AS postal_codes
)

SELECT CAST(
(SELECT *
FROM
(
SELECT (SELECT * FROM Origin FOR JSON AUTO, WITHOUT_ARRAY_WRAPPER) AS orig, (SELECT * FROM Destination FOR JSON AUTO, WITHOUT_ARRAY_WRAPPER) AS dest
) AS Q
	FOR JSON AUTO, WITHOUT_ARRAY_WRAPPER)
	AS VARCHAR(MAX))
"""

SEARCH_REQUEST_SECTION_LANE_POINTS = """ 
SELECT CAST(
(SELECT *
FROM
(
SELECT *
FROM dbo.SearchRequestSectionLanePoints('{0}', {1}, '{2}', '{3}')) AS Q
	FOR JSON AUTO)
	AS VARCHAR(MAX)) 
"""

SEARCH_ORIGIN_POSTAL_CODE = """ 
DECLARE @PostalCodeID BIGINT = (SELECT OriginPostalCodeID FROM dbo.RequestSectionLane WHERE RequestSectionLaneID = {0});

IF @PostalCodeID IS NOT NULL
BEGIN
	SELECT CAST((SELECT * FROM (
	SELECT DISTINCT TOP 100 PC.PostalCodeID, PC.PostalCodeName
	FROM dbo.PostalCode PC
	WHERE PC.PostalCodeID = @PostalCodeID AND PC.PostalCodeName LIKE '{1}%'
	) AS Q FOR JSON AUTO) AS VARCHAR(MAX))
END
ELSE
BEGIN 
	DECLARE @ServicePointID BIGINT = (SELECT OriginServicePointID FROM dbo.RequestSectionLane WHERE RequestSectionLaneID = {0});
	IF @ServicePointID IS NOT NULL
	BEGIN
		SELECT CAST((SELECT * FROM (
		SELECT DISTINCT TOP 100 PC.PostalCodeID, PC.PostalCodeName
		FROM dbo.PostalCode PC
		INNER JOIN dbo.ServicePoint SP ON PC.ServicePointID = SP.ServicePointID
		WHERE SP.ServicePointID = @ServicePointID AND PC.PostalCodeName LIKE '{1}%'
		) AS Q FOR JSON AUTO) AS VARCHAR(MAX))
	END
	ELSE
	BEGIN
		DECLARE @BasingPointID BIGINT = (SELECT OriginBasingPointID FROM dbo.RequestSectionLane WHERE RequestSectionLaneID = {0}	);
		IF @BasingPointID IS NOT NULL
		BEGIN
			SELECT CAST((SELECT * FROM (
			SELECT DISTINCT TOP 100 PC.PostalCodeID, PC.PostalCodeName
			FROM dbo.PostalCode PC
			INNER JOIN dbo.ServicePoint SP ON PC.ServicePointID = SP.ServicePointID
			INNER JOIN dbo.BasingPoint BP ON SP.BasingPointID = BP.BasingPointID
			WHERE BP.BasingPointID = @BasingPointID AND PC.PostalCodeName LIKE '{1}%'
			) AS Q FOR JSON AUTO) AS VARCHAR(MAX))
		END
		ELSE
		BEGIN
			DECLARE @TerminalID BIGINT = (SELECT OriginTerminalID FROM dbo.RequestSectionLane WHERE RequestSectionLaneID = {0});
			IF @TerminalID IS NOT NULL
			BEGIN
				SELECT CAST((SELECT * FROM (
				SELECT DISTINCT TOP 100 PC.PostalCodeID, PC.PostalCodeName
				FROM dbo.PostalCode PC
				INNER JOIN dbo.ServicePoint SP ON PC.ServicePointID = SP.ServicePointID
				INNER JOIN dbo.TerminalServicePoint TSP ON TSP.ServicePointID = SP.ServicePointID
				WHERE TSP.TerminalID = @TerminalID AND PC.PostalCodeName LIKE '{1}%'
				) AS Q FOR JSON AUTO) AS VARCHAR(MAX))
			END
			ELSE
			BEGIN
				DECLARE @ProvinceID BIGINT = (SELECT OriginProvinceID FROM dbo.RequestSectionLane WHERE RequestSectionLaneID = {0});
				IF @ProvinceID IS NOT NULL
				BEGIN
					SELECT CAST((SELECT * FROM (
					SELECT DISTINCT TOP 100 PC.PostalCodeID, PC.PostalCodeName
					FROM dbo.PostalCode PC
					INNER JOIN dbo.ServicePoint SP ON PC.ServicePointID = SP.ServicePointID
					LEFT JOIN dbo.BasingPoint BP ON SP.BasingPointID IS NOT NULL AND SP.BasingPointID = BP.BasingPointID
					LEFT JOIN dbo.Province P ON (BP.ProvinceID IS NOT NULL AND BP.ProvinceID = P.ProvinceID) OR (BP.ProvinceID IS NULL AND SP.ProvinceID = P.ProvinceID)
					WHERE P.ProvinceID = @ProvinceID AND PC.PostalCodeName LIKE '{1}%'
					) AS Q FOR JSON AUTO) AS VARCHAR(MAX))
				END
				ELSE
				BEGIN
					DECLARE @RegionID BIGINT = (SELECT OriginRegionID FROM dbo.RequestSectionLane WHERE RequestSectionLaneID = {0});
					IF @RegionID IS NOT NULL
					BEGIN
						SELECT CAST((SELECT * FROM (
						SELECT DISTINCT TOP 100 PC.PostalCodeID, PC.PostalCodeName
						FROM dbo.PostalCode PC
						INNER JOIN dbo.ServicePoint SP ON PC.ServicePointID = SP.ServicePointID
						LEFT JOIN dbo.BasingPoint BP ON SP.BasingPointID IS NOT NULL AND SP.BasingPointID = BP.BasingPointID
						LEFT JOIN dbo.Province P ON (BP.ProvinceID IS NOT NULL AND BP.ProvinceID = P.ProvinceID) OR (BP.ProvinceID IS NULL AND SP.ProvinceID = P.ProvinceID)
						LEFT JOIN dbo.Region R ON P.RegionID = R.RegionID
						WHERE R.RegionID = @RegionID AND PC.PostalCodeName LIKE '{1}%' 
						) AS Q FOR JSON AUTO) AS VARCHAR(MAX))
					END
					ELSE
					BEGIN
						DECLARE @CountryID BIGINT = (SELECT OriginCountryID FROM dbo.RequestSectionLane WHERE RequestSectionLaneID = {0});

						SELECT CAST((SELECT * FROM (
						SELECT DISTINCT TOP 100 PC.PostalCodeID, PC.PostalCodeName
						FROM dbo.PostalCode PC
						INNER JOIN dbo.ServicePoint SP ON PC.ServicePointID = SP.ServicePointID
						LEFT JOIN dbo.BasingPoint BP ON SP.BasingPointID IS NOT NULL AND SP.BasingPointID = BP.BasingPointID
						LEFT JOIN dbo.Province P ON (BP.ProvinceID IS NOT NULL AND BP.ProvinceID = P.ProvinceID) OR (BP.ProvinceID IS NULL AND SP.ProvinceID = P.ProvinceID)
						LEFT JOIN dbo.Region R ON P.RegionID = R.RegionID
						LEFT JOIN dbo.Country C ON R.CountryID = C.CountryID
						WHERE C.CountryID = @CountryID AND PC.PostalCodeName LIKE '{1}%' 
						) AS Q FOR JSON AUTO) AS VARCHAR(MAX))
					END
				END
			END
		END
	END
END
"""

SEARCH_DESTINATION_POSTAL_CODE = """ 
DECLARE @PostalCodeID BIGINT = (SELECT DestinationPostalCodeID FROM dbo.RequestSectionLane WHERE RequestSectionLaneID = {0});

IF @PostalCodeID IS NOT NULL
BEGIN
	SELECT CAST((SELECT * FROM (
	SELECT DISTINCT TOP 100 PC.PostalCodeID, PC.PostalCodeName
	FROM dbo.PostalCode PC
	WHERE PC.PostalCodeID = @PostalCodeID AND PC.PostalCodeName LIKE '{1}%'
	) AS Q FOR JSON AUTO) AS VARCHAR(MAX))
END
ELSE
BEGIN 
	DECLARE @ServicePointID BIGINT = (SELECT DestinationServicePointID FROM dbo.RequestSectionLane WHERE RequestSectionLaneID = {0});
	IF @ServicePointID IS NOT NULL
	BEGIN
		SELECT CAST((SELECT * FROM (
		SELECT DISTINCT TOP 100 PC.PostalCodeID, PC.PostalCodeName
		FROM dbo.PostalCode PC
		INNER JOIN dbo.ServicePoint SP ON PC.ServicePointID = SP.ServicePointID
		WHERE SP.ServicePointID = @ServicePointID AND PC.PostalCodeName LIKE '{1}%'
		) AS Q FOR JSON AUTO) AS VARCHAR(MAX))
	END
	ELSE
	BEGIN
		DECLARE @BasingPointID BIGINT = (SELECT DestinationBasingPointID FROM dbo.RequestSectionLane WHERE RequestSectionLaneID = {0});
		IF @BasingPointID IS NOT NULL
		BEGIN
			SELECT CAST((SELECT * FROM (
			SELECT DISTINCT TOP 100 PC.PostalCodeID, PC.PostalCodeName
			FROM dbo.PostalCode PC
			INNER JOIN dbo.ServicePoint SP ON PC.ServicePointID = SP.ServicePointID
			INNER JOIN dbo.BasingPoint BP ON SP.BasingPointID = BP.BasingPointID
			WHERE BP.BasingPointID = @BasingPointID AND PC.PostalCodeName LIKE '{1}%'
			) AS Q FOR JSON AUTO) AS VARCHAR(MAX))
		END
		ELSE
		BEGIN
			DECLARE @TerminalID BIGINT = (SELECT DestinationTerminalID FROM dbo.RequestSectionLane WHERE RequestSectionLaneID = {0});
			IF @TerminalID IS NOT NULL
			BEGIN
				SELECT CAST((SELECT * FROM (
				SELECT DISTINCT TOP 100 PC.PostalCodeID, PC.PostalCodeName
				FROM dbo.PostalCode PC
				INNER JOIN dbo.ServicePoint SP ON PC.ServicePointID = SP.ServicePointID
				INNER JOIN dbo.TerminalServicePoint TSP ON TSP.ServicePointID = SP.ServicePointID
				WHERE TSP.TerminalID = @TerminalID AND PC.PostalCodeName LIKE '{1}%'
				) AS Q FOR JSON AUTO) AS VARCHAR(MAX))
			END
			ELSE
			BEGIN
				DECLARE @ProvinceID BIGINT = (SELECT DestinationProvinceID FROM dbo.RequestSectionLane WHERE RequestSectionLaneID = {0});
				IF @ProvinceID IS NOT NULL
				BEGIN
					SELECT CAST((SELECT * FROM (
					SELECT DISTINCT TOP 100 PC.PostalCodeID, PC.PostalCodeName
					FROM dbo.PostalCode PC
					INNER JOIN dbo.ServicePoint SP ON PC.ServicePointID = SP.ServicePointID
					LEFT JOIN dbo.BasingPoint BP ON SP.BasingPointID IS NOT NULL AND SP.BasingPointID = BP.BasingPointID
					LEFT JOIN dbo.Province P ON (BP.ProvinceID IS NOT NULL AND BP.ProvinceID = P.ProvinceID) OR (BP.ProvinceID IS NULL AND SP.ProvinceID = P.ProvinceID)
					WHERE P.ProvinceID = @ProvinceID AND PC.PostalCodeName LIKE '{1}%'
					) AS Q FOR JSON AUTO) AS VARCHAR(MAX))
				END
				ELSE
				BEGIN
					DECLARE @RegionID BIGINT = (SELECT DestinationRegionID FROM dbo.RequestSectionLane WHERE RequestSectionLaneID = {0});
					IF @RegionID IS NOT NULL
					BEGIN
						SELECT CAST((SELECT * FROM (
						SELECT DISTINCT TOP 100 PC.PostalCodeID, PC.PostalCodeName
						FROM dbo.PostalCode PC
						INNER JOIN dbo.ServicePoint SP ON PC.ServicePointID = SP.ServicePointID
						LEFT JOIN dbo.BasingPoint BP ON SP.BasingPointID IS NOT NULL AND SP.BasingPointID = BP.BasingPointID
						LEFT JOIN dbo.Province P ON (BP.ProvinceID IS NOT NULL AND BP.ProvinceID = P.ProvinceID) OR (BP.ProvinceID IS NULL AND SP.ProvinceID = P.ProvinceID)
						LEFT JOIN dbo.Region R ON P.RegionID = R.RegionID
						WHERE R.RegionID = @RegionID AND PC.PostalCodeName LIKE '{1}%' 
						) AS Q FOR JSON AUTO) AS VARCHAR(MAX))
					END
					ELSE
					BEGIN
						DECLARE @CountryID BIGINT = (SELECT DestinationCountryID FROM dbo.RequestSectionLane WHERE RequestSectionLaneID = {0});

						SELECT CAST((SELECT * FROM (
						SELECT DISTINCT TOP 100 PC.PostalCodeID, PC.PostalCodeName
						FROM dbo.PostalCode PC
						INNER JOIN dbo.ServicePoint SP ON PC.ServicePointID = SP.ServicePointID
						LEFT JOIN dbo.BasingPoint BP ON SP.BasingPointID IS NOT NULL AND SP.BasingPointID = BP.BasingPointID
						LEFT JOIN dbo.Province P ON (BP.ProvinceID IS NOT NULL AND BP.ProvinceID = P.ProvinceID) OR (BP.ProvinceID IS NULL AND SP.ProvinceID = P.ProvinceID)
						LEFT JOIN dbo.Region R ON P.RegionID = R.RegionID
						LEFT JOIN dbo.Country C ON R.CountryID = C.CountryID
						WHERE C.CountryID = @CountryID AND PC.PostalCodeName LIKE '{1}%' 
						) AS Q FOR JSON AUTO) AS VARCHAR(MAX))
					END
				END
			END
		END
	END
END
"""

GET_PRICING_POINTS = """
 SELECT CAST((SELECT * FROM (
	SELECT RequestSectionLanePricingPointID AS request_section_lane_pricing_point_id,
	RequestSectionLaneID AS request_section_lane_id,
	OriginPostalCodeID AS origin_postal_code_id,
	OriginPostalCodeName AS origin_postal_code_name,
	DestinationPostalCodeID AS destination_postal_code_id,
	DestinationPostalCodeName AS destination_postal_code_name,
	DrRate AS dr_rate,
	FakRate AS fak_rate,
	Profitability AS profitability,
	Cost AS cost,
	SplitsAll AS splits_all,
	SplitsAllUsagePercentage AS splits_all_usage_percentage,
	PickupCount AS pickup_count,
	DeliveryCount AS delivery_count,
	DockAdjustment AS dock_adjustment,
	Margin AS margin,
	Density AS density,
	PickupCost AS pickup_cost,
	DeliveryCost AS delivery_cost,
	AccessorialsValue AS accessorials_value,
	AccessorialsPercentage AS accessorials_percentage,
	IsActive AS is_active,
	IsInactiveViewable AS is_inactive_viewable,
	CostOverrideAccessorialsPercentage  AS cost_override_accessorials_percentage,
    CostOverrideAccessorialsValue  AS  cost_override_accessorials_value,
    CostOverrideDeliveryCost  AS cost_override_delivery_cost,
    CostOverrideDeliveryCount  AS cost_override_delivery_count,
    CostOverrideDensity  AS cost_override_density,
    CostOverrideDockAdjustment  AS cost_override_dock_adjustment,
    CostOverrideMargin  AS cost_override_margin,
    CostOverridePickupCost  AS cost_override_pickup_cost,
    CostOverridePickupCount  AS cost_override_pickup_count,
	PricingRates AS pricing_rates,
	WorkflowErrors AS workflow_errors
FROM dbo.RequestSectionLanePricingPoint RSLPP
WHERE RSLPP.RequestSectionLaneID = {0}
AND RSLPP.IsActive = 1 AND RSLPP.IsInactiveViewable = 1 
) AS Q FOR JSON AUTO, INCLUDE_NULL_VALUES) AS VARCHAR(MAX))
"""

UPDATE_PRICING_POINTS_COST_OVERRIDE = """
UPDATE RequestSectionLanePricingPoint
SET CostOverrideAccessorialsPercentage ='{0}',
    CostOverrideAccessorialsValue ='{1}',
    CostOverrideDeliveryCost='{2}',
    CostOverrideDeliveryCount={3},
    CostOverrideDensity='{4}',
    CostOverrideDockAdjustment={5},
    CostOverrideMargin = '{6}',
    CostOverridePickupCost = '{7}',
    CostOverridePickupCount ='{8}'

WHERE RequestSectionLanePricingPointID IN ({9})
"""

GET_PRICING_POINTS_HISTORY = """
 SELECT CAST((SELECT * FROM (
	SELECT RSLPPH.RequestSectionLanePricingPointID AS request_section_lane_pricing_point_id,
	RSL.RequestSectionLaneID AS request_section_lane_id,
	RSLPP.OriginPostalCodeID AS origin_postal_code_id,
	RSLPPH.OriginPostalCodeName AS origin_postal_code_name,
	RSLPP.DestinationPostalCodeID AS destination_postal_code_id,
	RSLPPH.DestinationPostalCodeName AS destination_postal_code_name,
	RSLPPH.DrRate AS dr_rate,
	RSLPPH.FakRate AS fak_rate,
	RSLPPH.Profitability AS profitability,
	RSLPPH.Cost AS cost,
	RSLPPH.SplitsAll AS splits_all,
	RSLPPH.SplitsAllUsagePercentage AS splits_all_usage_percentage,
	RSLPPH.PickupCount AS pickup_count,
	RSLPPH.DeliveryCount AS delivery_count,
	RSLPPH.DockAdjustment AS dock_adjustment,
	RSLPPH.Margin AS margin,
	RSLPPH.Density AS density,
	RSLPPH.PickupCost AS pickup_cost,
	RSLPPH.DeliveryCost AS delivery_cost,
	RSLPPH.AccessorialsValue AS accessorials_value,
	RSLPPH.AccessorialsPercentage AS accessorials_percentage,
	RSLPPH.IsActive AS is_active,
	RSLPPH.IsInactiveViewable AS is_inactive_viewable,
	RSLPPH.CostOverrideAccessorialsPercentage  AS cost_override_accessorials_percentage,
    RSLPPH.CostOverrideAccessorialsValue  AS  cost_override_accessorials_value,
    RSLPPH.CostOverrideDeliveryCost  AS cost_override_delivery_cost,
    RSLPPH.CostOverrideDeliveryCount  AS cost_override_delivery_count,
    RSLPPH.CostOverrideDensity  AS cost_override_density,
    RSLPPH.CostOverrideDockAdjustment  AS cost_override_dock_adjustment,
    RSLPPH.CostOverrideMargin  AS cost_override_margin,
    RSLPPH.CostOverridePickupCost  AS cost_override_pickup_cost,
    RSLPPH.CostOverridePickupCount  AS cost_override_pickup_count,
	RSLPPH.PricingRates AS pricing_rates,
	RSLPPH.WorkflowErrors AS workflow_errors
FROM dbo.RequestSectionLanePricingPoint_History RSLPPH
INNER JOIN dbo.RequestSectionLanePricingPoint RSLPP ON RSLPPH.RequestSectionLanePricingPointID = RSLPP.RequestSectionLanePricingPointID
INNER JOIN dbo.RequestSectionLane_History RSL ON RSLPPH.RequestSectionLaneVersionID = RSL.RequestSectionLaneVersionID
INNER JOIN dbo.RequestSection_History RS ON RSL.RequestSectionVersionID = RS.RequestSectionVersionID
INNER JOIN dbo.RequestLane_History RL ON RS.RequestLaneVersionID = RL.RequestLaneVersionID
INNER JOIN dbo.Request_History R ON RL.RequestLaneVersionID = R.RequestLaneVersionID
WHERE RSL.RequestSectionLaneID = {0}
AND RSLPPH.IsActive = 1 AND RSLPPH.IsInactiveViewable = 1 AND R.VersionNum = {1}
) AS Q FOR JSON AUTO, INCLUDE_NULL_VALUES) AS VARCHAR(MAX))
"""

GET_PRICING_POINTS_Staging = """
 SELECT CAST((SELECT * FROM (
	SELECT RequestSectionLanePricingPointID AS request_section_lane_pricing_point_id,
	RequestSectionLaneID AS request_section_lane_id,
	OriginPostalCodeID AS origin_postal_code_id,
	OriginPostalCodeName AS origin_postal_code_name,
	DestinationPostalCodeID AS destination_postal_code_id,
	DestinationPostalCodeName AS destination_postal_code_name,
	DrRate AS dr_rate,
	NewDrRate AS new_dr_rate,
	FakRate AS fak_rate,
	NewFakRate AS new_fak_rate,
	Profitability AS profitability,
	Cost AS cost,
	NewProfitability AS new_profitability,
	SplitsAll AS splits_all,
	NewSplitsAll AS new_splits_all,
	SplitsAllUsagePercentage AS splits_all_usage_percentage,
	NewSplitsAllUsagePercentage AS new_splits_all_usage_percentage,
	PickupCount AS pickup_count,
	NewPickupCount AS new_pickup_count,
	DeliveryCount AS delivery_count,
	NewDeliveryCount AS new_delivery_count,
	DockAdjustment AS dock_adjustment,
	NewDockAdjustment AS new_dock_adjustment,
	Margin AS margin,
	NewMargin AS new_margin,
	Density AS density,
	NewDensity AS new_density,
	PickupCost AS pickup_cost,
	NewPickupCost AS new_pickup_cost,
	DeliveryCost AS delivery_cost,
	NewDeliveryCost AS new_delivery_cost,
	AccessorialsValue AS accessorials_value,
	NewAccessorialsValue AS new_accessorials_value,
	AccessorialsPercentage AS accessorials_percentage,
	NewAccessorialsPercentage AS new_accessorials_percentage,
	IsActive AS is_active,
	IsInactiveViewable AS is_inactive_viewable,
	IsUpdated AS is_updated,
	ContextID AS context_id,
	PricingRates AS pricing_rates,
	WorkflowErrors AS workflow_errors
FROM dbo.RequestSectionLanePricingPoint_Staging RSLPP
WHERE RSLPP.RequestSectionLaneID = {0} AND RSLPP.ContextID = '{1}'
AND RSLPP.IsActive = 1 AND RSLPP.IsInactiveViewable = 1 
) AS Q FOR JSON AUTO, INCLUDE_NULL_VALUES) AS VARCHAR(MAX))
"""

GET_REQUEST_SECTION_LANE_CHANGES_COUNT = """
DECLARE @Count INT = 0;

SELECT @Count = @Count + ISNULL(SUM(CASE WHEN IsUpdated = 1 THEN 1 ELSE 0 END), 0)
FROM dbo.RequestSectionLane_Staging
WHERE RequestSectionID = {0} AND ContextID LIKE '{1}' AND IsActive = 1 AND IsInactiveViewable = 1

SELECT @Count = @Count + ISNULL(SUM(CASE WHEN IsUpdated = 1 THEN 1 ELSE 0 END), 0)
FROM dbo.RequestSectionLane RSL
INNER JOIN dbo.RequestSectionLanePricingPoint_Staging RSLPP ON RSL.RequestSectionLaneID = RSLPP.RequestSectionLaneID
WHERE RSL.RequestSectionID = {0} AND RSLPP.ContextID LIKE '{1}' AND RSL.IsActive = 1 AND RSL.IsInactiveViewable = 1
AND RSLPP.IsActive = 1 AND RSLPP.IsInactiveViewable = 1

SELECT CAST((SELECT * FROM (
SELECT @Count AS [count]
) AS Q FOR JSON AUTO, WITHOUT_ARRAY_WRAPPER) AS VARCHAR(MAX))
"""

GET_DASHBOARD_HEADER = """
DECLARE @UserID BIGINT = {0};
DECLARE @NumTotalRequest INT, @NumAwaitingAnalysis INT, @NumAwaitingApproval INT, @NumReadyForPublish INT, @NumTenders INT;

With A1 AS (
SELECT DISTINCT RequestID
FROM dbo.RequestQueue
WHERE CompletedOn IS NULL AND (
UserID = @UserID OR 
UserID IN (SELECT UserID FROM dbo.[User] WHERE UserManagerID = @UserID)
)),
B1 AS (
SELECT RS.RequestID, RST.RequestStatusTypeNAme
FROM dbo.RequestStatus RS
INNER JOIN dbo.RequestStatusType RST ON RS.RequestStatusTypeID = RST.RequestStatusTypeID
INNER JOIN A1 ON RS.RequestID = A1.RequestID
),
C1 AS (
SELECT B1.*
FROM B1
WHERE B1.RequestStatusTypeName = 'RRF with Pricing'
),
D1 AS (
SELECT B1.*
FROM B1
WHERE B1.RequestStatusTypeName IN ('Pending Sales Approval', 'Pending Partner Carrier Approval')
),
E1 AS (
SELECT B1.*
FROM B1
WHERE B1.RequestStatusTypeName = 'Sales Approved'
),
F1 AS (
SELECT RT.RequestTypeName
FROM dbo.Request R
INNER JOIN A1 ON R.RequestID = A1.RequestID
INNER JOIN dbo.RequestInformation I ON R.RequestInformationID = I.RequestInformationID
INNER JOIN dbo.RequestType RT ON I.RequestTypeID = RT.RequestTypeID
WHERE RT.RequestTypeName = 'Tender'
)

SELECT @NumTotalRequest = (SELECT COUNT(*) FROM A1),
	@NumAwaitingAnalysis = (SELECT COUNT(*) FROM C1),
	@NumAwaitingApproval = (SELECT COUNT(*) FROM D1),
	@NumReadyForPublish = (SELECT COUNT(*) FROM E1),
	@NumTenders = (SELECT COUNT(*) FROM F1)

SELECT CAST((SELECT * FROM (
SELECT @NumTotalRequest AS num_total_request, 
	@NumAwaitingAnalysis AS num_awaiting_analysis, 
	@NumAwaitingApproval AS num_awaiting_approval, 
	@NumReadyForPublish AS num_ready_for_publish, 
	@NumTenders AS num_tenders
) AS Q FOR JSON AUTO, WITHOUT_ARRAY_WRAPPER) AS VARCHAR(MAX))
"""

GET_REQUEST_LIST = """
DECLARE @UserID BIGINT = {0};
DECLARE @UniType VARCHAR(50) = '{1}';
DECLARE @UserPersona VARCHAR(50);
SELECT @UserPersona = P.PersonaName FROM dbo.[User] U INNER JOIN dbo.Persona P ON U.PersonaID = P.PersonaID WHERE U.UserID = @UserID;

With A1 AS (
SELECT RequestID, AssignedOn
FROM dbo.RequestQueue
WHERE CompletedOn IS NULL AND IsActive = 1 AND IsInactiveViewable = 1 AND (
UserID = @UserID OR
UserID IN (SELECT UserID FROM dbo.[User] WHERE UserManagerID = @UserID)
)),
A2 AS (
SELECT DISTINCT RequestID
FROM A1
),
A3 AS (
SELECT Q.RequestID, Q.UserID, Q.AssignedOn, Q.CompletedOn, RST.AssignedPersona
FROM dbo.RequestQueue Q
INNER JOIN dbo.RequestStatusType RST ON Q.RequestStatusTypeID = RST.RequestStatusTypeID
WHERE Q.RequestID IN (SELECT RequestID FROM A2) AND Q.IsActive = 1 AND Q.IsInactiveViewable = 1 AND Q.IsActionable = 1
AND RST.AssignedPersona IN ('Pricing Analyst', 'Credit Analyst', 'Credit Manager', 'Partner Carrier')
),
B1 AS (
SELECT DISTINCT Q.RequestID, Q.RequestStatusTypeID, Q.AssignedOn, U.UserName, Q.UserID
FROM dbo.RequestQueue Q
INNER JOIN dbo.[User] U ON Q.UserID = U.UserID
WHERE Q.RequestID IN (SELECT RequestID FROM A1) AND Q.IsSecondary = 1 AND Q.IsActive = 1 AND Q.IsInactiveViewable = 1
),
C1 AS (
SELECT B1.RequestID, COUNT(DISTINCT B1.RequestStatusTypeID) AS NumApprovalsRequested
FROM B1
INNER JOIN dbo.RequestStatusType RST ON RST.RequestStatusTypeID = B1.RequestStatusTypeID
WHERE RST.RequestStatusTypeName IN ('Pending DRM Approval', 'Pending EPT Approval', 'Pending PC Approval', 'Pending PCR Approval')
GROUP BY B1.RequestID
),
D1 AS (
SELECT B1.RequestID, COUNT(DISTINCT B1.RequestStatusTypeID) AS NumApprovalsCompleted
FROM B1
INNER JOIN dbo.RequestStatusType RST ON RST.RequestStatusTypeID = B1.RequestStatusTypeID
WHERE RST.RequestStatusTypeName IN ('DRM Approved', 'DRM Declined', 'EPT Approved', 'EPT Declined', 'PC Approved', 'PC Declined', 'PCR Approved', 'PCR Declined')
GROUP BY B1.RequestID
),
E1 AS (
SELECT RequestID, [secondary_approval], [status], [date], [user], [is_actionable] FROM (
SELECT B1.RequestID, 'Deal Review' AS [secondary_approval],
	CASE WHEN RST.RequestStatusTypeName = 'Pending DRM Approval' THEN 'Requested' WHEN RST.RequestStatusTypeName = 'DRM Approved' THEN 'Approved' WHEN RST.RequestStatusTypeName = 'DRM Declined' THEN 'Declined' ELSE NULL END AS [status],
	B1.UserName AS [user],
	CASE WHEN RST.RequestStatusTypeName = 'Pending DRM Approval' AND B1.UserID = @UserID THEN 1 ELSE 0 END AS [is_actionable],
	B1.AssignedOn AS [date],
ROW_NUMBER() OVER(PARTITION BY B1.RequestID ORDER BY AssignedOn DESC) AS RN
FROM B1
INNER JOIN dbo.RequestStatusType RST ON RST.RequestStatusTypeID = B1.RequestStatusTypeID
WHERE RST.RequestStatusTypeName IN ('Pending DRM Approval', 'DRM Approved', 'DRM Declined')) AS T
WHERE RN = 1

UNION

SELECT RequestID, [secondary_approval], [status], [date], [user], [is_actionable] FROM (
SELECT B1.RequestID, 'Pricing Committee' AS [secondary_approval],
	CASE WHEN RST.RequestStatusTypeName = 'Pending PCR Approval' THEN 'Requested' WHEN RST.RequestStatusTypeName = 'PCR Approved' THEN 'Approved' WHEN RST.RequestStatusTypeName = 'PCR Declined' THEN 'Declined' ELSE NULL END AS [status],
	B1.UserName AS [user],
	CASE WHEN RST.RequestStatusTypeName = 'Pending PCR Approval' AND B1.UserID = @UserID THEN 1 ELSE 0 END AS [is_actionable],
	B1.AssignedOn AS [date],
ROW_NUMBER() OVER(PARTITION BY B1.RequestID ORDER BY AssignedOn DESC) AS RN
FROM B1
INNER JOIN dbo.RequestStatusType RST ON RST.RequestStatusTypeID = B1.RequestStatusTypeID
WHERE RST.RequestStatusTypeName IN ('Pending PCR Approval', 'PCR Approved', 'PCR Declined')) AS T
WHERE RN = 1

UNION

SELECT RequestID, [secondary_approval], [status], [date], [user], [is_actionable] FROM (
SELECT B1.RequestID, 'Priority Change' AS [secondary_approval],
	CASE WHEN RST.RequestStatusTypeName = 'Pending PC Approval' THEN 'Requested' WHEN RST.RequestStatusTypeName = 'PC Approved' THEN 'Approved' WHEN RST.RequestStatusTypeName = 'PC Declined' THEN 'Declined' ELSE NULL END AS [status],
	B1.UserName AS [user],
	CASE WHEN RST.RequestStatusTypeName = 'Pending PC Approval' AND B1.UserID = @UserID THEN 1 ELSE 0 END AS [is_actionable],
	B1.AssignedOn AS [date],
ROW_NUMBER() OVER(PARTITION BY B1.RequestID ORDER BY AssignedOn DESC) AS RN
FROM B1
INNER JOIN dbo.RequestStatusType RST ON RST.RequestStatusTypeID = B1.RequestStatusTypeID
WHERE RST.RequestStatusTypeName IN ('Pending PC Approval', 'PC Approved', 'PC Declined')) AS T
WHERE RN = 1

UNION

SELECT RequestID, [secondary_approval], [status], [date], [user], [is_actionable] FROM (
SELECT B1.RequestID, 'Extended Payment' AS [secondary_approval],
	CASE WHEN RST.RequestStatusTypeName = 'Pending EPT Approval' THEN 'Requested' WHEN RST.RequestStatusTypeName = 'EPT Approved' THEN 'Approved' WHEN RST.RequestStatusTypeName = 'EPT Declined' THEN 'Declined' ELSE NULL END AS [status],
	B1.UserName AS [user],
	CASE WHEN RST.RequestStatusTypeName = 'Pending EPT Approval' AND B1.UserID = @UserID THEN 1 ELSE 0 END AS [is_actionable],
	B1.AssignedOn AS [date],
ROW_NUMBER() OVER(PARTITION BY B1.RequestID ORDER BY AssignedOn DESC) AS RN
FROM B1
INNER JOIN dbo.RequestStatusType RST ON RST.RequestStatusTypeID = B1.RequestStatusTypeID
WHERE RST.RequestStatusTypeName IN ('Pending EPT Approval', 'EPT Approved', 'EPT Declined')) AS T
WHERE RN = 1
),
F1 AS
(
SELECT E1.RequestID, (SELECT E2.[secondary_approval], E2.[status], E2.[date], E2.[user], E2.[is_actionable] FROM E1 AS E2 WHERE E1.RequestID = E2.RequestID FOR JSON AUTO) AS approvals
FROM E1
GROUP BY E1.RequestID),
G1 AS (
SELECT * FROM (
SELECT RequestID, AssignedOn,
ROW_NUMBER() OVER(PARTITION BY A3.RequestID ORDER BY A3.AssignedOn DESC) AS RN
FROM A3 WHERE AssignedPersona = 'Credit Analyst') AS T
WHERE RN = 1
),
G2 AS (
SELECT * FROM (
SELECT RequestID, AssignedOn,
ROW_NUMBER() OVER(PARTITION BY A3.RequestID ORDER BY A3.AssignedOn DESC) AS RN
FROM A3 WHERE AssignedPersona = 'Credit Manager') AS T
WHERE RN = 1
),
G3 AS (
SELECT * FROM (
SELECT RequestID, AssignedOn,
ROW_NUMBER() OVER(PARTITION BY A3.RequestID ORDER BY A3.AssignedOn DESC) AS RN
FROM A3 WHERE AssignedPersona = 'Partner Carrier') AS T
WHERE RN = 1
),
G4 AS (
SELECT * FROM (
SELECT RequestID, UserID, SUM(DATEDIFF(MINUTE, AssignedOn, ISNULL(CompletedON, GETUTCDATE()))) / (24*60) AS ElapsedTime
FROM A3 WHERE AssignedPersona = 'Pricing Analyst'
GROUP BY RequestID, UserID) AS T
)

SELECT CAST((SELECT * FROM (
SELECT R.RequestNumber AS request_number,
    R.RequestID AS request,
	R.RequestCode AS request_code,
	ISNULL(A.AccountNumber,'') AS account_number,
	ISNULL(C.CustomerName,'') AS customer_name,
	C.ServiceLevelID AS service_level_id,
	SL.ServiceLevelCode AS service_level_code,
	ISNULL(RSU.PricingAnalystID,'') AS pricing_analyst_id,
	ISNULL(UPA.UserName,'') AS pricing_analyst_name,
	ISNULL(RSU.SalesRepresentativeID,'') AS sales_representative_id,
	ISNULL(USR.UserName,'') AS sales_representative_name,
	ISNULL(RSU.CurrentEditorID,'') AS current_editor_id,
	ISNULL(CUE.UserName,'') AS current_editor_name,
	ISNULL(I.[Priority],'') AS [priority],
	RSU.RequestStatusTypeID AS request_status_type_id,
	RST.RequestStatusTypeName AS request_status_type_name,
	R.InitiatedOn AS date_initiated,
	ISNULL(R.SubmittedON,'') AS date_submitted,
	R.InitiatedBy AS initiated_by_id,
	IBY.UserName AS initiated_by_name,
	ISNULL(R.SubmittedBy,'') AS submitted_by_id,
	ISNULL(SBY.UserName,'') AS submitted_by_name,
	I.IsNewBusiness AS is_new_business,
	CASE WHEN A.AccountID IS NULL THEN 'New' ELSE 'Expanded' END AS business_type_name,
	ISNULL(G4.ElapsedTime, 0) AS days_in_queue,
	ISNULL(C1.NumApprovalsRequested, 0) AS approvals_requested,
	ISNULL(D1.NumApprovalsCompleted, 0) approvals_completed,
	ISNULL(F1.Approvals, '[]') AS approvals,
	ISNULL(G1.AssignedOn, '') AS date_submitted_credit_analyst,
	ISNULL(G2.AssignedOn, '') AS date_submitted_credit_manager,
	ISNULL(G3.AssignedOn, '') AS date_submitted_partner_carrier,
	RT.RequestTypeName AS request_type_name,
	CASE WHEN RSU.CurrentEditorID = @UserID THEN 1 ELSE 0 END AS is_current_editor,
    R.SpeedsheetName AS speedsheet_name,
    (select LanguageCode from Language where LanguageId = I.LanguageID) AS language_code
FROM dbo.Request R
INNER JOIN dbo.RequestStatus RSU ON R.RequestID = RSU.RequestID
INNER JOIN dbo.RequestStatusType RST ON RSU.RequestStatusTypeID = RST.RequestStatusTypeID
INNER JOIN dbo.RequestInformation I ON R.RequestInformationID = I.RequestInformationID
INNER JOIN dbo.Customer C ON I.CustomerID = C.CustomerID
INNER JOIN dbo.ServiceLevel SL ON C.ServiceLevelID = SL.ServiceLevelID
LEFT JOIN A2 ON R.RequestID = A2.RequestID
LEFT JOIN dbo.RequestType RT ON I.RequestTypeID = RT.RequestTypeID
LEFT JOIN dbo.Account A ON C.AccountID = A.AccountID
LEFT JOIN dbo.[User] UPA ON RSU.PricingAnalystID = UPA.UserID
LEFT JOIN dbo.[User] USR ON RSU.SalesRepresentativeID = USR.UserID
LEFT JOIN dbo.[User] CUE ON RSU.CurrentEditorID = CUE.UserID
LEFT JOIN dbo.[User] IBY ON R.InitiatedBy = IBY.UserID
LEFT JOIN dbo.[User] SBY ON R.SubmittedBy = SBY.UserID
LEFT JOIN C1 ON R.RequestID = C1.RequestID
LEFT JOIN D1 ON R.RequestID = D1.RequestID
LEFT JOIN F1 ON R.RequestID = F1.RequestID
LEFT JOIN G1 ON R.RequestID = G1.RequestID
LEFT JOIN G2 ON R.RequestID = G2.RequestID
LEFT JOIN G3 ON R.RequestID = G3.RequestID
LEFT JOIN G4 ON R.RequestID = G4.RequestID AND G4.UserID = @UserID
WHERE ((@UniType = 'SPEEDSHEET' AND R.UniType = @UniType) OR (@UniType = 'REQUEST' AND R.UniType is NULL) ) and R.IsInactiveViewable = 1 AND (A2.RequestID IS NOT NULL OR @UserPersona IN ('Pricing Analyst', 'Pricing Manager'))
) AS Q FOR JSON AUTO) AS VARCHAR(MAX))
"""

GET_SPEEDSHEET_LIST = """
DECLARE @UserID BIGINT = {0};
DECLARE @UniType VARCHAR(50) = '{1}';
DECLARE @UserPersona VARCHAR(50);
SELECT @UserPersona = P.PersonaName FROM dbo.[User] U INNER JOIN dbo.Persona P ON U.PersonaID = P.PersonaID WHERE U.UserID = @UserID;

With A1 AS (
SELECT RequestID, AssignedOn
FROM dbo.RequestQueue
WHERE CompletedOn IS NULL AND IsActive = 1 AND IsInactiveViewable = 1 AND (
UserID = @UserID OR
UserID IN (SELECT UserID FROM dbo.[User] WHERE UserManagerID = @UserID)
)),
A2 AS (
SELECT DISTINCT RequestID
FROM A1
),
A3 AS (
SELECT Q.RequestID, Q.UserID, Q.AssignedOn, Q.CompletedOn, RST.AssignedPersona
FROM dbo.RequestQueue Q
INNER JOIN dbo.RequestStatusType RST ON Q.RequestStatusTypeID = RST.RequestStatusTypeID
WHERE Q.RequestID IN (SELECT RequestID FROM A2) AND Q.IsActive = 1 AND Q.IsInactiveViewable = 1 AND Q.IsActionable = 1
AND RST.AssignedPersona IN ('Pricing Analyst','Sales Representative', 'Credit Analyst', 'Credit Manager', 'Partner Carrier')
),
B1 AS (
SELECT DISTINCT Q.RequestID, Q.RequestStatusTypeID, Q.AssignedOn, U.UserName, Q.UserID
FROM dbo.RequestQueue Q
INNER JOIN dbo.[User] U ON Q.UserID = U.UserID
WHERE Q.RequestID IN (SELECT RequestID FROM A1) AND Q.IsSecondary = 1 AND Q.IsActive = 1 AND Q.IsInactiveViewable = 1
),
C1 AS (
SELECT B1.RequestID, COUNT(DISTINCT B1.RequestStatusTypeID) AS NumApprovalsRequested
FROM B1
INNER JOIN dbo.RequestStatusType RST ON RST.RequestStatusTypeID = B1.RequestStatusTypeID
WHERE RST.RequestStatusTypeName IN ('Pending DRM Approval', 'Pending EPT Approval', 'Pending PC Approval', 'Pending PCR Approval')
GROUP BY B1.RequestID
),
D1 AS (
SELECT B1.RequestID, COUNT(DISTINCT B1.RequestStatusTypeID) AS NumApprovalsCompleted
FROM B1
INNER JOIN dbo.RequestStatusType RST ON RST.RequestStatusTypeID = B1.RequestStatusTypeID
WHERE RST.RequestStatusTypeName IN ('DRM Approved', 'DRM Declined', 'EPT Approved', 'EPT Declined', 'PC Approved', 'PC Declined', 'PCR Approved', 'PCR Declined')
GROUP BY B1.RequestID
),
E1 AS (
SELECT RequestID, [secondary_approval], [status], [date], [user], [is_actionable] FROM (
SELECT B1.RequestID, 'Deal Review' AS [secondary_approval],
	CASE WHEN RST.RequestStatusTypeName = 'Pending DRM Approval' THEN 'Requested' WHEN RST.RequestStatusTypeName = 'DRM Approved' THEN 'Approved' WHEN RST.RequestStatusTypeName = 'DRM Declined' THEN 'Declined' ELSE NULL END AS [status],
	B1.UserName AS [user],
	CASE WHEN RST.RequestStatusTypeName = 'Pending DRM Approval' AND B1.UserID = @UserID THEN 1 ELSE 0 END AS [is_actionable],
	B1.AssignedOn AS [date],
ROW_NUMBER() OVER(PARTITION BY B1.RequestID ORDER BY AssignedOn DESC) AS RN
FROM B1
INNER JOIN dbo.RequestStatusType RST ON RST.RequestStatusTypeID = B1.RequestStatusTypeID
WHERE RST.RequestStatusTypeName IN ('Pending DRM Approval', 'DRM Approved', 'DRM Declined')) AS T
WHERE RN = 1

UNION

SELECT RequestID, [secondary_approval], [status], [date], [user], [is_actionable] FROM (
SELECT B1.RequestID, 'Pricing Committee' AS [secondary_approval],
	CASE WHEN RST.RequestStatusTypeName = 'Pending PCR Approval' THEN 'Requested' WHEN RST.RequestStatusTypeName = 'PCR Approved' THEN 'Approved' WHEN RST.RequestStatusTypeName = 'PCR Declined' THEN 'Declined' ELSE NULL END AS [status],
	B1.UserName AS [user],
	CASE WHEN RST.RequestStatusTypeName = 'Pending PCR Approval' AND B1.UserID = @UserID THEN 1 ELSE 0 END AS [is_actionable],
	B1.AssignedOn AS [date],
ROW_NUMBER() OVER(PARTITION BY B1.RequestID ORDER BY AssignedOn DESC) AS RN
FROM B1
INNER JOIN dbo.RequestStatusType RST ON RST.RequestStatusTypeID = B1.RequestStatusTypeID
WHERE RST.RequestStatusTypeName IN ('Pending PCR Approval', 'PCR Approved', 'PCR Declined')) AS T
WHERE RN = 1

UNION

SELECT RequestID, [secondary_approval], [status], [date], [user], [is_actionable] FROM (
SELECT B1.RequestID, 'Priority Change' AS [secondary_approval],
	CASE WHEN RST.RequestStatusTypeName = 'Pending PC Approval' THEN 'Requested' WHEN RST.RequestStatusTypeName = 'PC Approved' THEN 'Approved' WHEN RST.RequestStatusTypeName = 'PC Declined' THEN 'Declined' ELSE NULL END AS [status],
	B1.UserName AS [user],
	CASE WHEN RST.RequestStatusTypeName = 'Pending PC Approval' AND B1.UserID = @UserID THEN 1 ELSE 0 END AS [is_actionable],
	B1.AssignedOn AS [date],
ROW_NUMBER() OVER(PARTITION BY B1.RequestID ORDER BY AssignedOn DESC) AS RN
FROM B1
INNER JOIN dbo.RequestStatusType RST ON RST.RequestStatusTypeID = B1.RequestStatusTypeID
WHERE RST.RequestStatusTypeName IN ('Pending PC Approval', 'PC Approved', 'PC Declined')) AS T
WHERE RN = 1

UNION

SELECT RequestID, [secondary_approval], [status], [date], [user], [is_actionable] FROM (
SELECT B1.RequestID, 'Extended Payment' AS [secondary_approval],
	CASE WHEN RST.RequestStatusTypeName = 'Pending EPT Approval' THEN 'Requested' WHEN RST.RequestStatusTypeName = 'EPT Approved' THEN 'Approved' WHEN RST.RequestStatusTypeName = 'EPT Declined' THEN 'Declined' ELSE NULL END AS [status],
	B1.UserName AS [user],
	CASE WHEN RST.RequestStatusTypeName = 'Pending EPT Approval' AND B1.UserID = @UserID THEN 1 ELSE 0 END AS [is_actionable],
	B1.AssignedOn AS [date],
ROW_NUMBER() OVER(PARTITION BY B1.RequestID ORDER BY AssignedOn DESC) AS RN
FROM B1
INNER JOIN dbo.RequestStatusType RST ON RST.RequestStatusTypeID = B1.RequestStatusTypeID
WHERE RST.RequestStatusTypeName IN ('Pending EPT Approval', 'EPT Approved', 'EPT Declined')) AS T
WHERE RN = 1
),
F1 AS
(
SELECT E1.RequestID, (SELECT E2.[secondary_approval], E2.[status], E2.[date], E2.[user], E2.[is_actionable] FROM E1 AS E2 WHERE E1.RequestID = E2.RequestID FOR JSON AUTO) AS approvals
FROM E1
GROUP BY E1.RequestID),
G1 AS (
SELECT * FROM (
SELECT RequestID, AssignedOn,
ROW_NUMBER() OVER(PARTITION BY A3.RequestID ORDER BY A3.AssignedOn DESC) AS RN
FROM A3 WHERE AssignedPersona = 'Credit Analyst') AS T
WHERE RN = 1
),
G2 AS (
SELECT * FROM (
SELECT RequestID, AssignedOn,
ROW_NUMBER() OVER(PARTITION BY A3.RequestID ORDER BY A3.AssignedOn DESC) AS RN
FROM A3 WHERE AssignedPersona = 'Credit Manager') AS T
WHERE RN = 1
),
G3 AS (
SELECT * FROM (
SELECT RequestID, AssignedOn,
ROW_NUMBER() OVER(PARTITION BY A3.RequestID ORDER BY A3.AssignedOn DESC) AS RN
FROM A3 WHERE AssignedPersona = 'Partner Carrier') AS T
WHERE RN = 1
),
G4 AS (
SELECT * FROM (
SELECT RequestID, UserID, SUM(DATEDIFF(MINUTE, AssignedOn, ISNULL(CompletedON, GETUTCDATE()))) / (24*60) AS ElapsedTime
FROM A3 WHERE AssignedPersona = 'Pricing Analyst'
GROUP BY RequestID, UserID) AS T
)

SELECT CAST((SELECT * FROM (
SELECT R.RequestNumber AS request_number,
    R.RequestID AS request,
	R.RequestCode AS request_code,
	ISNULL(A.AccountNumber,'') AS account_number,
	ISNULL(C.CustomerName,'') AS customer_name,
	C.ServiceLevelID AS service_level_id,
	SL.ServiceLevelCode AS service_level_code,
	ISNULL(RSU.PricingAnalystID,'') AS pricing_analyst_id,
	ISNULL(UPA.UserName,'') AS pricing_analyst_name,
	ISNULL(RSU.SalesRepresentativeID,'') AS sales_representative_id,
	ISNULL(USR.UserName,'') AS sales_representative_name,
	ISNULL(RSU.CurrentEditorID,'') AS current_editor_id,
	ISNULL(CUE.UserName,'') AS current_editor_name,
	ISNULL(I.[Priority],'') AS [priority],
	RSU.RequestStatusTypeID AS request_status_type_id,
	RST.RequestStatusTypeName AS request_status_type_name,
	R.InitiatedOn AS date_initiated,
	ISNULL(R.SubmittedON,'') AS date_submitted,
	R.InitiatedBy AS initiated_by_id,
	IBY.UserName AS initiated_by_name,
	ISNULL(R.SubmittedBy,'') AS submitted_by_id,
	ISNULL(SBY.UserName,'') AS submitted_by_name,
	I.IsNewBusiness AS is_new_business,
	CASE WHEN A.AccountID IS NULL THEN 'New' ELSE 'Expanded' END AS business_type_name,
	ISNULL(G4.ElapsedTime, 0) AS days_in_queue,
	ISNULL(C1.NumApprovalsRequested, 0) AS approvals_requested,
	ISNULL(D1.NumApprovalsCompleted, 0) approvals_completed,
	ISNULL(F1.Approvals, '[]') AS approvals,
	ISNULL(G1.AssignedOn, '') AS date_submitted_credit_analyst,
	ISNULL(G2.AssignedOn, '') AS date_submitted_credit_manager,
	ISNULL(G3.AssignedOn, '') AS date_submitted_partner_carrier,
	RT.RequestTypeName AS request_type_name,
	CASE WHEN RSU.CurrentEditorID = @UserID THEN 1 ELSE 0 END AS is_current_editor,
    R.SpeedsheetName AS speedsheet_name,
    (select LanguageCode from Language where LanguageId = I.LanguageID) AS language_code
FROM dbo.Request R
INNER JOIN dbo.RequestStatus RSU ON R.RequestID = RSU.RequestID
INNER JOIN dbo.RequestStatusType RST ON RSU.RequestStatusTypeID = RST.RequestStatusTypeID
INNER JOIN dbo.RequestInformation I ON R.RequestInformationID = I.RequestInformationID
INNER JOIN dbo.Customer C ON I.CustomerID = C.CustomerID
INNER JOIN dbo.ServiceLevel SL ON C.ServiceLevelID = SL.ServiceLevelID
LEFT JOIN A2 ON R.RequestID = A2.RequestID
LEFT JOIN dbo.RequestType RT ON I.RequestTypeID = RT.RequestTypeID
LEFT JOIN dbo.Account A ON C.AccountID = A.AccountID
LEFT JOIN dbo.[User] UPA ON RSU.PricingAnalystID = UPA.UserID
LEFT JOIN dbo.[User] USR ON RSU.SalesRepresentativeID = USR.UserID
LEFT JOIN dbo.[User] CUE ON RSU.CurrentEditorID = CUE.UserID
LEFT JOIN dbo.[User] IBY ON R.InitiatedBy = IBY.UserID
LEFT JOIN dbo.[User] SBY ON R.SubmittedBy = SBY.UserID
LEFT JOIN C1 ON R.RequestID = C1.RequestID
LEFT JOIN D1 ON R.RequestID = D1.RequestID
LEFT JOIN F1 ON R.RequestID = F1.RequestID
LEFT JOIN G1 ON R.RequestID = G1.RequestID
LEFT JOIN G2 ON R.RequestID = G2.RequestID
LEFT JOIN G3 ON R.RequestID = G3.RequestID
LEFT JOIN G4 ON R.RequestID = G4.RequestID AND G4.UserID = @UserID
WHERE ((@UniType = 'SPEEDSHEET' AND R.UniType = @UniType) OR (@UniType = 'REQUEST' AND R.UniType is NULL) ) and R.IsInactiveViewable = 1 AND (A2.RequestID IS NOT NULL OR @UserPersona IN ('Sales Representative', 'Sales Manager', 'Sales Coordinator', 'Pricing Analyst', 'Pricing Manager'))
) AS Q FOR JSON AUTO) AS VARCHAR(MAX))
"""

GET_REQUEST = """
DECLARE @UserID BIGINT = {0};
DECLARE @UniType VARCHAR(50) = '{1}';
DECLARE @RequestId VARCHAR(50) = '{2}';
DECLARE @UserPersona VARCHAR(50);
SELECT @UserPersona = P.PersonaName FROM dbo.[User] U INNER JOIN dbo.Persona P ON U.PersonaID = P.PersonaID WHERE U.UserID = @UserID;

With A1 AS (
SELECT RequestID, AssignedOn
FROM dbo.RequestQueue
WHERE CompletedOn IS NULL AND IsActive = 1 AND IsInactiveViewable = 1 AND (
UserID = @UserID OR 
UserID IN (SELECT UserID FROM dbo.[User] WHERE UserManagerID = @UserID)
)),
A2 AS (
SELECT DISTINCT RequestID
FROM A1
),
A3 AS (
SELECT Q.RequestID, Q.UserID, Q.AssignedOn, Q.CompletedOn, RST.AssignedPersona
FROM dbo.RequestQueue Q
INNER JOIN dbo.RequestStatusType RST ON Q.RequestStatusTypeID = RST.RequestStatusTypeID 
WHERE Q.RequestID IN (SELECT RequestID FROM A2) AND Q.IsActive = 1 AND Q.IsInactiveViewable = 1 AND Q.IsActionable = 1
AND RST.AssignedPersona IN ('Pricing Analyst', 'Credit Analyst', 'Credit Manager', 'Partner Carrier')
),
B1 AS (
SELECT DISTINCT Q.RequestID, Q.RequestStatusTypeID, Q.AssignedOn, U.UserName, Q.UserID
FROM dbo.RequestQueue Q
INNER JOIN dbo.[User] U ON Q.UserID = U.UserID
WHERE Q.RequestID IN (SELECT RequestID FROM A1) AND Q.IsSecondary = 1 AND Q.IsActive = 1 AND Q.IsInactiveViewable = 1
),
C1 AS (
SELECT B1.RequestID, COUNT(DISTINCT B1.RequestStatusTypeID) AS NumApprovalsRequested
FROM B1
INNER JOIN dbo.RequestStatusType RST ON RST.RequestStatusTypeID = B1.RequestStatusTypeID
WHERE RST.RequestStatusTypeName IN ('Pending DRM Approval', 'Pending EPT Approval', 'Pending PC Approval', 'Pending PCR Approval')
GROUP BY B1.RequestID
),
D1 AS (
SELECT B1.RequestID, COUNT(DISTINCT B1.RequestStatusTypeID) AS NumApprovalsCompleted
FROM B1
INNER JOIN dbo.RequestStatusType RST ON RST.RequestStatusTypeID = B1.RequestStatusTypeID
WHERE RST.RequestStatusTypeName IN ('DRM Approved', 'DRM Declined', 'EPT Approved', 'EPT Declined', 'PC Approved', 'PC Declined', 'PCR Approved', 'PCR Declined')
GROUP BY B1.RequestID
),
E1 AS (
SELECT RequestID, [secondary_approval], [status], [date], [user], [is_actionable] FROM (
SELECT B1.RequestID, 'Deal Review' AS [secondary_approval], 
	CASE WHEN RST.RequestStatusTypeName = 'Pending DRM Approval' THEN 'Requested' WHEN RST.RequestStatusTypeName = 'DRM Approved' THEN 'Approved' WHEN RST.RequestStatusTypeName = 'DRM Declined' THEN 'Declined' ELSE NULL END AS [status],
	B1.UserName AS [user],  
	CASE WHEN RST.RequestStatusTypeName = 'Pending DRM Approval' AND B1.UserID = @UserID THEN 1 ELSE 0 END AS [is_actionable],
	B1.AssignedOn AS [date],
ROW_NUMBER() OVER(PARTITION BY B1.RequestID ORDER BY AssignedOn DESC) AS RN
FROM B1
INNER JOIN dbo.RequestStatusType RST ON RST.RequestStatusTypeID = B1.RequestStatusTypeID
WHERE RST.RequestStatusTypeName IN ('Pending DRM Approval', 'DRM Approved', 'DRM Declined')) AS T
WHERE RN = 1

UNION

SELECT RequestID, [secondary_approval], [status], [date], [user], [is_actionable] FROM (
SELECT B1.RequestID, 'Pricing Committee' AS [secondary_approval], 
	CASE WHEN RST.RequestStatusTypeName = 'Pending PCR Approval' THEN 'Requested' WHEN RST.RequestStatusTypeName = 'PCR Approved' THEN 'Approved' WHEN RST.RequestStatusTypeName = 'PCR Declined' THEN 'Declined' ELSE NULL END AS [status],
	B1.UserName AS [user], 
	CASE WHEN RST.RequestStatusTypeName = 'Pending PCR Approval' AND B1.UserID = @UserID THEN 1 ELSE 0 END AS [is_actionable], 
	B1.AssignedOn AS [date],
ROW_NUMBER() OVER(PARTITION BY B1.RequestID ORDER BY AssignedOn DESC) AS RN
FROM B1
INNER JOIN dbo.RequestStatusType RST ON RST.RequestStatusTypeID = B1.RequestStatusTypeID
WHERE RST.RequestStatusTypeName IN ('Pending PCR Approval', 'PCR Approved', 'PCR Declined')) AS T
WHERE RN = 1

UNION

SELECT RequestID, [secondary_approval], [status], [date], [user], [is_actionable] FROM (
SELECT B1.RequestID, 'Priority Change' AS [secondary_approval], 
	CASE WHEN RST.RequestStatusTypeName = 'Pending PC Approval' THEN 'Requested' WHEN RST.RequestStatusTypeName = 'PC Approved' THEN 'Approved' WHEN RST.RequestStatusTypeName = 'PC Declined' THEN 'Declined' ELSE NULL END AS [status],
	B1.UserName AS [user],  
	CASE WHEN RST.RequestStatusTypeName = 'Pending PC Approval' AND B1.UserID = @UserID THEN 1 ELSE 0 END AS [is_actionable],
	B1.AssignedOn AS [date],
ROW_NUMBER() OVER(PARTITION BY B1.RequestID ORDER BY AssignedOn DESC) AS RN
FROM B1
INNER JOIN dbo.RequestStatusType RST ON RST.RequestStatusTypeID = B1.RequestStatusTypeID
WHERE RST.RequestStatusTypeName IN ('Pending PC Approval', 'PC Approved', 'PC Declined')) AS T
WHERE RN = 1

UNION

SELECT RequestID, [secondary_approval], [status], [date], [user], [is_actionable] FROM (
SELECT B1.RequestID, 'Extended Payment' AS [secondary_approval], 
	CASE WHEN RST.RequestStatusTypeName = 'Pending EPT Approval' THEN 'Requested' WHEN RST.RequestStatusTypeName = 'EPT Approved' THEN 'Approved' WHEN RST.RequestStatusTypeName = 'EPT Declined' THEN 'Declined' ELSE NULL END AS [status],
	B1.UserName AS [user],
	CASE WHEN RST.RequestStatusTypeName = 'Pending EPT Approval' AND B1.UserID = @UserID THEN 1 ELSE 0 END AS [is_actionable],
	B1.AssignedOn AS [date],
ROW_NUMBER() OVER(PARTITION BY B1.RequestID ORDER BY AssignedOn DESC) AS RN
FROM B1
INNER JOIN dbo.RequestStatusType RST ON RST.RequestStatusTypeID = B1.RequestStatusTypeID
WHERE RST.RequestStatusTypeName IN ('Pending EPT Approval', 'EPT Approved', 'EPT Declined')) AS T
WHERE RN = 1
),
F1 AS 
(
SELECT E1.RequestID, (SELECT E2.[secondary_approval], E2.[status], E2.[date], E2.[user], E2.[is_actionable] FROM E1 AS E2 WHERE E1.RequestID = E2.RequestID FOR JSON AUTO) AS approvals
FROM E1
GROUP BY E1.RequestID),
G1 AS (
SELECT * FROM (
SELECT RequestID, AssignedOn,
ROW_NUMBER() OVER(PARTITION BY A3.RequestID ORDER BY A3.AssignedOn DESC) AS RN
FROM A3 WHERE AssignedPersona = 'Credit Analyst') AS T
WHERE RN = 1
),
G2 AS (
SELECT * FROM (
SELECT RequestID, AssignedOn, 
ROW_NUMBER() OVER(PARTITION BY A3.RequestID ORDER BY A3.AssignedOn DESC) AS RN
FROM A3 WHERE AssignedPersona = 'Credit Manager') AS T
WHERE RN = 1
),
G3 AS (
SELECT * FROM (
SELECT RequestID, AssignedOn, 
ROW_NUMBER() OVER(PARTITION BY A3.RequestID ORDER BY A3.AssignedOn DESC) AS RN
FROM A3 WHERE AssignedPersona = 'Partner Carrier') AS T
WHERE RN = 1
),
G4 AS (
SELECT * FROM (
SELECT RequestID, UserID, SUM(DATEDIFF(MINUTE, AssignedOn, ISNULL(CompletedON, GETUTCDATE()))) / (24*60) AS ElapsedTime 
FROM A3 WHERE AssignedPersona = 'Pricing Analyst'
GROUP BY RequestID, UserID) AS T
)

SELECT CAST((SELECT * FROM (
SELECT R.RequestNumber AS request_number,
    R.RequestID AS request,
	R.RequestCode AS request_code,
	ISNULL(A.AccountNumber,'') AS account_number, 
	ISNULL(C.CustomerName,'') AS customer_name, 
	C.ServiceLevelID AS service_level_id, 
	SL.ServiceLevelCode AS service_level_code, 
	ISNULL(RSU.PricingAnalystID,'') AS pricing_analyst_id,
	ISNULL(UPA.UserName,'') AS pricing_analyst_name,
	ISNULL(RSU.SalesRepresentativeID,'') AS sales_representative_id,
	ISNULL(USR.UserName,'') AS sales_representative_name,
	ISNULL(RSU.CurrentEditorID,'') AS current_editor_id,
	ISNULL(CUE.UserName,'') AS current_editor_name,
	ISNULL(I.[Priority],'') AS [priority],
	RSU.RequestStatusTypeID AS request_status_type_id,
	RST.RequestStatusTypeName AS request_status_type_name,
	R.InitiatedOn AS date_initiated,
	ISNULL(R.SubmittedON,'') AS date_submitted,
	R.InitiatedBy AS initiated_by_id,
	IBY.UserName AS initiated_by_name,
	ISNULL(R.SubmittedBy,'') AS submitted_by_id,
	ISNULL(SBY.UserName,'') AS submitted_by_name,
	I.IsNewBusiness AS is_new_business,
	CASE WHEN A.AccountID IS NULL THEN 'New' ELSE 'Expanded' END AS business_type_name,
	ISNULL(G4.ElapsedTime, 0) AS days_in_queue,
	ISNULL(C1.NumApprovalsRequested, 0) AS approvals_requested,
	ISNULL(D1.NumApprovalsCompleted, 0) approvals_completed,
	ISNULL(F1.Approvals, '[]') AS approvals,
	ISNULL(G1.AssignedOn, '') AS date_submitted_credit_analyst,
	ISNULL(G2.AssignedOn, '') AS date_submitted_credit_manager,
	ISNULL(G3.AssignedOn, '') AS date_submitted_partner_carrier,
	RT.RequestTypeName AS request_type_name,
	CASE WHEN RSU.CurrentEditorID = @UserID THEN 1 ELSE 0 END AS is_current_editor,
    R.SpeedsheetName AS speedsheet_name,
    (select LanguageCode from Language where LanguageId = I.LanguageID) AS language_code
FROM dbo.Request R
INNER JOIN dbo.RequestStatus RSU ON R.RequestID = RSU.RequestID
INNER JOIN dbo.RequestStatusType RST ON RSU.RequestStatusTypeID = RST.RequestStatusTypeID
INNER JOIN dbo.RequestInformation I ON R.RequestInformationID = I.RequestInformationID
INNER JOIN dbo.Customer C ON I.CustomerID = C.CustomerID
INNER JOIN dbo.ServiceLevel SL ON C.ServiceLevelID = SL.ServiceLevelID
LEFT JOIN A2 ON R.RequestID = A2.RequestID
LEFT JOIN dbo.RequestType RT ON I.RequestTypeID = RT.RequestTypeID
LEFT JOIN dbo.Account A ON C.AccountID = A.AccountID
LEFT JOIN dbo.[User] UPA ON RSU.PricingAnalystID = UPA.UserID
LEFT JOIN dbo.[User] USR ON RSU.SalesRepresentativeID = USR.UserID
LEFT JOIN dbo.[User] CUE ON RSU.CurrentEditorID = CUE.UserID
LEFT JOIN dbo.[User] IBY ON R.InitiatedBy = IBY.UserID
LEFT JOIN dbo.[User] SBY ON R.SubmittedBy = SBY.UserID
LEFT JOIN C1 ON R.RequestID = C1.RequestID
LEFT JOIN D1 ON R.RequestID = D1.RequestID
LEFT JOIN F1 ON R.RequestID = F1.RequestID
LEFT JOIN G1 ON R.RequestID = G1.RequestID 
LEFT JOIN G2 ON R.RequestID = G2.RequestID 
LEFT JOIN G3 ON R.RequestID = G3.RequestID 
LEFT JOIN G4 ON R.RequestID = G4.RequestID AND G4.UserID = @UserID 
WHERE R.RequestID = @RequestId AND (@UniType = 'SPEEDSHEET' AND R.UniType = @UniType) OR (@UniType = 'REQUEST' AND R.UniType is NULL) and R.IsInactiveViewable = 1 AND (A2.RequestID IS NOT NULL OR @UserPersona IN ('Pricing Analyst', 'Pricing Manager'))
) AS Q FOR JSON AUTO) AS VARCHAR(MAX))
"""

GET_PRICING_POINT_DESTINATION = """
DECLARE @OPC BIGINT;
DECLARE @DPC BIGINT;
DECLARE @RequestSectionLaneID BIGINT;

SELECT @OPC = OriginPostalCodeID,
	 @DPC = DestinationPostalCodeID,
	 @RequestSectionLaneID = RequestSectionLaneID
FROM dbo.RequestSectionLanePricingPoint
WHERE RequestSectionLanePricingPointID = {0};

WITH A AS (
SELECT PC.PostalCodeID, SP.ServicePointID, SP.BasingPointID, TSP.TerminalID, P.ProvinceID, R.RegionID, C.CountryID
FROM dbo.PostalCode PC 
INNER JOIN dbo.ServicePoint SP ON PC.ServicePointID = SP.ServicePointID
INNER JOIN dbo.TerminalServicePoint TSP ON TSP.ServicePointID = SP.ServicePointID
INNER JOIN dbo.Province P ON SP.ProvinceID = P.ProvinceID
INNER JOIN dbo.Region R ON P.RegionID = R.RegionID
INNER JOIN dbo.Country C ON R.CountryID = C.CountryID
WHERE PC.PostalCodeID = @OPC
), B AS (
SELECT PC.PostalCodeID, SP.ServicePointID, SP.BasingPointID, TSP.TerminalID, P.ProvinceID, R.RegionID, C.CountryID
FROM dbo.PostalCode PC 
INNER JOIN dbo.ServicePoint SP ON PC.ServicePointID = SP.ServicePointID
INNER JOIN dbo.TerminalServicePoint TSP ON TSP.ServicePointID = SP.ServicePointID
INNER JOIN dbo.Province P ON SP.ProvinceID = P.ProvinceID
INNER JOIN dbo.Region R ON P.RegionID = R.RegionID
INNER JOIN dbo.Country C ON R.CountryID = C.CountryID
WHERE PC.PostalCodeID = @DPC
), O AS (
SELECT RSL.*
FROM dbo.RequestSectionLane RSL 
WHERE RSL.RequestSectionID = {1}
AND ( 
		(RSL.OriginPointTypeName = 'Country' AND RSL.OriginCountryID IN (SELECT CountryID FROM A))
		OR (RSL.OriginPointTypeName = 'Region' AND RSL.OriginRegionID IN (SELECT RegionID FROM A))
		OR (RSL.OriginPointTypeName = 'Province' AND RSL.OriginProvinceID IN (SELECT ProvinceID FROM A))
		OR (RSL.OriginPointTypeName = 'Terminal' AND RSL.OriginTerminalID IN (SELECT TerminalID FROM A))
		OR (RSL.OriginPointTypeName = 'Basing Point' AND RSL.OriginBasingPointID IN (SELECT BasingPointID FROM A))
		OR (RSL.OriginPointTypeName = 'Service Point' AND RSL.OriginBasingPointID IN (SELECT ServicePointID FROM A))
		OR (RSL.OriginPointTypeName = 'Postal Code' AND RSL.OriginPostalCodeID IN (SELECT PostalCodeID FROM A))
	)
), D AS (
SELECT RSL.*
FROM dbo.RequestSectionLane RSL 
INNER JOIN O ON O.RequestSectionLaneID = RSL.RequestSectionLaneID
WHERE RSL.RequestSectionID = {1} 
AND ( 
		(RSL.DestinationPointTypeName = 'Country' AND RSL.DestinationCountryID IN (SELECT CountryID FROM B))
		OR (RSL.DestinationPointTypeName = 'Region' AND RSL.DestinationRegionID IN (SELECT RegionID FROM B))
		OR (RSL.DestinationPointTypeName = 'Province' AND RSL.DestinationProvinceID IN (SELECT ProvinceID FROM B))
		OR (RSL.DestinationPointTypeName = 'Terminal' AND RSL.DestinationTerminalID IN (SELECT TerminalID FROM B))
		OR (RSL.DestinationPointTypeName = 'Basing Point' AND RSL.DestinationBasingPointID IN (SELECT BasingPointID FROM B))
		OR (RSL.DestinationPointTypeName = 'Service Point' AND RSL.DestinationBasingPointID IN (SELECT ServicePointID FROM B))
		OR (RSL.DestinationPointTypeName = 'Postal Code' AND RSL.DestinationPostalCodeID IN (SELECT PostalCodeID FROM B))
	)
)

SELECT CAST((SELECT * FROM (
SELECT * FROM D
WHERE RequestSectionLaneID <> @RequestSectionLaneID
) AS Q FOR JSON AUTO) AS VARCHAR(MAX))
"""

GET_REQUEST_HEADER = """
SET NOCOUNT ON;
DECLARE @UserID BIGINT = {1}; 
DECLARE @RequestNumber NVARCHAR(32) = '{0}'; 
DECLARE @RequestID BIGINT = (SELECT RequestID FROM dbo.Request WHERE RequestNumber = @RequestNumber);
DECLARE @IsActionable BIT = 0;
DECLARE @SecondaryStatus NVARCHAR(MAX);
DECLARE @Approvals NVARCHAR(MAX);
DECLARE @IsCurrentEditor BIT;
DECLARE @CanRequestEditorRights BIT = 1;

IF EXISTS (SELECT TOP 1 NotificationID FROM dbo.RequestEditorRight WHERE RequestID = @RequestID AND UserID = @UserID AND IsActive = 1 AND IsInactiveViewable = 1)
SELECT @CanRequestEditorRights = 0;

IF NOT EXISTS (SELECT RequestQueueID FROM dbo.RequestQueue WHERE RequestID = @RequestID AND UserID = @UserID AND IsActive = 1 AND IsInactiveViewable = 1 AND CompletedON IS NULL)
SELECT @CanRequestEditorRights = 0;

DECLARE @Q AS TABLE 
(
	IsSecondary BIT NOT NULL,
	RequestStatusTypeID BIGINT NOT NULL,
	UserPersona NVARCHAR(50) NOT NULL,
	CompletedOn DATETIME2(7) NULL,
	UserID BIGINT NOT NULL,
	IsActionable BIT NOT NULL
)
INSERT INTO @Q
(
	IsSecondary,
	RequestStatusTypeID,
	UserPersona,
	CompletedOn,
	UserID,
	IsActionable
)
SELECT IsSecondary,
	RequestStatusTypeID,
	UserPersona,
	CompletedOn,
	UserID,
	IsActionable
FROM dbo.RequestQueue
WHERE RequestID = @RequestID  
AND IsActive = 1 AND IsInactiveViewable = 1 

-- IH: If the User is assigned multiple personas in dbo.RequestQueue, e.g. Sales Coordinator or Pricing Manager initiate request and are both their own persona and assigned sales rep 
-- IH: then they will have multiple rows of queue data of which one is actionable and the other is not which prevents them from submitting requests
SELECT @IsActionable = (select top 1 IsActionable
FROM dbo.RequestQueue 
WHERE RequestID = @RequestID AND UserID = @UserID AND CompletedOn IS NULL AND IsSecondary = 0
Order By IsActionable DESC)

SELECT @IsCurrentEditor = CASE WHEN RS.CurrentEditorID IS NOT NULL AND RS.CurrentEditorID = @UserID THEN 1 ELSE 0 END
FROM dbo.RequestStatus RS WHERE RS.RequestID = @RequestID

SELECT @SecondaryStatus = 
(
SELECT DISTINCT Y.RequestStatusTypeName
FROM @Q Q
INNER JOIN dbo.RequestStatusType Y ON Q.RequestStatusTypeID = Y.RequestStatusTypeID
WHERE Q.IsSecondary = 1 AND (Q.UserID = @UserID OR @IsCurrentEditor = 1)
FOR JSON AUTO
) 

SELECT @approvals = 
(
SELECT  Y.RequestStatusTypeName
FROM @Q Q
INNER JOIN dbo.RequestStatusType Y ON Q.RequestStatusTypeID = Y.RequestStatusTypeID
WHERE Q.CompletedON IS NULL AND Q.CompletedON IS NULL AND Q.IsSecondary = 1 AND Q.UserID = @UserID AND Q.IsActionable = 1 AND Y.RequestStatusTypeName IN ('Pending DRM Approval', 'Pending EPT Approval', 'Pending PC Approval', 'Pending PCR Approval')

FOR JSON AUTO
) 

SELECT CAST((SELECT * FROM (
SELECT R.RequestID AS request_id,
	R.RequestNumber AS request_number,
	R.RequestCode AS request_code,
	RST.RequestStatusTypeName AS request_status_type,
	CASE WHEN IH.VersionNum > 1 THEN 1 ELSE 0 END information_tab,
	CASE WHEN PH.VersionNum > 1 THEN 1 ELSE 0 END profile_tab,
	CASE WHEN LH.VersionNum > 1 THEN 1 ELSE 0 END lanes_tab,
	ISNULL(C.CustomerName,'') AS customer_name,
	ISNULL(A.AccountNumber, '') AS account_number,
	RH.VersionNum AS num_versions,
	SL.ServiceLevelID AS service_level_id,
	SL.ServiceLevelCode AS service_level_code,
	SL.PricingType AS service_level_pricing_type,
	SO.ServiceOfferingID AS service_offering_id,
	SO.ServiceOfferingName AS service_offering_name,
	ISNULL(RT.RequestTypeName, '') AS request_type_name,
	@IsCurrentEditor AS is_current_editor,
	ISNULL(I.[Priority], 0) AS [priority],
	ISNULL(I.IsExtendedPayment, 0) AS is_extended_payment,
	ISNULL(@SecondaryStatus, '[]') AS secondary_statuses,
	ISNULL(@IsActionable, 0) AS is_actionable,
	ISNULL(@Approvals, '[]') AS actionable_approvals,
	@CanRequestEditorRights AS can_request_editor_rights,
	ISNULL(I.ExtendedPaymentDays, 0) AS extended_payment_days,
	IH.RequestInformationID AS request_information_id,
	PH.RequestProfileID AS request_profile_id,
	LH.RequestLaneID AS request_lane_id
FROM dbo.Request R
INNER JOIN dbo.Request_History RH ON R.RequestID = RH.RequestID AND RH.IsLatestVersion = 1
INNER JOIN dbo.RequestInformation I ON R.RequestInformationID = I.RequestInformationID
INNER JOIN dbo.RequestStatus RS ON R.RequestID = RS.RequestID
INNER JOIN dbo.RequestStatusType RST ON RS.RequestStatusTypeID = RST.RequestStatusTypeID
INNER JOIN dbo.RequestInformation_History IH ON R.RequestNumber = IH.RequestNumber AND IH.IsLatestVersion = 1
INNER JOIN dbo.RequestProfile_History PH ON R.RequestNumber = PH.RequestNumber AND PH.IsLatestVersion = 1
INNER JOIN dbo.RequestLane_History LH ON R.RequestNumber = LH.RequestNumber AND LH.IsLatestVersion = 1
INNER JOIN dbo.Customer C ON I.CustomerID = C.CustomerID
INNER JOIN dbo.ServiceLevel SL ON C.ServiceLevelID = SL.ServiceLevelID
INNER JOIN dbo.ServiceOffering SO ON SL.ServiceOfferingID = SO.ServiceOfferingID
LEFT JOIN dbo.Account A ON C.AccountID = A.AccountID
LEFT JOIN dbo.RequestType RT ON I.RequestTypeID = RT.RequestTypeID
WHERE R.RequestNumber = @RequestNumber
) AS Q FOR JSON AUTO, WITHOUT_ARRAY_WRAPPER) AS VARCHAR(MAX))
"""

GET_REQUEST_HEADER_HISTORY = """
SET NOCOUNT ON;
DECLARE @UserID BIGINT = {2}; 
DECLARE @RequestNumber NVARCHAR(32) = '{0}'; 
DECLARE @VersionNum INT = {1}; 
DECLARE @RequestID BIGINT = (SELECT RequestID FROM dbo.Request WHERE RequestNumber = @RequestNumber);
DECLARE @IsActionable BIT = 0;
DECLARE @IsCurrentEditor BIT;
DECLARE @CanRequestEditorRights BIT = 1;

IF EXISTS (SELECT TOP 1 NotificationID FROM dbo.RequestEditorRight WHERE RequestID = @RequestID AND UserID = @UserID AND IsActive = 1 AND IsInactiveViewable = 1)
SELECT @CanRequestEditorRights = 0;

IF NOT EXISTS (SELECT RequestQueueID FROM dbo.RequestQueue WHERE RequestID = @RequestID AND UserID = @UserID AND IsActive = 1 AND IsInactiveViewable = 1 AND CompletedON IS NULL)
SELECT @CanRequestEditorRights = 0;

DECLARE @Q AS TABLE 
(
	IsSecondary BIT NOT NULL,
	RequestStatusTypeID BIGINT NOT NULL,
	UserPersona NVARCHAR(50) NOT NULL,
	CompletedOn DATETIME2(7) NULL,
	UserID BIGINT NOT NULL,
	IsActionable BIT NOT NULL
)
INSERT INTO @Q
(
	IsSecondary,
	RequestStatusTypeID,
	UserPersona,
	CompletedOn,
	UserID,
	IsActionable
)
SELECT IsSecondary,
	RequestStatusTypeID,
	UserPersona,
	CompletedOn,
	UserID,
	IsActionable
FROM dbo.RequestQueue
WHERE RequestID = @RequestID  
AND IsActive = 1 AND IsInactiveViewable = 1 

SELECT @IsActionable = IsActionable
FROM dbo.RequestQueue 
WHERE RequestID = @RequestID AND UserID = @UserID AND CompletedOn IS NULL

SELECT @IsCurrentEditor = CASE WHEN RS.CurrentEditorID IS NOT NULL AND RS.CurrentEditorID = @UserID THEN 1 ELSE 0 END
FROM dbo.RequestStatus RS WHERE RS.RequestID = @RequestID

SELECT CAST((SELECT * FROM (
SELECT R.RequestID AS request_id,
	RH.RequestNumber AS request_number,
	RH.RequestCode AS request_code,
	RST.RequestStatusTypeName AS request_status_type,
	CASE WHEN IH.VersionNum > 1 THEN 1 ELSE 0 END information_tab,
	CASE WHEN PH.VersionNum > 1 THEN 1 ELSE 0 END profile_tab,
	CASE WHEN LH.VersionNum > 1 THEN 1 ELSE 0 END lanes_tab,
	ISNULL(C.CustomerName,'') AS customer_name,
	ISNULL(A.AccountNumber,'') AS account_number,
	R.VersionNum AS num_versions,
	SL.ServiceLevelID AS service_level_id,
	SL.ServiceLevelCode AS service_level_code,
	SL.PricingType AS service_level_pricing_type,
	SO.ServiceOfferingID AS service_offering_id,
	SO.ServiceOfferingName AS service_offering_name,
	ISNULL(RT.RequestTypeName, '') AS request_type_name,
	@IsCurrentEditor AS is_current_editor,
	ISNULL(IH.[Priority], 0) AS [priority],
	ISNULL(IH.IsExtendedPayment, 0) AS is_extended_payment,
	'[]' AS secondary_statuses,
	'[]' AS actionable_approvals,
	ISNULL(@IsActionable, 0) AS is_actionable,
	@CanRequestEditorRights AS can_request_editor_rights,
	ISNULL(IH.ExtendedPaymentDays, 0) AS extended_payment_days,
	IH.RequestInformationID AS request_information_id,
	PH.RequestProfileID AS request_profile_id,
	LH.RequestLaneID AS request_lane_id
FROM dbo.Request_History R 
INNER JOIN dbo.Request_History RH ON R.RequestID = RH.RequestID AND RH.VersionNum = @VersionNum
INNER JOIN dbo.RequestStatus RS ON R.RequestID = RS.RequestID
INNER JOIN dbo.RequestStatusType RST ON RS.RequestStatusTypeID = RST.RequestStatusTypeID
INNER JOIN dbo.RequestInformation_History IH ON RH.RequestInformationVersionID = IH.RequestInformationVersionID
INNER JOIN dbo.RequestProfile_History PH ON RH.RequestProfileVersionID = PH.RequestProfileVersionID
INNER JOIN dbo.RequestLane_History LH ON RH.RequestLaneVersionID = LH.RequestLaneVersionID
INNER JOIN dbo.Customer_History C ON IH.CustomerVersionID = C.CustomerVersionID
INNER JOIN dbo.ServiceLevel_History SL ON C.ServiceLevelVersionID = SL.ServiceLevelVersionID
INNER JOIN dbo.ServiceOffering_History SO ON SL.ServiceOfferingVersionID = SO.ServiceOfferingVersionID
LEFT JOIN dbo.Account_History A ON C.AccountVersionID = A.AccountVersionID
LEFT JOIN dbo.RequestType_History RT ON IH.RequestTypeVersionID = RT.RequestTypeVersionID
WHERE R.RequestNumber = @RequestNumber AND R.IsLatestVersion = 1 
) AS Q FOR JSON AUTO, WITHOUT_ARRAY_WRAPPER) AS VARCHAR(MAX))
"""

RESOLVE_NAME_TO_ID = """
DECLARE @ID CHAR(32)
SET @ID = '{0}'
SELECT RSLIQ.RequestSectionID                as RequestSectionID,
       OGRSLPT.RequestSectionLanePointTypeID as OriginGroupTypeID,
       CASE
           WHEN OGRSLPT.RequestSectionLanePointTypeName = 'Country' THEN
               (SELECT C.CountryID
                FROM dbo.Country C
                         INNER JOIN dbo.RequestSectionLaneImportQueue RSLIQ ON C.CountryCode = RSLIQ.OriginGroupCode
                WHERE RSLIQ.id = @ID)

           WHEN OGRSLPT.RequestSectionLanePointTypeName = 'Region' THEN
               (SELECT R.RegionID
                FROM dbo.Region R
                         INNER JOIN dbo.RequestSectionLaneImportQueue RSLIQ ON R.RegionCode = RSLIQ.OriginGroupCode
                WHERE RSLIQ.id = @ID)

           WHEN OGRSLPT.RequestSectionLanePointTypeName = 'Province' THEN
               (SELECT P.ProvinceID
                FROM dbo.Province P
                         Inner Join dbo.RequestSectionLaneImportQueue RSLIQ
                                    ON P.ProvinceCode = RSLIQ.OriginGroupCode
                WHERE RSLIQ.id = @ID)
           END                               as OriginGroupID,
       OPRSLPT.RequestSectionLanePointTypeID as OriginPointTypeID,
       CASE
           WHEN OPRSLPT.RequestSectionLanePointTypeName = 'Country' THEN
               (SELECT C.CountryID
                FROM dbo.Country C
                         INNER JOIN dbo.RequestSectionLaneImportQueue RSLIQ ON C.CountryCode = RSLIQ.OriginPointCode
                WHERE RSLIQ.id = @ID)
           WHEN OPRSLPT.RequestSectionLanePointTypeName = 'Region' THEN
               (SELECT R.RegionID
                FROM dbo.Region R
                         INNER JOIN dbo.RequestSectionLaneImportQueue RSLIQ ON R.RegionCode = RSLIQ.OriginPointCode
                WHERE RSLIQ.id = @ID)
           WHEN OPRSLPT.RequestSectionLanePointTypeName = 'Province' THEN
               (SELECT P.ProvinceID
                FROM dbo.Province P
                         INNER JOIN dbo.RequestSectionLaneImportQueue RSLIQ ON P.ProvinceCode = RSLIQ.OriginPointCode
                WHERE RSLIQ.id = @ID)
           WHEN OPRSLPT.RequestSectionLanePointTypeName = 'Terminal' THEN
               (SELECT T.TerminalID
                FROM dbo.Terminal T
                         INNER JOIN dbo.RequestSectionLaneImportQueue RSLIQ ON T.TerminalCode = RSLIQ.OriginPointCode
                WHERE RSLIQ.id = @ID)
            -- Add logic to ensure correct basing point match
           WHEN OPRSLPT.RequestSectionLanePointTypeName = 'Basing Point' THEN
               (SELECT BP.BasingPointID
                FROM dbo.BasingPoint BP
                         INNER JOIN dbo.RequestSectionLaneImportQueue RSLIQ
                                    ON BP.BasingPointName = RSLIQ.OriginPointCode
						 Inner Join dbo.Province P
									ON P.ProvinceCode = RSLIQ.OriginGroupCode
                WHERE RSLIQ.id = @ID
				AND P.ProvinceID = BP.ProvinceID)
            -- Add logic to ensure correct service point match
           WHEN OPRSLPT.RequestSectionLanePointTypeName = 'Service Point' THEN
               (Select SP.ServicePointID
                FROM dbo.ServicePoint SP
                         INNER JOIN dbo.RequestSectionLaneImportQueue RSLIQ
                                    ON SP.ServicePointName = RSLIQ.OriginPointCode
						Inner Join dbo.Province P
									ON P.ProvinceCode = RSLIQ.OriginGroupCode
                WHERE RSLIQ.id = @ID
				AND P.ProvinceID = SP.ProvinceID)
           WHEN OPRSLPT.RequestSectionLanePointTypeName = 'Postal Code' THEN
               (Select PC.PostalCodeID
                FROM dbo.PostalCode PC
                         INNER JOIN dbo.RequestSectionLaneImportQueue RSLIQ
                                    ON PC.PostalCodeName = RSLIQ.OriginPointCode
                WHERE RSLIQ.id = @ID)
           END                               as OriginPointID,
       DGRSLPT.RequestSectionLanePointTypeID as DestinationGroupTypeID,


       CASE
           WHEN DGRSLPT.RequestSectionLanePointTypeName = 'Country' THEN
               (Select C.CountryID
                FROM dbo.Country C
                         Inner Join dbo.RequestSectionLaneImportQueue RSLIQ
                                    ON C.CountryCode = RSLIQ.DestinationGroupCode
                WHERE RSLIQ.id = @ID)
           WHEN DGRSLPT.RequestSectionLanePointTypeName = 'Region' THEN
               (Select R.RegionID
                FROM dbo.Region R
                         Inner Join dbo.RequestSectionLaneImportQueue RSLIQ
                                    ON R.RegionCode = RSLIQ.DestinationGroupCode
                WHERE RSLIQ.id = @ID)
           WHEN DGRSLPT.RequestSectionLanePointTypeName = 'Province' THEN
               (Select P.ProvinceID
                FROM dbo.Province P
                         Inner Join dbo.RequestSectionLaneImportQueue RSLIQ
                                    ON P.ProvinceCode = RSLIQ.DestinationGroupCode
                WHERE RSLIQ.id = @ID)
           END                               as DestinationGroupID,
       DPRSLPT.RequestSectionLanePointTypeID as DestinationPointTypeID,

       CASE
           WHEN DPRSLPT.RequestSectionLanePointTypeName = 'Country' THEN
               (Select C.CountryID
                FROM dbo.Country C
                         Inner Join dbo.RequestSectionLaneImportQueue RSLIQ
                                    ON C.CountryCode = RSLIQ.DestinationPointCode
                WHERE RSLIQ.id = @ID)
           WHEN DPRSLPT.RequestSectionLanePointTypeName = 'Region' THEN
               (Select R.RegionID
                FROM dbo.Region R
                         Inner Join dbo.RequestSectionLaneImportQueue RSLIQ
                                    ON R.RegionCode = RSLIQ.DestinationPointCode
                WHERE RSLIQ.id = @ID)
           WHEN DPRSLPT.RequestSectionLanePointTypeName = 'Province' THEN
               (Select P.ProvinceID
                FROM dbo.Province P
                         Inner Join dbo.RequestSectionLaneImportQueue RSLIQ
                                    ON P.ProvinceCode = RSLIQ.DestinationPointCode
                WHERE RSLIQ.id = @ID)
           WHEN DPRSLPT.RequestSectionLanePointTypeName = 'Terminal' THEN
               (Select T.TerminalID
                FROM dbo.Terminal T
                         Inner Join dbo.RequestSectionLaneImportQueue RSLIQ
                                    ON T.TerminalCode = RSLIQ.DestinationPointCode
                WHERE RSLIQ.id = @ID)
            -- Add logic to ensure correct basing point match
           WHEN DPRSLPT.RequestSectionLanePointTypeName = 'Basing Point' THEN
               (Select BP.BasingPointID
                FROM dbo.BasingPoint BP
                         Inner Join dbo.RequestSectionLaneImportQueue RSLIQ
                                    ON BP.BasingPointName = RSLIQ.DestinationPointCode
						 Inner Join dbo.Province P
									ON P.ProvinceCode = RSLIQ.DestinationGroupCode

                WHERE RSLIQ.id = @ID
				AND P.ProvinceID = BP.ProvinceID)
            -- Add logic to ensure correct service point match
           WHEN DPRSLPT.RequestSectionLanePointTypeName = 'Service Point' THEN
               (SELECT SP.ServicePointID
                FROM dbo.ServicePoint SP
                         INNER JOIN dbo.RequestSectionLaneImportQueue RSLIQ
                                    ON SP.ServicePointName = RSLIQ.DestinationPointCode
						 Inner Join dbo.Province P
									ON P.ProvinceCode = RSLIQ.DestinationGroupCode
                WHERE RSLIQ.id = @ID
				AND P.ProvinceID = SP.ProvinceID)
           WHEN DPRSLPT.RequestSectionLanePointTypeName = 'Postal Code' THEN
               (Select PC.PostalCodeID
                FROM dbo.PostalCode PC
                         Inner Join dbo.RequestSectionLaneImportQueue RSLIQ
                                    ON PC.PostalCodeName = RSLIQ.DestinationPointCode
                WHERE RSLIQ.id = @ID)
           END                               as DestinationPointID,
       RSLIQ.IsBetween

FROM dbo.RequestSectionLaneImportQueue RSLIQ
         INNER JOIN dbo.RequestSection RS ON RS.RequestSectionID = RSLIQ.RequestSectionID
         INNER JOIN dbo.SubServiceLevel SSLL ON RS.SubServiceLevelID = SSLL.SubServiceLevelID
         INNER JOIN dbo.ServiceLevel SL ON SSLL.ServiceLevelID = SL.ServiceLevelID
         INNER JOIN dbo.RequestSectionLanePointType OGRSLPT
                    ON OGRSLPT.RequestSectionLanePointTypeName = RSLIQ.OriginGroupTypeName
         INNER JOIN dbo.RequestSectionLanePointType OPRSLPT
                    ON OPRSLPT.RequestSectionLanePointTypeName = RSLIQ.OriginPointTypeName
         INNER JOIN dbo.RequestSectionLanePointType DGRSLPT
                    ON DGRSLPT.RequestSectionLanePointTypeName = RSLIQ.DestinationGroupTypeName
         INNER JOIN dbo.RequestSectionLanePointType DPRSLPT
                    ON DPRSLPT.RequestSectionLanePointTypeName = RSLIQ.DestinationPointTypeName

WHERE RSLIQ.id = @id
  AND -- We only need to run RequestSectionLane_Insert for NEW LANES ONLY
    RS.IsDensityPricing = OGRSLPT.IsDensityPricing
  AND RS.IsDensityPricing = OPRSLPT.IsDensityPricing
  AND RS.IsDensityPricing = DGRSLPT.IsDensityPricing
  AND RS.IsDensityPricing = DPRSLPT.IsDensityPricing
  AND OGRSLPT.IsGroupType = 1
  AND DGRSLPT.IsGroupType = 1
  AND OPRSLPT.IsPointType = 1
  AND DPRSLPT.IsPointType = 1
  AND OGRSLPT.LocationHierarchy <= OPRSLPT.LocationHierarchy
  AND DGRSLPT.LocationHierarchy <= DPRSLPT.LocationHierarchy
  AND OPRSLPT.ServiceOfferingID = SL.ServiceOfferingID
  AND OGRSLPT.ServiceOfferingID = SL.ServiceOfferingID
  AND DPRSLPT.ServiceOfferingID = SL.ServiceOfferingID
  AND DGRSLPT.ServiceOfferingID = SL.ServiceOfferingID
  AND RS.IsActive = 1
  AND RS.IsInactiveViewable = 1
  AND SL.IsActive = 1
  AND SL.IsInactiveViewable = 1
  AND SSLL.IsActive = 1
  AND SSLL.IsInactiveViewable = 1
  AND OGRSLPT.IsActive = 1
  AND OGRSLPT.IsInactiveViewable = 1
  AND OPRSLPT.IsActive = 1
  AND OPRSLPT.IsInactiveViewable = 1
  AND DGRSLPT.IsActive = 1
  AND DGRSLPT.IsInactiveViewable = 1
  AND DPRSLPT.IsActive = 1
  AND DPRSLPT.IsInactiveViewable = 1"""

# -- For Pricing Point Template we need to convert the following values from RequestSectionLanePricingPointImportQueue into the IDs to use with RequestSectionLanePricingPoint_Insert Stored Procedure for NEW Pricing Points ONLY
RESOLVE_PP_NAME_TO_ID = """
DECLARE @ID CHAR(32)
SET @ID = '{0}'
SELECT RSLPPIQ.RequestSectionID     as RequestSectionID,
       RSLPPIQ.RequestSectionLaneID as RequestSectionLaneID,
       OPC.PostalCodeID             as OriginPostalCodeID,
       DPC.PostalCodeID             as DestinationPostalCodeID
FROM dbo.RequestSectionLanePricingPointImportQueue RSLPPIQ
         INNER JOIN dbo.RequestSection RS ON RS.RequestSectionID = RSLPPIQ.RequestSectionID
         INNER JOIN dbo.RequestSectionLane RSL ON RSL.RequestSectionLaneID = RSLPPIQ.RequestSectionLaneID
         INNER JOIN dbo.PostalCode OPC ON RSLPPIQ.OriginPostalCodeName = OPC.PostalCodeName
         INNER JOIN dbo.PostalCode DPC ON RSLPPIQ.DestinationPostalCodeName = DPC.PostalCodeName
WHERE RSLPPIQ.id = @ID
  AND RS.IsDensityPricing=0
  AND RSL.OriginCode = RSLPPIQ.OriginPointCode
  AND RSL.DestinationCode = RSLPPIQ.DestinationPointCode
  AND RS.IsActive = 1
  AND RS.IsInactiveViewable = 1
  AND RSL.IsActive = 1
  AND RSL.IsInactiveViewable = 1
  AND OPC.IsActive = 1
  AND OPC.IsInactiveViewable = 1
  AND DPC.IsActive = 1
  AND DPC.IsInactiveViewable = 1"""
