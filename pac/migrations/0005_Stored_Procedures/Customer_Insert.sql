CREATE OR ALTER PROCEDURE [dbo].[Customer_Insert]
	@ServiceLevelID       BIGINT,
	@IsValidData          BIT,
    @CustomerName         NVARCHAR (100) = NULL,
    @CustomerAlias        NVARCHAR (100) = NULL,
    @CustomerAddressLine1 NVARCHAR (100) = NULL,
    @CustomerAddressLine2 NVARCHAR (100) = NULL,
    @PostalCode           NVARCHAR (10)  = NULL,
    @ContactName          NVARCHAR (100) = NULL,
    @ContactTitle         NVARCHAR (100) = NULL,
    @Phone               NVARCHAR (100) = NULL,
    @Email                NVARCHAR (100) = NULL,
    @Website              NVARCHAR (100) = NULL,
    @AccountID            BIGINT        = NULL,
    @CityID               BIGINT        = NULL,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL,
	@CustomerID BIGINT output
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ROWCOUNT1 INT, @ROWCOUNT2 INT

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

DECLARE @Customer table 
( 
    [CustomerID]           BIGINT        NOT NULL,
    [CustomerName]         NVARCHAR (100) NULL,
    [CustomerAlias]        NVARCHAR (100) NULL,
    [CustomerAddressLine1] NVARCHAR (100) NULL,
    [CustomerAddressLine2] NVARCHAR (100) NULL,
    [PostalCode]           NVARCHAR (10)  NULL,
    [ContactName]          NVARCHAR (100) NULL,
    [ContactTitle]         NVARCHAR (100) NULL,
    [Phone]                NVARCHAR (100) NULL,
    [Email]                NVARCHAR (100) NULL,
    [Website]              NVARCHAR (100) NULL,
    [IsValidData]          BIT           NOT NULL,
    [AccountID]            BIGINT        NULL,
    [CityID]               BIGINT        NULL,
    [ServiceLevelID]       BIGINT        NOT NULL
)

BEGIN TRAN

INSERT INTO [dbo].[Customer]
(
	[CustomerName],
    [CustomerAlias],
    [CustomerAddressLine1],
    [CustomerAddressLine2],
    [PostalCode],
    [ContactName],
    [ContactTitle],
    [Phone],
    [Email],
    [Website],
    [IsValidData],
    [AccountID],
    [CityID],
    [ServiceLevelID],
	[IsActive],
	[IsInactiveViewable]
)
OUTPUT INSERTED.[CustomerID],
	INSERTED.[CustomerName],
    INSERTED.[CustomerAlias],
    INSERTED.[CustomerAddressLine1],
    INSERTED.[CustomerAddressLine2],
    INSERTED.[PostalCode],
    INSERTED.[ContactName],
    INSERTED.[ContactTitle],
    INSERTED.[Phone],
    INSERTED.[Email],
    INSERTED.[Website],
    INSERTED.[IsValidData],
    INSERTED.[AccountID],
    INSERTED.[CityID],
    INSERTED.[ServiceLevelID]
INTO @Customer
(
	[CustomerID],
	[CustomerName],
    [CustomerAlias],
    [CustomerAddressLine1],
    [CustomerAddressLine2],
    [PostalCode],
    [ContactName],
    [ContactTitle],
    [Phone],
    [Email],
    [Website],
    [IsValidData],
    [AccountID],
    [CityID],
    [ServiceLevelID]
)
VALUES
(
	@CustomerName,
    @CustomerAlias,
    @CustomerAddressLine1,
    @CustomerAddressLine2,
    @PostalCode,
    @ContactName,
    @ContactTitle,
    @Phone,
    @Email,
    @Website,
    @IsValidData,
    @AccountID,
    @CityID,
    @ServiceLevelID,
	1,
	1
)

SELECT @ERROR1 = @@ERROR, @ROWCOUNT1 = @@ROWCOUNT  

INSERT INTO [dbo].[Customer_History]
(
	[CustomerID],
	[CustomerName],
    [CustomerAlias],
    [CustomerAddressLine1],
    [CustomerAddressLine2],
    [PostalCode],
    [ContactName],
    [ContactTitle],
    [Phone],
    [Email],
    [Website],
    [IsValidData],
    [AccountVersionID],
    [CityVersionID],
    [ServiceLevelVersionID],
	[IsActive],
	[VersionNum],
	[IsLatestVersion],
	[IsInactiveViewable],
	[UpdatedOn],
	[UpdatedBy],
	[Comments]
)
SELECT C.[CustomerID],
	C.[CustomerName],
    C.[CustomerAlias],
    C. [CustomerAddressLine1],
    C.[CustomerAddressLine2],
    C.[PostalCode],
    C.[ContactName],
    C.[ContactTitle],
    C.[Phone],
    C.[Email],
    C.[Website],
	C.[IsValidData],
    A.[AccountVersionID],
    Y.[CityVersionID],
    SL.[ServiceLevelVersionID],
	 1,
	 1,
	 1,
	 1,
	 GETUTCDATE(),
	 @UpdatedBy,
	 @Comments
FROM @Customer C
INNER JOIN dbo.ServiceLevel_History SL ON C.ServiceLevelID = SL.ServiceLevelID AND SL.IsLatestVersion = 1
LEFT JOIN dbo.City_History Y ON C.CityID = Y.CityID AND Y.IsLatestVersion = 1
LEFT JOIN dbo.Account_History A ON C.AccountID = A.AccountID AND A.IsLatestVersion = 1

SELECT @ERROR2 = @@ERROR, @ROWCOUNT2 = @@ROWCOUNT 

SELECT @CustomerID = C.CustomerID
FROM dbo.Customer C
WHERE C.ServiceLevelID = @ServiceLevelID;

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

