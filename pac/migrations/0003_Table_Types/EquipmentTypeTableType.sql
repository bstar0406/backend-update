IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'EquipmentTypeTableType')
BEGIN
CREATE TYPE [dbo].[EquipmentTypeTableType] AS TABLE
(
    [EquipmentTypeName]        NVARCHAR (50) NOT NULL,
	[EquipmentTypeCode]        NVARCHAR (2) NOT NULL,
	INDEX IX NONCLUSTERED([EquipmentTypeCode])
)
END