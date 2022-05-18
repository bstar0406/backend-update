CREATE OR ALTER PROCEDURE [dbo].[Unit_Insert_Bulk]
	@UnitTableType UnitTableType READONLY,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ROWCOUNT1 INT, @ROWCOUNT2 INT, @InputCount INT;

SELECT @InputCount = Count(*) FROM @UnitTableType;

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

BEGIN TRAN

DECLARE @Unit table 
( 
	[UnitID]       BIGINT          NOT NULL,
    [UnitName]           NVARCHAR (50) NOT NULL,
    [UnitSymbol]         NVARCHAR (50) NOT NULL,
    [UnitType]           NVARCHAR (50) NOT NULL
)

INSERT INTO [dbo].[Unit]
(
	[UnitName],
    [UnitSymbol],
	[UnitType],
	[IsActive],
	[IsInactiveViewable]
)
OUTPUT INSERTED.[UnitID],
	 INSERTED.[UnitName],
	 INSERTED.[UnitSymbol],
	 INSERTED.[UnitType]
INTO @Unit
(
	[UnitID],
	[UnitName],
    [UnitSymbol],
	[UnitType]
)
SELECT [UnitName],
    [UnitSymbol],
	[UnitType],
	1,
	1
FROM @UnitTableType 

SELECT @ERROR1 = @@ERROR, @ROWCOUNT1 = @@ROWCOUNT  

INSERT INTO [dbo].[Unit_History]
(
	[UnitID],
	[UnitName],
    [UnitSymbol],
	[UnitType],
	[IsActive],
	[VersionNum],
	[IsLatestVersion],
	[IsInactiveViewable],
	[UpdatedOn],
	[UpdatedBy],
	[Comments]
)
SELECT [UnitID],
	[UnitName],
    [UnitSymbol],
	[UnitType],
	 1,
	 1,
	 1,
	 1,
	 GETUTCDATE(),
	 @UpdatedBy,
	 @Comments
FROM @Unit 

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
