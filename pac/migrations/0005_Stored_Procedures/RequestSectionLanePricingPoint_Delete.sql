CREATE OR ALTER PROCEDURE [dbo].[RequestSectionLanePricingPoint_Delete]
	@RequestSectionLaneID BIGINT,
	@RequestSectionLanePricingPointIDs NVARCHAR(MAX),
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ERROR3 INT;

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

BEGIN TRAN

	DECLARE @RequestSectionLanePricingPoints IDTableType;
	INSERT INTO @RequestSectionLanePricingPoints
	(
		ID
	)
	SELECT [value]
	FROM OPENJSON(@RequestSectionLanePricingPointIDs)

	DECLARE @FilterCount INT;
	SELECT @FilterCount = COUNT(*) FROM @RequestSectionLanePricingPoints;

	IF @FilterCount = 0
	BEGIN
		INSERT INTO @RequestSectionLanePricingPoints
		(
			ID
		)
		SELECT RequestSectionLanePricingPointID
		FROM dbo.RequestSectionLanePricingPoint 
		WHERE RequestSectionLaneID = @RequestSectionLaneID AND [IsActive] = 1 AND [IsInactiveViewable] = 1
	END

	Update dbo.RequestSectionLanePricingPoint
	SET IsActive = 0
	WHERE dbo.RequestSectionLanePricingPoint.RequestSectionLanePricingPointID IN (SELECT ID FROM @RequestSectionLanePricingPoints)

	DECLARE @RequestSectionLaneTableTypeID  IDTableType;

	DECLARE @SourcePricingPointsCount INT;
	SELECT @SourcePricingPointsCount = COUNT(*) FROM dbo.RequestSectionLanePricingPoint WHERE RequestSectionLaneID = @RequestSectionLaneID AND [IsActive] = 1 AND [IsInactiveViewable] = 1

	IF @SourcePricingPointsCount = 0
	BEGIN
		Update dbo.RequestSectionLane
		SET IsLaneGroup = 0
		WHERE dbo.RequestSectionLane.RequestSectionLaneID = @RequestSectionLaneID

		INSERT INTO @RequestSectionLaneTableTypeID (ID) SELECT @RequestSectionLaneID
		EXEC dbo.RequestSectionLane_History_Update @RequestSectionLaneTableTypeID, @UpdatedBy, @Comments
	END
	ELSE
	BEGIN
		EXEC dbo.RequestSectionLanePricingPoint_History_Update @RequestSectionLanePricingPoints, @UpdatedBy, @Comments
	END

COMMIT TRAN
RETURN 1

