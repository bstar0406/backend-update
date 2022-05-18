CREATE OR ALTER PROCEDURE [dbo].[Request_Create_Select]
	@UserID BIGINT,
	@ServiceLevelID BIGINT,
	@AccountID BIGINT = NULL,
	@OutputRequestID BIGINT output,
	@IsNewRequest BIT output
AS

SET NOCOUNT ON;

BEGIN TRAN

DECLARE @CustomerID BIGINT;
EXEC [dbo].[Customer_Create_Select] @ServiceLevelID, @AccountID, @CustomerID output

DECLARE @RequestID BIGINT, @RequestNumber NVARCHAR (32);

SELECT @RequestNumber = R.RequestNumber
FROM dbo.RequestInformation R
WHERE R.CustomerID = @CustomerID

IF @RequestNumber IS NOT NULL
	BEGIN
		SELECT @RequestID = R.RequestID
		FROM dbo.Request R
		WHERE R.RequestNumber = @RequestNumber

		SELECT @IsNewRequest = 0;
	END
ELSE
	BEGIN
		SELECT @IsNewRequest = 1;
		DECLARE @PersonaName NVARCHAR(50), @UpdatedBy nvarchar(50), @Comments nvarchar(4000);

		SELECT @PersonaName = P.PersonaName
		FROM dbo.[User] U 
		INNER JOIN dbo.Persona P ON U.PersonaID = P.PersonaID
		WHERE UserID = @UserID;

		EXEC dbo.Request_Insert @UserID, @UpdatedBy, @Comments, @RequestID output, @RequestNumber output

		DECLARE @RequestInformationID BIGINT;
		EXEC dbo.RequestInformation_Insert @RequestNumber, @CustomerID, @UpdatedBy, @Comments, @RequestInformationID output

		DECLARE @RequestProfileID BIGINT;
		EXEC dbo.RequestProfile_Insert @RequestNumber, @UpdatedBy, @Comments, @RequestProfileID output

		DECLARE @RequestAccessorialsID BIGINT;
		EXEC dbo.RequestAccessorials_Insert @RequestNumber, @UpdatedBy, @Comments, @RequestAccessorialsID output

		DECLARE @RequestLaneID BIGINT;
		EXEC dbo.RequestLane_Insert @RequestNumber, @UpdatedBy, @Comments, @RequestLaneID output

		UPDATE dbo.Request 
		SET RequestInformationID = @RequestInformationID,
		RequestProfileID = @RequestProfileID,
		RequestAccessorialsID = @RequestAccessorialsID,
		RequestLaneID = @RequestLaneID
		WHERE dbo.Request.RequestID = @RequestID

		DECLARE @RequestInformationVersionID BIGINT;
		SELECT @RequestInformationVersionID = RequestInformationVersionID
		FROM dbo.RequestInformation_History
		WHERE RequestInformationID = @RequestInformationID AND IsLatestVersion = 1;

		DECLARE @RequestProfileVersionID BIGINT;
		SELECT @RequestProfileVersionID = RequestProfileVersionID
		FROM dbo.RequestProfile_History
		WHERE RequestProfileID = @RequestProfileID AND IsLatestVersion = 1;

		DECLARE @RequestAccessorialsVersionID BIGINT;
		SELECT @RequestAccessorialsVersionID = RequestAccessorialsVersionID
		FROM dbo.RequestAccessorials_History
		WHERE RequestAccessorialsID = @RequestAccessorialsID AND IsLatestVersion = 1;

		DECLARE @RequestLaneVersionID BIGINT;
		SELECT @RequestLaneVersionID = RequestLaneVersionID
		FROM dbo.RequestLane_History
		WHERE RequestLaneID = @RequestLaneID AND IsLatestVersion = 1;

		UPDATE dbo.Request_History 
		SET RequestInformationVersionID = @RequestInformationVersionID,
		RequestProfileVersionID = @RequestProfileVersionID,
		RequestAccessorialsVersionID = @RequestAccessorialsVersionID,
		RequestLaneVersionID = @RequestLaneVersionID
		WHERE dbo.Request_History.RequestID = @RequestID AND dbo.Request_History.IsLatestVersion = 1

		DECLARE @RequestStatusTableType AS RequestStatusTableType;
		INSERT INTO @RequestStatusTableType
		(
			[RequestID],
			[SalesRepresentativeID],
			[PricingAnalystID],
			[CurrentEditorID],
			[RequestStatusTypeName]
		)
		SELECT @RequestID, @UserID, CASE WHEN @PersonaName = 'Pricing Analyst' OR @PersonaName = 'Pricing Manager' THEN @UserID ELSE NULL END, @UserID, 'RRF Initiated'
		EXEC [dbo].[RequestStatus_Insert_Bulk] @RequestStatusTableType

	END

SET @OutputRequestID = (SELECT @RequestID);

COMMIT TRAN

RETURN 1

GO
