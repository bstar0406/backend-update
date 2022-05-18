IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'ServiceLevelTableType')
BEGIN
CREATE TYPE [dbo].[ServiceLevelTableType] AS TABLE
(
	[ServiceOfferingName] [nvarchar](50) NOT NULL,
	[ServiceLevelName]    NVARCHAR (50) NOT NULL,
    [ServiceLevelCode]    NVARCHAR (3)  NOT NULL,
	[PricingType] NVARCHAR (50) NOT NULL,
    INDEX IX NONCLUSTERED(ServiceOfferingName, ServiceLevelCode)
)
END