CREATE OR ALTER PROCEDURE [dbo].[RequestSectionLane_Insert_Bulk]
	@RequestSectionLaneTableType RequestSectionLaneTableType READONLY,
	@RequestLaneID BIGINT,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL
AS

SET NOCOUNT ON;

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

BEGIN TRAN

-- Get Distinct RequestSections

DECLARE @DistinctRequestSectionID IDTableType;

INSERT INTO @DistinctRequestSectionID
(
	ID
)
SELECT DISTINCT [RequestSectionID]
FROM @RequestSectionLaneTableType

-- Get Union of RequestSectionLanes, mark the identical ones

DECLARE @AllRequestSectionLane TABLE
(
	[RequestSectionID] BIGINT NOT NULL,
	[LaneNumber] NVARCHAR(32) NOT NULL,
	[LaneHashCode] VARBINARY(8000) NOT NULL,
	[BasingPointHashCode] VARBINARY(8000) NULL
)
INSERT INTO @AllRequestSectionLane
(
	[RequestSectionID],
	[LaneNumber],
	[LaneHashCode],
	[BasingPointHashCode]
)
SELECT RSL.[RequestSectionID], RSL.[LaneNumber], RSL.[LaneHashCode], RSL.[BasingPointHashCode]
FROM dbo.RequestSectionLane RSL
INNER JOIN @DistinctRequestSectionID RS ON RSL.[RequestSectionID] = RS.ID
UNION
SELECT [RequestSectionID], [LaneNumber], [LaneHashCode], [BasingPointHashCode]
FROM @RequestSectionLaneTableType

DECLARE @IdenticalLaneHashCode TABLE
(
	[RequestSectionID] BIGINT NOT NULL,
	[LaneHashCode] VARBINARY(8000) NOT NULL
)
INSERT INTO @IdenticalLaneHashCode
(
	[RequestSectionID],
	[LaneHashCode]
)
SELECT [RequestSectionID], [LaneHashCode]
FROM @AllRequestSectionLane
GROUP BY [RequestSectionID], [LaneHashCode]
HAVING COUNT(*) > 1

DECLARE @IdenticalRequestSectionLane TABLE
(
	[RequestSectionID] BIGINT NOT NULL,
	[LaneNumber] NVARCHAR(32) NOT NULL
)
INSERT INTO @IdenticalRequestSectionLane
(
	[RequestSectionID],
	[LaneNumber]
)
SELECT A.[RequestSectionID], A.[LaneNumber]
FROM @AllRequestSectionLane A
INNER JOIN @IdenticalLaneHashCode B ON A.[RequestSectionID] = B.[RequestSectionID] AND A.[LaneHashCode] = B.[LaneHashCode]

-- Get Union of Active RequestSectionLanes, mark the duplicate ones 

DECLARE @AllActiveRequestSectionLane TABLE
(
	[RequestSectionID] BIGINT NOT NULL,
	[LaneNumber] NVARCHAR(32) NOT NULL,
	[LaneHashCode] VARBINARY(8000) NOT NULL,
	[BasingPointHashCode] VARBINARY(8000) NULL
)
INSERT INTO @AllActiveRequestSectionLane
(
	[RequestSectionID],
	[LaneNumber],
	[LaneHashCode],
	[BasingPointHashCode]
)
SELECT RSL.[RequestSectionID], RSL.[LaneNumber], RSL.[LaneHashCode], RSL.[BasingPointHashCode]
FROM dbo.RequestSectionLane RSL 
INNER JOIN @DistinctRequestSectionID RS ON RSL.[RequestSectionID] = RS.ID
WHERE (RSL.IsActive = 1 AND RSL.[IsInactiveViewable] = 1) OR RSL.[LaneNumber] IN (SELECT [LaneNumber] FROM @IdenticalLaneHashCode)
UNION
SELECT [RequestSectionID], [LaneNumber], [LaneHashCode], [BasingPointHashCode]
FROM @RequestSectionLaneTableType
WHERE IsActive = 1 AND [IsInactiveViewable] = 1 AND [LaneNumber] NOT IN (SELECT [LaneNumber] FROM @IdenticalLaneHashCode)

DECLARE @DuplicateBasingPointHashCode TABLE
(
	[RequestSectionID] BIGINT NOT NULL,
	[BasingPointHashCode] VARBINARY(8000) NOT NULL
)
INSERT INTO @DuplicateBasingPointHashCode
(
	[RequestSectionID],
	[BasingPointHashCode]
)
SELECT [RequestSectionID], [BasingPointHashCode]
FROM @AllActiveRequestSectionLane
WHERE [BasingPointHashCode] IS NOT NULL
GROUP BY [RequestSectionID], [BasingPointHashCode]
HAVING COUNT(*) > 1

DECLARE @DuplicateRequestSectionLane TABLE
(
	[RequestSectionID] BIGINT NOT NULL,
	[LaneNumber] NVARCHAR(32) NOT NULL
)
INSERT INTO @DuplicateRequestSectionLane
(
	[RequestSectionID],
	[LaneNumber]
)
SELECT A.[RequestSectionID], A.[LaneNumber]
FROM @AllActiveRequestSectionLane A
INNER JOIN @DuplicateBasingPointHashCode B ON A.[RequestSectionID] = B.[RequestSectionID] AND A.[BasingPointHashCode] = B.[BasingPointHashCode]

DECLARE @ToBeUpDatedRequestSectionLane TABLE
(
	[RequestSectionLaneID] BIGINT NOT NULL,
	[RequestSectionID] BIGINT NOT NULL,
	[IsDuplicate]        BIT NOT NULL,
	[IsActive] BIT NOT NULL,
    [IsInactiveViewable] BIT NOT NULL
)
INSERT INTO @ToBeUpDatedRequestSectionLane
(
	[RequestSectionLaneID],
	[RequestSectionID],
	[IsDuplicate],
	[IsActive],
	[IsInactiveViewable]
)
SELECT A.[RequestSectionLaneID],
	A.[RequestSectionID],
	1,
	1,
	1
FROM dbo.RequestSectionLane A
INNER JOIN @DuplicateRequestSectionLane B ON A.[RequestSectionID] = B.[RequestSectionID] AND A.[LaneNumber] = B.[LaneNumber]
UNION
SELECT A.[RequestSectionLaneID],
	A.[RequestSectionID],
	0,
	1,
	1
FROM dbo.RequestSectionLane A 
INNER JOIN @IdenticalRequestSectionLane B ON A.[RequestSectionID] = B.[RequestSectionID] AND A.[LaneNumber] = B.[LaneNumber]
WHERE (A.[IsActive] = 0 OR A.[IsInactiveViewable] = 0) AND A.[LaneNumber] NOT IN (SELECT [LaneNumber] FROM @DuplicateRequestSectionLane)

-- Prepare VersionID

DECLARE @ProvinceVersionID table 
( 
	[ProvinceID] [bigint] NOT NULL,
	[ProvinceVersionID] [bigint] NOT NULL
)
INSERT INTO @ProvinceVersionID 
( 
	[ProvinceID],
	[ProvinceVersionID]
)
SELECT [ProvinceID],
	[ProvinceVersionID]
FROM [dbo].[Province_History]
WHERE [IsLatestVersion] = 1
AND [ProvinceID] IN 
(SELECT DISTINCT ProvinceID FROM 
(SELECT [OriginProvinceID] AS ProvinceID FROM @RequestSectionLaneTableType WHERE [OriginProvinceID] IS NOT NULL
UNION 
SELECT [DestinationProvinceID] AS ProvinceID FROM @RequestSectionLaneTableType WHERE [DestinationProvinceID] IS NOT NULL) AS A)

DECLARE @CountryVersionID table 
( 
	[CountryID] [bigint] NOT NULL,
	[CountryVersionID] [bigint] NOT NULL
)
INSERT INTO @CountryVersionID 
( 
	[CountryID],
	[CountryVersionID]
)
SELECT [CountryID],
	[CountryVersionID]
FROM [dbo].[Country_History]
WHERE [IsLatestVersion] = 1
AND [CountryID] IN 
(SELECT DISTINCT CountryID FROM 
(SELECT [OriginCountryID] AS CountryID FROM @RequestSectionLaneTableType WHERE [OriginCountryID] IS NOT NULL
UNION 
SELECT [DestinationCountryID] AS CountryID FROM @RequestSectionLaneTableType WHERE [DestinationCountryID] IS NOT NULL) AS A)

DECLARE @RegionVersionID table 
( 
	[RegionID] [bigint] NOT NULL,
	[RegionVersionID] [bigint] NOT NULL
)
INSERT INTO @RegionVersionID 
( 
	[RegionID],
	[RegionVersionID]
)
SELECT [RegionID],
	[RegionVersionID]
FROM [dbo].[Region_History]
WHERE [IsLatestVersion] = 1
AND [RegionID] IN 
(SELECT DISTINCT RegionID FROM 
(SELECT [OriginRegionID] AS RegionID FROM @RequestSectionLaneTableType WHERE [OriginRegionID] IS NOT NULL
UNION 
SELECT [DestinationRegionID] AS RegionID FROM @RequestSectionLaneTableType WHERE [DestinationRegionID] IS NOT NULL) AS A)

DECLARE @ZoneVersionID table 
( 
	[ZoneID] [bigint] NOT NULL,
	[ZoneVersionID] [bigint] NOT NULL
)
INSERT INTO @ZoneVersionID 
( 
	[ZoneID],
	[ZoneVersionID]
)
SELECT [ZoneID],
	[ZoneVersionID]
FROM [dbo].[Zone_History]
WHERE [IsLatestVersion] = 1
AND [ZoneID] IN 
(SELECT DISTINCT ZoneID FROM 
(SELECT [OriginZoneID] AS ZoneID FROM @RequestSectionLaneTableType WHERE [OriginZoneID] IS NOT NULL
UNION 
SELECT [DestinationZoneID] AS ZoneID FROM @RequestSectionLaneTableType WHERE [DestinationZoneID] IS NOT NULL) AS A)

DECLARE @ServicePointVersionID table 
( 
	[ServicePointID] [bigint] NOT NULL,
	[ServicePointVersionID] [bigint] NOT NULL
)
INSERT INTO @ServicePointVersionID 
( 
	[ServicePointID],
	[ServicePointVersionID]
)
SELECT [ServicePointID],
	[ServicePointVersionID]
FROM [dbo].[ServicePoint_History]
WHERE [IsLatestVersion] = 1
AND [ServicePointID] IN 
(SELECT DISTINCT ServicePointID FROM 
(SELECT [OriginServicePointID] AS ServicePointID FROM @RequestSectionLaneTableType WHERE [OriginServicePointID] IS NOT NULL
UNION 
SELECT [DestinationServicePointID] AS ServicePointID FROM @RequestSectionLaneTableType WHERE [DestinationServicePointID] IS NOT NULL) AS A)

DECLARE @PostalCodeVersionID table 
( 
	[PostalCodeID] [bigint] NOT NULL,
	[PostalCodeVersionID] [bigint] NOT NULL
)
INSERT INTO @PostalCodeVersionID 
( 
	[PostalCodeID],
	[PostalCodeVersionID]
)
SELECT [PostalCodeID],
	[PostalCodeVersionID]
FROM [dbo].[PostalCode_History]
WHERE [IsLatestVersion] = 1
AND [PostalCodeID] IN 
(SELECT DISTINCT PostalCodeID FROM 
(SELECT [OriginPostalCodeID] AS PostalCodeID FROM @RequestSectionLaneTableType WHERE [OriginPostalCodeID] IS NOT NULL
UNION 
SELECT [DestinationPostalCodeID] AS PostalCodeID FROM @RequestSectionLaneTableType WHERE [DestinationPostalCodeID] IS NOT NULL) AS A)

DECLARE @TerminalVersionID table 
( 
	[TerminalID] [bigint] NOT NULL,
	[TerminalVersionID] [bigint] NOT NULL
)
INSERT INTO @TerminalVersionID 
( 
	[TerminalID],
	[TerminalVersionID]
)
SELECT [TerminalID],
	[TerminalVersionID]
FROM [dbo].[Terminal_History]
WHERE [IsLatestVersion] = 1
AND [TerminalID] IN 
(SELECT DISTINCT TerminalID FROM 
(SELECT [OriginTerminalID] AS TerminalID FROM @RequestSectionLaneTableType WHERE [OriginTerminalID] IS NOT NULL
UNION 
SELECT [DestinationTerminalID] AS TerminalID FROM @RequestSectionLaneTableType WHERE [DestinationTerminalID] IS NOT NULL) AS A)

DECLARE @BasingPointVersionID table 
( 
	[BasingPointID] [bigint] NOT NULL,
	[BasingPointVersionID] [bigint] NOT NULL
)
INSERT INTO @BasingPointVersionID 
( 
	[BasingPointID],
	[BasingPointVersionID]
)
SELECT [BasingPointID],
	[BasingPointVersionID]
FROM [dbo].[BasingPoint_History]
WHERE [IsLatestVersion] = 1
AND [BasingPointID] IN 
(SELECT DISTINCT BasingPointID FROM 
(SELECT [OriginBasingPointID] AS BasingPointID FROM @RequestSectionLaneTableType WHERE [OriginBasingPointID] IS NOT NULL
UNION 
SELECT [DestinationBasingPointID] AS BasingPointID FROM @RequestSectionLaneTableType WHERE [DestinationBasingPointID] IS NOT NULL) AS A)

DECLARE @PointTypeVersionID table 
( 
	[PointTypeID] [bigint] NOT NULL,
	[PointTypeVersionID] [bigint] NOT NULL
)
INSERT INTO @PointTypeVersionID 
( 
	[PointTypeID],
	[PointTypeVersionID]
)
SELECT [RequestSectionLanePointTypeID],
	[RequestSectionLanePointTypeVersionID]
FROM [dbo].[RequestSectionLanePointType_History]
WHERE [IsLatestVersion] = 1
AND [RequestSectionLanePointTypeID] IN 
(SELECT DISTINCT PointTypeID FROM 
(SELECT [OriginPointTypeID] AS PointTypeID FROM @RequestSectionLaneTableType
UNION 
SELECT [DestinationPointTypeID] AS PointTypeID FROM @RequestSectionLaneTableType) AS A)

-- Insert new RequestSectionLane

DECLARE @NewRequestSectionLaneTableType RequestSectionLaneTableType

INSERT INTO dbo.RequestSectionLane
(	
	[IsActive],
    [IsInactiveViewable],
	[RequestSectionID],
    [LaneNumber],
	[IsPublished],
	[IsEdited],
	[IsDuplicate],
	[IsBetween],
	[IsLaneGroup],
	[OriginProvinceID],
	[OriginProvinceCode],
	[OriginRegionID],
	[OriginRegionCode],
	[OriginCountryID],
	[OriginCountryCode],
	[OriginTerminalID],
	[OriginTerminalCode],
	[OriginZoneID],
	[OriginZoneName],
	[OriginBasingPointID],
	[OriginBasingPointName],
	[OriginServicePointID],
	[OriginServicePointName],
	[OriginPostalCodeID],
	[OriginPostalCodeName],
	[OriginPointTypeID],
	[OriginPointTypeName],
	[OriginCode],
	[DestinationProvinceID],
	[DestinationProvinceCode],
	[DestinationRegionID],
	[DestinationRegionCode],
	[DestinationCountryID],
	[DestinationCountryCode],
	[DestinationTerminalID],
	[DestinationTerminalCode],
	[DestinationZoneID],
	[DestinationZoneName],
	[DestinationBasingPointID],
	[DestinationBasingPointName],
	[DestinationServicePointID],
	[DestinationServicePointName],
	[DestinationPostalCodeID],
	[DestinationPostalCodeName],
	[DestinationPointTypeID],
	[DestinationPointTypeName],
	[DestinationCode],
	[LaneHashCode],
	[BasingPointHashCode],
	[Cost],
	[DoNotMeetCommitment],
	[Commitment],
	[CustomerRate],
	[CustomerDiscount],
	[DrRate],
	[PartnerRate],
	[PartnerDiscount],
	[Profitability],
	[PickupCount],
	[DeliveryCount],
	[DockAdjustment],
	[Margin],
	[Density],
	[PickupCost],
	[DeliveryCost],
	[AccessorialsValue],
	[AccessorialsPercentage]
)
OUTPUT INSERTED.[RequestSectionLaneID],
	INSERTED.[IsActive],
    INSERTED.[IsInactiveViewable],
	INSERTED.[RequestSectionID],
    INSERTED.[LaneNumber],
	INSERTED.[IsPublished],
	INSERTED.[IsEdited],
	INSERTED.[IsDuplicate],
	INSERTED.[IsBetween],
	INSERTED.[IsLaneGroup],
	INSERTED.[OriginProvinceID],
	INSERTED.[OriginProvinceCode],
	INSERTED.[OriginRegionID],
	INSERTED.[OriginRegionCode],
	INSERTED.[OriginCountryID],
	INSERTED.[OriginCountryCode],
	INSERTED.[OriginTerminalID],
	INSERTED.[OriginTerminalCode],
	INSERTED.[OriginZoneID],
	INSERTED.[OriginZoneName],
	INSERTED.[OriginBasingPointID],
	INSERTED.[OriginBasingPointName],
	INSERTED.[OriginServicePointID],
	INSERTED.[OriginServicePointName],
	INSERTED.[OriginPostalCodeID],
	INSERTED.[OriginPostalCodeName],
	INSERTED.[OriginPointTypeID],
	INSERTED.[OriginPointTypeName],
	INSERTED.[OriginCode],
	INSERTED.[DestinationProvinceID],
	INSERTED.[DestinationProvinceCode],
	INSERTED.[DestinationRegionID],
	INSERTED.[DestinationRegionCode],
	INSERTED.[DestinationCountryID],
	INSERTED.[DestinationCountryCode],
	INSERTED.[DestinationTerminalID],
	INSERTED.[DestinationTerminalCode],
	INSERTED.[DestinationZoneID],
	INSERTED.[DestinationZoneName],
	INSERTED.[DestinationBasingPointID],
	INSERTED.[DestinationBasingPointName],
	INSERTED.[DestinationServicePointID],
	INSERTED.[DestinationServicePointName],
	INSERTED.[DestinationPostalCodeID],
	INSERTED.[DestinationPostalCodeName],
	INSERTED.[DestinationPointTypeID],
	INSERTED.[DestinationPointTypeName],
	INSERTED.[DestinationCode],
	INSERTED.[LaneHashCode],
	INSERTED.[BasingPointHashCode],
	INSERTED.[Cost],
	INSERTED.[DoNotMeetCommitment],
	INSERTED.[Commitment],
	INSERTED.[CustomerRate],
	INSERTED.[CustomerDiscount],
	INSERTED.[DrRate],
	INSERTED.[PartnerRate],
	INSERTED.[PartnerDiscount],
	INSERTED.[Profitability],
	INSERTED.[PickupCount],
	INSERTED.[DeliveryCount],
	INSERTED.[DockAdjustment],
	INSERTED.[Margin],
	INSERTED.[Density],
	INSERTED.[PickupCost],
	INSERTED.[DeliveryCost],
	INSERTED.[AccessorialsValue],
	INSERTED.[AccessorialsPercentage]
INTO @NewRequestSectionLaneTableType
(
	[NewRequestSectionLaneID],
	[IsActive],
    [IsInactiveViewable],
	[RequestSectionID],
    [LaneNumber],
	[IsPublished],
	[IsEdited],
	[IsDuplicate],
	[IsBetween],
	[IsLaneGroup],
	[OriginProvinceID],
	[OriginProvinceCode],
	[OriginRegionID],
	[OriginRegionCode],
	[OriginCountryID],
	[OriginCountryCode],
	[OriginTerminalID],
	[OriginTerminalCode],
	[OriginZoneID],
	[OriginZoneName],
	[OriginBasingPointID],
	[OriginBasingPointName],
	[OriginServicePointID],
	[OriginServicePointName],
	[OriginPostalCodeID],
	[OriginPostalCodeName],
	[OriginPointTypeID],
	[OriginPointTypeName],
	[OriginCode],
	[DestinationProvinceID],
	[DestinationProvinceCode],
	[DestinationRegionID],
	[DestinationRegionCode],
	[DestinationCountryID],
	[DestinationCountryCode],
	[DestinationTerminalID],
	[DestinationTerminalCode],
	[DestinationZoneID],
	[DestinationZoneName],
	[DestinationBasingPointID],
	[DestinationBasingPointName],
	[DestinationServicePointID],
	[DestinationServicePointName],
	[DestinationPostalCodeID],
	[DestinationPostalCodeName],
	[DestinationPointTypeID],
	[DestinationPointTypeName],
	[DestinationCode],
	[LaneHashCode],
	[BasingPointHashCode],
	[Cost],
	[DoNotMeetCommitment],
	[Commitment],
	[CustomerRate],
	[CustomerDiscount],
	[DrRate],
	[PartnerRate],
	[PartnerDiscount],
	[Profitability],
	[PickupCount],
	[DeliveryCount],
	[DockAdjustment],
	[Margin],
	[Density],
	[PickupCost],
	[DeliveryCost],
	[AccessorialsValue],
	[AccessorialsPercentage]
)
SELECT [IsActive],
    [IsInactiveViewable],
	A.[RequestSectionID],
    A.[LaneNumber],
	[IsPublished],
	[IsEdited],
	CASE WHEN B.[LaneNumber] IS NOT NULL THEN 1 ELSE 0 END,
	[IsBetween],
	[IsLaneGroup],
	[OriginProvinceID],
	[OriginProvinceCode],
	[OriginRegionID],
	[OriginRegionCode],
	[OriginCountryID],
	[OriginCountryCode],
	[OriginTerminalID],
	[OriginTerminalCode],
	[OriginZoneID],
	[OriginZoneName],
	[OriginBasingPointID],
	[OriginBasingPointName],
	[OriginServicePointID],
	[OriginServicePointName],
	[OriginPostalCodeID],
	[OriginPostalCodeName],
	[OriginPointTypeID],
	[OriginPointTypeName],
	[OriginCode],
	[DestinationProvinceID],
	[DestinationProvinceCode],
	[DestinationRegionID],
	[DestinationRegionCode],
	[DestinationCountryID],
	[DestinationCountryCode],
	[DestinationTerminalID],
	[DestinationTerminalCode],
	[DestinationZoneID],
	[DestinationZoneName],
	[DestinationBasingPointID],
	[DestinationBasingPointName],
	[DestinationServicePointID],
	[DestinationServicePointName],
	[DestinationPostalCodeID],
	[DestinationPostalCodeName],
	[DestinationPointTypeID],
	[DestinationPointTypeName],
	[DestinationCode],
	[LaneHashCode],
	[BasingPointHashCode],
	[Cost],
	[DoNotMeetCommitment],
	[Commitment],
	[CustomerRate],
	[CustomerDiscount],
	[DrRate],
	[PartnerRate],
	[PartnerDiscount],
	[Profitability],
	[PickupCount],
	[DeliveryCount],
	[DockAdjustment],
	[Margin],
	[Density],
	[PickupCost],
	[DeliveryCost],
	[AccessorialsValue],
	[AccessorialsPercentage]
FROM @RequestSectionLaneTableType A
LEFT JOIN @DuplicateRequestSectionLane B ON A.RequestSectionID = B.RequestSectionID AND A.[LaneNumber] = B.[LaneNumber]
WHERE A.[LaneNumber] NOT IN (SELECT [LaneNumber] FROM @IdenticalRequestSectionLane)

-- Update IsDuplicate/IsActive for existing lanes

UPDATE dbo.RequestSectionLane
SET [IsDuplicate] = A.[IsDuplicate],
	[IsActive] = A.[IsActive],
	[IsInactiveViewable] = A.[IsInactiveViewable],
	[Cost] = dbo.GetRequestSectionLaneDefaultCost(A.[RequestSectionID])
FROM @ToBeUpDatedRequestSectionLane A
WHERE dbo.RequestSectionLane.[RequestSectionLaneID] = A.[RequestSectionLaneID]

-- Check If there was a change

DECLARE @InsertedCount BIGINT, @UpdatedCount BIGINT;

SELECT @InsertedCount = COUNT(*) FROM @NewRequestSectionLaneTableType
SELECT @UpdatedCount = COUNT(*) FROM @ToBeUpDatedRequestSectionLane

IF (@InsertedCount IS NULL OR @InsertedCount < 1) AND (@UpdatedCount IS NULL OR @UpdatedCount < 1) 
BEGIN

	SELECT CAST(
	(SELECT *
	FROM
	(
		SELECT 
			(SELECT * 
			FROM @RequestSectionLaneTableType
			WHERE [LaneNumber] IN (SELECT [LaneNumber] FROM @IdenticalRequestSectionLane)
			FOR JSON AUTO) AS identical_lanes_not_added,
			(SELECT * 
			FROM @RequestSectionLaneTableType
			WHERE [LaneNumber] IN (SELECT [LaneNumber] FROM @DuplicateRequestSectionLane)
			FOR JSON AUTO) AS duplicate_lanes_added
		) AS Q
	FOR JSON AUTO, WITHOUT_ARRAY_WRAPPER)
	AS VARCHAR(MAX))

	COMMIT TRAN
	RETURN 1
END

-- Update RequestSection

DECLARE @RequestSectionStatistics TABLE
(
	[RequestSectionID] BIGINT NOT NULL,
	[NumLanes] INT NOT NULL,
	[NumUnpublishedLanes] INT NOT NULL,
	[NumEditedLanes] INT NOT NULL,
	[NumDuplicateLanes] INT NOT NULL,
	[NumDoNotMeetCommitmentLanes] INT NOT NULL
)
INSERT INTO @RequestSectionStatistics
(
	[RequestSectionID],
	[NumLanes],
	[NumUnpublishedLanes],
	[NumEditedLanes],
	[NumDuplicateLanes],
	[NumDoNotMeetCommitmentLanes]
)
SELECT RSL.[RequestSectionID],
	ISNULL(SUM(CASE WHEN RSL.IsActive = 1 AND RSL.[IsInactiveViewable] = 1 THEN 1 ELSE 0 END), 0),
	ISNULL(SUM(CASE WHEN RSL.IsActive = 1 AND RSL.[IsInactiveViewable] = 1 AND RSL.IsPublished = 0 THEN 1 ELSE 0 END), 0),
	ISNULL(SUM(CASE WHEN RSL.IsActive = 1 AND RSL.[IsInactiveViewable] = 1 AND RSL.IsEdited = 1 THEN 1 ELSE 0 END), 0),
	ISNULL(SUM(CASE WHEN RSL.IsActive = 1 AND RSL.[IsInactiveViewable] = 1 AND RSL.IsDuplicate = 1 THEN 1 ELSE 0 END), 0),
	ISNULL(SUM(CASE WHEN RSL.IsActive = 1 AND RSL.[IsInactiveViewable] = 1 AND RSL.[DoNotMeetCommitment] = 1 THEN 1 ELSE 0 END), 0)
FROM dbo.RequestSectionLane RSL
INNER JOIN @DistinctRequestSectionID RS ON RSL.[RequestSectionID] = RS.ID
GROUP BY RSL.[RequestSectionID]

UPDATE dbo.RequestSection
SET [NumLanes] = A.[NumLanes],
	[NumUnpublishedLanes] = A.[NumUnpublishedLanes],
    [NumEditedLanes] = A.[NumEditedLanes],
    [NumDuplicateLanes] = A.[NumDuplicateLanes],
	[NumDoNotMeetCommitmentLanes] = A.[NumDoNotMeetCommitmentLanes]
FROM @RequestSectionStatistics A
WHERE dbo.RequestSection.[RequestSectionID] = A.[RequestSectionID]

-- Update RequestLane

DECLARE @RequestLaneStatistics TABLE
(
	[RequestLaneID] BIGINT NOT NULL,
	[NumLanes] INT NOT NULL,
	[NumUnpublishedLanes] INT NOT NULL,
	[NumEditedLanes] INT NOT NULL,
	[NumDuplicateLanes] INT NOT NULL,
	[NumSections] INT NOT NULL,
	[NumDoNotMeetCommitmentLanes] INT NOT NULL
)
INSERT INTO @RequestLaneStatistics
(
	[RequestLaneID],
	[NumLanes],
	[NumUnpublishedLanes],
	[NumEditedLanes],
	[NumDuplicateLanes],
	[NumSections],
	[NumDoNotMeetCommitmentLanes]
)
SELECT RS.[RequestLaneID],
	ISNULL(SUM(CASE WHEN RS.IsActive = 1 AND RS.[IsInactiveViewable] = 1 THEN [NumLanes] ELSE 0 END), 0),
	ISNULL(SUM(CASE WHEN RS.IsActive = 1 AND RS.[IsInactiveViewable] = 1 THEN [NumUnPublishedLanes] ELSE 0 END), 0),
	ISNULL(SUM(CASE WHEN RS.IsActive = 1 AND RS.[IsInactiveViewable] = 1 THEN [NumEditedLanes] ELSE 0 END), 0),
	ISNULL(SUM(CASE WHEN RS.IsActive = 1 AND RS.[IsInactiveViewable] = 1 THEN [NumDuplicateLanes] ELSE 0 END), 0),
	ISNULL(SUM(CASE WHEN RS.IsActive = 1 AND RS.[IsInactiveViewable] = 1 THEN 1 ELSE 0 END), 0),
	ISNULL(SUM(CASE WHEN RS.IsActive = 1 AND RS.[IsInactiveViewable] = 1 THEN [NumDoNotMeetCommitmentLanes] ELSE 0 END), 0)
FROM dbo.RequestSection RS
WHERE RS.[RequestLaneID] = @RequestLaneID 
GROUP BY RS.[RequestLaneID]

UPDATE dbo.RequestLane
SET [NumLanes] = A.[NumLanes],
	[NumUnpublishedLanes] = A.[NumUnpublishedLanes],
	[NumEditedLanes] = A.[NumEditedLanes],
	[NumDuplicateLanes] = A.[NumDuplicateLanes],
	[NumDoNotMeetCommitmentLanes] = A.[NumDoNotMeetCommitmentLanes]
FROM @RequestLaneStatistics A
WHERE dbo.RequestLane.[RequestLaneID] = A.[RequestLaneID]

-- INSERT RequestLane_History

DECLARE @RequestLaneHistory TABLE
(
    [VersionNum]            INT             NOT NULL,
    [IsActive]              BIT             NOT NULL,
    [IsInactiveViewable]    BIT             NOT NULL,
    [RequestLaneVersionID] BIGINT          NOT NULL,
    [RequestNumber]         NVARCHAR (32)   NOT NULL,
	[NumSections]	INT NOT NULL,
	[NumLanes]	INT NOT NULL,
	[NumUnpublishedLanes]	INT NOT NULL,
	[NumDuplicateLanes]	INT NOT NULL,
	[NumEditedLanes]	INT NOT NULL,
	[NumDoNotMeetCommitmentLanes] INT NOT NULL,
    [IsValidData]           BIT             NOT NULL,
    [RequestLaneID]        BIGINT          NOT NULL
)

INSERT INTO @RequestLaneHistory
(
    [VersionNum],
    [IsActive],
    [IsInactiveViewable],
    [RequestLaneVersionID],
    [RequestNumber],
	[NumSections],
	[NumLanes],
	[NumUnpublishedLanes],
	[NumDuplicateLanes],
	[NumEditedLanes],
	[NumDoNotMeetCommitmentLanes],
    [IsValidData],
    [RequestLaneID]
)
SELECT RLH.[VersionNum],
    RLH.[IsActive],
    RLH.[IsInactiveViewable],
    RLH.[RequestLaneVersionID],
    RLH.[RequestNumber],
	RLH.[NumSections],
	RL.[NumLanes],
	RL.[NumUnpublishedLanes],
	RL.[NumDuplicateLanes],
	RL.[NumEditedLanes],
	RL.[NumDoNotMeetCommitmentLanes],
    RLH.[IsValidData],
    RLH.[RequestLaneID]
FROM dbo.RequestLane_History RLH
INNER JOIN dbo.RequestLane RL ON RLH.[RequestLaneID] = RL.[RequestLaneID]
WHERE RLH.[RequestLaneID] = @RequestLaneID
AND RLH.IsLatestVersion = 1

UPDATE dbo.RequestLane_History
SET IsLatestVersion = 0
WHERE dbo.RequestLane_History.RequestLaneVersionID IN (SELECT RequestLaneVersionID FROM @RequestLaneHistory)

INSERT INTO dbo.RequestLane_History
(	
	[VersionNum],
    [IsActive],
    [IsInactiveViewable],
    [RequestNumber],
	[NumSections],
	[NumLanes],
	[NumUnpublishedLanes],
	[NumEditedLanes],
	[NumDoNotMeetCommitmentLanes],
	[NumDuplicateLanes],
    [IsValidData],
    [RequestLaneID],
	UpdatedOn,
	UpdatedBy,
	Comments,
	IsLatestVersion
)
SELECT [VersionNum]+1,
    [IsActive],
    [IsInactiveViewable],
    [RequestNumber],
	[NumSections],
	[NumLanes],
	[NumUnpublishedLanes],
	[NumEditedLanes],
	[NumDoNotMeetCommitmentLanes],
	[NumDuplicateLanes],
    [IsValidData],
    [RequestLaneID],
	GETUTCDATE(),
	@UpdatedBy,
	@Comments,
	1
FROM @RequestLaneHistory

-- INSERT RequestSection_History

DECLARE @RequestLaneVersionID BIGINT;

SELECT @RequestLaneVersionID = RequestLaneVersionID
FROM dbo.RequestLane_History WHERE RequestLaneID = @RequestLaneID AND IsLatestVersion = 1;

DECLARE @RequestSectionHistory TABLE
(
	[VersionNum]          INT             NOT NULL,
    [IsActive]            BIT             NOT NULL,
    [IsInactiveViewable]  BIT             NOT NULL,
    [RequestSectionVersionID]          BIGINT        NOT NULL,
	[RequestSectionID]          BIGINT        NOT NULL,
	[RequestLaneVersionID]          BIGINT        NOT NULL,
    [SectionNumber]        NVARCHAR (50) NOT NULL, 
	[SectionName]        NVARCHAR (50) NOT NULL,
	[SubServiceLevelVersionID]        BIGINT NOT NULL,
	[WeightBreak]        NVARCHAR(MAX) NOT NULL,
	[WeightBreakHeaderVersionID]        BIGINT NOT NULL,
	[IsDensityPricing] [BIT] NOT NULL,
	[OverrideDensity] DECIMAL (19,6) NULL,
	[RateBaseVersionID]        BIGINT NULL,
	[OverrideClassVersionID]        BIGINT NULL,
	[EquipmentTypeVersionID]        BIGINT NULL, 
	[Commodity] NVARCHAR(100) NULL,
	[NumLanes] INT NOT NULL,
	[NumUnpublishedLanes] INT NOT NULL,
	[NumEditedLanes] INT NOT NULL,
	[NumDuplicateLanes] INT NOT NULL,
	[NumDoNotMeetCommitmentLanes] INT NOT NULL
)

INSERT INTO @RequestSectionHistory
(
	[VersionNum],
    [IsActive],
    [IsInactiveViewable],
    [RequestSectionVersionID],
	[RequestSectionID],
	[RequestLaneVersionID],
    [SectionNumber], 
	[SectionName],
	[SubServiceLevelVersionID],
	[WeightBreak],
	[WeightBreakHeaderVersionID],
	[IsDensityPricing],
	[OverrideDensity],
	[RateBaseVersionID],
	[OverrideClassVersionID],
	[EquipmentTypeVersionID], 
	[Commodity],
	[NumLanes],
	[NumUnpublishedLanes],
	[NumEditedLanes],
	[NumDuplicateLanes],
	[NumDoNotMeetCommitmentLanes]
)
SELECT RSH.[VersionNum],
    RSH.[IsActive],
    RSH.[IsInactiveViewable],
    RSH.[RequestSectionVersionID],
	RSH.[RequestSectionID],
	@RequestLaneVersionID,
    RSH.[SectionNumber], 
	RSH.[SectionName],
	RSH.[SubServiceLevelVersionID],
	RSH.[WeightBreak],
	RSH.[WeightBreakHeaderVersionID],
	RSH.[IsDensityPricing],
	RSH.[OverrideDensity],
	RSH.[RateBaseVersionID],
	RSH.[OverrideClassVersionID],
	RSH.[EquipmentTypeVersionID], 
	RSH.[Commodity],
	RS.[NumLanes],
	RS.[NumUnpublishedLanes],
	RS.[NumEditedLanes],
	RS.[NumDuplicateLanes],
	RS.[NumDoNotMeetCommitmentLanes]
FROM dbo.RequestSection_History RSH
INNER JOIN dbo.RequestSection RS ON RSH.[RequestSectionID] = RS.[RequestSectionID] AND RSH.IsLatestVersion = 1
INNER JOIN @DistinctRequestSectionID A ON RSH.[RequestSectionID] = A.ID

UPDATE dbo.RequestSection_History
SET IsLatestVersion = 0
WHERE dbo.RequestSection_History.RequestSectionVersionID IN (SELECT RequestSectionVersionID FROM @RequestSectionHistory)

DECLARE @RequestSectionVersion TABLE
(
	[RequestSectionID] BIGINT NOT NULL,
	[RequestSectionVersionID] BIGINT NOT NULL
)

INSERT INTO dbo.RequestSection_History
(
	[VersionNum],
    [IsActive],
    [IsInactiveViewable],
	[RequestSectionID],
	[RequestLaneVersionID],
    [SectionNumber], 
	[SectionName],
	[SubServiceLevelVersionID],
	[WeightBreak],
	[WeightBreakHeaderVersionID],
	[IsDensityPricing],
	[OverrideDensity],
	[RateBaseVersionID],
	[OverrideClassVersionID],
	[EquipmentTypeVersionID], 
	[Commodity],
	[NumLanes],
	[NumUnpublishedLanes],
	[NumEditedLanes],
	[NumDoNotMeetCommitmentLanes],
	[NumDuplicateLanes],
	UpdatedOn,
	UpdatedBy,
	Comments,
	IsLatestVersion
)
OUTPUT INSERTED.[RequestSectionID],
	INSERTED.[RequestSectionVersionID]
INTO @RequestSectionVersion
(
	[RequestSectionID],
	[RequestSectionVersionID]
)
SELECT [VersionNum] + 1,
    [IsActive],
    [IsInactiveViewable],
	[RequestSectionID],
	[RequestLaneVersionID],
    [SectionNumber], 
	[SectionName],
	[SubServiceLevelVersionID],
	[WeightBreak],
	[WeightBreakHeaderVersionID],
	[IsDensityPricing],
	[OverrideDensity],
	[RateBaseVersionID],
	[OverrideClassVersionID],
	[EquipmentTypeVersionID], 
	[Commodity],
	[NumLanes],
	[NumUnpublishedLanes],
	[NumEditedLanes],
	[NumDoNotMeetCommitmentLanes],
	[NumDuplicateLanes],
	GETUTCDATE(),
	@UpdatedBy,
	@Comments,
	1
FROM @RequestSectionHistory RSH

-- INSERT RequestSectionLane_History

DECLARE @RequestSectionLaneVersion TABLE
(
	[RequestSectionLaneID] BIGINT NOT NULL,
	[RequestSectionLaneVersionID] BIGINT NOT NULL
)

INSERT INTO dbo.RequestSectionLane_History
(
	[VersionNum],
    [IsLatestVersion],
    [UpdatedOn],
    [UpdatedBy],
    [Comments],
	[IsActive],
    [IsInactiveViewable],
	[RequestSectionLaneID],
	[RequestSectionVersionID],
    [LaneNumber],
	[IsPublished],
	[IsEdited],
	[IsDuplicate],
	[IsBetween],
	[IsLaneGroup],
	[OriginProvinceVersionID],
	[OriginProvinceCode],
	[OriginRegionVersionID],
	[OriginRegionCode],
	[OriginCountryVersionID],
	[OriginCountryCode],
	[OriginTerminalVersionID],
	[OriginTerminalCode],
	[OriginZoneVersionID],
	[OriginZoneName],
	[OriginBasingPointVersionID],
	[OriginBasingPointName],
	[OriginServicePointVersionID],
	[OriginServicePointName],
	[OriginPostalCodeVersionID],
	[OriginPostalCodeName],
	[OriginPointTypeVersionID],
	[OriginPointTypeName],
	[OriginCode],
	[DestinationProvinceVersionID],
	[DestinationProvinceCode],
	[DestinationRegionVersionID],
	[DestinationRegionCode],
	[DestinationCountryVersionID],
	[DestinationCountryCode],
	[DestinationTerminalVersionID],
	[DestinationTerminalCode],
	[DestinationZoneVersionID],
	[DestinationZoneName],
	[DestinationBasingPointVersionID],
	[DestinationBasingPointName],
	[DestinationServicePointVersionID],
	[DestinationServicePointName],
	[DestinationPostalCodeVersionID],
	[DestinationPostalCodeName],
	[DestinationPointTypeVersionID],
	[DestinationPointTypeName],
	[DestinationCode],
	[LaneHashCode],
	[BasingPointHashCode],
	[Cost],
	[DoNotMeetCommitment],
	[Commitment],
	[CustomerRate],
	[CustomerDiscount],
	[DrRate],
	[PartnerRate],
	[PartnerDiscount],
	[Profitability],
	[PickupCount],
	[DeliveryCount],
	[DockAdjustment],
	[Margin],
	[Density],
	[PickupCost],
	[DeliveryCost],
	[AccessorialsValue],
	[AccessorialsPercentage]
)
OUTPUT INSERTED.[RequestSectionLaneID],
	INSERTED.[RequestSectionLaneVersionID]
INTO @RequestSectionLaneVersion
(
	[RequestSectionLaneID],
	[RequestSectionLaneVersionID]
)
SELECT 	1,
    1,
    GETUTCDATE(),
    @UpdatedBy,
    @Comments,
	RSL.[IsActive],
    RSL.[IsInactiveViewable],
	RSL.[NewRequestSectionLaneID],
	RS.[RequestSectionVersionID],
    RSL.[LaneNumber],
	RSL.[IsPublished],
	RSL.[IsEdited],
	RSL.[IsDuplicate],
	RSL.[IsBetween],
	RSL.[IsLaneGroup],
	O_P.[ProvinceVersionID],
	RSL.[OriginProvinceCode],
	O_R.[RegionVersionID],
	RSL.[OriginRegionCode],
	O_C.[CountryVersionID],
	RSL.[OriginCountryCode],
	O_T.[TerminalVersionID],
	RSL.[OriginTerminalCode],
	O_Z.[ZoneVersionID],
	RSL.[OriginZoneName],
	O_BP.[BasingPointVersionID],
	RSL.[OriginBasingPointName],
	O_Y.[ServicePointVersionID],
	RSL.[OriginServicePointName],
	O_PC.[PostalCodeVersionID],
	RSL.[OriginPostalCodeName],
	O_PT.[PointTypeVersionID],
	RSL.[OriginPointTypeName],
	RSL.[OriginCode],
	D_P.[ProvinceVersionID],
	RSL.[DestinationProvinceCode],
	D_R.[RegionVersionID],
	RSL.[DestinationRegionCode],
	D_C.[CountryVersionID],
	RSL.[DestinationCountryCode],
	D_T.[TerminalVersionID],
	RSL.[DestinationTerminalCode],
	D_Z.[ZoneVersionID],
	RSL.[DestinationZoneName],
	D_BP.[BasingPointVersionID],
	RSL.[DestinationBasingPointName],
	D_Y.[ServicePointVersionID],
	RSL.[DestinationServicePointName],
	D_PC.[PostalCodeVersionID],
	RSL.[DestinationPostalCodeName],
	D_PT.[PointTypeVersionID],
	RSL.[DestinationPointTypeName],
	RSL.[DestinationCode],
	RSL.[LaneHashCode],
	RSL.[BasingPointHashCode],
	RSL.[Cost],
	RSL.[DoNotMeetCommitment],
	RSL.[Commitment],
	RSL.[CustomerRate],
	RSL.[CustomerDiscount],
	RSL.[DrRate],
	RSL.[PartnerRate],
	RSL.[PartnerDiscount],
	RSL.[Profitability],
	RSL.[PickupCount],
	RSL.[DeliveryCount],
	RSL.[DockAdjustment],
	RSL.[Margin],
	RSL.[Density],
	RSL.[PickupCost],
	RSL.[DeliveryCost],
	RSL.[AccessorialsValue],
	RSL.[AccessorialsPercentage]
FROM @NewRequestSectionLaneTableType RSL
INNER JOIN @RequestSectionVersion RS ON RSL.RequestSectionID = RS.RequestSectionID
INNER JOIN @PointTypeVersionID O_PT ON RSL.OriginPointTypeID = O_PT.PointTypeID
INNER JOIN @PointTypeVersionID D_PT ON RSL.DestinationPointTypeID = D_PT.PointTypeID
LEFT JOIN @ProvinceVersionID O_P ON RSL.OriginProvinceID = O_P.ProvinceID
LEFT JOIN @ProvinceVersionID D_P ON RSL.DestinationProvinceID = D_P.ProvinceID
LEFT JOIN @RegionVersionID O_R ON RSL.OriginRegionID = O_R.RegionID
LEFT JOIN @RegionVersionID D_R ON RSL.DestinationRegionID = D_R.RegionID
LEFT JOIN @CountryVersionID O_C ON RSL.OriginCountryID = O_C.CountryID
LEFT JOIN @CountryVersionID D_C ON RSL.DestinationCountryID = D_C.CountryID
LEFT JOIN @ServicePointVersionID O_Y ON RSL.OriginServicePointID = O_Y.ServicePointID
LEFT JOIN @ServicePointVersionID D_Y ON RSL.DestinationServicePointID = D_Y.ServicePointID
LEFT JOIN @TerminalVersionID O_T ON RSL.OriginTerminalID = O_T.TerminalID
LEFT JOIN @TerminalVersionID D_T ON RSL.DestinationTerminalID = D_T.TerminalID
LEFT JOIN @PostalCodeVersionID O_PC ON RSL.OriginPostalCodeID = O_PC.PostalCodeID
LEFT JOIN @PostalCodeVersionID D_PC ON RSL.DestinationPostalCodeID = D_PC.PostalCodeID
LEFT JOIN @ZoneVersionID O_Z ON RSL.OriginZoneID = O_Z.ZoneID
LEFT JOIN @ZoneVersionID D_Z ON RSL.DestinationZoneID = D_Z.ZoneID
LEFT JOIN @BasingPointVersionID O_BP ON RSL.OriginBasingPointID = O_BP.BasingPointID
LEFT JOIN @BasingPointVersionID D_BP ON RSL.DestinationBasingPointID = D_BP.BasingPointID

-- Update the history of existing modified request-section-lanes

DECLARE @RequestSectionLaneTableTypeID  IDTableType;

INSERT INTO @RequestSectionLaneTableTypeID
(	
	ID
)
SELECT [RequestSectionLaneID]
FROM @ToBeUpDatedRequestSectionLane

EXEC dbo.RequestSectionLane_History_Update @RequestSectionLaneTableTypeID, @UpdatedBy, @Comments

-- INSERT RequestSectionLanePricingPoint

DECLARE @RequestSectionCost TABLE
(
	[RequestSectionID] BIGINT NOT NULL,
	[Cost] NVARCHAR(MAX) NOT NULL
)

INSERT INTO @RequestSectionCost
(
	[RequestSectionID],
	[Cost]
)
SELECT ID,
	dbo.GetRequestSectionLaneDefaultCost(ID)
FROM @DistinctRequestSectionID

DECLARE @RequestSectionLaneCost TABLE
(
	[RequestSectionLaneID] BIGINT NOT NULL,
	[Cost] NVARCHAR(MAX) NOT NULL
)

INSERT INTO @RequestSectionLaneCost
(
	[RequestSectionLaneID],
	[Cost]
)
SELECT RSL.RequestSectionLaneID,
	RS.[Cost]
FROM @RequestSectionLaneTableType RSL
INNER JOIN @RequestSectionCost RS ON RSL.RequestSectionID = RS.RequestSectionID
WHERE RSL.RequestSectionLaneID IS NOT NULL

DECLARE @RequestSectionLanePricingPoint RequestSectionLanePricingPointTableType;

INSERT INTO @RequestSectionLanePricingPoint
(	
	[IsActive],
	[IsInactiveViewable],
	[RequestSectionLaneID],
	[PricingPointNumber],
	[OriginPostalCodeID],
	[OriginPostalCodeName],
	[DestinationPostalCodeID],
	[DestinationPostalCodeName],
	[PricingPointHashCode],
	[Cost],
	[DrRate],
	[FakRate],
	[Profitability],
	[SplitsAll],
	[SplitsAllUsagePercentage],
	[PickupCount],
	[DeliveryCount],
	[DockAdjustment],
	[Margin],
	[Density],
	[PickupCost],
	[DeliveryCost],
	[AccessorialsValue],
	[AccessorialsPercentage]
)
SELECT 1,
	1,
	NRSL.[NewRequestSectionLaneID],
	REPLACE(NEWID(), '-', ''),
	PP.[OriginPostalCodeID],
	PP.[OriginPostalCodeName],
	PP.[DestinationPostalCodeID],
	PP.[DestinationPostalCodeName],
	PP.[PricingPointHashCode],
	RSLC.Cost,
	RSLC.Cost,
	RSLC.Cost,
	RSLC.Cost,
	RSLC.Cost,
	0,
	NULL,
	NULL,
	NULL,
	RSLC.Cost,
	RSLC.Cost,
	RSLC.Cost,
	RSLC.Cost,
	RSLC.Cost,
	RSLC.Cost
FROM [dbo].[RequestSectionLanePricingPoint] PP
INNER JOIN @RequestSectionLaneTableType RSL ON PP.RequestSectionLaneID = RSL.RequestSectionLaneID
INNER JOIN @NewRequestSectionLaneTableType NRSL ON RSL.LaneNumber = NRSL.LaneNumber
INNER JOIN @RequestSectionLaneCost RSLC ON RSL.RequestSectionLaneID = RSLC.RequestSectionLaneID
WHERE PP.IsActive = 1 AND PP.IsInactiveViewable = 1 

EXEC dbo.RequestSectionLanePricingPoint_Insert_Bulk @RequestSectionLanePricingPoint, @UpdatedBy, @Comments

SELECT CAST(
(SELECT *
FROM
(
	SELECT 
		(SELECT * 
		FROM @RequestSectionLaneTableType
		WHERE [LaneNumber] IN (SELECT [LaneNumber] FROM @IdenticalRequestSectionLane)
		FOR JSON AUTO) AS identical_lanes_not_added,
		(SELECT * 
		FROM @RequestSectionLaneTableType
		WHERE [LaneNumber] IN (SELECT [LaneNumber] FROM @DuplicateRequestSectionLane)
		FOR JSON AUTO) AS duplicate_lanes_added
	) AS Q
FOR JSON AUTO, WITHOUT_ARRAY_WRAPPER)
AS VARCHAR(MAX))

COMMIT TRAN
RETURN 1

