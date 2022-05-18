CREATE OR ALTER PROCEDURE [dbo].[User_Insert_Bulk]
	@UserTableType UserTableType READONLY,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ROWCOUNT1 INT, @ROWCOUNT2 INT, @InputCount INT;

SELECT @InputCount = Count(*) FROM @UserTableType;

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

DECLARE @User table 
( 
	[UserID] [bigint] NOT NULL,
	[UserName] [nvarchar](50) NOT NULL,
	[UserEmail]        NVARCHAR (50) NOT NULL,
    [PersonaID]        BIGINT NOT NULL,
	[AzureIsActive]	   BIT NOT NULL,
	[IsAway]	   BIT NOT NULL,
	[HasSelfAssign]	   BIT NOT NULL,
	[CanProcessSCS]			BIT NOT NULL,
	[CanProcessRequests]			BIT NOT NULL,
	[CanProcessReviews]			BIT NOT NULL
)

BEGIN TRAN

INSERT INTO [dbo].[User]
(
	[UserName],
	[UserEmail],
	[PersonaID],
	[password],
	[IsActive],
	[IsInactiveViewable],
	[AzureIsActive],
	[IsAway],
	[HasSelfAssign],
	[CanProcessSCS],
	[CanProcessRequests],
	[CanProcessReviews]
)
OUTPUT INSERTED.[UserID],
	 INSERTED.[UserName],
	 INSERTED.[UserEmail],
	 INSERTED.[PersonaID],
	 INSERTED.[AzureIsActive],
	 INSERTED.[IsAway],
	 INSERTED.[HasSelfAssign],
	 INSERTED.[CanProcessSCS],
	 INSERTED.[CanProcessRequests],
	 INSERTED.[CanProcessReviews]
INTO @User
(
	[UserID],
	[UserName],
	[UserEmail],
	[PersonaID],
	[AzureIsActive],
	[IsAway],
	[HasSelfAssign],
	[CanProcessSCS],
	[CanProcessRequests],
	[CanProcessReviews]
)
SELECT U.[UserName],
	U.[UserEmail],
	P.[PersonaID],
	'',
	1,
	1,
	1,
	0,
	0,
	[CanProcessSCS],
	[CanProcessRequests],
	[CanProcessReviews]
FROM @UserTableType U
INNER JOIN dbo.Persona P ON U.PersonaName = P.PersonaName

SELECT @ERROR1 = @@ERROR, @ROWCOUNT1 = @@ROWCOUNT 

UPDATE dbo.[User]
SET [UserManagerID] = A.[UserManagerID]
FROM 
(SELECT UTT.[UserEmail], U.[UserID] AS [UserManagerID]
FROM @User AS U
INNER JOIN @UserTableType UTT ON U.[UserEmail] = UTT.[UserManagerEmail]
WHERE UTT.[UserManagerEmail] IS NOT NULL) AS A
WHERE dbo.[User].[UserEmail] = A.[UserEmail]

DECLARE @UserHistory TABLE
(
	[UserID] BIGINT NOT NULL,
	[UserEmail] NVARCHAR (50) NOT NULL,
	[UserVersionID] BIGINT NOT NULL
)

INSERT INTO [dbo].[User_History]
(
	[UserID],
	[UserName],
	[UserEmail],
	[PersonaVersionID],
	[password],
	[IsActive],
	[VersionNum],
	[IsLatestVersion],
	[IsInactiveViewable],
	[UpdatedOn],
	[UpdatedBy],
	[Comments],
	[AzureIsActive],
	[IsAway],
	[HasSelfAssign],
	[CanProcessSCS],
	[CanProcessRequests],
	[CanProcessReviews]
)
OUTPUT INSERTED.[UserID],
	 INSERTED.[UserVersionID],
	 INSERTED.[UserEmail]
INTO @UserHistory
(
	[UserID],
	[UserVersionID],
	[UserEmail]
)
SELECT U.[UserID],
	 U.[UserName],
	 U.[UserEmail],
	 PH.[PersonaVersionID],
	 '',
	 1,
	 1,
	 1,
	 1,
	 GETUTCDATE(),
	 @UpdatedBy,
	 @Comments,
	U.[AzureIsActive],
	U.[IsAway],
	U.[HasSelfAssign],
	[CanProcessSCS],
	[CanProcessRequests],
	[CanProcessReviews]
FROM @User U
INNER JOIN dbo.Persona_History PH ON U.PersonaID = PH.PersonaID AND PH.IsLatestVersion = 1

SELECT @ERROR2 = @@ERROR, @ROWCOUNT2 = @@ROWCOUNT 

UPDATE dbo.User_History
SET UserManagerVersionID = A.UserManagerVersionID
FROM
(SELECT UTT.[UserEmail], U.[UserVersionID] AS UserManagerVersionID
FROM @UserHistory AS U
INNER JOIN @UserTableType UTT ON U.[UserEmail] = UTT.[UserManagerEmail]
WHERE UTT.[UserManagerEmail] IS NOT NULL) AS A
WHERE dbo.User_History.[UserEmail] = A.[UserEmail]

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
