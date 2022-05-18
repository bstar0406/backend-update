CREATE OR ALTER PROCEDURE [dbo].[AccountTree_Insert_Bulk]
	@AccountTreeTableType AccountTreeTableType READONLY,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ROWCOUNT1 INT, @ROWCOUNT2 INT, @InputCount INT;

SELECT @InputCount = Count(*) FROM @AccountTreeTableType;

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

DECLARE @AccountTree table 
( 
	[AccountTreeID] [bigint] NOT NULL,
    [ParentAccountID] BIGINT          NULL,
    [AccountID]         BIGINT          NOT NULL
)

BEGIN TRAN

INSERT INTO [dbo].[AccountTree]
(
	[AccountID],
	[ParentAccountID],
	[IsActive],
	[IsInactiveViewable]
)
OUTPUT INSERTED.[AccountTreeID], 
	 INSERTED.[AccountID],
	 INSERTED.[ParentAccountID]
INTO @AccountTree
(
	[AccountTreeID],
	[AccountID],
	[ParentAccountID]
)
SELECT T.[AccountID],
	A.[AccountID],
	1,
	1
FROM @AccountTreeTableType T
LEFT JOIN dbo.[Account] A ON T.[ParentAccountNumber] = A.[AccountNumber] 


SELECT @ERROR1 = @@ERROR, @ROWCOUNT1 = @@ROWCOUNT  

INSERT INTO [dbo].[AccountTree_History]
(
	[AccountTreeID],
	[AccountVersionID],
	[ParentAccountVersionID],
	[IsActive],
	[VersionNum],
	[IsLatestVersion],
	[IsInactiveViewable],
	[UpdatedOn],
	[UpdatedBy],
	[Comments]
)
SELECT [AccountTreeID],
	 AH.[AccountVersionID],
	 PH.[AccountVersionID],
	 1,
	 1,
	 1,
	 1,
	 GETUTCDATE(),
	 @UpdatedBy,
	 @Comments
FROM @AccountTree T
INNER JOIN dbo.Account_History AH ON T.AccountID = AH.AccountID AND AH.IsLatestVersion = 1
LEFT JOIN dbo.Account_History PH ON T.ParentAccountID = PH.AccountID AND AH.IsLatestVersion = 1

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
