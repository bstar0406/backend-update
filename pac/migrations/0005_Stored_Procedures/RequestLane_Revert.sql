CREATE OR ALTER PROCEDURE [dbo].[RequestLane_Revert]
	@RequestID		BIGINT,
	@VersionNum	INT,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL

AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ERROR3 INT, @ERROR4 INT, @ERROR5 INT, @ERROR6 INT;

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Saving RequestLane_History.';

BEGIN TRAN

DECLARE @RequestLaneVersionID BIGINT, @RequestLaneID BIGINT, @LatestRequestLaneVersionID BIGINT;

SELECT @RequestLaneVersionID = RLH.RequestLaneVersionID,
	@RequestLaneID = RLH.RequestLaneID
FROM dbo.RequestLane_History RLH
INNER JOIN dbo.Request_History R ON RLH.RequestLaneVersionID = R.RequestLaneVersionID
WHERE R.RequestID = @RequestID AND R.VersionNum = @VersionNum

SELECT @LatestRequestLaneVersionID = R.RequestLaneVersionID
FROM dbo.Request_History R
WHERE R.RequestID = @RequestID AND R.IsLatestVersion = 1

DECLARE @RequestSectionVersionID TABLE
(
	[RequestSectionVersionID] BIGINT        NOT NULL,
	[RequestSectionID] BIGINT        NOT NULL
)
INSERT INTO @RequestSectionVersionID
(
	[RequestSectionVersionID],
	[RequestSectionID]
)
SELECT [RequestSectionVersionID], [RequestSectionID]
FROM
(SELECT [RequestSectionVersionID], [RequestSectionID],
	ROW_NUMBER() OVER(PARTITION BY RequestSectionID ORDER BY VersionNum DESC) AS RN
FROM dbo.RequestSection_History
WHERE RequestLaneVersionID = @RequestLaneVersionID) AS A
WHERE A.RN = 1

DECLARE @RequestSectionID TABLE
(
	[RequestSectionID] BIGINT        NOT NULL
)
INSERT INTO @RequestSectionID
(
	[RequestSectionID]
)
SELECT [RequestSectionID]
FROM dbo.RequestSection
WHERE RequestLaneID = @RequestLaneID

DECLARE @RequestSectionToBeDeleted TABLE
(
	[RequestSectionID] BIGINT        NOT NULL
) 
INSERT INTO @RequestSectionToBeDeleted
(
	[RequestSectionID]
)
SELECT [RequestSectionID]
FROM @RequestSectionID
WHERE [RequestSectionID] NOT IN (SELECT [RequestSectionID] FROM @RequestSectionVersionID)

DECLARE @LatestRequestSectionVersionNum TABLE
(
	[RequestSectionID] BIGINT        NOT NULL,
	[RequestSectionVersionID] BIGINT        NOT NULL,
	[VersionNum] INT NOT NULL
)
INSERT INTO @LatestRequestSectionVersionNum
(
	[RequestSectionID],
	[RequestSectionVersionID],
	[VersionNum]
)
SELECT RSH.[RequestSectionID],
	RSH.[RequestSectionVersionID],
	RSH.[VersionNum]
FROM dbo.RequestSection_History RSH
INNER JOIN @RequestSectionID RS ON RSH.[RequestSectionID] = RS.[RequestSectionID]
WHERE RSH.IsLatestVersion = 1

DECLARE @RequestSectionHistory TABLE
(
	[VersionNum]          INT             NOT NULL,
    [IsActive]            BIT             NOT NULL,
    [IsInactiveViewable]  BIT             NOT NULL,
    [RequestSectionVersionID]          BIGINT,
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
SELECT VN.[VersionNum],
    [IsActive],
    [IsInactiveViewable],
    RSH.[RequestSectionVersionID],
	RSH.[RequestSectionID],
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
FROM dbo.RequestSection_History RSH
INNER JOIN @LatestRequestSectionVersionNum VN ON RSH.[RequestSectionID] = VN.[RequestSectionID]
WHERE RSH.RequestSectionVersionID IN (SELECT RequestSectionVersionID FROM @RequestSectionVersionID)
UNION
SELECT VN.[VersionNum],
    0,
    [IsInactiveViewable],
    RSH.[RequestSectionVersionID],
	RSH.[RequestSectionID],
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
FROM dbo.RequestSection_History RSH
INNER JOIN @LatestRequestSectionVersionNum VN ON RSH.RequestSectionVersionID = VN.RequestSectionVersionID
WHERE VN.RequestSectionID IN (SELECT RequestSectionID FROM @RequestSectionToBeDeleted)

UPDATE dbo.RequestSection_History
SET IsLatestVersion = 0
WHERE dbo.RequestSection_History.RequestSectionVersionID IN (SELECT RequestSectionVersionID FROM @LatestRequestSectionVersionNum)

UPDATE dbo.RequestSection
SET [IsActive] = A.[IsActive],
	[IsInactiveViewable] = A.[IsInactiveViewable],
	[SectionNumber] = A.[SectionNumber],
	[SectionName] = A.[SectionName],
	[WeightBreak] = A.[WeightBreak],
	[IsDensityPricing] = A.[IsDensityPricing],
	[OverrideDensity] = A.[OverrideDensity],
	[Commodity] = A.[Commodity],
	[NumLanes] = A.[NumLanes],
	[NumUnpublishedLanes] = A.[NumUnpublishedLanes],
	[NumEditedLanes] = A.[NumEditedLanes],
	[NumDuplicateLanes] = A.[NumDuplicateLanes],
	[NumDoNotMeetCommitmentLanes] = A.[NumDoNotMeetCommitmentLanes],
	[EquipmentTypeID] = E.[EquipmentTypeID],
	[OverrideClassID] = FC.[FreightClassID],
	[RateBaseID] = RB.[RateBaseID],
	[RequestLaneID] = @RequestLaneID,
	[SubServiceLevelID] = SL.[SubServiceLevelID],
	[WeightBreakHeaderID] = WB.[WeightBreakHeaderID]
FROM @RequestSectionHistory A
LEFT JOIN dbo.[EquipmentType_History] E ON A.[EquipmentTypeVersionID] = E.[EquipmentTypeVersionID]
LEFT JOIN dbo.[FreightClass_History] FC ON A.[OverrideClassVersionID] = FC.[FreightClassVersionID]
LEFT JOIN dbo.[RateBase_History] RB ON A.[RateBaseVersionID] = RB.[RateBaseVersionID]
LEFT JOIN dbo.[SubServiceLevel_History] SL ON A.[SubServiceLevelVersionID] = SL.[SubServiceLevelVersionID]
LEFT JOIN dbo.[WeightBreakHeader_History] WB ON A.[WeightBreakHeaderVersionID] = WB.[WeightBreakHeaderVersionID]
WHERE dbo.RequestSection.RequestSectionID = A.RequestSectionID

SELECT @ERROR1 = @@ERROR

DECLARE @RequestSectionVersion TABLE
(
	[RequestSectionID] BIGINT        NOT NULL,
	[RequestSectionVersionID] BIGINT        NOT NULL
)

INSERT INTO dbo.RequestSection_History
(
	[VersionNum],
    [IsLatestVersion],
    [UpdatedOn],
    [UpdatedBy],
    [Comments],
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
	[NumDuplicateLanes],
	[NumDoNotMeetCommitmentLanes]
)
OUTPUT INSERTED.RequestSectionID,
	INSERTED.RequestSectionVersionID
INTO @RequestSectionVersion
(
	RequestSectionID,
	RequestSectionVersionID
)
SELECT [VersionNum]+1,
	1,
	GETUTCDATE(),
	@UpdatedBy,
	@Comments,
	[IsActive],
    [IsInactiveViewable],
	[RequestSectionID],
	@LatestRequestLaneVersionID,
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
FROM @RequestSectionHistory

SELECT @ERROR2 = @@ERROR

DECLARE @RequestSectionLaneVersionID TABLE
(
	[RequestSectionLaneVersionID] BIGINT        NOT NULL,
	[RequestSectionLaneID] BIGINT        NOT NULL,
	[RequestSectionVersionID] BIGINT        NOT NULL
)
INSERT INTO @RequestSectionLaneVersionID
(
	[RequestSectionLaneVersionID],
	[RequestSectionLaneID],
	[RequestSectionVersionID]
)
SELECT [RequestSectionLaneVersionID], [RequestSectionLaneID], [RequestSectionVersionID]
FROM
(SELECT RSLH.[RequestSectionLaneVersionID], 
	RSLH.[RequestSectionLaneID], 
	RSLH.[RequestSectionVersionID],
	ROW_NUMBER() OVER(PARTITION BY [RequestSectionLaneID] ORDER BY VersionNum DESC) AS RN
FROM dbo.RequestSectionLane_History RSLH
INNER JOIN @RequestSectionVersionID RSV ON RSLH.[RequestSectionVersionID] = RSV.[RequestSectionVersionID]) AS A
WHERE A.RN = 1

DECLARE @RequestSectionLaneID TABLE
(
	[RequestSectionLaneID] BIGINT        NOT NULL,
	[RequestSectionID] BIGINT        NOT NULL
)
INSERT INTO @RequestSectionLaneID
(
	[RequestSectionLaneID],
	[RequestSectionID]
)
SELECT [RequestSectionLaneID], [RequestSectionID]
FROM dbo.RequestSectionLane
WHERE RequestSectionID IN (SELECT RequestSectionID FROM @RequestSectionID)

DECLARE @RequestSectionLaneToBeDeleted TABLE
(
	[RequestSectionLaneID] BIGINT        NOT NULL
)
INSERT INTO @RequestSectionLaneToBeDeleted
(
	[RequestSectionLaneID]
)
SELECT [RequestSectionLaneID] 
FROM @RequestSectionLaneID
WHERE [RequestSectionLaneID] NOT IN (SELECT [RequestSectionLaneID] FROM @RequestSectionLaneVersionID)

DECLARE @LatestRequestSectionLaneVersionNum TABLE
(
	[RequestSectionLaneID] BIGINT        NOT NULL,
	[RequestSectionLaneVersionID] BIGINT        NOT NULL,
	[VersionNum] INT NOT NULL
)
INSERT INTO @LatestRequestSectionLaneVersionNum
(
	[RequestSectionLaneID],
	[RequestSectionLaneVersionID],
	[VersionNum]
)
SELECT RSH.[RequestSectionLaneID],
	RSH.[RequestSectionLaneVersionID],
	RSH.[VersionNum]
FROM dbo.RequestSectionLane_History RSH
INNER JOIN @RequestSectionLaneID RS ON RSH.[RequestSectionLaneID] = RS.[RequestSectionLaneID]
WHERE RSH.IsLatestVersion = 1

DECLARE @RequestSectionLaneHistory TABLE
(
	[VersionNum]          INT             NOT NULL,
	[IsActive]           BIT           NOT NULL,
    [IsInactiveViewable] BIT           NOT NULL,
	[RequestSectionLaneVersionID]          BIGINT        NOT NULL,
	[RequestSectionLaneID]          BIGINT    NOT NULL,
	[RequestSectionVersionID]          BIGINT        NOT NULL,
    [LaneNumber]        NVARCHAR(32) NOT NULL,
	[IsPublished]        BIT NOT NULL,
	[IsEdited]        BIT NOT NULL,
	[IsDuplicate]        BIT NOT NULL,
	[IsBetween]        BIT NOT NULL,
	[IsLaneGroup]        BIT NOT NULL,
	[OriginProvinceVersionID] BIGINT NULL,
	[OriginProvinceCode] NVARCHAR(2) NULL,
	[OriginRegionVersionID] BIGINT NULL,
	[OriginRegionCode] NVARCHAR(4) NULL,
	[OriginCountryVersionID] BIGINT NULL,
	[OriginCountryCode] NVARCHAR(2) NULL,
	[OriginTerminalVersionID] BIGINT NULL,
	[OriginTerminalCode] NVARCHAR(3) NULL,
	[OriginZoneVersionID] BIGINT NULL,
	[OriginZoneName] NVARCHAR(50) NULL,
	[OriginBasingPointVersionID] BIGINT NULL,
	[OriginBasingPointName] NVARCHAR(50) NULL,
	[OriginServicePointVersionID] BIGINT NULL,
	[OriginServicePointName] NVARCHAR(50) NULL,
	[OriginPostalCodeVersionID] BIGINT NULL,
	[OriginPostalCodeName] NVARCHAR(10) NULL,
	[OriginPointTypeVersionID] BIGINT NOT NULL,
	[OriginPointTypeName] NVARCHAR(50) NOT NULL,
	[OriginCode] NVARCHAR(50) NOT NULL,
	[DestinationProvinceVersionID] BIGINT NULL,
	[DestinationProvinceCode] NVARCHAR(2) NULL,
	[DestinationRegionVersionID] BIGINT NULL,
	[DestinationRegionCode] NVARCHAR(4) NULL,
	[DestinationCountryVersionID] BIGINT NULL,
	[DestinationCountryCode] NVARCHAR(2) NULL,
	[DestinationTerminalVersionID] BIGINT NULL,
	[DestinationTerminalCode] NVARCHAR(3) NULL,
	[DestinationZoneVersionID] BIGINT NULL,
	[DestinationZoneName] NVARCHAR(50) NULL,
	[DestinationBasingPointVersionID] BIGINT NULL,
	[DestinationBasingPointName] NVARCHAR(50) NULL,
	[DestinationServicePointVersionID] BIGINT NULL,
	[DestinationServicePointName] NVARCHAR(50) NULL,
	[DestinationPostalCodeVersionID] BIGINT NULL,
	[DestinationPostalCodeName] NVARCHAR(10) NULL,
	[DestinationPointTypeVersionID] BIGINT NOT NULL,
	[DestinationPointTypeName] NVARCHAR(50) NOT NULL,
	[DestinationCode] NVARCHAR(50) NOT NULL,
	[LaneHashCode] VARBINARY(8000) NOT NULL,
	[BasingPointHashCode] VARBINARY(8000) NULL,
	[Cost]        NVARCHAR(MAX) NULL,
	[DoNotMeetCommitment] BIT NOT NULL,
	[Commitment] NVARCHAR(MAX) NULL,
	[CustomerRate] NVARCHAR(MAX) NOT NULL,
	[CustomerDiscount] NVARCHAR(MAX) NOT NULL,
	[DrRate] NVARCHAR(MAX) NOT NULL,
	[PartnerRate] NVARCHAR(MAX) NOT NULL,
	[PartnerDiscount] NVARCHAR(MAX) NOT NULL,
	[Profitability] NVARCHAR(MAX) NOT NULL,
	[PickupCount] INT NULL,
	[DeliveryCount] INT NULL,
	[DockAdjustment] DECIMAL(19,6) NULL,
	[Margin] NVARCHAR(MAX) NOT NULL,
	[Density] NVARCHAR(MAX) NOT NULL,
	[PickupCost] NVARCHAR(MAX) NOT NULL,
	[DeliveryCost] NVARCHAR(MAX) NOT NULL,
	[AccessorialsValue] NVARCHAR(MAX) NOT NULL,
	[AccessorialsPercentage] NVARCHAR(MAX) NOT NULL
)

INSERT INTO @RequestSectionLaneHistory
(
	[VersionNum],
	[IsActive],
    [IsInactiveViewable],
	[RequestSectionLaneVersionID],
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
SELECT VN.[VersionNum],
	[IsActive],
    [IsInactiveViewable],
	RSLH.[RequestSectionLaneVersionID],
	RSLH.[RequestSectionLaneID],
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
FROM dbo.RequestSectionLane_History RSLH
INNER JOIN @LatestRequestSectionLaneVersionNum VN ON RSLH.[RequestSectionLaneID] = VN.[RequestSectionLaneID]
WHERE RSLH.RequestSectionLaneVersionID IN (SELECT RequestSectionLaneVersionID FROM @RequestSectionLaneVersionID)
UNION
SELECT VN.[VersionNum],
	0,
    [IsInactiveViewable],
	RSLH.[RequestSectionLaneVersionID],
	RSLH.[RequestSectionLaneID],
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
FROM dbo.RequestSectionLane_History RSLH
INNER JOIN @LatestRequestSectionLaneVersionNum VN ON RSLH.RequestSectionLaneVersionID = VN.RequestSectionLaneVersionID
WHERE VN.RequestSectionLaneID IN (SELECT RequestSectionLaneID FROM @RequestSectionLaneToBeDeleted)

UPDATE dbo.RequestSectionLane_History 
SET IsLatestVersion = 0
WHERE dbo.RequestSectionLane_History.RequestSectionLaneVersionID IN (SELECT RequestSectionLaneVersionID FROM @LatestRequestSectionLaneVersionNum)

UPDATE dbo.RequestSectionLane
SET [IsActive] = A.[IsActive],
	[IsInactiveViewable] = A.[IsInactiveViewable],
	[LaneNumber] = A.[LaneNumber],
	[IsPublished] = A.[IsPublished],
	[IsEdited] = A.[IsEdited],
	[IsDuplicate] = A.[IsDuplicate],
	[IsBetween] = A.[IsBetween],
	[IsLaneGroup] = A.[IsLaneGroup],
	[OriginProvinceID] = O_P.[ProvinceID],
	[OriginProvinceCode] = A.[OriginProvinceCode],
	[OriginRegionID] = O_R.[RegionID],
	[OriginRegionCode] = A.[OriginRegionCode],
	[OriginCountryID] = O_C.[CountryID],
	[OriginCountryCode] = A.[OriginCountryCode],
	[OriginTerminalID] = O_T.[TerminalID],
	[OriginTerminalCode] = A.[OriginTerminalCode],
	[OriginZoneID] = O_Z.[ZoneID],
	[OriginZoneName] = A.[OriginZoneName],
	[OriginBasingPointID] = O_BP.[BasingPointID],
	[OriginBasingPointName] = A.[OriginBasingPointName],
	[OriginServicePointID] = O_SP.[ServicePointID],
	[OriginServicePointName] = A.[OriginServicePointName],
	[OriginPostalCodeID] = O_PC.[PostalCodeID],
	[OriginPostalCodeName] = A.[OriginPostalCodeName],
	[OriginPointTypeID] = O_PT.[RequestSectionLanePointTypeID],
	[OriginPointTypeName] = A.[OriginPointTypeName],
	[OriginCode] = A.[OriginCode],
	[DestinationProvinceID] = D_P.[ProvinceID],
	[DestinationProvinceCode] = A.[DestinationProvinceCode],
	[DestinationRegionID] = D_R.[RegionID],
	[DestinationRegionCode] = A.[DestinationRegionCode],
	[DestinationCountryID] = D_C.[CountryID],
	[DestinationCountryCode] = A.[DestinationCountryCode],
	[DestinationTerminalID] = D_T.[TerminalID],
	[DestinationTerminalCode] = A.[DestinationTerminalCode],
	[DestinationZoneID] = D_Z.[ZoneID],
	[DestinationZoneName] = A.[DestinationZoneName],
	[DestinationBasingPointID] = D_BP.[BasingPointID],
	[DestinationBasingPointName] = A.[DestinationBasingPointName],
	[DestinationServicePointID] = D_SP.[ServicePointID],
	[DestinationServicePointName] = A.[DestinationServicePointName],
	[DestinationPostalCodeID] = D_PC.[PostalCodeID],
	[DestinationPostalCodeName] = A.[DestinationPostalCodeName],
	[DestinationPointTypeID] = D_PT.[RequestSectionLanePointTypeID],
	[DestinationPointTypeName] = A.[DestinationPointTypeName],
	[DestinationCode] = A.[DestinationCode],
	[LaneHashCode] = A.[LaneHashCode],
	[BasingPointHashCode] = A.[BasingPointHashCode],
	[Cost] = A.[Cost],
	[DoNotMeetCommitment] = A.[DoNotMeetCommitment],
	[Commitment] = A.[Commitment],
	[CustomerRate] = A.[CustomerRate],
	[CustomerDiscount] = A.[CustomerDiscount],
	[DrRate] = A.[DrRate],
	[PartnerRate] = A.[PartnerRate],
	[PartnerDiscount] = A.[PartnerDiscount],
	[Profitability] = A.[Profitability],
	[PickupCount] = A.[PickupCount],
	[DeliveryCount] = A.[DeliveryCount],
	[DockAdjustment] = A.[DockAdjustment],
	[Margin] = A.[Margin],
	[Density] = A.[Density],
	[PickupCost] = A.[PickupCost],
	[DeliveryCost] = A.[DeliveryCost],
	[AccessorialsValue] = A.[AccessorialsValue],
	[AccessorialsPercentage] = A.[AccessorialsPercentage]
FROM @RequestSectionLaneHistory A
LEFT JOIN dbo.[Province_History] O_P ON A.[OriginProvinceVersionID] = O_P.[ProvinceVersionID]
LEFT JOIN dbo.[Province_History] D_P ON A.[DestinationProvinceVersionID] = D_P.[ProvinceVersionID]
LEFT JOIN dbo.[Region_History] O_R ON A.[OriginRegionVersionID] = O_R.[RegionVersionID]
LEFT JOIN dbo.[Region_History] D_R ON A.[DestinationRegionVersionID] = D_R.[RegionVersionID]
LEFT JOIN dbo.[Country_History] O_C ON A.[OriginCountryVersionID] = O_C.[CountryVersionID]
LEFT JOIN dbo.[Country_History] D_C ON A.[DestinationCountryVersionID] = D_C.[CountryVersionID]
LEFT JOIN dbo.[Terminal_History] O_T ON A.[OriginTerminalVersionID] = O_T.[TerminalVersionID]
LEFT JOIN dbo.[Terminal_History] D_T ON A.[DestinationTerminalVersionID] = D_T.[TerminalVersionID]
LEFT JOIN dbo.[Zone_History] O_Z ON A.[OriginZoneVersionID] = O_Z.[ZoneVersionID]
LEFT JOIN dbo.[Zone_History] D_Z ON A.[DestinationZoneVersionID] = D_Z.[ZoneVersionID]
LEFT JOIN dbo.[BasingPoint_History] O_BP ON A.[OriginBasingPointVersionID] = O_BP.[BasingPointVersionID]
LEFT JOIN dbo.[BasingPoint_History] D_BP ON A.[DestinationBasingPointVersionID] = D_BP.[BasingPointVersionID]
LEFT JOIN dbo.[ServicePoint_History] O_SP ON A.[OriginServicePointVersionID] = O_SP.[ServicePointVersionID]
LEFT JOIN dbo.[ServicePoint_History] D_SP ON A.[DestinationServicePointVersionID] = D_SP.[ServicePointVersionID]
LEFT JOIN dbo.[PostalCode_History] O_PC ON A.[OriginPostalCodeVersionID] = O_PC.[PostalCodeVersionID]
LEFT JOIN dbo.[PostalCode_History] D_PC ON A.[DestinationPostalCodeVersionID] = D_PC.[PostalCodeVersionID]
LEFT JOIN dbo.[RequestSectionLanePointType_History] O_PT ON A.[OriginPointTypeVersionID] = O_PT.[RequestSectionLanePointTypeVersionID]
LEFT JOIN dbo.[RequestSectionLanePointType_History] D_PT ON A.[DestinationPointTypeVersionID] = D_PT.[RequestSectionLanePointTypeVersionID]
WHERE dbo.RequestSectionLane.RequestSectionLaneID = A.RequestSectionLaneID

SELECT @ERROR3 = @@ERROR

-- Insert INTO RequestSectionLane_History

DECLARE @RequestSectionLaneVersion TABLE
(
	[RequestSectionLaneID] BIGINT        NOT NULL,
	[RequestSectionLaneVersionID] BIGINT        NOT NULL
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
OUTPUT INSERTED.RequestSectionLaneVersionID,
	INSERTED.RequestSectionLaneID
INTO @RequestSectionLaneVersion
(
	RequestSectionLaneVersionID,
	RequestSectionLaneID
)
SELECT [VersionNum]+1,
	1,
	GETUTCDATE(),
	@UpdatedBy,
	@Comments,
	[IsActive],
    [IsInactiveViewable],
	RSLH.[RequestSectionLaneID],
	RS.[RequestSectionVersionID],
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
FROM @RequestSectionLaneHistory RSLH
INNER JOIN @RequestSectionLaneID RSL ON RSLH.RequestSectionLaneID = RSL.RequestSectionLaneID
INNER JOIN @RequestSectionVersion RS ON RSL.RequestSectionID = RS.RequestSectionID

SELECT @ERROR4 = @@ERROR

DECLARE @RequestSectionLanePricingPointVersionID TABLE
(
	[RequestSectionLanePricingPointVersionID] BIGINT        NOT NULL,
	[RequestSectionLanePricingPointID] BIGINT        NOT NULL,
	[RequestSectionLaneVersionID] BIGINT        NOT NULL
)
INSERT INTO @RequestSectionLanePricingPointVersionID
(
	[RequestSectionLanePricingPointVersionID],
	[RequestSectionLanePricingPointID],
	[RequestSectionLaneVersionID]
)
SELECT [RequestSectionLanePricingPointVersionID], [RequestSectionLanePricingPointID], [RequestSectionLaneVersionID]
FROM
(SELECT RSLH.[RequestSectionLanePricingPointVersionID], 
	RSLH.[RequestSectionLanePricingPointID], 
	RSLH.[RequestSectionLaneVersionID],
	ROW_NUMBER() OVER(PARTITION BY [RequestSectionLanePricingPointID] ORDER BY VersionNum DESC) AS RN
FROM dbo.RequestSectionLanePricingPoint_History RSLH
INNER JOIN @RequestSectionLaneVersionID RSV ON RSLH.[RequestSectionLaneVersionID] = RSV.[RequestSectionLaneVersionID]) AS A
WHERE A.RN = 1

DECLARE @RequestSectionLanePricingPointID TABLE
(
	[RequestSectionLaneID] BIGINT        NOT NULL,
	[RequestSectionLanePricingPointID] BIGINT        NOT NULL
)
INSERT INTO @RequestSectionLanePricingPointID
(
	[RequestSectionLaneID],
	[RequestSectionLanePricingPointID]
)
SELECT [RequestSectionLaneID], [RequestSectionLanePricingPointID]
FROM dbo.RequestSectionLanePricingPoint
WHERE [RequestSectionLaneID] IN (SELECT [RequestSectionLaneID] FROM @RequestSectionLaneID)

DECLARE @RequestSectionLanePricingPointToBeDeleted TABLE
(
	[RequestSectionLanePricingPointID] BIGINT        NOT NULL
)
INSERT INTO @RequestSectionLanePricingPointToBeDeleted
(
	[RequestSectionLanePricingPointID]
)
SELECT [RequestSectionLanePricingPointID] 
FROM @RequestSectionLanePricingPointID
WHERE [RequestSectionLanePricingPointID] NOT IN (SELECT [RequestSectionLanePricingPointID] FROM @RequestSectionLanePricingPointVersionID)

DECLARE @LatestRequestSectionLanePricingPointVersionNum TABLE
(
	[RequestSectionLanePricingPointID] BIGINT        NOT NULL,
	[RequestSectionLanePricingPointVersionID] BIGINT        NOT NULL,
	[VersionNum] INT NOT NULL
)
INSERT INTO @LatestRequestSectionLanePricingPointVersionNum
(
	[RequestSectionLanePricingPointID],
	[RequestSectionLanePricingPointVersionID],
	[VersionNum]
)
SELECT RSH.[RequestSectionLanePricingPointID],
	RSH.[RequestSectionLanePricingPointVersionID],
	RSH.[VersionNum]
FROM dbo.RequestSectionLanePricingPoint_History RSH
INNER JOIN @RequestSectionLanePricingPointID RS ON RSH.[RequestSectionLanePricingPointID] = RS.[RequestSectionLanePricingPointID]
WHERE RSH.IsLatestVersion = 1

DECLARE @RequestSectionLanePricingPointHistory TABLE
(
	[VersionNum]          INT             NOT NULL,
	[IsActive]           BIT           NOT NULL,
    [IsInactiveViewable] BIT           NOT NULL,
	[RequestSectionLanePricingPointVersionID]          BIGINT     NOT NULL,
	[RequestSectionLanePricingPointID]          BIGINT     NOT NULL,
	[RequestSectionLaneVersionID]          BIGINT     NOT NULL,
    [PricingPointNumber]        NVARCHAR(32) NOT NULL,
	[OriginPostalCodeVersionID] BIGINT NULL,
	[OriginPostalCodeName] NVARCHAR(10) NULL,
	[DestinationPostalCodeVersionID] BIGINT NULL,
	[DestinationPostalCodeName] NVARCHAR(10) NULL,
	[PricingPointHashCode] VARBINARY(8000) NOT NULL,
	[Cost]        NVARCHAR(MAX) NULL,
	[DrRate] NVARCHAR(MAX) NOT NULL,
	[FakRate] NVARCHAR(MAX) NOT NULL,
	[Profitability] NVARCHAR(MAX) NOT NULL,
	[SplitsAll] NVARCHAR(MAX) NOT NULL,
	[SplitsAllUsagePercentage] DECIMAL(19,6) NOT NULL,
	[PickupCount] INT NULL,
	[DeliveryCount] INT NULL,
	[DockAdjustment] DECIMAL(19,6) NULL,
	[Margin] NVARCHAR(MAX) NOT NULL,
	[Density] NVARCHAR(MAX) NOT NULL,
	[PickupCost] NVARCHAR(MAX) NOT NULL,
	[DeliveryCost] NVARCHAR(MAX) NOT NULL,
	[AccessorialsValue] NVARCHAR(MAX) NOT NULL,
	[AccessorialsPercentage] NVARCHAR(MAX) NOT NULL
)
INSERT INTO @RequestSectionLanePricingPointHistory
(
	[VersionNum],
	[IsActive],
    [IsInactiveViewable],
	[RequestSectionLanePricingPointVersionID],
	[RequestSectionLanePricingPointID],
	[RequestSectionLaneVersionID],
    [PricingPointNumber],
	[OriginPostalCodeVersionID],
	[OriginPostalCodeName],
	[DestinationPostalCodeVersionID],
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
SELECT VN.[VersionNum],
	[IsActive],
    [IsInactiveViewable],
	PPH.[RequestSectionLanePricingPointVersionID],
	PPH.[RequestSectionLanePricingPointID],
	[RequestSectionLaneVersionID],
    [PricingPointNumber],
	[OriginPostalCodeVersionID],
	[OriginPostalCodeName],
	[DestinationPostalCodeVersionID],
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
FROM dbo.RequestSectionLanePricingPoint_History PPH
INNER JOIN @LatestRequestSectionLanePricingPointVersionNum VN ON PPH.[RequestSectionLanePricingPointID] = VN.[RequestSectionLanePricingPointID]
WHERE PPH.RequestSectionLanePricingPointVersionID IN (SELECT RequestSectionLanePricingPointVersionID FROM @RequestSectionLanePricingPointVersionID)
UNION
SELECT VN.[VersionNum],
	0,
    [IsInactiveViewable],
	PPH.[RequestSectionLanePricingPointVersionID],
	PPH.[RequestSectionLanePricingPointID],
	[RequestSectionLaneVersionID],
    [PricingPointNumber],
	[OriginPostalCodeVersionID],
	[OriginPostalCodeName],
	[DestinationPostalCodeVersionID],
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
FROM dbo.RequestSectionLanePricingPoint_History PPH
INNER JOIN @LatestRequestSectionLanePricingPointVersionNum VN ON PPH.RequestSectionLanePricingPointVersionID = VN.RequestSectionLanePricingPointVersionID
WHERE VN.RequestSectionLanePricingPointID IN (SELECT RequestSectionLanePricingPointID FROM @RequestSectionLanePricingPointToBeDeleted)

UPDATE dbo.RequestSectionLanePricingPoint_History
SET IsLatestVersion = 0
WHERE dbo.RequestSectionLanePricingPoint_History.[RequestSectionLanePricingPointVersionID] IN (SELECT [RequestSectionLanePricingPointVersionID] FROM @LatestRequestSectionLanePricingPointVersionNum)

UPDATE dbo.RequestSectionLanePricingPoint
SET [IsActive] = A.[IsActive],
	[IsInactiveViewable] = A.[IsInactiveViewable],
	[PricingPointNumber] = A.[PricingPointNumber],
	[OriginPostalCodeID] = O_PC.PostalCodeID,
	[OriginPostalCodeName] = A.[OriginPostalCodeName],
	[DestinationPostalCodeID] = D_PC.PostalCodeID,
	[DestinationPostalCodeName] = A.[DestinationPostalCodeName],
	[PricingPointHashCode] = A.[PricingPointHashCode],
	[Cost] = A.[Cost],
	[DrRate] = A.[DrRate],
	[FakRate] = A.[FakRate],
	[Profitability] = A.[Profitability],
	[SplitsAll] = A.[SplitsAll],
	[SplitsAllUsagePercentage] = A.[SplitsAllUsagePercentage],
	[PickupCount] = A.[PickupCount],
	[DeliveryCount] = A.[DeliveryCount],
	[DockAdjustment] = A.[DockAdjustment],
	[Margin] = A.[Margin],
	[Density] = A.[Density],
	[PickupCost] = A.[PickupCost],
	[DeliveryCost] = A.[DeliveryCost],
	[AccessorialsValue] = A.[AccessorialsValue],
	[AccessorialsPercentage] = A.[AccessorialsPercentage]
FROM @RequestSectionLanePricingPointHistory A
LEFT JOIN dbo.PostalCode_History O_PC ON A.OriginPostalCodeVersionID = O_PC.PostalCodeVersionID
LEFT JOIN dbo.PostalCode_History D_PC ON A.DestinationPostalCodeVersionID = D_PC.PostalCodeVersionID
WHERE dbo.RequestSectionLanePricingPoint.RequestSectionLanePricingPointID = A.RequestSectionLanePricingPointID

SELECT @ERROR5 = @@ERROR

INSERT INTO RequestSectionLanePricingPoint_History
(
	[VersionNum],
    [IsLatestVersion],
    [UpdatedOn],
    [UpdatedBy],
    [Comments],
	[IsActive],
    [IsInactiveViewable],
	[RequestSectionLanePricingPointID],
	[RequestSectionLaneVersionID],
    [PricingPointNumber],
	[OriginPostalCodeVersionID],
	[OriginPostalCodeName],
	[DestinationPostalCodeVersionID],
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
SELECT [VersionNum]+1,
	1,
	GETUTCDATE(),
	@UpdatedBy,
	@Comments,
	[IsActive],
    [IsInactiveViewable],
	PPH.[RequestSectionLanePricingPointID],
	RSL.[RequestSectionLaneVersionID],
    [PricingPointNumber],
	[OriginPostalCodeVersionID],
	[OriginPostalCodeName],
	[DestinationPostalCodeVersionID],
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
FROM @RequestSectionLanePricingPointHistory PPH
INNER JOIN @RequestSectionLanePricingPointID PP ON PPH.RequestSectionLanePricingPointID = PP.RequestSectionLanePricingPointID
INNER JOIN @RequestSectionLaneVersion RSL ON PP.RequestSectionLaneID = RSL.RequestSectionLaneID

SELECT @ERROR6 = @@ERROR

	IF (@ERROR1 <> 0) OR (@ERROR2 <> 0) OR (@ERROR3 <> 0) OR (@ERROR4 <> 0) OR (@ERROR5 <> 0) OR (@ERROR6 <> 0)
	BEGIN
	ROLLBACK TRAN
	RAISERROR('Insert Procedure Failed!', 16, 1)
	RETURN 0
	END

COMMIT TRAN
RETURN 1

