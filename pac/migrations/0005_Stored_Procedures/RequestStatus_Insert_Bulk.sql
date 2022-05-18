CREATE OR ALTER PROCEDURE [dbo].[RequestStatus_Insert_Bulk]
	@RequestStatusTableType RequestStatusTableType READONLY,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ROWCOUNT1 INT, @ROWCOUNT2 INT, @InputCount INT;

SELECT @InputCount = Count(*) FROM @RequestStatusTableType;

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

DECLARE @RequestStatus table 
( 
	[RequestStatusID]  BIGINT NOT NULL,
    [RequestID]        BIGINT NOT NULL,
	[SalesRepresentativeID]        BIGINT NOT NULL,
	[PricingAnalystID]        BIGINT NULL,
	[CurrentEditorID]        BIGINT NOT NULL,
	[RequestStatusTypeID]        BIGINT NOT NULL
)

BEGIN TRAN

INSERT INTO [dbo].[RequestStatus]
(
	[RequestID],
	[SalesRepresentativeID],
	[PricingAnalystID],
	[CurrentEditorID],
	[RequestStatusTypeID],
	[IsActive],
	[IsInactiveViewable]
)
OUTPUT INSERTED.RequestStatusID,
	 INSERTED.[RequestID],
	 INSERTED.[SalesRepresentativeID],
	 INSERTED.[PricingAnalystID],
	 INSERTED.[CurrentEditorID],
	 INSERTED.[RequestStatusTypeID]
INTO @RequestStatus
(
	[RequestStatusID],
	[RequestID],
	[SalesRepresentativeID],
	[PricingAnalystID],
	[CurrentEditorID],
	[RequestStatusTypeID]
)
SELECT RS.[RequestID],
	RS.[SalesRepresentativeID],
	RS.[PricingAnalystID],
	RS.[CurrentEditorID],
	T.[RequestStatusTypeID],
	1,
	1
FROM @RequestStatusTableType RS
INNER JOIN dbo.[RequestStatusType] T ON RS.[RequestStatusTypeName] = T.[RequestStatusTypeName]

SELECT @ERROR1 = @@ERROR, @ROWCOUNT1 = @@ROWCOUNT  

INSERT INTO [dbo].[RequestStatus_History]
(
	[RequestStatusID],
	[RequestVersionID],
	[SalesRepresentativeVersionID],
	[PricingAnalystVersionID],
	[CurrentEditorVersionID],
	[RequestStatusTypeVersionID],
	[IsActive],
	[VersionNum],
	[IsLatestVersion],
	[IsInactiveViewable],
	[UpdatedOn],
	[UpdatedBy],
	[Comments]
)
SELECT 	RS.[RequestStatusID],
	Q.[RequestVersionID],
	S.[UserVersionID],
	P.[UserVersionID],
	E.[UserVersionID],
	T.[RequestStatusTypeVersionID],
	 1,
	 1,
	 1,
	 1,
	 GETUTCDATE(),
	 @UpdatedBy,
	 @Comments
FROM @RequestStatus RS
INNER JOIN dbo.[Request_History] Q ON RS.[RequestID] = Q.[RequestID] AND Q.IsLatestVersion = 1
INNER JOIN dbo.[User_History] S ON RS.[SalesRepresentativeID] = S.UserID AND S.IsLatestVersion = 1
INNER JOIN dbo.[User_History] E ON RS.[CurrentEditorID] = E.UserID AND E.IsLatestVersion = 1
INNER JOIN dbo.[RequestStatusType_History] T ON RS.[RequestStatusTypeID] = T.[RequestStatusTypeID] AND T.IsLatestVersion = 1
LEFT JOIN dbo.[User_History] P ON RS.[PricingAnalystID] = P.UserID AND P.IsLatestVersion = 1

SELECT @ERROR2 = @@ERROR, @ROWCOUNT2 = @@ROWCOUNT 

IF (@ERROR1 <> 0) OR (@ERROR2 <> 0)

	BEGIN
	ROLLBACK TRAN
	RAISERROR('Insert Procedure Failed!', 16, 1)
	RETURN 0
	END

IF (@ROWCOUNT1 <> @InputCount) OR (@ROWCOUNT2 <> @InputCount)
	
	BEGIN
	ROLLBACK TRAN
	IF (@ROWCOUNT1 <> @InputCount)
		RAISERROR('%d Records Affected by Insert Procedure while the expected number of record is %d!', 16, 1, @ROWCOUNT1,  @InputCount);
	IF (@ROWCOUNT2 <> @InputCount)
		RAISERROR('%d Records Affected by Insert Procedure while the expected number of record is %d!', 16, 1, @ROWCOUNT2, @InputCount);
	RETURN 0
	END

COMMIT TRAN

RETURN 1

GO
