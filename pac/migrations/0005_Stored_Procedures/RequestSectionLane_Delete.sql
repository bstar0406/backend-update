CREATE OR ALTER PROCEDURE [dbo].[RequestSectionLane_Delete]
	@RequestSectionID BIGINT,
	@OrigPointTypeName NVARCHAR(50),
	@OrigPointID BIGINT,
	@DestPointTypeName NVARCHAR(50),
	@DestPointID BIGINT,
	@LaneStatusName NVARCHAR(50),
	@RequestSectionLaneTableType_ID NVARCHAR(MAX)
AS

SET NOCOUNT ON;

BEGIN TRAN

DECLARE @RequestSectionLaneTableType IDTableType;
INSERT INTO @RequestSectionLaneTableType
(
	ID
)
SELECT [value]
FROM OPENJSON(@RequestSectionLaneTableType_ID)

DECLARE @FilterCount INT;
SELECT @FilterCount = COUNT(*) FROM @RequestSectionLaneTableType;

WITH A AS 
(
	SELECT RequestSectionLaneID
	FROM dbo.RequestSectionLane RSLS
	WHERE RSLS.RequestSectionID = @RequestSectionID 
	AND (
		( (@LaneStatusName = 'None') OR (@LaneStatusName = 'New' AND [IsPublished] = 0) OR (@LaneStatusName = 'Changed' AND [IsEdited] = 1) OR (@LaneStatusName = 'Duplicated' AND [IsDuplicate] = 1) OR (@LaneStatusName = 'DoNotMeetCommitment' AND [DoNotMeetCommitment] = 1))
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
		)
	AND ((@FilterCount = 0) OR (@FilterCount > 0 AND RSLS.RequestSectionLaneID IN (SELECT ID FROM @RequestSectionLaneTableType)))
)

UPDATE dbo.RequestSectionLane
SET IsActive = 0
FROM A
WHERE dbo.RequestSectionLane.RequestSectionLaneID = A.RequestSectionLaneID 

DECLARE @RequestLaneID BIGINT;
SELECT @RequestLaneID = RequestLaneID FROM dbo.RequestSection WHERE RequestSectionID = @RequestSectionID;
EXEC dbo.RequestLane_Count @RequestLaneID

COMMIT TRAN

RETURN 1

GO
