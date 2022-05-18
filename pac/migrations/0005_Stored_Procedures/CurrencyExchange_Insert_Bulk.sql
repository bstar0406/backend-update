CREATE OR ALTER PROCEDURE [dbo].[CurrencyExchange_Insert_Bulk]
	@CurrencyExchangeTableType CurrencyExchangeTableType READONLY,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ROWCOUNT1 INT, @ROWCOUNT2 INT, @InputCount INT;

SELECT @InputCount = Count(*) FROM @CurrencyExchangeTableType;

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

BEGIN TRAN

DECLARE @CurrencyExchange table 
( 
	[CurrencyExchangeID]       BIGINT          NOT NULL,
    [CADtoUSD]         NUMERIC (19, 6) NOT NULL,
    [USDtoCAD]         NUMERIC (19, 6) NOT NULL
)

INSERT INTO [dbo].[CurrencyExchange]
(
	[CADtoUSD],
    [USDtoCAD],
	[IsActive],
	[IsInactiveViewable]
)
OUTPUT INSERTED.CurrencyExchangeID,
	 INSERTED.[CADtoUSD],
	 INSERTED.[USDtoCAD]
INTO @CurrencyExchange
(
	[CurrencyExchangeID],
	[CADtoUSD],
	[USDtoCAD]
)
SELECT [CADtoUSD],
    [USDtoCAD],
	1,
	1
FROM @CurrencyExchangeTableType 

SELECT @ERROR1 = @@ERROR, @ROWCOUNT1 = @@ROWCOUNT  

INSERT INTO [dbo].[CurrencyExchange_History]
(
	[CurrencyExchangeID],
	[CADtoUSD],
	[USDtoCAD],
	[IsActive],
	[VersionNum],
	[IsLatestVersion],
	[IsInactiveViewable],
	[UpdatedOn],
	[UpdatedBy],
	[Comments]
)
SELECT [CurrencyExchangeID],
	[CADtoUSD],
	[USDtoCAD],
	 1,
	 1,
	 1,
	 1,
	 GETUTCDATE(),
	 @UpdatedBy,
	 @Comments
FROM @CurrencyExchange 

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
