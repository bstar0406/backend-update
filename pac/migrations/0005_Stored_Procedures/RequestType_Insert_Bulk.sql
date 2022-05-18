CREATE OR ALTER PROCEDURE [dbo].[RequestType_Insert_Bulk]
	@RequestTypeTableType RequestTypeTableType READONLY,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ROWCOUNT1 INT, @ROWCOUNT2 INT, @InputCount INT;

SELECT @InputCount = Count(*) FROM @RequestTypeTableType;

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

DECLARE @RequestType table 
( 
	[RequestTypeID] [bigint] NOT NULL,
	[RequestTypeName] [nvarchar](50) NOT NULL,
	[ApplyToCustomerUnderReview] BIT NOT NULL,
	[ApplyToRevision] BIT NOT NULL,
	[AllowSalesCommitment] BIT NOT NULL
)

BEGIN TRAN

INSERT INTO [dbo].[RequestType]
(
	[RequestTypeName],
	[ApplyToCustomerUnderReview],
	[ApplyToRevision],
	[AllowSalesCommitment],
	[IsActive],
	[IsInactiveViewable]
)
OUTPUT INSERTED.RequestTypeID,
	 INSERTED.RequestTypeName,
	 INSERTED.[ApplyToCustomerUnderReview],
	 INSERTED.[ApplyToRevision],
	 INSERTED.[AllowSalesCommitment]
INTO @RequestType
(
	[RequestTypeID],
	[RequestTypeName],
	[ApplyToCustomerUnderReview],
	[ApplyToRevision],
	[AllowSalesCommitment]
)
SELECT [RequestTypeName],
	[ApplyToCustomerUnderReview],
	[ApplyToRevision],
	[AllowSalesCommitment],
	1,
	1
FROM @RequestTypeTableType 

SELECT @ERROR1 = @@ERROR, @ROWCOUNT1 = @@ROWCOUNT  

INSERT INTO [dbo].[RequestType_History]
(
	[RequestTypeID],
	[RequestTypeName],
	[ApplyToCustomerUnderReview],
	[ApplyToRevision],
	[AllowSalesCommitment],
	[IsActive],
	[VersionNum],
	[IsLatestVersion],
	[IsInactiveViewable],
	[UpdatedOn],
	[UpdatedBy],
	[Comments]
)
SELECT [RequestTypeID],
	 [RequestTypeName],
	 [ApplyToCustomerUnderReview],
	[ApplyToRevision],
	[AllowSalesCommitment],
	 1,
	 1,
	 1,
	 1,
	 GETUTCDATE(),
	 @UpdatedBy,
	 @Comments
FROM @RequestType

SELECT @ERROR2 = @@ERROR, @ROWCOUNT2 = @@ROWCOUNT 

IF (@ERROR1 <> 0) OR (@ERROR2 <> 0)

	BEGIN
	ROLLBACK TRAN
	RAISERROR('Insert Procedure Failed!', 16, 1)
	RETURN 0
	END

IF (@ROWCOUNT1 <> @InputCount) OR (@ROWCOUNT2 <> @InputCount)
	
	BEGIN
	ROLLBACK TRAN
	IF (@ROWCOUNT1 <> @InputCount)
		RAISERROR('%d Records Affected by Insert Procedure while the expected number of record is %d!', 16, 1, @ROWCOUNT1,  @InputCount);
	IF (@ROWCOUNT2 <> @InputCount)
		RAISERROR('%d Records Affected by Insert Procedure while the expected number of record is %d!', 16, 1, @ROWCOUNT2, @InputCount);
	RETURN 0
	END

COMMIT TRAN

RETURN 1

GO
