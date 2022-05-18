IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'SubServiceLevelTableType')
BEGIN
CREATE TYPE [dbo].[SubServiceLevelTableType] AS TABLE
(
	[ServiceLevelID] BIGINT NOT NULL,
	[SubServiceLevelName]    NVARCHAR (50) NOT NULL,
    [SubServiceLevelCode]    NVARCHAR (2)  NOT NULL,
    INDEX IX NONCLUSTERED(ServiceLevelID, SubServiceLevelCode)
)
END