CREATE OR ALTER PROCEDURE [dbo].[Currency_Insert_Bulk]
	@CurrencyTableType CurrencyTableType READONLY,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ROWCOUNT1 INT, @ROWCOUNT2 INT, @InputCount INT;

SELECT @InputCount = Count(*) FROM @CurrencyTableType;

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

DECLARE @Currency table 
( 
	[CurrencyID] [bigint] NOT NULL,
	[CurrencyName] [nvarchar](50) NOT NULL,
	[CurrencyCode] [nvarchar](3) NOT NULL
)

BEGIN TRAN

INSERT INTO [dbo].[Currency]
(
	[CurrencyName],
	[CurrencyCode],
	[IsActive],
	[IsInactiveViewable]
)
OUTPUT INSERTED.CurrencyID,
	 INSERTED.CurrencyName,
	 INSERTED.CurrencyCode
INTO @Currency
(
	[CurrencyID],
	[CurrencyName],
	[CurrencyCode]
)
SELECT [CurrencyName],
	[CurrencyCode],
	1,
	1
FROM @CurrencyTableType 

SELECT @ERROR1 = @@ERROR, @ROWCOUNT1 = @@ROWCOUNT  

INSERT INTO [dbo].[Currency_History]
(
	[CurrencyID],
	[CurrencyName],
	[CurrencyCode],
	[IsActive],
	[VersionNum],
	[IsLatestVersion],
	[IsInactiveViewable],
	[UpdatedOn],
	[UpdatedBy],
	[Comments]
)
SELECT [CurrencyID],
	 [CurrencyName],
	 [CurrencyCode],
	 1,
	 1,
	 1,
	 1,
	 GETUTCDATE(),
	 @UpdatedBy,
	 @Comments
FROM @Currency

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
