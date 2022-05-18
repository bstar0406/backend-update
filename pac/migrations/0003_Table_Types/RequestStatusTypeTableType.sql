IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'RequestStatusTypeTableType')
BEGIN
CREATE TYPE [dbo].[RequestStatusTypeTableType] AS TABLE
(
    [RequestStatusTypeName]        NVARCHAR (50) NOT NULL,
	[NextRequestStatusType]			  NVARCHAR (MAX) NULL,
	[AssignedPersona]           NVARCHAR (50) NULL,
	[Editor]           NVARCHAR (50) NULL,
	[QueuePersonas]           NVARCHAR (MAX) NULL,
	[IsSecondary] BIT           NULL,
	[IsFinal] BIT           NULL,
	INDEX IX NONCLUSTERED([RequestStatusTypeName])
)
END