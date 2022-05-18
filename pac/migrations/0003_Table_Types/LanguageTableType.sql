IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'LanguageTableType')
BEGIN
CREATE TYPE [dbo].[LanguageTableType] AS TABLE
(
    [LanguageName]        NVARCHAR (50) NOT NULL,
	[LanguageCode]        NVARCHAR (2) NOT NULL,
	INDEX IX NONCLUSTERED([LanguageCode])
)
END