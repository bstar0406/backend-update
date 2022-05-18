ALTER TABLE RequestSectionLane
    ADD CostOverridePickupCount INT,
        CostOverrideDeliveryCount INT,
        CostOverrideDockAdjustment DECIMAL(19, 6),
        CostOverrideMargin nvarchar(MAX),
        CostOverrideDensity nvarchar(MAX),
        CostOverridePickupCost nvarchar(MAX),
        CostOverrideDeliveryCost nvarchar(MAX),
        CostOverrideAccessorialsValue nvarchar(MAX),
        CostOverrideAccessorialsPercentage nvarchar(MAX)
GO


CREATE or
ALTER PROCEDURE [dbo].[RequestSectionLane_Cost_Override] @RequestSectionLaneIDS VARCHAR(MAX),
                                                         @CostOverridePickupCount BIGINT,
                                                         @CostOverrideDeliveryCount BIGINT,
                                                         @CostOverrideDockAdjustment DECIMAL(19, 6),
                                                         @CostOverrideMargin NVARCHAR(MAX),
                                                         @CostOverrideDensity NVARCHAR(MAX),
                                                         @CostOverridePickupCost NVARCHAR(MAX),
                                                         @CostOverrideDeliveryCost NVARCHAR(MAX),
                                                         @CostOverrideAccessorialsValue NVARCHAR(MAX),
                                                         @CostOverrideAccessorialsPercentage NVARCHAR(MAX)
AS

    SET NOCOUNT ON;


    IF OBJECT_ID(N'tempdb..#RequestSectionLaneId') IS NOT NULL
        DROP TABLE #RequestSectionLaneId
    CREATE TABLE #RequestSectionLaneId
    (
        RequestSectionLaneId BIGINT
    );

INSERT INTO #RequestSectionLaneId (RequestSectionLaneId)
SELECT value
FROM STRING_SPLIT(@RequestSectionLaneIDS, ',');

UPDATE RequestSectionLane
SET CostOverridePickupCount= @CostOverridePickupCount,
    CostOverrideDeliveryCount=@CostOverrideDeliveryCount,
    CostOverrideDockAdjustment=@CostOverrideDockAdjustment,
    CostOverrideMargin=@CostOverrideMargin,
    CostOverrideDensity=@CostOverrideDensity,
    CostOverridePickupCost=@CostOverridePickupCost,
    CostOverrideDeliveryCost=@CostOverrideDeliveryCost,
    CostOverrideAccessorialsValue=@CostOverrideAccessorialsValue,
    CostOverrideAccessorialsPercentage=@CostOverrideAccessorialsPercentage

WHERE RequestSectionLaneID IN (SELECT RequestSectionLaneId FROM #RequestSectionLaneId)

    RETURN 1
go



