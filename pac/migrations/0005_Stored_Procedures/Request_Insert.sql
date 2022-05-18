CREATE OR ALTER PROCEDURE [dbo].[Request_Insert]
	@InitiatedBy       BIGINT,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL,
	@RequestID BIGINT output,
	@RequestNumber NVARCHAR (32) output
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ROWCOUNT1 INT, @ROWCOUNT2 INT

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

DECLARE @Request table 
( 
    [RequestID]          BIGINT        NOT NULL,
    [RequestNumber]        NVARCHAR (32) NOT NULL,
	[RequestCode]        NVARCHAR (32) NOT NULL,
	[RequestInformationID]        BIGINT NULL,
	[RequestProfileID]        BIGINT NULL,
	[RequestLaneID]        BIGINT NULL,	
	[RequestAccessorialsID]		 BIGINT NULL,
	[InitiatedOn]                DATETIME2 (7)   NOT NULL,
    [InitiatedBy]                BIGINT   NOT NULL,
	[SubmittedOn]                DATETIME2 (7)   NULL,
    [SubmittedBy]                BIGINT   NULL,
	[IsValidData]	BIT NOT NULL,
	[IsReview] BIT NOT NULL
)

BEGIN TRAN

INSERT INTO [dbo].[Request]
(
    [RequestNumber],
	[RequestInformationID],
	[RequestProfileID],
	[RequestLaneID],	
	[RequestAccessorialsID],
	[InitiatedOn],
    [InitiatedBy],
	[SubmittedOn],
    [SubmittedBy],
	[IsValidData],
	[IsReview],
	[IsActive],
	[IsInactiveViewable]
)
OUTPUT INSERTED.[RequestID],
    INSERTED.[RequestNumber],
	CONCAT(LEFT(DATEPART(yy, GETUTCDATE()), 2), REPLICATE('0', 7 - LEN(INSERTED.[RequestID]%10000000)), INSERTED.[RequestID]%10000000),
	INSERTED.[RequestInformationID],
	INSERTED.[RequestProfileID],
	INSERTED.[RequestLaneID],	
	INSERTED.[RequestAccessorialsID],
	INSERTED.[InitiatedOn],
    INSERTED.[InitiatedBy],
	INSERTED.[SubmittedOn],
    INSERTED.[SubmittedBy],
	INSERTED.[IsValidData],
	INSERTED.[IsReview]
INTO @Request
(
	[RequestID],
    [RequestNumber],
	[RequestCode],
	[RequestInformationID],
	[RequestProfileID],
	[RequestLaneID],	
	[RequestAccessorialsID],
	[InitiatedOn],
    [InitiatedBy],
	[SubmittedOn],
    [SubmittedBy],
	[IsValidData],
	[IsReview]
)
VALUES
(
    REPLACE(NEWID(), '-', ''),
	NULL,
	NULL,
	NULL,	
	NULL,
	GETUTCDATE(),
    @InitiatedBy,
	NULL,
    NULL,
	0,
	0,
	1,
	1
)

SELECT @ERROR1 = @@ERROR, @ROWCOUNT1 = @@ROWCOUNT  

UPDATE dbo.Request 
SET RequestCode = A.RequestCode
FROM @Request A
WHERE dbo.Request.RequestID = A.RequestID


INSERT INTO [dbo].[Request_History]
(
	[RequestID],
    [RequestNumber],
	[RequestCode],
	[RequestInformationVersionID],
	[RequestProfileVersionID],
	[RequestLaneVersionID],	
	[RequestAccessorialsVersionID],
	[InitiatedOn],
    [InitiatedByVersion],
	[SubmittedOn],
    [SubmittedByVersion],
	[IsValidData],
	[IsReview],
	[IsActive],
	[VersionNum],
	[IsLatestVersion],
	[IsInactiveViewable],
	[UpdatedOn],
	[UpdatedBy],
	[Comments]
)
SELECT R.[RequestID],
    R.[RequestNumber],
	R.[RequestCode],
	NULL,
	NULL,
	NULL,	
	NULL,
	R.[InitiatedOn],
    UH.[UserVersionID],
	NULL,
    NULL,
	R.[IsValidData],
	R.[IsReview],
	 1,
	 1,
	 1,
	 1,
	 GETUTCDATE(),
	 @UpdatedBy,
	 @Comments
FROM @Request R
INNER JOIN dbo.User_History UH ON R.InitiatedBy = UH.UserID AND UH.IsLatestVersion = 1

SELECT @ERROR2 = @@ERROR, @ROWCOUNT2 = @@ROWCOUNT 

SELECT @RequestID = R.RequestID,
	@RequestNumber = R.RequestNumber
FROM @Request R
WHERE R.InitiatedBy = @InitiatedBy

IF (@ERROR1 <> 0) OR (@ERROR2 <> 0)

	BEGIN
	ROLLBACK TRAN
	RAISERROR('Insert Procedure Failed!', 16, 1)
	RETURN 0
	END

IF (@ROWCOUNT1 <> 1) OR (@ROWCOUNT2 <> 1)
	
	BEGIN
	ROLLBACK TRAN
	IF (@ROWCOUNT1 <> 1)
		RAISERROR('%d Records Affected by Insert Procedure!', 16, 1, @ROWCOUNT1);
	IF (@ROWCOUNT2 <> 1)
		RAISERROR('%d Records Affected by Insert Procedure!', 16, 1, @ROWCOUNT2);
	RETURN 0
	END

COMMIT TRAN
RETURN 1

