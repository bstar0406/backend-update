IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'AccountTableType')
BEGIN
    CREATE TYPE [dbo].[AccountTableType] AS TABLE
(
        [AccountNumber] NVARCHAR (50) NOT NULL,
        [AccountName] NVARCHAR (100) NOT NULL,
        [AddressLine1] NVARCHAR (100) NOT NULL,
        [AddressLine2] NVARCHAR (100) NULL,
        [CityID] BIGINT NOT NULL,
        [PostalCode] NVARCHAR (10) NOT NULL,
        [Phone] NVARCHAR (100) NULL,
        [ContactName] NVARCHAR (100) NULL,
        [ContactTitle] NVARCHAR (100) NULL,
        [Email] NVARCHAR (100) NULL,
        [Website] NVARCHAR (100) NULL,
        INDEX IX NONCLUSTERED([AccountNumber])
)
END