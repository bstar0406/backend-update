IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'RequestSectionTableType_Pair')
BEGIN
CREATE TYPE [dbo].[RequestSectionTableType_Pair] AS TABLE
(
	[SourceRequestSectionID] BIGINT NOT NULL,
	[DestinationRequestSectionID] BIGINT NOT NULL,
	INDEX IX NONCLUSTERED([SourceRequestSectionID], [DestinationRequestSectionID])
)
END