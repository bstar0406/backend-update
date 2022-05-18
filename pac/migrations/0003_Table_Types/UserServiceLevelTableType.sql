IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'UserServiceLevelTableType')
BEGIN
CREATE TYPE [dbo].[UserServiceLevelTableType] AS TABLE
(
	[UserID] [bigint] NOT NULL,
	[ServiceLevelID] [bigint] NOT NULL,
	INDEX IX NONCLUSTERED([UserID], [ServiceLevelID])
)
END
