CREATE OR ALTER PROCEDURE [dbo].[RequestSectionLanePointType_Insert_Bulk]
	@RequestSectionLanePointTypeTableType RequestSectionLanePointTypeTableType READONLY,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ROWCOUNT1 INT, @ROWCOUNT2 INT, @InputCount INT;

SELECT @InputCount = Count(*) FROM @RequestSectionLanePointTypeTableType;

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

DECLARE @RequestSectionLanePointType table 
( 
	[RequestSectionLanePointTypeID] [bigint] NOT NULL,
	[RequestSectionLanePointTypeName] [nvarchar](50) NOT NULL,
	[ServiceOfferingID] [bigint] NOT NULL,
	[IsDensityPricing] [bit] NOT NULL,
	[LocationHierarchy] [int] NOT NULL,
	[IsGroupType] [bit] NOT NULL,
	[IsPointType] [bit] NOT NULL
)

BEGIN TRAN


DECLARE @ServiceOfferingVersionID table 
( 
	[ServiceOfferingID] [bigint] NOT NULL,
	[ServiceOfferingVersionID] [bigint] NOT NULL
)


INSERT INTO [dbo].[RequestSectionLanePointType]
(
	[RequestSectionLanePointTypeName],
	[ServiceOfferingID],
	[IsDensityPricing],
	[LocationHierarchy],
	[IsGroupType],
	[IsPointType],
	[IsActive],
	[IsInactiveViewable]
)
OUTPUT INSERTED.RequestSectionLanePointTypeID,
	 INSERTED.RequestSectionLanePointTypeName,
	 INSERTED.ServiceOfferingID,
	 INSERTED.[IsDensityPricing],
	 INSERTED.LocationHierarchy,
	 INSERTED.[IsGroupType],
	 INSERTED.[IsPointType]
INTO @RequestSectionLanePointType
(
	[RequestSectionLanePointTypeID],
	[RequestSectionLanePointTypeName],
	[ServiceOfferingID],
	[IsDensityPricing],
	[LocationHierarchy],
	[IsGroupType],
	[IsPointType]
)
SELECT RSL.[RequestSectionLanePointTypeName],
	SO.[ServiceOfferingID],
	RSL.[IsDensityPricing],
	RSL.[LocationHierarchy],
	RSL.[IsGroupType],
	RSL.[IsPointType],
	1,
	1
FROM @RequestSectionLanePointTypeTableType RSL
INNER JOIN dbo.ServiceOffering SO ON RSL.[ServiceOfferingName] = SO.[ServiceOfferingName]

SELECT @ERROR1 = @@ERROR, @ROWCOUNT1 = @@ROWCOUNT 

INSERT INTO @ServiceOfferingVersionID 
( 
	[ServiceOfferingID],
	[ServiceOfferingVersionID]
)
SELECT [ServiceOfferingID],
	[ServiceOfferingVersionID]
FROM [dbo].[ServiceOffering_History]
WHERE [IsLatestVersion] = 1
AND [ServiceOfferingID] IN (SELECT DISTINCT [ServiceOfferingID] FROM @RequestSectionLanePointType) 

INSERT INTO [dbo].[RequestSectionLanePointType_History]
(
	[RequestSectionLanePointTypeID],
	[RequestSectionLanePointTypeName],
	[ServiceOfferingVersionID],
	[IsDensityPricing],
	[LocationHierarchy],
	[IsGroupType],
	[IsPointType],
	[IsActive],
	[VersionNum],
	[IsLatestVersion],
	[IsInactiveViewable],
	[UpdatedOn],
	[UpdatedBy],
	[Comments]
)
SELECT RSL.[RequestSectionLanePointTypeID],
	 RSL.[RequestSectionLanePointTypeName],
	 SO.[ServiceOfferingVersionID],
	 RSL.[IsDensityPricing],
	 RSL.[LocationHierarchy],
	 RSL.[IsGroupType],
	 RSL.[IsPointType],
	 1,
	 1,
	 1,
	 1,
	 GETUTCDATE(),
	 @UpdatedBy,
	 @Comments
FROM @RequestSectionLanePointType RSL
INNER JOIN @ServiceOfferingVersionID SO ON RSL.[ServiceOfferingID] = SO.[ServiceOfferingID]

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
