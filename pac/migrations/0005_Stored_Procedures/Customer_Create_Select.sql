CREATE OR ALTER PROCEDURE [dbo].[Customer_Create_Select]
	@ServiceLevelID BIGINT,
	@AccountID BIGINT = NULL,
	@OutputCustomerID BIGINT output
AS

SET NOCOUNT ON;

BEGIN TRAN

DECLARE @Customer table
(	
	[CustomerID] BIGINT NOT NULL
)

DECLARE @CustomerID BIGINT;

DECLARE @IsValidData          BIT = 0,
    @CustomerName         NVARCHAR (100) = NULL,
    @CustomerAlias        NVARCHAR (100) = NULL,
    @CustomerAddressLine1 NVARCHAR (100) = NULL,
    @CustomerAddressLine2 NVARCHAR (100) = NULL,
    @PostalCode           NVARCHAR (10)  = NULL,
    @ContactName          NVARCHAR (100) = NULL,
    @ContactTitle         NVARCHAR (100) = NULL,
    @Phone                NVARCHAR (100) = NULL,
    @Email                NVARCHAR (100) = NULL,
    @Website              NVARCHAR (100) = NULL,
    @CityID               BIGINT        = NULL,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL;

IF @AccountID IS NOT NULL
	BEGIN
		SELECT @CustomerID = C.CustomerID
		FROM dbo.Customer C
		WHERE C.ServiceLevelID = @ServiceLevelID AND C.AccountID = @AccountID

		IF @CustomerID IS NULL
			BEGIN	
				SELECT @CustomerName = A.AccountName, @CustomerAlias = A.AccountAlias, @CustomerAddressLine1 = A.AddressLine1, 
				@CustomerAddressLine2 = A.AddressLine2, @PostalCode = A.PostalCode, @ContactName = A.ContactName,
				@ContactTitle = A.ContactTitle, @Phone = A.Phone, @Email = A.Email, @Website = A.Website, @CityID = A.CityID
				FROM dbo.Account A
				WHERE A.AccountID = @AccountID
				
				SELECT @IsValidData = 1;

				EXEC dbo.Customer_Insert @ServiceLevelID, @IsValidData, @CustomerName, @CustomerAlias, @CustomerAddressLine1, @CustomerAddressLine2,
				@PostalCode, @ContactName, @ContactTitle, @Phone, @Email, @Website, @AccountID, @CityID, @UpdatedBy, @Comments, @CustomerID output 
			END
	END
ELSE
	BEGIN
		EXEC dbo.Customer_Insert @ServiceLevelID, @IsValidData, @CustomerName, @CustomerAlias, @CustomerAddressLine1, @CustomerAddressLine2,
		@PostalCode, @ContactName, @ContactTitle, @Phone, @Email, @Website, @AccountID, @CityID, @UpdatedBy, @Comments, @CustomerID output 	
	END

SET @OutputCustomerID = (SELECT @CustomerID);

COMMIT TRAN

RETURN 1

GO
