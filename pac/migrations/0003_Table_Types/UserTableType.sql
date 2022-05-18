IF NOT EXISTS (SELECT *
FROM sys.types
WHERE is_table_type = 1 AND name = 'UserTableType')
BEGIN
CREATE TYPE [dbo].[UserTableType] AS TABLE
(
    [UserName]        NVARCHAR (50) NOT NULL,
	[UserEmail]        NVARCHAR (50) NOT NULL,
    [PersonaName]        NVARCHAR (50) NOT NULL,
	[CanProcessSCS]			BIT NOT NULL,
	[CanProcessRequests]			BIT NOT NULL,
	[CanProcessReviews]			BIT NOT NULL,
	[UserManagerEmail]        NVARCHAR (50) NULL,
	INDEX IX NONCLUSTERED([UserEmail])
)
END