CREATE OR ALTER PROCEDURE [dbo].[RequestInformation_Insert]
	@RequestNumber        NVARCHAR (32),
	@CustomerID        BIGINT,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL,
	@RequestInformationID NVARCHAR (32) output
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ROWCOUNT1 INT, @ROWCOUNT2 INT

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

DECLARE @RequestInformation table 
( 
    [RequestInformationID]          BIGINT        NOT NULL,
    [RequestNumber]        NVARCHAR (32) NOT NULL,
    [CustomerID]                BIGINT   NOT NULL,
	[IsValidData]	BIT NOT NULL
)

BEGIN TRAN

INSERT INTO [dbo].[RequestInformation]
(
	[RequestNumber],
	[CustomerID],
	[IsValidData],
	[IsActive],
	[IsInactiveViewable]
)
OUTPUT INSERTED.[RequestInformationID],
    INSERTED.[RequestNumber],
	INSERTED.[CustomerID],
	INSERTED.[IsValidData]
INTO @RequestInformation
(
	[RequestInformationID],
	[RequestNumber],
	[CustomerID],
	[IsValidData]
)
VALUES
(
    @RequestNumber,
	@CustomerID,
	0,
	1,
	1
)

SELECT @ERROR1 = @@ERROR, @ROWCOUNT1 = @@ROWCOUNT  

INSERT INTO [dbo].[RequestInformation_History]
(
	[RequestInformationID],
    [RequestNumber],
	[CustomerVersionID],
	[IsValidData],
	[IsActive],
	[VersionNum],
	[IsLatestVersion],
	[IsInactiveViewable],
	[UpdatedOn],
	[UpdatedBy],
	[Comments]
)
SELECT R.[RequestInformationID],
    R.[RequestNumber],
	CH.[CustomerVersionID],
	R.[IsValidData],
	 1,
	 1,
	 1,
	 1,
	 GETUTCDATE(),
	 @UpdatedBy,
	 @Comments
FROM @RequestInformation R
INNER JOIN dbo.Customer_History CH ON R.CustomerID = CH.CustomerID AND CH.IsLatestVersion = 1

SELECT @ERROR2 = @@ERROR, @ROWCOUNT2 = @@ROWCOUNT 

SELECT @RequestInformationID = R.RequestInformationID
FROM @RequestInformation R
WHERE R.CustomerID = @CustomerID

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

