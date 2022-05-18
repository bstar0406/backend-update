IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'ServicePointTableType')
BEGIN
CREATE TYPE [dbo].[ServicePointTableType] AS TABLE
(
	[ServicePointName] [nvarchar](50) NOT NULL,
	[BasingPointName] [nvarchar](50) NULL,
	[ProvinceCode] [nvarchar](2) NULL,
	INDEX IX1 NONCLUSTERED([ServicePointName] ASC),
	INDEX IX2 NONCLUSTERED([BasingPointName] ASC),
	INDEX IX3 NONCLUSTERED([ProvinceCode] ASC)
)
END