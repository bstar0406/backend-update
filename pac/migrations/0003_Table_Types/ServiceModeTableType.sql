IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'ServiceModeTableType')
BEGIN
CREATE TYPE [dbo].[ServiceModeTableType] AS TABLE
(
	[ServiceOfferingName] [nvarchar](50) NOT NULL,
	[ServiceModeName]    NVARCHAR (50) NOT NULL,
    [ServiceModeCode]    NVARCHAR (1)  NOT NULL,
    INDEX IX NONCLUSTERED(ServiceOfferingName, ServiceModeCode)
)
END