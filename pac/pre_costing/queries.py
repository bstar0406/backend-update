DOCK_ROUTES_DASHBOARD = """ WITH
    O
    AS
    (
        SELECT T.TerminalID, T.TerminalCode, P.ProvinceID, P.ProvinceCode, R.RegionID, R.RegionCode
        FROM [dbo].[Terminal] T
            INNER JOIN [dbo].[City] C ON T.[CityID] = C.[CityID]
            INNER JOIN [dbo].[Province] P ON C.[ProvinceID] = P.[ProvinceID]
            INNER JOIN [dbo].[Region] R ON T.[RegionID] = R.[RegionID]
        WHERE T.TerminalID IN (SELECT OriginTerminalID
        FROM [dbo].[Lane])
    ),
    D
    AS
    (
        SELECT T.TerminalID, T.TerminalCode, P.ProvinceID, P.ProvinceCode, R.RegionID, R.RegionCode
        FROM [dbo].[Terminal] T
            INNER JOIN [dbo].[City] C ON T.[CityID] = C.[CityID]
            INNER JOIN [dbo].[Province] P ON C.[ProvinceID] = P.[ProvinceID]
            INNER JOIN [dbo].[Region] R ON T.[RegionID] = R.[RegionID]
        WHERE T.TerminalID IN (SELECT DestinationTerminalID
        FROM [dbo].[Lane])
    ),
    L
    AS
    (
        SELECT A.LaneID,
            O.TerminalID AS OriginTerminalID,
            O.TerminalCode AS OriginTerminalCode,
            O.ProvinceID AS OriginProvinceID,
            O.ProvinceCode AS OriginProvinceCode,
            O.RegionID AS OriginRegionID,
            O.RegionCode AS OriginRegionCode,
            D.TerminalID AS DestinationTerminalID,
            D.TerminalCode AS DestinationTerminalCode,
            D.ProvinceID AS DestinationProvinceID,
            D.ProvinceCode AS DestinationProvinceCode,
            D.RegionID AS DestinationRegionID,
            D.RegionCode AS DestinationRegionCode,
            A.SubServiceLevelID,
            A.IsActive AS IsActive,
            A.IsInactiveViewable AS IsInactiveViewable
        FROM [dbo].[Lane] A
            INNER JOIN O ON A.[OriginTerminalID] = O.[TerminalID]
            INNER JOIN D ON A.[DestinationTerminalID] = D.[TerminalID]
    )
SELECT CAST(
(SELECT *
    FROM
        (
SELECT DR.DockRouteID as dock_route_id,
            L.OriginTerminalID AS origin_terminal_id,
            L.OriginTerminalCode AS origin_terminal_code,
            L.OriginProvinceID AS origin_province_id,
            L.OriginProvinceCode AS origin_province_code,
            L.OriginRegionID AS origin_region_id,
            L.OriginRegionCode AS origin_region_code,
            L.DestinationTerminalID AS destination_terminal_id,
            L.DestinationTerminalCode AS destination_terminal_code,
            L.DestinationProvinceID AS destination_province_id,
            L.DestinationProvinceCode AS destination_province_code,
            L.DestinationRegionID AS destination_region_id,
            L.DestinationRegionCode AS destination_region_code,
            SSL.SubServiceLevelID as sub_service_level_id,
            SSL.SubServiceLevelCode as sub_service_level_code,
            L.LaneID as lane_id,
            L.IsActive as is_active,
            L.IsInactiveViewable as is_inactive_viewable,
            DRH.UpdatedOn as updated_on
        FROM L
            INNER JOIN [dbo].[DockRoute] DR ON L.[LaneID] = DR.[LaneID]
            INNER JOIN [dbo].[DockRoute_History] DRH ON DR.[DockRouteID] = DRH.[DockRouteID] AND DRH.[IsLatestVersion]=1
            INNER JOIN [dbo].[SubServiceLevel] SSL ON L.[SubServiceLevelID] = SSL.[SubServiceLevelID]
            INNER JOIN [dbo].[ServiceLevel] SL ON SSL.[ServiceLevelID] = SL.[ServiceLevelID] AND SL.[ServiceOfferingID] = {0}
        WHERE L.[IsInactiveViewable] = 1
)  AS DockRoute
    FOR JSON AUTO) AS VARCHAR(MAX))
 """

LANE_ROUTES_DASHBOARD = """ WITH
    O
    AS
    (
        SELECT T.TerminalID, T.TerminalCode, P.ProvinceID, P.ProvinceCode, R.RegionID, R.RegionCode
        FROM [dbo].[Terminal] T
            INNER JOIN [dbo].[City] C ON T.[CityID] = C.[CityID]
            INNER JOIN [dbo].[Province] P ON C.[ProvinceID] = P.[ProvinceID]
            INNER JOIN [dbo].[Region] R ON T.[RegionID] = R.[RegionID]
        WHERE T.TerminalID IN (SELECT DISTINCT OriginTerminalID
        FROM [dbo].[Lane])
    ),
    D
    AS
    (
        SELECT T.TerminalID, T.TerminalCode, P.ProvinceID, P.ProvinceCode, R.RegionID, R.RegionCode
        FROM [dbo].[Terminal] T
            INNER JOIN [dbo].[City] C ON T.[CityID] = C.[CityID]
            INNER JOIN [dbo].[Province] P ON C.[ProvinceID] = P.[ProvinceID]
            INNER JOIN [dbo].[Region] R ON T.[RegionID] = R.[RegionID]
        WHERE T.TerminalID IN (SELECT DISTINCT DestinationTerminalID
        FROM [dbo].[Lane])
    ),
    L
    AS
    (
        SELECT A.LaneID,
            O.TerminalID AS OriginTerminalID,
            O.TerminalCode AS OriginTerminalCode,
            O.ProvinceID AS OriginProvinceID,
            O.ProvinceCode AS OriginProvinceCode,
            O.RegionID AS OriginRegionID,
            O.RegionCode AS OriginRegionCode,
            D.TerminalID AS DestinationTerminalID,
            D.TerminalCode AS DestinationTerminalCode,
            D.ProvinceID AS DestinationProvinceID,
            D.ProvinceCode AS DestinationProvinceCode,
            D.RegionID AS DestinationRegionID,
            D.RegionCode AS DestinationRegionCode,
            A.SubServiceLevelID,
            A.IsHeadhaul,
            A.IsActive
        FROM [dbo].[Lane] A
            INNER JOIN O ON A.[OriginTerminalID] = O.[TerminalID]
            INNER JOIN D ON A.[DestinationTerminalID] = D.[TerminalID]
        WHERE A.[IsInactiveViewable] = 1
    )
SELECT CAST(
(SELECT *
    FROM
        (
SELECT LR.LaneRouteID as lane_route_id,
            L.OriginTerminalID AS origin_terminal_id,
            L.OriginTerminalCode AS origin_terminal_code,
            L.OriginProvinceID AS origin_province_id,
            L.OriginProvinceCode AS origin_province_code,
            L.OriginRegionID AS origin_region_id,
            L.OriginRegionCode AS origin_region_code,
            L.DestinationTerminalID AS destination_terminal_id,
            L.DestinationTerminalCode AS destination_terminal_code,
            L.DestinationProvinceID AS destination_province_id,
            L.DestinationProvinceCode AS destination_province_code,
            L.DestinationRegionID AS destination_region_id,
            L.DestinationRegionCode AS destination_region_code,
            SSL.SubServiceLevelID as sub_service_level_id,
            SSL.SubServiceLevelCode as sub_service_level_code,
            L.LaneID as lane_id,
            L.IsActive as is_active,
            L.IsHeadhaul as is_headhaul,
            LRH.UpdatedOn as updated_on
        FROM L
            INNER JOIN [dbo].[SubServiceLevel] SSL ON L.[SubServiceLevelID] = SSL.[SubServiceLevelID]
            INNER JOIN [dbo].[ServiceLevel] SL ON SSL.[ServiceLevelID] = SL.[ServiceLevelID] AND SL.[ServiceOfferingID]={0}
            INNER JOIN [dbo].[LaneCost] LC ON L.LaneID = LC.LaneID
            LEFT OUTER JOIN [dbo].[LaneRoute] LR ON L.[LaneID] = LR.[LaneID]
            LEFT OUTER JOIN [dbo].[LaneRoute_History] LRH ON LR.[LaneRouteID] = LRH.[LaneRouteid] AND LRH.[IsLatestVersion] = 1
)  AS LaneRoute
    FOR JSON AUTO) AS VARCHAR(MAX))
 """

LANE_COSTS_REDUCED_DASHBOARD = """
WITH T AS (
    SELECT N.[TerminalID], N.[TerminalCode], P.[ProvinceID], P.[ProvinceCode], R.[RegionID], R.[RegionCode]
    FROM [dbo].[Terminal] N
        INNER JOIN [dbo].[City] C ON N.[CityID] = C.[CityID]
        INNER JOIN [dbo].[Province] P ON C.[ProvinceID] = P.[ProvinceID]
        INNER JOIN [dbo].[Region] R ON N.[RegionID] = R.[RegionID]
)
{{opening_clause}}
SELECT LC.[LaneCostID],
        L.[LaneID],
        O.[TerminalID] AS OriginTerminalID,
        O.[TerminalCode] AS OriginTerminalCode,
        O.[ProvinceID] AS OriginProvinceID,
        O.[ProvinceCode] AS OriginProvinceCode,
        O.[RegionID] AS OriginRegionID,
        O.[RegionCode] AS OriginRegionCode,
        D.[TerminalID] AS DestinationTerminalID,
        D.[TerminalCode] AS DestinationTerminalCode,
        D.[ProvinceID] AS DestinationProvinceID,
        D.[ProvinceCode] AS DestinationProvinceCode,
        D.[RegionID] AS DestinationRegionID,
        D.[RegionCode] AS DestinationRegionCode,
        SSL.[SubServiceLevelID],
        SSL.[SubServiceLevelCode],
        L.IsHeadhaul,
        LC.[MinimumCost],
        LC.[Cost],
        CASE WHEN LC.IsInactiveViewable = 0 THEN 'Deleted'
            ELSE CASE WHEN LC.IsActive = 0 THEN 'Disabled' ELSE 'Enabled' END
        END AS Status,
        LCH.[UpdatedOn]
    FROM [dbo].[LaneCost] LC
        INNER JOIN [dbo].[Lane] L ON LC.[LaneID] = L.[LaneID]
        INNER JOIN T AS O on O.TerminalID = L.OriginTerminalID
        INNER JOIN T AS D on D.TerminalID = L.DestinationTerminalID
        INNER JOIN [dbo].[SubServiceLevel] SSL ON L.[SubServiceLevelID] = SSL.[SubServiceLevelID]
        INNER JOIN [dbo].[ServiceLevel] SL ON SL.[ServiceLevelID] = SSL.[ServiceLevelID]
        INNER JOIN [dbo].[LaneCost_History] LCH ON LC.[LaneCostID] = LCH.[LaneCostID] AND LCH.[IsLatestVersion] = 1
    WHERE SL.[ServiceOfferingID] = {service_offering_id}
    {{where_clauses}}
    {{sort_clause}}
    {{page_clause}}
    {{closing_clause}}
"""

LEG_COSTS_DASHBOARD = """
WITH T AS (
    SELECT N.[TerminalID], N.[TerminalCode], P.[ProvinceID], P.[ProvinceCode], R.[RegionID], R.[RegionCode]
    FROM [dbo].[Terminal] N
        INNER JOIN [dbo].[City] C ON N.[CityID] = C.[CityID]
        INNER JOIN [dbo].[Province] P ON C.[ProvinceID] = P.[ProvinceID]
        INNER JOIN [dbo].[Region] R ON N.[RegionID] = R.[RegionID]
)
{{opening_clause}}
SELECT LC.[LegCostID],
        LC.[LaneID],
        SSL.SubServiceLevelID,
        SSL.SubServiceLevelCode,
        SM.[ServiceModeID],
        SM.[ServiceModeCode],
        O.[TerminalID] AS OriginTerminalID,
        O.[TerminalCode] AS OriginTerminalCode,
        O.[ProvinceID] AS OriginProvinceID,
        O.[ProvinceCode] AS OriginProvinceCode,
        O.[RegionID] AS OriginRegionID,
        O.[RegionCode] AS OriginRegionCode,
        D.[TerminalID] AS DestinationTerminalID,
        D.[TerminalCode] AS DestinationTerminalCode,
        D.[ProvinceID] AS DestinationProvinceID,
        D.[ProvinceCode] AS DestinationProvinceCode,
        D.[RegionID] AS DestinationRegionID,
        D.[RegionCode] AS DestinationRegionCode,
        LC.[Cost],
        LC.[IsActive],
        LC.[IsInactiveViewable],
        LCH.[UpdatedOn],
        L.IsHeadhaul,
        CASE WHEN LC.IsInactiveViewable = 0 THEN 'Deleted'
            ELSE CASE WHEN LC.IsActive = 0 THEN 'Disabled' ELSE 'Enabled' END
        END AS Status
    FROM [dbo].[Lane] L
        INNER JOIN T AS O ON L.[OriginTerminalID] = O.[TerminalID]
        INNER JOIN T AS D ON L.[DestinationTerminalID] = D.[TerminalID]
        INNER JOIN [dbo].[SubServiceLevel] SSL ON L.[SubServiceLevelID] = SSL.[SubServiceLevelID]
        INNER JOIN [dbo].[ServiceLevel] SL ON SL.[ServiceLevelID] = SSL.[ServiceLevelID]
        INNER JOIN [dbo].[LegCost] LC ON LC.[LaneID] = L.[LaneID]
        INNER JOIN [dbo].[LegCost_History] LCH ON LC.[LegCostID] = LCH.[LegCostID] AND LCH.[IsLatestVersion] = 1
        INNER JOIN [dbo].[ServiceMode] SM ON LC.[ServiceModeID] = SM.[ServiceModeID]
        WHERE SL.[ServiceOfferingID] = {service_offering_id}
        {{where_clauses}}
        {{sort_clause}}
        {{page_clause}}
        {{closing_clause}}
 """

WEIGHT_BREAK_HEADERS_DASHBOARD = """
SELECT CAST(
(SELECT *
FROM
(SELECT WBH.[WeightBreakHeaderID] as weight_break_header_id,
        WBH.[WeightBreakHeaderName] as weight_break_header_name,
        WBH.[ServiceLevelID] as service_level_id,
        SL.[ServiceLevelCode] as service_level_code,
        WBH.[UnitFactor] as unit_factor,
        WBH.[AsRating] as as_rating_allowed,
        WBH.[HasMin] as has_min,
        WBH.[HasMax] as has_max,
        WBH.[Levels] as levels,
        WBH.[MaximumValue] as maximum_value,
        WBH.[BaseRate] as base_rate,
        U.[UnitID] as unit_id,
        U.[UnitType] as unit_type,
        U.[UnitSymbol] as unit_symbol,
        U.[UnitName] as unit_name,
        WBH.[IsActive] as is_active,
        WBHH.[UpdatedOn] as updated_on
    FROM [dbo].[WeightBreakHeader] as WBH
        INNER JOIN [dbo].ServiceLevel SL ON SL.ServiceLevelID = WBH.ServiceLevelID
        INNER JOIN [dbo].Unit U ON WBH.[UnitID] = U.[UnitID]
        INNER JOIN [dbo].WeightBreakHeader_History WBHH ON WBH.[WeightBreakHeaderID] = WBHH.[WeightBreakHeaderID] AND WBHH.[IsLatestVersion] = 1
    WHERE SL.[ServiceOfferingID] = {0}
        AND WBH.IsInactiveViewable = 1
) AS WeightBreakHeader
FOR JSON AUTO) AS VARCHAR(MAX))
"""

WEIGHT_BREAK_HEADERS_LEVEL = """
SELECT CAST(
(SELECT *
FROM
(SELECT WBH.[WeightBreakHeaderID] as weight_break_header_id,
        WBH.[WeightBreakHeaderName] as weight_break_header_name,
        WBH.[ServiceLevelID] as service_level_id,
        SL.[ServiceLevelCode] as service_level_code,
        WBH.[UnitFactor] as unit_factor,
        WBH.[AsRating] as as_rating_allowed,
        WBH.[HasMin] as has_min,
        WBH.[HasMax] as has_max,
        WBH.[Levels] as levels,
        WBH.[MaximumValue] as maximum_value,
        WBH.[BaseRate] as base_rate,
        U.[UnitID] as unit_id,
        U.[UnitType] as unit_type,
        U.[UnitSymbol] as unit_symbol,
        U.[UnitName] as unit_name,
        WBH.[IsActive] as is_active,
        WBHH.[UpdatedOn] as updated_on
    FROM [dbo].[WeightBreakHeader] as WBH
        INNER JOIN [dbo].ServiceLevel SL ON SL.ServiceLevelID = WBH.ServiceLevelID
        INNER JOIN [dbo].Unit U ON WBH.[UnitID] = U.[UnitID]
        INNER JOIN [dbo].WeightBreakHeader_History WBHH ON WBH.[WeightBreakHeaderID] = WBHH.[WeightBreakHeaderID] AND WBHH.[IsLatestVersion] = 1
    WHERE SL.[ServiceLevelID] = {0}
        AND WBH.IsInactiveViewable = 1
) AS WeightBreakHeader
FOR JSON AUTO) AS VARCHAR(MAX))
"""

LEGS_FOR_ROUTES = """ WITH
     T
     AS
     (
         SELECT N.[TerminalID], N.[TerminalCode], P.[ProvinceID], P.[ProvinceCode], R.[RegionID], R.[RegionCode]
         FROM [dbo].[Terminal] N
             INNER JOIN [dbo].[City] C ON N.[CityID] = C.[CityID]
             INNER JOIN [dbo].[Province] P ON C.[ProvinceID] = P.[ProvinceID]
             INNER JOIN [dbo].[Region] R ON N.[RegionID] = R.[RegionID]
     )
SELECT CAST(
    (SELECT *
        FROM
        (
            SELECT L.[LaneID] AS lane_id,
                O.[TerminalID] AS origin_terminal_id,
                O.[TerminalCode] AS origin_terminal_code,
                D.[TerminalID] AS destination_terminal_id,
                D.[TerminalCode] AS destination_terminal_code,
                SM.[ServiceModeID] AS service_mode_id,
                SM.[ServiceModeCode] AS service_mode_code,
                LC.[Cost] as cost,
                L.[IsActive] AS is_active
            FROM [dbo].[LegCost] LC
                INNER JOIN [dbo].[Lane] L ON LC.[LaneID] = L.[LaneID]
                INNER JOIN T AS O ON L.[OriginTerminalID] = O.[TerminalID]
                INNER JOIN T AS D ON L.[DestinationTerminalID] = D.[TerminalID]
                INNER JOIN [dbo].[ServiceMode] SM ON LC.[ServiceModeID] = SM.[ServiceModeID]
            WHERE
                L.[OriginTerminalID] = {0}
                AND L.[ServiceLevelID] = {1}
                AND L.[IsInactiveViewable] = 1
        ) AS LaneCost
    FOR JSON AUTO)
AS VARCHAR(MAX))
"""

LANES_DESTINATION_TERMINALS = """
    SELECT CAST(
    (
        select distinct
            T.TerminalID terminal_id,
            T.TerminalCode terminal_code,
            T.TerminalName terminal_name
        from LaneCost LC
        inner join Lane L
        on L.LaneID = LC.LaneID
        inner join Terminal T
        on T.TerminalID = L.DestinationTerminalID
        where L.ServiceLevelID = {0}
		and L.OriginTerminalID = {1}
        and LC.IsInactiveViewable = 1
    FOR JSON AUTO) AS VARCHAR(MAX))
"""

ACCOUNT_SEARCH_BY_NAME = """
	WITH P AS 
	(SELECT T.ParentAccountID AS ParentAccountID, N.AccountName AS ParentAccountName FROM dbo.Account N
	INNER JOIN dbo.AccountTree T ON T.ParentAccountID = N.AccountID)
	
	SELECT CAST((
        SELECT * FROM (
            SELECT TOP 100
                A.AccountID AS account_id,
                ISNULL(P.ParentAccountID, '') AS parent_account_id,
				ISNULL(P.ParentAccountName, '') AS parent_account_name,
                ISNULL(A.AccountNumber, '') AS account_number,
                ISNULL(A.AccountName, '') AS account_name,
				ISNULL(A.AccountAlias, '') AS account_alias,
				ISNULL(A.AddressLine1, '') AS address_line_1,
				ISNULL(A.AddressLine2, '') AS address_line_2,
				ISNULL(C.CityID, '') AS city_id,
				ISNULL(C.CityName, '') AS city_name,
				ISNULL(V.ProvinceCode, '') AS province_code,
				ISNULL(V.ProvinceName, '') AS province_name,
				ISNULL(Y.CountryCode, '') AS country_code,
				ISNULL(Y.CountryName, '') AS country_name,
				ISNULL(A.PostalCode, '') AS postal_code,
				ISNULL(A.ContactName, '') AS contact_name,
				ISNULL(A.ContactTitle, '') AS contact_title,
				ISNULL(A.Phone, '') AS phone,
				ISNULL(A.Email, '') AS email,
				ISNULL(A.Website, '') AS website
            FROM dbo.Account A
			INNER JOIN dbo.City C ON A.CityID = C.CityID
			INNER JOIN dbo.Province V ON C.ProvinceID = V.ProvinceID
            INNER JOIN dbo.Region R ON R.RegionID = V.RegionID
			INNER JOIN dbo.Country Y ON R.CountryID = Y.CountryID
            INNER JOIN dbo.AccountTree T ON A.AccountID = T.AccountID
			LEFT JOIN P ON T.ParentAccountID = P.ParentAccountID
            WHERE A.AccountName LIKE '{1}%'
			AND A.AccountID NOT IN
			    (SELECT DISTINCT AccountID FROM dbo.Customer C WHERE AccountID IS NOT NULL AND C.ServiceLevelID = {0})
            ORDER BY A.AccountName
        ) AS C FOR JSON AUTO)
    AS VARCHAR(MAX))
"""


SERVICE_POINT_SEARCH_BY_NAME = """
    SELECT CAST((
        SELECT * FROM (
            SELECT TOP 100
                SP.ServicePointID AS service_point_id,
                SP.ServicePointName + ', ' + P.ProvinceCode AS service_point_name,
                P.ProvinceID AS province_id
            FROM dbo.ServicePoint SP
            INNER JOIN dbo.Province P ON SP.ProvinceID = P.ProvinceID
            INNER JOIN dbo.TerminalServicePoint TSP ON SP.ServicePointID = TSP.ServicePointID
            INNER JOIN dbo.TerminalCost TC ON TSP.TerminalID = TC.TerminalID
            WHERE TC.ServiceOfferingID = {0}
                AND SP.ServicePointName LIKE '{1}%'
            ORDER BY SP.ServicePointName
        ) AS C FOR JSON AUTO)
    AS VARCHAR(MAX))
"""

CITY_SEARCH_BY_NAME = """
    SELECT CAST((
        SELECT * FROM (
            SELECT TOP 100 *
            FROM dbo.City
            WHERE ProvinceID = {0}
                AND CityName LIKE '{1}%'
            ORDER BY CityName
        ) AS C FOR JSON AUTO)
    AS VARCHAR(MAX))
"""

TERMINAL_SERVICE_POINT_DASHBOARD = """ 
SELECT CAST(
    (SELECT *
    FROM
    (
    SELECT TSP.TerminalServicePointID AS terminal_service_point_id,
        TSP.TerminalID AS terminal_id,
        T.TerminalCode AS terminal_code,
        TSP.ServicePointID AS service_point_id,
        SP.ServicePointName AS service_point_name,
        SPP.ProvinceCode AS service_point_province_code, 
        SP.BasingPointID AS base_service_point_id,
        BP.BasingPointName AS base_service_point_name,
        BPP.ProvinceCode AS base_service_point_province_code,
        TSP.ExtraMiles AS extra_miles,
        TSP.IsActive AS is_active,
        TSPH.UpdatedOn AS updated_on
    FROM dbo.TerminalServicePoint TSP
    INNER JOIN dbo.Terminal AS T ON TSP.TerminalID = T.TerminalID
    INNER JOIN dbo.TerminalServicePoint_History TSPH ON TSP.TerminalServicePointID = TSPH.TerminalServicePointID AND TSPH.IsLatestVersion = 1
    INNER JOIN dbo.ServicePoint SP ON TSP.ServicePointID = SP.ServicePointID
    INNER JOIN dbo.Province SPP ON SP.ProvinceID = SPP.ProvinceID
    LEFT JOIN dbo.BasingPoint BP ON SP.BasingPointID = BP.BasingPointID
    LEFT JOIN dbo.Province BPP ON BP.ProvinceID = BPP.ProvinceID
    WHERE TSP.IsInactiveViewable = 1) AS ExtraMiles
    FOR JSON AUTO) AS VARCHAR(MAX))
"""
