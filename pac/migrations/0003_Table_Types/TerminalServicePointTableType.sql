IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'TerminalServicePointTableType')
BEGIN
CREATE TYPE [dbo].[TerminalServicePointTableType] AS TABLE (
    [TerminalCode]             NVARCHAR (3)    NOT NULL,
    [ServicePointName]         NVARCHAR (50)   NOT NULL,
    [ServicePointProvinceCode] NVARCHAR (2)    NOT NULL,
    [ExtraMiles]               DECIMAL (19, 6) NOT NULL,
    INDEX [IX1] ([TerminalCode], [ServicePointName], [ServicePointProvinceCode]));
END