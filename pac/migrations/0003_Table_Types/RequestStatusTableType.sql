IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'RequestStatusTableType')
BEGIN
CREATE TYPE [dbo].[RequestStatusTableType] AS TABLE
(
	[RequestID]        BIGINT NOT NULL,
	[SalesRepresentativeID]   BIGINT NOT NULL,
	[PricingAnalystID]        BIGINT NULL,
	[CurrentEditorID]        BIGINT NOT NULL,
	[RequestStatusTypeName]        NVARCHAR(50) NOT NULL,
	INDEX IX1 NONCLUSTERED([RequestID]),
	INDEX IX2 NONCLUSTERED([RequestStatusTypeName])
)
END