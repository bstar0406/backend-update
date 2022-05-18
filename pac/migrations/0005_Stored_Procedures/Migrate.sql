CREATE OR ALTER PROCEDURE [dbo].[Migrate]

AS

DECLARE	@return_value int
EXEC	@return_value = [dbo].[Delete]

/****** ServiceOffering ******/

EXEC [dbo].[ServiceOffering_Insert] 'Freight';
EXEC [dbo].[ServiceOffering_Insert] 'SameDay';

/****** CurrencyExchange ******/

DECLARE @CurrencyExchangeTableType AS CurrencyExchangeTableType; 

INSERT INTO @CurrencyExchangeTableType
(
    [CADtoUSD],
	[USDtoCAD]
)
SELECT 0.76, 1.32

EXEC [dbo].[CurrencyExchange_Insert_Bulk] @CurrencyExchangeTableType

/****** Currency ******/

DECLARE @CurrencyTableType AS CurrencyTableType;

INSERT INTO @CurrencyTableType
(
	[CurrencyName],
	[CurrencyCode]
)
SELECT 'Canadian Dollar', 'CAD'
UNION
SELECT 'US Dollar', 'USD'

EXEC [dbo].[Currency_Insert_Bulk] @CurrencyTableType

/****** Language ******/

DECLARE @LanguageTableType AS LanguageTableType;

INSERT INTO @LanguageTableType
(
	[LanguageName],
	[LanguageCode]
)
SELECT 'English', 'EN'
UNION
SELECT 'French', 'FR'

EXEC [dbo].[Language_Insert_Bulk] @LanguageTableType

/****** RequestType ******/

DECLARE @RequestTypeTableType AS RequestTypeTableType;

INSERT INTO @RequestTypeTableType
(
	[RequestTypeName],
	[ApplyToCustomerUnderReview],
	[ApplyToRevision],
	[AllowSalesCommitment]
)
--SELECT 'Add Lanes', 1, 1, 0
--UNION
SELECT 'Cost+', 0, 0, 0
UNION
SELECT 'Commitment', 0, 0, 1
UNION
SELECT 'Tender', 0, 0, 1
UNION
SELECT 'Revision', 0, 1, 0

EXEC [dbo].[RequestType_Insert_Bulk] @RequestTypeTableType

/****** RequestStatusType ******/

DECLARE @Managers NVARCHAR(MAX) = '["Sales Representative", "Pricing Manager", "Sales Coordinator", "Sales Manager", "Account Owner"]';
DECLARE @ManagersPricingAnalyst NVARCHAR(MAX) = '["Sales Representative", "Pricing Manager", "Sales Coordinator", "Sales Manager", "Account Owner", "Pricing Analyst"]';
DECLARE @ManagersCreditAnalyst NVARCHAR(MAX) = '["Sales Representative", "Pricing Manager", "Sales Coordinator", "Sales Manager", "Account Owner", "Credit Analyst"]';
DECLARE @ManagersCreditManager NVARCHAR(MAX) = '["Sales Representative", "Pricing Manager", "Sales Coordinator", "Sales Manager", "Account Owner", "Credit Manager", "Pricing Analyst"]';
DECLARE @ManagersPartnerCarrier NVARCHAR(MAX) = '["Sales Representative", "Pricing Manager", "Sales Coordinator", "Sales Manager", "Account Owner", "Partner Carrier", "Pricing Analyst"]';

DECLARE @RequestStatusTypeTableType RequestStatusTypeTableType
INSERT INTO @RequestStatusTypeTableType
(
	RequestStatusTypeName,
	NextRequestStatusType,
	AssignedPersona,
	Editor,
	QueuePersonas,
	IsSecondary,
	IsFinal
)
SELECT 'RRF Initiated', '["RRF Submitted", "RRF Archived", "RRF Cancelled"]', 'Sales Representative', 'Sales Representative', @Managers, 0, 0
UNION
SELECT 'RRF Submitted', '["Assign Pricing Analyst", "Pending Cost+ Approval", "Assign Credit Analyst"]', 'Sales Representative', 'System Calculator', @Managers, 0, 0
UNION 
SELECT 'Assign Credit Analyst', '["Pending Credit Approval"]', 'System Calculator', 'System Calculator', @ManagersCreditAnalyst, 0, 0
UNION
SELECT 'Pending Credit Approval', '["Credit Approved", "Credit Declined"]', 'Credit Analyst', 'Credit Analyst', @ManagersCreditAnalyst, 0, 0
UNION
SELECT 'Credit Approved', '["Assign Pricing Analyst", "Pending Cost+ Approval"]', 'System Calculator', 'System Calculator', @Managers, 0, 0
UNION
SELECT 'Credit Declined', '["RRF Archived", "RRF Cancelled"]', 'Sales Representative', 'Sales Representative', @Managers, 0, 0
UNION
SELECT 'RRF Archived', '["RRF Reactivated", "RRF Cancelled"]', 'Sales Representative', 'Sales Representative', @Managers, 0, 0
UNION
SELECT 'RRF Cancelled', '[]', 'System Calculator', 'System Calculator', '[]', 0, 1
UNION
SELECT 'RRF Reactivated', '["RRF Initiated"]', 'System Calculator', 'System Calculator', @Managers, 0, 0
UNION
SELECT 'Pending Cost+ Approval', '["Cost+ Approved", "Cost+ Declined"]', 'Sales Manager', 'Sales Manager', @Managers, 0, 0
UNION
SELECT 'Cost+ Approved', '["Assign Pricing Analyst"]', 'System Calculator', 'System Calculator', @Managers, 0, 0
UNION
SELECT 'Cost+ Declined', '["RRF Archived", "RRF Cancelled", "RRF Submitted"]', 'Sales Representative', 'Sales Representative', @Managers, 0, 0
UNION
SELECT 'Assign Pricing Analyst', '["RRF with Pricing"]', 'System Calculator', 'System Calculator', @ManagersPricingAnalyst, 0, 0
UNION
SELECT 'RRF with Pricing', '["In Analysis", "RRF with Sales"]', 'Pricing Analyst', 'Pricing Analyst', @ManagersPricingAnalyst, 0, 0
UNION
SELECT 'RRF with Sales', '["RRF Archived", "RRF Cancelled", "RRF Submitted"]', 'Sales Representative', 'Sales Representative', @ManagersPricingAnalyst, 0, 0
UNION
SELECT 'In Analysis', '["Reassign to SCS", "With Pricing Engine", "Pending Sales Approval", "Pending Partner Carrier Approval", "Submitted to Publish", "RRF with Sales", "RRF Archived", "RRF Cancelled"]', 'Pricing Analyst', 'Pricing Analyst', @ManagersPricingAnalyst, 0, 0
UNION 
SELECT 'Reassign to SCS', '["RRF with Pricing"]', 'System Calculator', 'System Calculator', @ManagersPricingAnalyst, 0, 0
UNION 
SELECT 'With Pricing Engine', '["In Analysis"]', 'System Calculator', 'System Calculator', @ManagersPricingAnalyst, 0, 0
UNION 
SELECT 'Pending Sales Approval', '["Sales Approved", "Sales Declined"]', 'Sales Representative', 'System Calculator', @ManagersPricingAnalyst, 0, 0
UNION 
SELECT 'Sales Declined', '["In Analysis"]', 'Pricing Analyst', 'Pricing Analyst', @ManagersPricingAnalyst, 0, 0
UNION 
SELECT 'Sales Approved', '["In Analysis"]', 'Pricing Analyst', 'Pricing Analyst', @ManagersPricingAnalyst, 0, 0
UNION 
SELECT 'Submitted to Publish', '["Pending Publishing"]', 'System Calculator', 'System Calculator', @ManagersPricingAnalyst, 0, 0
UNION 
SELECT 'Pending Partner Carrier Approval', '["Partner Carrier Approved", "Partner Carrier Declined"]', 'Partner Carrier', 'System Calculator', @ManagersPartnerCarrier, 0, 0
UNION 
SELECT 'Partner Carrier Approved', '["In Analysis"]', 'System Calculator', 'System Calculator', @ManagersPartnerCarrier, 0, 0
UNION 
SELECT 'Partner Carrier Declined', '["In Analysis"]', 'System Calculator', 'Pricing Analyst', @ManagersPartnerCarrier, 0, 0
UNION 
SELECT 'Pending Publishing', '["Published Successfully", "Publishing Failed"]', 'System Calculator', 'System Calculator', @ManagersPricingAnalyst, 0, 0
UNION 
SELECT 'Published Successfully', '[]', 'System Calculator', 'System Calculator', @ManagersPricingAnalyst, 0, 1
UNION 
SELECT 'Publishing Failed', '["In Analysis"]', 'System Calculator', 'System Calculator', @ManagersPricingAnalyst, 0, 0
UNION 
SELECT 'Pending DRM Approval', '["DRM Approved", "DRM Declined"]', 'Sales Manager', 'N/A', @ManagersPricingAnalyst, 1, 0
UNION 
SELECT 'DRM Approved', '[]', 'System Calculator', 'N/A', @ManagersPricingAnalyst, 1, 1
UNION 
SELECT 'DRM Declined', '[]', 'System Calculator', 'N/A', @ManagersPricingAnalyst, 1, 1
UNION 
SELECT 'Pending PCR Approval', '["PCR Approved", "PCR Declined"]', 'Sales Manager', 'N/A', @ManagersPricingAnalyst, 1, 0
UNION 
SELECT 'PCR Approved', '[]', 'System Calculator', 'N/A', @ManagersPricingAnalyst, 1, 1
UNION 
SELECT 'PCR Declined', '[]', 'System Calculator', 'N/A', @ManagersPricingAnalyst, 1, 1
UNION 
SELECT 'Pending PC Approval', '["PC Approved", "PC Declined"]', 'Sales Manager', 'N/A', @ManagersPricingAnalyst, 1, 0
UNION 
SELECT 'PC Approved', '[]', 'System Calculator', 'N/A', @ManagersPricingAnalyst, 1, 1
UNION 
SELECT 'PC Declined', '[]', 'System Calculator', 'N/A', @ManagersPricingAnalyst, 1, 1
UNION 
SELECT 'Pending EPT Approval', '["EPT Approved", "EPT Declined"]', 'Credit Manager', 'N/A', @ManagersCreditManager, 1, 0
UNION 
SELECT 'EPT Approved', '[]', 'System Calculator', 'N/A', @ManagersPricingAnalyst, 1, 1
UNION 
SELECT 'EPT Declined', '[]', 'System Calculator', 'N/A', @ManagersPricingAnalyst, 1, 1

EXEC [dbo].[RequestStatusType_Insert_Bulk] @RequestStatusTypeTableType

/****** FreightClass ******/

DECLARE @FreightClassTableType AS FreightClassTableType;

INSERT INTO @FreightClassTableType
(
	[FreightClassName]
)
SELECT '50'
UNION
SELECT '55'
UNION
SELECT '60'
UNION
SELECT '65'
UNION
SELECT '70'
UNION
SELECT '77.5'
UNION
SELECT '85'
UNION
SELECT '92.5'
UNION
SELECT '100'
UNION
SELECT '110'
UNION
SELECT '125'
UNION
SELECT '150'
UNION
SELECT '175'
UNION
SELECT '200'
UNION
SELECT '250'
UNION
SELECT '300'
UNION
SELECT '400'
UNION
SELECT '500'

EXEC [dbo].[FreightClass_Insert_Bulk] @FreightClassTableType

--/****** Persona ******/

DECLARE @PersonaTableType PersonaTableType;

INSERT INTO @PersonaTableType ([PersonaName])
SELECT 'Admin'
UNION
SELECT 'Credit Analyst'
UNION
SELECT 'Credit Manager'
UNION
SELECT 'Partner Carrier'
UNION
SELECT 'Pricing Analyst'
UNION
SELECT 'Pricing Manager'
UNION
SELECT 'Review Analyst'
UNION
SELECT 'Sales Coordinator'
UNION
SELECT 'Sales Manager'
UNION
SELECT 'Sales Representative'
UNION
SELECT 'Spot Quote Analyst'
UNION
SELECT 'VP of Pricing'

EXEC [dbo].[Persona_Insert_Bulk] @PersonaTableType

/****** User ******/

DECLARE @UserTableType AS UserTableType;

INSERT INTO @UserTableType
(
	[UserName],
	[UserEmail],
	[PersonaName],
	[CanProcessSCS],
	[CanProcessRequests],
	[CanProcessReviews],
	[UserManagerEmail]
)

SELECT 'Christopher Oliphant', 'christopher.oliphant@dayandrossinc.ca','Sales Representative', 1, 1, 1, 'kyle.wong@dayandrossinc.ca'
UNION
SELECT 'Sabhya Sachdeva', 'sabhya.sachdeva@dayandrossinc.ca', 'Pricing Analyst', 1, 1, 1, 'alex.little@dayandrossinc.ca'
UNION
SELECT 'Mohammad Khalil', 'mohammad.khalil@dayandrossinc.ca', 'Pricing Analyst', 1, 1, 1, 'alex.little@dayandrossinc.ca'
UNION
SELECT 'Alex Little', 'alex.little@dayandrossinc.ca', 'Pricing Manager', 1, 1, 1, NULL
UNION
SELECT 'Ish Habib', 'ish.habib@dayandrossinc.ca','Sales Representative', 1, 1, 1, 'kyle.wong@dayandrossinc.ca'
UNION
SELECT 'Kyle Wong', 'kyle.wong@dayandrossinc.ca', 'Sales Manager', 1, 1, 1, NULL
UNION
SELECT 'CLARK, JOLENE R.', 'jrclark@dayandrossinc.ca', 'Pricing Analyst', 1, 1, 1, 'angela.villeneuve@dayandrossinc.ca'
UNION
SELECT 'VILLENEUVE, ANGELA D.', 'angela.villeneuve@dayandrossinc.ca', 'Pricing Manager', 1, 1, 1, NULL
UNION
SELECT 'WILSON, LEEANN', 'leeann.wilson@dayross.com','Pricing Manager', 1, 1, 1, NULL
UNION
SELECT 'CARVELL, FRANK B.', 'FBCARVEL@DAYANDROSSINC.CA','Pricing Manager', 1, 1, 1, NULL
UNION
SELECT 'CRANN, TONY', 'TRCRANN@DAYANDROSSINC.CA','Pricing Manager', 1, 1, 1, NULL
UNION
SELECT PersonaName + ' temp',
	PersonaName + '@dayandrossinc.ca',
	PersonaName,
	 1, 1, 1,
	 CASE WHEN PersonaName = 'Credit Analyst' THEN 'Credit Manager@dayandrossinc.ca'
		WHEN PersonaName = 'Pricing Analyst' THEN 'Pricing Manager@dayandrossinc.ca'
		WHEN PersonaName = 'Review Analyst' THEN 'Pricing Manager@dayandrossinc.ca'
		WHEN PersonaName = 'Review Analyst' THEN 'Pricing Manager@dayandrossinc.ca'
		WHEN PersonaName = 'Sales Coordinator' THEN 'Sales Manager@dayandrossinc.ca'
		WHEN PersonaName = 'Sales Representative' THEN 'Sales Manager@dayandrossinc.ca'
		WHEN PersonaName = 'Spot Quote Analyst' THEN 'Pricing Manager@dayandrossinc.ca'
		ELSE NULL END AS [UserManagerEmail]
FROM dbo.Persona

EXEC [dbo].[User_Insert_Bulk] @UserTableType


/****** Country ******/

DECLARE @CountryTableType AS CountryTableType;

INSERT INTO @CountryTableType
(
	[CountryName],
	[CountryCode]
)
SELECT DISTINCT [CountryName],
	[CountryCode] 
FROM [staging].[Country] 
WHERE [CountryCode] IN ('CA', 'US')

EXEC [dbo].[Country_Insert_Bulk] @CountryTableType

/****** Region ******/

DECLARE @RegionTableType AS RegionTableType;

INSERT INTO @RegionTableType
(
	[RegionName],
	[RegionCode],
	[CountryCode]
)
SELECT DISTINCT [RegionName],
	[RegionCode],
	[CountryCode]
FROM [staging].[Region] 

EXEC [dbo].[Region_Insert_Bulk] @RegionTableType

/****** Province ******/

DECLARE @ProvinceTableType AS ProvinceTableType;

INSERT INTO @ProvinceTableType
(
	[ProvinceName],
	[ProvinceCode],
	[CountryCode],
	[RegionCode]
)
SELECT DISTINCT [ProvinceName],
	[ProvinceCode],
	[CountryCode],
	[RegionCode]
FROM [staging].[Province]

EXEC [dbo].[Province_Insert_Bulk] @ProvinceTableType

/****** City ******/

DECLARE @CityTableType AS CityTableType;

INSERT INTO @CityTableType
(
	[CityName],
	[ProvinceCode],
	[CountryCode]
)
SELECT DISTINCT [CityName],
	[ProvinceCode],
	[CountryCode]
FROM [staging].[City]

EXEC [dbo].[City_Insert_Bulk] @CityTableType

/****** Terminal ******/

UPDATE staging.Terminal
SET RegionCode = 'ONT'
WHERE staging.Terminal.RegionCode IN ('INT', 'TOR')

DECLARE @TerminalTableType AS TerminalTableType;

INSERT INTO @TerminalTableType
(
	[TerminalName],
	[TerminalCode],
	[CityName],
	[ProvinceCode],
	[CountryCode],
	[RegionCode]
)
SELECT DISTINCT [TerminalName],
	[TerminalCode],
	[CityName],
	[ProvinceCode],
	[CountryCode],
	[RegionCode]
FROM [staging].[Terminal]

EXEC [dbo].[Terminal_Insert_Bulk] @TerminalTableType

/****** TerminalCostWeightBreakLevel ******/

DECLARE @TerminalCostWeightBreakLevelTableType AS CostWeightBreakLevelTableType;

INSERT INTO @TerminalCostWeightBreakLevelTableType
(
	[ServiceOfferingName],
    [WeightBreakLevelName],
    [WeightBreakLowerBound]
)
SELECT DISTINCT [ServiceOfferingName],
	[LevelName],
	[LevelLowerBound]
FROM [staging].[TerminalCostFreight]

EXEC [dbo].[TerminalCostWeightBreakLevel_Insert_Bulk] @TerminalCostWeightBreakLevelTableType

/****** TerminalCost ******/

DECLARE @TerminalCostTableType AS TerminalCostTableType;

INSERT INTO @TerminalCostTableType
(
	[ServiceOfferingName],
	[TerminalCode],
	[Cost],
	[IsIntraRegionMovementEnabled],
	[IntraRegionMovementFactor]
)
SELECT DISTINCT C.[ServiceOfferingName],
	C.[TerminalCode],
	(SELECT C.Cost AS [CostComponents.CostByWeightBreak], C.[CrossDockCost] AS [CostComponents.CrossDockCost]  FOR JSON PATH, WITHOUT_ARRAY_WRAPPER) AS Cost,
	C.[IsIntraRegionMovementEnabled],
	C.[IntraRegionMovementFactor]
FROM 
(SELECT DISTINCT 
  TCF.[ServiceOfferingName],
  TCF.TerminalCode, '{' +
  STUFF((
    SELECT ', ' + '"' +  CAST(A.[WeightBreakLevelID] AS VARCHAR(MAX)) + '"' + ':' + CAST(C.Cost AS VARCHAR(MAX)) 
    FROM dbo.TerminalCostWeightBreakLevel A
	INNER JOIN dbo.ServiceOffering B ON A.ServiceOfferingID = B.ServiceOfferingID
	INNER JOIN staging.TerminalCostFreight C ON A.WeightBreakLowerBound = C.LevelLowerBound AND B.ServiceOfferingName = C.ServiceOfferingName
    WHERE (A.[ServiceOfferingID] = TCWB.[ServiceOfferingID] AND C.TerminalCode = TCF.TerminalCode) 
    FOR XML PATH(''),TYPE).value('(./text())[1]','VARCHAR(MAX)')
  ,1,2,'') + '}' AS Cost,
  	(CASE WHEN TCF.[IsIntraRegionMovementEnabled] = 1 THEN 1 ELSE 0 END) AS IsIntraRegionMovementEnabled,
	(CASE WHEN TCF.[IsIntraRegionMovementEnabled] = 1 THEN 2 ELSE 1 END) AS IntraRegionMovementFactor,
	'' AS CrossDockCost
FROM dbo.TerminalCostWeightBreakLevel TCWB
INNER JOIN dbo.ServiceOffering SO ON TCWB.ServiceOfferingID = SO.ServiceOfferingID
INNER JOIN staging.TerminalCostFreight TCF ON TCWB.WeightBreakLowerBound = LevelLowerBound AND SO.ServiceOfferingName = TCF.ServiceOfferingName
GROUP BY TCWB.[ServiceOfferingID], TCF.[ServiceOfferingName], TCF.TerminalCode, TCF.[IsIntraRegionMovementEnabled]) AS C
INNER JOIN [dbo].[Terminal] T ON C.[TerminalCode] = T.[TerminalCode]
UNION
SELECT DISTINCT J.[ServiceOfferingName], 
	J.[TerminalCode], 
	(SELECT '' AS [CostComponents.CostByWeightBreak], (SELECT CrossDockCostPerWeightUnit, CrossDockCostMin, CrossDockCostMax FROM [staging].[TerminalCostSameday] TC WHERE TC.TerminalCode=J.TerminalCode FOR JSON AUTO, WITHOUT_ARRAY_WRAPPER) AS [CostComponents.CrossDockCost]  FOR JSON PATH, WITHOUT_ARRAY_WRAPPER) AS Cost,
	0 AS IsIntraRegionMovementEnabled,
	1 AS IntraRegionMovementFactor
FROM [staging].[TerminalCostSameday] J
INNER JOIN [dbo].[Terminal] T ON J.[TerminalCode] = T.[TerminalCode]

EXEC [dbo].[TerminalCost_Insert_Bulk] @TerminalCostTableType

/****** ServiceMode ******/

DECLARE @ServiceModeTableType AS ServiceModeTableType;

INSERT INTO @ServiceModeTableType
(
	[ServiceOfferingName],
	[ServiceModeName],
    [ServiceModeCode]
)
SELECT DISTINCT SM.[ServiceOfferingName],
	SM.[ServiceModeName],
	SM.[ServiceModeCode]
FROM [staging].[ServiceMode] SM

EXEC [dbo].[ServiceMode_Insert_Bulk] @ServiceModeTableType

/****** ServiceLevel ******/

DECLARE @ServiceLevelTableType AS ServiceLevelTableType;

INSERT INTO @ServiceLevelTableType
(
	[ServiceOfferingName],
	[ServiceLevelName],
    [ServiceLevelCode]
)
SELECT DISTINCT SL.[ServiceOfferingName],
	SL.[ServiceLevelName],
	SL.[ServiceLevelCode]
FROM [staging].[ServiceLevel] SL

EXEC [dbo].[ServiceLevel_Insert_Bulk] @ServiceLevelTableType

/****** SpeedSheet ******/

DECLARE @SpeedSheetTableType AS SpeedSheetTableType; 

INSERT INTO @SpeedSheetTableType
(
	[ServiceOfferingName],
    [Margin],
	[MinDensity],
    [MaxDensity]
)
SELECT 'Freight', 40, 6, 78
UNION
SELECT 'SameDay', 32, 6.2, 75.8

EXEC [dbo].[SpeedSheet_Insert_Bulk] @SpeedSheetTableType

/****** Unit ******/

DECLARE @UnitTableType AS UnitTableType; 

INSERT INTO @UnitTableType
(
    [UnitSymbol],
	[UnitName],
	[UnitType]
)
SELECT 'CAD', 'Canadian Dollars', 'Y'
UNION
SELECT 'CCWT', 'Hundredweight', 'W'
UNION
SELECT 'Day', 'Day', 'T'
UNION
SELECT 'FLT', 'Flat', 'T'
UNION
SELECT 'FT', 'Foot', 'L'
UNION
SELECT 'FT3', 'Cubic Feet', 'C'
UNION
SELECT 'KM', 'Kilometer', 'D'
UNION
SELECT 'LB', 'LB', 'W'
UNION
SELECT 'M', 'Meter', 'L'
UNION
SELECT 'M3', 'Cubic Meter', 'C'
UNION
SELECT 'PC', 'Piece', 'I'
UNION
SELECT 'PLT', 'Pallets', 'P'

EXEC [dbo].[Unit_Insert_Bulk] @UnitTableType

/****** WeightBreakHeader ******/

DECLARE @WeightBreakHeaderTableType AS WeightBreakHeaderTableType; 

INSERT INTO @WeightBreakHeaderTableType
(
	[ServiceOfferingName],
    [WeightBreakHeaderName],
    [UnitFactor],
    [MaximumValue],
    [AsRating],
	[HasMin],
	[HasMax],
    [BaseRate],
    [Levels],
    [ServiceLevelCode],
    [UnitSymbol]
)

SELECT SO.ServiceOfferingName,
	'CCWT Weigh Break Header',
	100,
	45000,
	1,
	1,
	1,
	1,
	'[{"LevelLowerBound":0,"LevelName":"CCWT 0","IsMin":1, "IsMax":0},{"LevelLowerBound":1000,"LevelName":"CCWT 1000","IsMin":0, "IsMax":0}, {"LevelLowerBound":5000,"LevelName":"CCWT 5000","IsMin":0, "IsMax":0}, {"LevelLowerBound":10000,"LevelName":"CCWT 10000","IsMin":0, "IsMax":0}, {"LevelLowerBound":20000,"LevelName":"CCWT 20000","IsMin":0, "IsMax":0}, {"LevelLowerBound":30000,"LevelName":"CCWT 30000","IsMin":0, "IsMax":0}, {"LevelLowerBound":45000,"LevelName":"CCWT 45000","IsMin":0, "IsMax":1}]', 
	SL.ServiceLevelCode,
	U.UnitSymbol
FROM dbo.Unit U,
dbo.ServiceLevel SL
INNER JOIN dbo.ServiceOffering SO ON SL.ServiceOfferingID = SO.ServiceOfferingID
WHERE U.UnitName Like 'Hundredweight'

EXEC [dbo].[WeightBreakHeader_Insert_Bulk] @WeightBreakHeaderTableType 

/****** RequestSectionLanePointType ******/

DECLARE @RequestSectionLanePointTypeTableType AS RequestSectionLanePointTypeTableType; 

INSERT INTO @RequestSectionLanePointTypeTableType
(
	[ServiceOfferingName],
    [IsDensityPricing],
    [RequestSectionLanePointTypeName],
    [LocationHierarchy],
	[IsGroupType],
	[IsPointType]
)

SELECT 'Freight', 1, 'Postal Code', 7, 0, 1
UNION
SELECT 'Freight', 1, 'Service Point', 6, 0, 1
UNION
SELECT 'Freight', 1, 'Basing Point', 5, 0, 1
UNION
SELECT 'Freight', 1, 'Terminal', 4, 0, 1
UNION
SELECT 'Freight', 1, 'Province', 3, 1, 0
UNION
SELECT 'Freight', 1, 'Region', 2, 1, 0
UNION
SELECT 'Freight', 1, 'Country', 1, 1, 0
UNION
SELECT 'SameDay', 1, 'Postal Code', 7, 0, 1
UNION
SELECT 'SameDay', 1, 'Service Point', 6, 0, 1
UNION
SELECT 'SameDay', 1, 'Zone', 5, 0, 1 
UNION
SELECT 'SameDay', 1, 'Terminal', 4, 0, 1
UNION
SELECT 'SameDay', 1, 'Province', 3, 1, 0
UNION
SELECT 'SameDay', 1, 'Region', 2, 1, 0
UNION
SELECT 'SameDay', 1, 'Country', 1, 1, 0
UNION
SELECT 'Freight', 0, 'Postal Code', 7, 0, 1
UNION
SELECT 'Freight', 0, 'Service Point', 6, 0, 1
UNION
SELECT 'Freight', 0, 'Basing Point', 5, 0, 1
UNION
SELECT 'Freight', 0, 'Terminal', 4, 0, 1
UNION
SELECT 'Freight', 0, 'Province', 3, 1, 1
UNION
SELECT 'Freight', 0, 'Region', 2, 1, 1
UNION
SELECT 'Freight', 0, 'Country', 1, 1, 1
UNION
SELECT 'SameDay', 0, 'Postal Code', 7, 0, 1
UNION
SELECT 'SameDay', 0, 'Service Point', 6, 0, 1
UNION
SELECT 'SameDay', 0, 'Zone', 5, 0, 1 
UNION
SELECT 'SameDay', 0, 'Terminal', 4, 0, 1
UNION
SELECT 'SameDay', 0, 'Province', 3, 1, 1 
UNION
SELECT 'SameDay', 0, 'Region', 2, 1, 1
UNION
SELECT 'SameDay', 0, 'Country', 1, 1, 1

EXEC [dbo].[RequestSectionLanePointType_Insert_Bulk] @RequestSectionLanePointTypeTableType

/****** EquipmentType ******/

DECLARE @EquipmentTypeTableType AS EquipmentTypeTableType; 

INSERT INTO @EquipmentTypeTableType
(
	[EquipmentTypeCode],
	[EquipmentTypeName]
)
SELECT 'CH', 'CHASSIS'
UNION
SELECT 'CN', 'CONTAINER'
UNION
SELECT 'CO', 'CONVERTER'
UNION
SELECT 'CR', 'CRANE'
UNION
SELECT 'CU', 'CUBE VAN'
UNION
SELECT 'CV', 'CARGO VAN'
UNION
SELECT 'DC', 'DAY CAB'
UNION
SELECT 'FT', 'FLAT BED TRAILER'
UNION
SELECT 'GN', 'GENSET'
UNION
SELECT 'PJ', 'ELECTRIC PALLET JACK'
UNION
SELECT 'SC', 'SLEEPER CAB'
UNION
SELECT 'SD', 'SINGLE DROP TRAILER'
UNION
SELECT 'ST', 'STRAIGHT TRUCK / 5 TONNE'
UNION
SELECT 'SV', 'SUPER VAN'
UNION
SELECT 'TA', 'TRAILER - HEATED/INSUL./VENT.'
UNION
SELECT 'TF', 'TRAILER - DRY FREIGHT'
UNION
SELECT 'TR', 'PICKUP TRUCK / HALF TONNE'
UNION
SELECT 'TW', 'TRAILER - REFRIGERATED'

EXEC [dbo].[EquipmentType_Insert_Bulk] @EquipmentTypeTableType

/****** RateBase ******/

DECLARE @RateBaseTableType AS RateBaseTableType; 

INSERT INTO @RateBaseTableType
(
	[RateBaseName]
)
SELECT 'FCAC'
UNION
SELECT 'CanRate'

EXEC [dbo].[RateBase_Insert_Bulk] @RateBaseTableType

/****** SubServiceLevel ******/

DECLARE @SubServiceLevelTableType AS SubServiceLevelTableType; 

INSERT INTO @SubServiceLevelTableType
(
	[ServiceLevelID],
	[SubServiceLevelName],
	[SubServiceLevelCode]
)
SELECT SL.ServiceLevelID, SL.ServiceLevelName, SL.ServiceLevelCode
FROM dbo.ServiceLevel SL

EXEC [dbo].[SubServiceLevel_Insert_Bulk] @SubServiceLevelTableType

/****** UserServiceLevel ******/ 

DECLARE @UserServiceLevelTableType UserServiceLevelTableType;
INSERT INTO @UserServiceLevelTableType
(
	[UserID],
	[ServiceLevelID]
)
SELECT U.[UserID], SL.[ServiceLevelID]
FROM dbo.[User] U
INNER JOIN dbo.[User_History] UH ON U.[UserID] = UH.[UserID] AND UH.IsLatestVersion = 1
CROSS JOIN dbo.ServiceLevel SL

EXEC dbo.UserServiceLevel_Insert_Bulk @UserServiceLevelTableType

/****** Account ******/

DECLARE @AccountTableType AS AccountTableType;

INSERT INTO @AccountTableType
(
    [AccountNumber],
	[AccountName],
	[AddressLine1],
    [AddressLine2],
	[CityID],
    [PostalCode],
	[Phone],
    [ContactName],
    [ContactTitle],
    [Email],
    [Website]
)
SELECT A.[AccountNumber]L,
	A.[AccountName],
	A.[AddressLine1],
    A.[AddressLine2],
	C.[CityID],
    A.[PostalCode],
	A.[Phone],
    A.[ContactName],
    A.[ContactTitle],
    A.[Email],
    A.[Website]
FROM staging.Account A
INNER JOIN dbo.City C ON A.CityName = C.CityName
INNER JOIN dbo.Province P ON C.ProvinceID = P.ProvinceID AND A.ProvinceCode = P.ProvinceCode

EXEC [dbo].[Account_Insert_Bulk] @AccountTableType

/****** AccountTree ******/

DECLARE @AccountTreeTableType AS AccountTreeTableType;

INSERT INTO @AccountTreeTableType
(
	[AccountID]
)
SELECT [AccountID]
FROM dbo.Account

EXEC [dbo].[AccountTree_Insert_Bulk] @AccountTreeTableType

/****** Basing Points ******/

UPDATE staging.LocationTree
SET BaseServicePointName = BaseServicePointName + ' ' + ProvinceCode
WHERE staging.LocationTree.BaseServicePointName IN
(
SELECT BaseServicePointName
FROM staging.LocationTree
WHERE BaseServicePointName IS NOT NULL
GROUP BY BaseServicePointName
HAVING COUNT (DISTINCT ProvinceCode) > 1
)

DECLARE @BasingPointTableType BasingPointTableType

INSERT INTO @BasingPointTableType 
(
	BasingPointName,
	ProvinceCode, 
	CountryCode
)
SELECT DISTINCT BaseServicePointName,
	ProvinceCode,
	CountryCode
FROM staging.LocationTree
WHERE BaseServicePointName IS NOT NULL

EXEC dbo.BasingPoint_Insert_Bulk @BasingPointTableType

/****** ServicePoint ******/

DECLARE @ServicePointTableType AS ServicePointTableType; 

INSERT INTO @ServicePointTableType
(
	[ServicePointName],
	[BasingPointName],
	[ProvinceCode]
)
SELECT DISTINCT [ServicePointName], 
	[BaseServicePointName], 
	[ProvinceCode]
FROM [staging].[LocationTree]
WHERE [TerminalCode] IN (SELECT [TerminalCode] FROM dbo.Terminal)
AND ([ServicePointName] + [ProvinceCode]) NOT IN
(SELECT ServicePointName + ProvinceCode
FROM staging.LocationTree
WHERE [TerminalCode] IN (SELECT [TerminalCode] FROM dbo.Terminal)
GROUP BY ServicePointName, ProvinceCode
HAVING COUNT(DISTINCT TerminalCode) > 1)

EXEC [dbo].[ServicePoint_Insert_Bulk] @ServicePointTableType

/****** TerminalServicePoint ******/

DECLARE @TerminalServicePointTableType AS TerminalServicePointTableType; 

INSERT INTO @TerminalServicePointTableType
(
	[TerminalCode],
	[ServicePointName],
	[ServicePointProvinceCode],
	[ExtraMiles]
)
SELECT DISTINCT [TerminalCode],
	[ServicePointName],
	[ProvinceCode],
	0
FROM [staging].[LocationTree]
WHERE [TerminalCode] IN (SELECT [TerminalCode] FROM dbo.Terminal)
AND ([ServicePointName] + [ProvinceCode]) NOT IN
(SELECT ServicePointName + ProvinceCode
FROM staging.LocationTree
WHERE [TerminalCode] IN (SELECT [TerminalCode] FROM dbo.Terminal)
GROUP BY ServicePointName, ProvinceCode
HAVING COUNT(DISTINCT TerminalCode) > 1)

EXEC [dbo].[TerminalServicePoint_Insert_Bulk] @TerminalServicePointTableType 

/****** PostalCode ******/

DECLARE @PostalCodeTableType AS PostalCodeTableType; 

INSERT INTO @PostalCodeTableType
(
	[PostalCodeName],
	[ServicePointName],
	[ProvinceCode]
)
SELECT DISTINCT [PostalCodeName],
	[ServicePointName],
	[ProvinceCode]
FROM [staging].[PostalCode]
WHERE ([ServicePointName] + [ProvinceCode]) IN
(SELECT SP.ServicePointName + P.ProvinceCode
FROM dbo.ServicePoint SP
INNER JOIN dbo.Province P ON SP.ProvinceID = P.ProvinceID)

EXEC [dbo].[PostalCode_Insert_Bulk] @PostalCodeTableType 

/****** Lane ******/

DECLARE @LaneTableType AS LaneTableType;

DECLARE @TempLaneTableType table 
( 
	[ServiceOfferingName]      NVARCHAR(50) NOT NULL,
    [OriginTerminalCode] NVARCHAR(3) NOT NULL,
	[DestinationTerminalCode] NVARCHAR(3) NOT NULL
)

INSERT INTO @TempLaneTableType
(
	[ServiceOfferingName],
	[OriginTerminalCode],
	[DestinationTerminalCode]
)
SELECT DISTINCT L.[ServiceOfferingName],
	L.[OriginTerminalCode],
	L.[DestinationTerminalCode]
FROM [staging].[Lane] L
INNER JOIN [dbo].[Terminal] O ON L.[OriginTerminalCode] = O.[TerminalCode]
INNER JOIN [dbo].[Terminal] D ON L.[DestinationTerminalCode] = D.[TerminalCode]
UNION
SELECT Distinct [ServiceOfferingName],
	[OriginTerminalCode], 
	[DestinationTerminalCode]
FROM
(
SELECT DISTINCT [ServiceOfferingName], 
	[OriginTerminalCode], 
	[DestinationTerminalCode]
FROM [staging].[DockRoute] A
WHERE [OriginTerminalCode] IN (SELECT TerminalCode FROM [dbo].[Terminal])
AND [DestinationTerminalCode] IN (SELECT TerminalCode FROM [dbo].[Terminal])
UNION
SELECT DISTINCT [ServiceOfferingName], 
	[LegOriginTerminalCode] AS [OriginTerminalCode], 
	[LegDestinationTerminalCode] AS [DestinationTerminalCode]
FROM [staging].[DockRoute] B 
WHERE [LegOriginTerminalCode] IN (SELECT TerminalCode FROM [dbo].[Terminal])
AND [LegDestinationTerminalCode] IN (SELECT TerminalCode FROM [dbo].[Terminal])
UNION
SELECT DISTINCT [ServiceOfferingName],
	[OriginTerminalCode], 
	[DestinationTerminalCode]
FROM [staging].[LaneCost] E
WHERE [OriginTerminalCode] IN (SELECT TerminalCode FROM [dbo].[Terminal])
AND [DestinationTerminalCode] IN (SELECT TerminalCode FROM [dbo].[Terminal])
UNION 
SELECT DISTINCT [ServiceOfferingName],
	[OriginTerminalCode], 
	[DestinationTerminalCode]
FROM [staging].[LegCostFreight] F
WHERE [OriginTerminalCode] IN (SELECT TerminalCode FROM [dbo].[Terminal])
AND [DestinationTerminalCode] IN (SELECT TerminalCode FROM [dbo].[Terminal])
UNION 
SELECT DISTINCT [ServiceOfferingName],
	[OriginTerminalCode], 
	[DestinationTerminalCode]
FROM [staging].[LegCostSameday] G
WHERE [OriginTerminalCode] IN (SELECT TerminalCode FROM [dbo].[Terminal])
AND [DestinationTerminalCode] IN (SELECT TerminalCode FROM [dbo].[Terminal])
) AS C

INSERT INTO @LaneTableType
(
	[ServiceOfferingName],
	[OriginTerminalCode],
	[DestinationTerminalCode],
	[ServiceLevelCode],
	[IsHeadhaul]
)
SELECT TLTT.[ServiceOfferingName],
	TLTT.[OriginTerminalCode],
	TLTT.[DestinationTerminalCode],
	SL.[ServiceLevelCode],
	1
FROM @TempLaneTableType TLTT
INNER JOIN [dbo].[ServiceOffering] SO ON TLTT.[ServiceOfferingName] = SO.[ServiceOfferingName]
INNER JOIN [dbo].[ServiceLevel] SL ON SO.[ServiceOfferingID] = SL.[ServiceOfferingID]
--EXCEPT
--SELECT SO.[ServiceOfferingName],
--	O.TerminalCode,
--	D.TerminalCode,
--	SL.[ServiceLevelCode]
--FROM dbo.Lane L
--INNER JOIN dbo.Terminal O ON L.OriginTerminalID = O.TerminalID
--INNER JOIN dbo.Terminal D ON L.DestinationTerminalID = D.TerminalID
--INNER JOIN dbo.ServiceLevel SL ON L.ServiceLevelID = SL.ServiceLevelID
--INNER JOIN dbo.ServiceOffering SO ON SL.ServiceOfferingID = SO.ServiceOfferingID

EXEC [dbo].[Lane_Insert_Bulk] @LaneTableType

/****** BrokerContractCost ******/

DECLARE @BrokerContractCostTableType AS BrokerContractCostTableType; 

WITH A AS (
SELECT DISTINCT 
	BC.ServiceOfferingName,
	BC.TerminalCode, 
	SL.ServiceLevelID,
	SL.ServiceLevelCode, 
	BC.PickupDeliveryCount,
	(SELECT BCT.LevelLowerBound AS WeightBreakLowerBound, CAST (BCT.LevelLowerBound AS NVARCHAR(50)) AS WeightBreakLevelName, BCT.PickupDeliveryCost AS Cost FROM staging.BrokerContractCostFreight BCT WHERE BCT.PickupDeliveryCount > 0 AND BC.TerminalCode = BCT.TerminalCode AND BC.PickupDeliveryCount = BCT.PickupDeliveryCount FOR JSON AUTO) AS Cost
FROM staging.BrokerContractCostFreight BC
INNER JOIN dbo.ServiceOffering SO ON BC.ServiceOfferingName = SO.ServiceOfferingName
INNER JOIN dbo.ServiceLevel SL ON SO.ServiceOfferingID = SL.ServiceOfferingID
WHERE BC.TerminalCode IN (SELECT TerminalCode FROM dbo.Terminal)
	AND BC.PickupDeliveryCount > 0
GROUP BY BC.ServiceOfferingName, BC.TerminalCode, SL.ServiceLevelCode, SL.ServiceLevelID, BC.PickupDeliveryCount
),
B AS (
SELECT DISTINCT 
	BC.ServiceOfferingName,
	BC.TerminalCode, 
	BC.ServiceLevelCode,
	(SELECT BCT.LevelLowerBound AS WeightBreakLowerBound, CAST (BCT.LevelLowerBound AS NVARCHAR(50)) AS WeightBreakLevelName, BCT.PickupDeliveryCost AS Cost FROM staging.BrokerContractCostSameday BCT WHERE BC.TerminalCode = BCT.TerminalCode AND BC.ServiceLevelCode = BCT.ServiceLevelCode FOR JSON AUTO) AS Cost,
	BC.RateBase,
	BC.RateMax
FROM staging.BrokerContractCostSameday BC
WHERE BC.TerminalCode IN (SELECT TerminalCode FROM dbo.Terminal)
GROUP BY BC.ServiceOfferingName, BC.TerminalCode, BC.ServiceLevelCode, BC.RateBase, BC.RateMax)


INSERT INTO @BrokerContractCostTableType  
(   
	[ServiceOfferingName],   
	[TerminalCode],   
	[ServiceLevelCode],   
	[Cost]  
)
SELECT DISTINCT E.[ServiceOfferingName],   
	E.[TerminalCode],   
	E.[ServiceLevelCode],   
	(SELECT E.CostByWeightBreakByPickupDeliveryCount AS [CostComponents.CostByWeightBreakByPickupDeliveryCount], E.[CostByWeightBreak] AS [CostComponents.CostByWeightBreak] FOR JSON PATH, WITHOUT_ARRAY_WRAPPER) AS Cost  
FROM 
(
SELECT DISTINCT A.ServiceOfferingName, A.TerminalCode, A.ServiceLevelID, A.ServiceLevelCode,
	(SELECT D.[PickupDeliveryCount], D.[Cost] FROM A AS D WHERE A.[TerminalCode] = D.[TerminalCode] AND A.ServiceLevelID = D.ServiceLevelID FOR JSON AUTO) AS CostByWeightBreakByPickupDeliveryCount,   
	'' AS CostByWeightBreak 
FROM A) AS E
UNION
SELECT DISTINCT E.[ServiceOfferingName],   
	E.[TerminalCode],   
	E.[ServiceLevelCode],   
	(SELECT E.CostByWeightBreakByPickupDeliveryCount AS [CostComponents.CostByWeightBreakByPickupDeliveryCount], E.[CostByWeightBreak] AS [CostComponents.CostByWeightBreak] FOR JSON PATH, WITHOUT_ARRAY_WRAPPER) AS Cost  
FROM 
(SELECT DISTINCT B.[ServiceOfferingName],
	B.[TerminalCode],
	B.[ServiceLevelCode],
	'' AS CostByWeightBreakByPickupDeliveryCount,
	(SELECT D.[RateBase], D.[RateMax], D.[Cost] FROM B AS D WHERE B.[TerminalCode] = D.[TerminalCode] AND B.[ServiceLevelCode] = D.[ServiceLevelCode] FOR JSON AUTO, WITHOUT_ARRAY_WRAPPER) AS CostByWeightBreak
FROM B) AS E

EXEC [dbo].[BrokerContractCost_Insert_Bulk] @BrokerContractCostTableType

/****** LaneCostWeightBreakLevel ******/

DECLARE @LaneCostWeightBreakLevelTableType AS CostWeightBreakLevelTableType; 

INSERT INTO @LaneCostWeightBreakLevelTableType
(
	[ServiceOfferingName],
    [WeightBreakLevelName],
    [WeightBreakLowerBound]
)
SELECT 'Freight', '0',  0
UNION
SELECT 'Freight', '1000',  1000
UNION
SELECT 'Freight', '2000',  2000
UNION
SELECT 'Freight', '5000',  5000
UNION
SELECT 'Freight', '10000',  10000
UNION
SELECT 'Freight', '20000',  20000
UNION
SELECT 'Freight', '30000',  30000
UNION
SELECT 'SameDay', '0',  0  
UNION
SELECT 'SameDay', '25000',  25000
UNION
SELECT 'SameDay', '50000',  50000
UNION
SELECT 'SameDay', '100000',  100000
UNION
SELECT 'SameDay', '200000',  200000
UNION
SELECT 'SameDay', '500000',  500000
UNION
SELECT 'SameDay', '1000000',  1000000

EXEC [dbo].[LaneCostWeightBreakLevel_Insert_Bulk] @LaneCostWeightBreakLevelTableType

/****** LaneCost ******/

DECLARE @LaneCostTableType AS LaneCostTableType;

INSERT INTO @LaneCostTableType  
(   
	[ServiceOfferingName],   
	[OriginTerminalCode],
	[DestinationTerminalCode],
	[ServiceLevelCode],   
	[MinimumCost],
	[Cost],
	[IsHeadhaul]
) 
SELECT LC.[ServiceOfferingName],   
	LC.[OriginTerminalCode],
	LC.[DestinationTerminalCode],
	LC.[ServiceLevelCode],   
	LC.[MinimumCost],
	A.Cost,
	1
FROM staging.LaneCost LC
INNER JOIN dbo.ServiceOffering SO ON LC.[ServiceOfferingName] = SO.[ServiceOfferingName]
INNER JOIN 
(
SELECT 
  [ServiceOfferingID], '{' +
  STUFF((
    SELECT ', ' + '"' +  CAST([WeightBreakLevelID] AS VARCHAR(MAX)) + '"' + ':' + CAST(0.100 AS VARCHAR(MAX)) 
    FROM dbo.LaneCostWeightBreakLevel
    WHERE ([ServiceOfferingID] = Results.[ServiceOfferingID]) 
    FOR XML PATH(''),TYPE).value('(./text())[1]','VARCHAR(MAX)')
  ,1,2,'') + '}' AS Cost
FROM dbo.LaneCostWeightBreakLevel Results
GROUP BY [ServiceOfferingID]
) AS A ON SO.[ServiceOfferingID] = A.[ServiceOfferingID]
WHERE LC.[OriginTerminalCode] IN (SELECT TerminalCode FROM [dbo].[Terminal])
AND LC.[DestinationTerminalCode] IN (SELECT TerminalCode FROM [dbo].[Terminal])

EXEC [dbo].[LaneCost_Insert_Bulk] @LaneCostTableType

/****** LegCost ******/

DECLARE @LegCostTableType AS LegCostTableType;

INSERT INTO @LegCostTableType
(
	[ServiceOfferingName],
	[OriginTerminalCode],
	[DestinationTerminalCode],
	[SubServiceLevelCode],
	[ServiceModeCode],
	[Cost]
)

SELECT A.ServiceOfferingName,
	A.OriginTerminalCode,
	A.DestinationTerminalCode,
	A.ServiceLevelCode,
	A.ServiceModeCode,
	(SELECT A.[CostByDistnce], A.[CostByWeight] FOR JSON PATH) AS Cost
FROM
(
SELECT LC.ServiceOfferingName,
	LC.OriginTerminalCode,
	LC.DestinationTerminalCode,
	LC.ServiceLevelCode,
	LC.ServiceModeCode,
	(SELECT LC.[LinehaulRatePerMile] AS [RatePerUnitDistance], 
			LC.[FerryCost],
			LC.[TrailerCapacity],
			LC.[MaximumDensity],
			LC.[LegMiles] AS [LegDistance],
			LC.[BackHaulMiles] AS [BackHaulDistance]
	  FOR JSON PATH) AS CostByDistnce,
	'' AS CostByWeight
FROM staging.LegCostFreight LC
WHERE LC.OriginTerminalCode IN (SELECT TerminalCode FROM [dbo].[Terminal])
AND LC.DestinationTerminalCode IN (SELECT TerminalCode FROM [dbo].[Terminal])
UNION
SELECT LC.ServiceOfferingName,
	LC.OriginTerminalCode,
	LC.DestinationTerminalCode,
	LC.ServiceLevelCode,
	LC.ServiceModeCode,
	(SELECT LC.[PerLBRate] AS [RatePerUnitWeight], 
			LC.[UseVolumetricWeightForCosting],
			LC.[SupplementalPerLBRate] AS [SupplementalPerUnitWeightRate]
	  FOR JSON PATH) AS CostByWeight,
	'' AS CostByDistnce
FROM staging.LegCostSameday LC
WHERE LC.OriginTerminalCode IN (SELECT TerminalCode FROM [dbo].[Terminal])
AND LC.DestinationTerminalCode IN (SELECT TerminalCode FROM [dbo].[Terminal])
) AS A

EXEC [dbo].[LegCost_Insert_Bulk] @LegCostTableType

/****** LaneRoute ******/

DECLARE @LaneRouteTableType AS LaneRouteTableType;

INSERT INTO @LaneRouteTableType
(
	[ServiceOfferingName],
	[OriginTerminalCode],
	[DestinationTerminalCode],
	[ServiceLevelCode],
	[SeqNum],
	[LegOriginTerminalCode],
	[LegDestinationTerminalCode],
	[LegServiceModeCode]
)
SELECT DISTINCT LR.[ServiceOfferingName],
	LR.[OriginTerminalCode],
	LR.[DestinationTerminalCode],
	LR.[ServiceLevelCode],
	LR.[SeqNum],
	LR.[LegOriginTerminalCode],
	LR.[LegDestinationTerminalCode],
	LR.[LegServiceModeCode]
FROM [staging].[LaneRoute] LR

INNER JOIN
(
SELECT LR.[ServiceOfferingName],
	LR.[OriginTerminalCode],
	LR.[DestinationTerminalCode],
	LR.[ServiceLevelCode]
FROM [staging].[LaneRoute] LR
WHERE LR.[OriginTerminalCode] IN (SELECT TerminalCode FROM dbo.Terminal)
AND LR.[DestinationTerminalCode] IN (SELECT TerminalCode FROM dbo.Terminal)
AND LR.[LegOriginTerminalCode] IN (SELECT TerminalCode FROM dbo.Terminal)
AND LR.[LegDestinationTerminalCode] IN (SELECT TerminalCode FROM dbo.Terminal)
) AS A
ON LR.[ServiceOfferingName] = A.[ServiceOfferingName]
AND LR.[OriginTerminalCode] = A.[OriginTerminalCode]
AND LR.[DestinationTerminalCode] = A.[DestinationTerminalCode]
AND LR.[ServiceLevelCode] = A.[ServiceLevelCode]

EXEC [dbo].[LaneRoute_Insert_Bulk] @LaneRouteTableType

/****** DockRoute ******/

DECLARE @DockRouteTableType AS DockRouteTableType;

INSERT INTO @DockRouteTableType
(
	[ServiceOfferingName],
	[OriginTerminalCode],
	[DestinationTerminalCode],
	[ServiceLevelCode],
	[SeqNum],
	[LegOriginTerminalCode],
	[LegDestinationTerminalCode]
)
SELECT DR.[ServiceOfferingName],
	DR.[OriginTerminalCode],
	DR.[DestinationTerminalCode],
	SL.[ServiceLevelCode],
	DR.[SeqNum],
	DR.[LegOriginTerminalCode],
	DR.[LegDestinationTerminalCode]
FROM [staging].[DockRoute] DR
INNER JOIN [dbo].[ServiceOffering] SO ON DR.[ServiceOfferingName] = SO.[ServiceOfferingName]
INNER JOIN [dbo].[ServiceLevel] SL ON SO.[ServiceOfferingID] = SL.[ServiceOfferingID]
INNER JOIN
(SELECT DR.[ServiceOfferingName],
	DR.[OriginTerminalCode],
	DR.[DestinationTerminalCode],
	SL.[ServiceLevelCode]
FROM [staging].[DockRoute] DR
INNER JOIN [dbo].[ServiceOffering] SO ON DR.[ServiceOfferingName] = SO.[ServiceOfferingName]
INNER JOIN [dbo].[ServiceLevel] SL ON SO.[ServiceOfferingID] = SL.[ServiceOfferingID]
WHERE DR.[OriginTerminalCode] IN (SELECT TerminalCode FROM dbo.Terminal)
AND DR.[DestinationTerminalCode] IN (SELECT TerminalCode FROM dbo.Terminal)
AND DR.[LegOriginTerminalCode] IN (SELECT TerminalCode FROM dbo.Terminal)
AND DR.[LegDestinationTerminalCode] IN (SELECT TerminalCode FROM dbo.Terminal)
) AS A
ON DR.[ServiceOfferingName] = A.[ServiceOfferingName]
AND DR.[OriginTerminalCode] = A.[OriginTerminalCode]
AND DR.[DestinationTerminalCode] = A.[DestinationTerminalCode]
AND SL.[ServiceLevelCode] = A.[ServiceLevelCode]

EXEC [dbo].[DockRoute_Insert_Bulk] @DockRouteTableType

RETURN 1
