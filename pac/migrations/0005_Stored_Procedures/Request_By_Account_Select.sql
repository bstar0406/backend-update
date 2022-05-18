CREATE OR ALTER PROCEDURE [dbo].[Request_By_Account_Select]
	@UserID BIGINT,
	@ServiceLevelID BIGINT,
	@AccountID BIGINT = NULL
AS

SET NOCOUNT ON;

DECLARE @RequestID BIGINT;
DECLARE @IsNewRequest BIT;

EXEC [dbo].[Request_Create_Select] @UserID, @ServiceLevelID, @AccountID, @RequestID output, @IsNewRequest output;

EXEC [dbo].[Request_By_ID_Select] @RequestID, @IsNewRequest;

RETURN 1

GO
