IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'CurrencyExchangeTableType')
BEGIN
CREATE TYPE [dbo].[CurrencyExchangeTableType] AS TABLE
(
    [CADtoUSD]         NUMERIC (19, 6) NOT NULL,
    [USDtoCAD]         NUMERIC (19, 6) NOT NULL,
	INDEX IX NONCLUSTERED([CADtoUSD], [USDtoCAD])
)
END