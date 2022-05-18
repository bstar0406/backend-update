CREATE OR ALTER PROCEDURE [dbo].[RequestAccessorials_Insert]
	@RequestNumber        NVARCHAR (32),
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL,
	@RequestAccessorialsID NVARCHAR (32) output
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ROWCOUNT1 INT, @ROWCOUNT2 INT

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

DECLARE @RequestAccessorials table 
( 
    [RequestAccessorialsID]          BIGINT        NOT NULL,
    [RequestNumber]        NVARCHAR (32) NOT NULL,
	[IsValidData]	BIT NOT NULL
)

BEGIN TRAN

INSERT INTO [dbo].[RequestAccessorials]
(
	[RequestNumber],
	[IsValidData],
	[IsActive],
	[IsInactiveViewable]
)
OUTPUT INSERTED.[RequestAccessorialsID],
    INSERTED.[RequestNumber],
	INSERTED.[IsValidData]
INTO @RequestAccessorials
(
	[RequestAccessorialsID],
	[RequestNumber],
	[IsValidData]
)
VALUES
(
    @RequestNumber,
	0,
	1,
	1
)

SELECT @ERROR1 = @@ERROR, @ROWCOUNT1 = @@ROWCOUNT  

INSERT INTO [dbo].[RequestAccessorials_History]
(
	[RequestAccessorialsID],
    [RequestNumber],
	[IsValidData],
	[IsActive],
	[VersionNum],
	[IsLatestVersion],
	[IsInactiveViewable],
	[UpdatedOn],
	[UpdatedBy],
	[Comments]
)
SELECT R.[RequestAccessorialsID],
    R.[RequestNumber],
	R.[IsValidData],
	 1,
	 1,
	 1,
	 1,
	 GETUTCDATE(),
	 @UpdatedBy,
	 @Comments
FROM @RequestAccessorials R

SELECT @ERROR2 = @@ERROR, @ROWCOUNT2 = @@ROWCOUNT 

SELECT @RequestAccessorialsID = R.RequestAccessorialsID
FROM @RequestAccessorials R
WHERE R.RequestNumber = @RequestNumber

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

