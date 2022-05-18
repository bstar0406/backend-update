CREATE OR ALTER PROCEDURE [dbo].[Account_Insert_Bulk]
	@AccountTableType AccountTableType READONLY,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ROWCOUNT1 INT, @ROWCOUNT2 INT, @InputCount INT;

SELECT @InputCount = Count(*) FROM @AccountTableType;

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

DECLARE @Account table 
( 
	[AccountID] [bigint] NOT NULL,
	[AccountNumber]        NVARCHAR (50) NOT NULL,
	[AccountName]			NVARCHAR (100) NOT NULL,
	[AddressLine1]			NVARCHAR (100) NOT NULL,
    [AddressLine2]			NVARCHAR (100) NULL,
	[CityID]               BIGINT        NOT NULL,
    [PostalCode]           NVARCHAR (10)  NOT NULL,
	[Phone]                NVARCHAR (100) NULL,
    [ContactName]          NVARCHAR (100) NULL,
    [ContactTitle]         NVARCHAR (100) NULL,
    [Email]                NVARCHAR (100) NULL,
    [Website]              NVARCHAR (100) NULL
)

BEGIN TRAN

DECLARE @CityVersionID table 
( 
	[CityID] [bigint] NOT NULL,
	[CityVersionID] [bigint] NOT NULL
)

INSERT INTO @CityVersionID 
( 
	[CityID],
	[CityVersionID]
)
SELECT [CityID],
	[CityVersionID]
FROM [dbo].[City_History]
WHERE [IsLatestVersion] = 1
AND [CityID] IN (SELECT DISTINCT [CityID] FROM @AccountTableType)


INSERT INTO [dbo].[Account]
(
    [AccountNumber],
	[CityID],
	[AccountOwnerID],
    [AccountName],
    [AccountAlias],
    [AddressLine1],
    [AddressLine2],
    [PostalCode],
    [ContactName],
    [ContactTitle],
    [Phone],
    [Email],
    [Website],
	[IsActive],
	[IsInactiveViewable]
)
OUTPUT INSERTED.[AccountID],
	INSERTED.[AccountNumber],
	INSERTED.[AccountName],
	INSERTED.[AddressLine1],
    INSERTED.[AddressLine2],
	INSERTED.[CityID],
    INSERTED.[PostalCode],
	INSERTED.[Phone],
    INSERTED.[ContactName],
    INSERTED.[ContactTitle],
    INSERTED.[Email],
    INSERTED.[Website]
INTO @Account
(	
	[AccountID],
	[AccountNumber],
	[AccountName],
	[AddressLine1],
    [AddressLine2],
	[CityID],
    [PostalCode],
	[Phone],
    [ContactName],
    [ContactTitle],
    [Email],
    [Website]
)
SELECT [AccountNumber],
	[CityID],
	NULL,
    [AccountName],
    NULL,
    [AddressLine1],
    [AddressLine2],
    [PostalCode],
    [ContactName],
    [ContactTitle],
    LTRIM(RTRIM(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE([Phone], 'EXT', 'x'), ' ', ''),'(',''),')',''),'-',''),'xtn','x'),'exr','x'), 'xt','x'),'ex','x'),':',''),',','x'),'#','x'),'cell','|'),'poste','x'),'local','x'),'or','|'),'.',''),';','|'),'p','|'),'*','|'),'&',''),'/','|'))),
    [Email],
    [Website],
	1,
	1
FROM @AccountTableType

SELECT @ERROR1 = @@ERROR, @ROWCOUNT1 = @@ROWCOUNT  

INSERT INTO [dbo].[Account_History]
(
	[AccountID],
	[AccountNumber],
	[CityVersionID],
	[AccountOwnerVersionID],
    [AccountName],
    [AccountAlias],
    [AddressLine1],
    [AddressLine2],
    [PostalCode],
    [ContactName],
    [ContactTitle],
    [Phone],
    [Email],
    [Website],
	[IsActive],
	[VersionNum],
	[IsLatestVersion],
	[IsInactiveViewable],
	[UpdatedOn],
	[UpdatedBy],
	[Comments]
)
SELECT A.[AccountID],
	A.[AccountNumber],
	CVID.[CityVersionID],
	NULL,
    A.[AccountName],
    NULL,
    A.[AddressLine1],
    A.[AddressLine2],
    A.[PostalCode],
    A.[ContactName],
    A.[ContactTitle],
    A.[Phone],
    A.[Email],
    A.[Website],
	 1,
	 1,
	 1,
	 1,
	 GETUTCDATE(),
	 @UpdatedBy,
	 @Comments
FROM @Account A
INNER JOIN @CityVersionID CVID ON A.[CityID] = CVID.[CityID]

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
