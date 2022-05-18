IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'UnitTableType')
BEGIN
CREATE TYPE [dbo].[UnitTableType] AS TABLE
(
    [UnitName]           NVARCHAR (50) NOT NULL,
    [UnitSymbol]         NVARCHAR (50) NOT NULL,
    [UnitType]           NVARCHAR (50) NOT NULL,
	INDEX IX NONCLUSTERED([UnitName], [UnitSymbol], [UnitType])
)
END