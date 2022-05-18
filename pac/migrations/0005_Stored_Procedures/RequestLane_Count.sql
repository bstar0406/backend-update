CREATE OR ALTER PROCEDURE [dbo].[RequestLane_Count]
	@RequestLaneID     BIGINT,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL

AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ERROR3 INT, @ERROR4 INT;

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Updating Lanes Count.';

BEGIN TRAN

DECLARE @DistinctRequestSectionID IDTableType;

INSERT INTO @DistinctRequestSectionID
(
	ID
)
SELECT DISTINCT [RequestSectionID]
FROM dbo.RequestSection
WHERE RequestLaneID = @RequestLaneID

-- Update RequestSection Count

DECLARE @RequestSectionCount TABLE
(
	[RequestSectionID] BIGINT NOT NULL,
	[NumLanes] INT NOT NULL,
	[NumUnpublishedLanes] INT NOT NULL,
	[NumEditedLanes] INT NOT NULL,
	[NumDuplicateLanes] INT NOT NULL,
	[NumDoNotMeetCommitmentLanes] INT NOT NULL
)
INSERT INTO @RequestSectionCount
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

GROUP BY RSL.[RequestSectionID];

UPDATE dbo.RequestSection
SET [NumLanes] = A.[NumLanes],
	[NumUnpublishedLanes] = A.[NumUnpublishedLanes],
	[NumEditedLanes] = A.[NumEditedLanes],
	[NumDuplicateLanes] = A.[NumDuplicateLanes],
	[NumDoNotMeetCommitmentLanes] = A.[NumDoNotMeetCommitmentLanes]
FROM @RequestSectionCount A
WHERE dbo.RequestSection.[RequestSectionID] = A.[RequestSectionID]

SELECT @ERROR1 = @@ERROR;

-- Update RequesLane Count

DECLARE @RequestLaneCount TABLE
(
	[RequestLaneID] BIGINT NOT NULL,
	[NumLanes] INT NOT NULL,
	[NumUnpublishedLanes] INT NOT NULL,
	[NumEditedLanes] INT NOT NULL,
	[NumDuplicateLanes] INT NOT NULL,
	[NumSections] INT NOT NULL,
	[NumDoNotMeetCommitmentLanes] INT NOT NULL
)
INSERT INTO @RequestLaneCount
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
	ISNULL(SUM(CASE WHEN RS.IsActive = 1 AND RS.[IsInactiveViewable] = 1 THEN [NumUnpublishedLanes] ELSE 0 END), 0),
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
	[NumSections] = A.[NumSections],
	[NumDoNotMeetCommitmentLanes] = A.[NumDoNotMeetCommitmentLanes]
FROM @RequestLaneCount A
WHERE dbo.RequestLane.[RequestLaneID] = A.[RequestLaneID]

SELECT @ERROR2 = @@ERROR

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
	RL.[IsActive],
	RL.[IsInactiveViewable],
	RLH.[RequestLaneVersionID],
	RL.[RequestNumber],
	RL.[NumSections],
	RL.[NumLanes],
	RL.[NumUnpublishedLanes],
	RL.[NumDuplicateLanes],
	RL.[NumEditedLanes],
	RL.[NumDoNotMeetCommitmentLanes],
	RL.[IsValidData],
	RL.[RequestLaneID]
FROM dbo.RequestLane_History RLH
INNER JOIN dbo.RequestLane RL ON RLH.[RequestLaneID] = RL.[RequestLaneID]
WHERE RLH.IsLatestVersion = 1

UPDATE dbo.RequestLane_History
SET IsLatestVersion = 0
WHERE dbo.RequestLane_History.RequestLaneVersionID IN (SELECT RequestLaneVersionID FROM @RequestLaneHistory)

SELECT @ERROR3 = @@ERROR

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

SELECT @ERROR4 = @@ERROR

IF (@ERROR1 <> 0) OR (@ERROR2 <> 0) OR (@ERROR3 <> 0) OR (@ERROR4 <> 0)
BEGIN
ROLLBACK TRAN
RAISERROR('Insert Procedure Failed!', 16, 1)
RETURN 0
END

EXEC dbo.RequestLane_History_Update @RequestLaneID, @UpdatedBy, @Comments

COMMIT TRAN
RETURN 1

