IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'PostalCodeTableType')
BEGIN
CREATE TYPE [dbo].[PostalCodeTableType] AS TABLE (
    [PostalCodeName]             NVARCHAR (10)    NOT NULL,
    [ServicePointName] NVARCHAR (50)    NOT NULL,
    [ProvinceCode]               NVARCHAR (2) NOT NULL,
    INDEX [IX1] ([PostalCodeName], [ServicePointName], [ProvinceCode]));
END