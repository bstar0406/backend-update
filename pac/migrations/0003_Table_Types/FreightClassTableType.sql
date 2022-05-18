IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'FreightClassTableType')
BEGIN
CREATE TYPE [dbo].[FreightClassTableType] AS TABLE
(
    [FreightClassName]        NVARCHAR (50) NOT NULL,
	INDEX IX NONCLUSTERED([FreightClassName])
)
END