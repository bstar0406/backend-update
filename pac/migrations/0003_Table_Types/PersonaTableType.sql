IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'PersonaTableType')
BEGIN
CREATE TYPE [dbo].[PersonaTableType] AS TABLE
(
    [PersonaName]        NVARCHAR (50) NOT NULL,
	INDEX IX NONCLUSTERED([PersonaName])
)
END