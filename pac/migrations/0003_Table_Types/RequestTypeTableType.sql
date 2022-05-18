IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'RequestTypeTableType')
BEGIN
CREATE TYPE [dbo].[RequestTypeTableType] AS TABLE
(
    [RequestTypeName]        NVARCHAR (50) NOT NULL,
	[ApplyToCustomerUnderReview]        BIT NOT NULL,
	[ApplyToRevision] BIT NOT NULL,
	[AllowSalesCommitment] BIT NOT NULL,
	INDEX IX NONCLUSTERED([RequestTypeName])
)
END