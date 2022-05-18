CREATE OR ALTER PROCEDURE [dbo].[EquipmentType_Insert_Bulk]
	@EquipmentTypeTableType EquipmentTypeTableType READONLY,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ROWCOUNT1 INT, @ROWCOUNT2 INT, @InputCount INT;

SELECT @InputCount = Count(*) FROM @EquipmentTypeTableType;

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

DECLARE @EquipmentType table 
( 
	[EquipmentTypeID] [bigint] NOT NULL,
	[EquipmentTypeName] [nvarchar](50) NOT NULL,
	[EquipmentTypeCode] [nvarchar](2) NOT NULL
)

BEGIN TRAN

INSERT INTO [dbo].[EquipmentType]
(
	[EquipmentTypeName],
	[EquipmentTypeCode],
	[IsActive],
	[IsInactiveViewable]
)
OUTPUT INSERTED.EquipmentTypeID,
	 INSERTED.EquipmentTypeName,
	 INSERTED.EquipmentTypeCode
INTO @EquipmentType
(
	[EquipmentTypeID],
	[EquipmentTypeName],
	[EquipmentTypeCode]
)
SELECT [EquipmentTypeName],
	[EquipmentTypeCode],
	1,
	1
FROM @EquipmentTypeTableType 

SELECT @ERROR1 = @@ERROR, @ROWCOUNT1 = @@ROWCOUNT  

INSERT INTO [dbo].[EquipmentType_History]
(
	[EquipmentTypeID],
	[EquipmentTypeName],
	[EquipmentTypeCode],
	[IsActive],
	[VersionNum],
	[IsLatestVersion],
	[IsInactiveViewable],
	[UpdatedOn],
	[UpdatedBy],
	[Comments]
)
SELECT [EquipmentTypeID],
	 [EquipmentTypeName],
	 [EquipmentTypeCode],
	 1,
	 1,
	 1,
	 1,
	 GETUTCDATE(),
	 @UpdatedBy,
	 @Comments
FROM @EquipmentType

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
