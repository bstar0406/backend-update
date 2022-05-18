IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'CurrencyTableType')
BEGIN
CREATE TYPE [dbo].[CurrencyTableType] AS TABLE
(
    [CurrencyName]        NVARCHAR (50) NOT NULL,
	[CurrencyCode]        NVARCHAR (3) NOT NULL,
	INDEX IX NONCLUSTERED([CurrencyCode])
)
END