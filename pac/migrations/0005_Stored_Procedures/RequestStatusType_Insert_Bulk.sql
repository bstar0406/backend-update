CREATE OR ALTER PROCEDURE [dbo].[RequestStatusType_Insert_Bulk]
	@RequestStatusTypeTableType RequestStatusTypeTableType READONLY,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ROWCOUNT1 INT, @ROWCOUNT2 INT, @InputCount INT;

SELECT @InputCount = Count(*) FROM @RequestStatusTypeTableType;

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

DECLARE @RequestStatusType table 
( 
	[RequestStatusTypeID] [bigint] NOT NULL,
	[RequestStatusTypeName] [nvarchar](50) NOT NULL,
	[NextRequestStatusType]			  NVARCHAR (MAX) NULL,
	[AssignedPersona]           NVARCHAR (50) NULL,
	[Editor]           NVARCHAR (50) NULL,
	[QueuePersonas]           NVARCHAR (MAX) NULL,
	[IsSecondary] BIT           NULL,
	[IsFinal] BIT           NULL
)

BEGIN TRAN

INSERT INTO [dbo].[RequestStatusType]
(
	[RequestStatusTypeName],
	[NextRequestStatusType],
	[AssignedPersona],
	[Editor],
	[QueuePersonas],
	[IsSecondary],
	[IsFinal],
	[IsActive],
	[IsInactiveViewable]
)
OUTPUT INSERTED.RequestStatusTypeID,
	 INSERTED.RequestStatusTypeName,
	 INSERTED.[NextRequestStatusType],
	 INSERTED.[AssignedPersona],
	 INSERTED.[Editor],
	 INSERTED.[QueuePersonas],
	 INSERTED.[IsSecondary],
	 INSERTED.[IsFinal]
INTO @RequestStatusType
(
	[RequestStatusTypeID],
	[RequestStatusTypeName],
	[NextRequestStatusType],
	[AssignedPersona],
	[Editor],
	[QueuePersonas],
	[IsSecondary],
	[IsFinal]
)
SELECT [RequestStatusTypeName],
	[NextRequestStatusType],
	[AssignedPersona],
	[Editor],
	[QueuePersonas],
	[IsSecondary],
	[IsFinal],
	1,
	1
FROM @RequestStatusTypeTableType 

SELECT @ERROR1 = @@ERROR, @ROWCOUNT1 = @@ROWCOUNT  

INSERT INTO [dbo].[RequestStatusType_History]
(
	[RequestStatusTypeID],
	[RequestStatusTypeName],
	[NextRequestStatusType],
	[AssignedPersona],
	[Editor],
	[QueuePersonas],
	[IsSecondary],
	[IsFinal],
	[IsActive],
	[VersionNum],
	[IsLatestVersion],
	[IsInactiveViewable],
	[UpdatedOn],
	[UpdatedBy],
	[Comments]
)
SELECT [RequestStatusTypeID],
	 [RequestStatusTypeName],
	 [NextRequestStatusType],
	 [AssignedPersona],
	 [Editor],
	 [QueuePersonas],
	 [IsSecondary],
	 [IsFinal],
	 1,
	 1,
	 1,
	 1,
	 GETUTCDATE(),
	 @UpdatedBy,
	 @Comments
FROM @RequestStatusType

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
