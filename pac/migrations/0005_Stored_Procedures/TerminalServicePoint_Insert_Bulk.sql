CREATE OR ALTER PROCEDURE [dbo].[TerminalServicePoint_Insert_Bulk]
	@TerminalServicePointTableType TerminalServicePointTableType READONLY,
	@UpdatedBy nvarchar(50) = NULL,
	@Comments nvarchar(4000) = NULL
AS

SET NOCOUNT ON;

DECLARE @ERROR1 INT, @ERROR2 INT, @ROWCOUNT1 INT, @ROWCOUNT2 INT, @InputCount INT;

SELECT @InputCount = Count(*) FROM @TerminalServicePointTableType;

IF @UpdatedBy IS NULL
	SELECT @UpdatedBy = 'P&C System';

IF @Comments IS NULL
	SELECT @Comments = 'Created first version.';

BEGIN TRAN

DECLARE @TerminalServicePoint table 
( 
	[TerminalServicePointID] [bigint] NOT NULL,
	[TerminalID] [bigint] NOT NULL,
	[ServicePointID] [bigint] NOT NULL,
	[ExtraMiles] [decimal](19,6) NOT NULL
)

DECLARE @ServicePointVersionID table 
( 
	[ServicePointID] [bigint] NOT NULL,
	[ServicePointVersionID] [bigint] NOT NULL
)

DECLARE @TerminalVersionID table 
( 
	[TerminalID] [bigint] NOT NULL,
	[TerminalVersionID] [bigint] NOT NULL
)

INSERT INTO [dbo].[TerminalServicePoint]
(
	[TerminalID],
	[ServicePointID],
	[ExtraMiles],
	[IsActive],
	[IsInactiveViewable]
)
OUTPUT INSERTED.TerminalServicePointID,
	 INSERTED.[TerminalID],
	 INSERTED.[ServicePointID],
	 INSERTED.[ExtraMiles]
INTO @TerminalServicePoint
(
	[TerminalServicePointID],
	[TerminalID],
	[ServicePointID],
	[ExtraMiles]
)
SELECT T.[TerminalID],
	SP.[ServicePointID],
	TSPTT.[ExtraMiles],
	1,
	1
FROM @TerminalServicePointTableType TSPTT
INNER JOIN dbo.ServicePoint SP ON TSPTT.ServicePointName = SP.ServicePointName
INNER JOIN dbo.Province P ON TSPTT.[ServicePointProvinceCode] = P.[ProvinceCode] AND SP.ProvinceID = P.ProvinceID
INNER JOIN [dbo].[Terminal] T ON TSPTT.[TerminalCode] = T.[TerminalCode] 

SELECT @ERROR1 = @@ERROR, @ROWCOUNT1 = @@ROWCOUNT 

INSERT INTO @ServicePointVersionID 
( 
	[ServicePointID],
	[ServicePointVersionID]
)
SELECT [ServicePointID],
	[ServicePointVersionID]
FROM [dbo].[ServicePoint_History]
WHERE [IsLatestVersion] = 1
AND [ServicePointID] IN (SELECT DISTINCT [ServicePointID] FROM @TerminalServicePoint)

INSERT INTO @TerminalVersionID 
( 
	[TerminalID],
	[TerminalVersionID]
)
SELECT [TerminalID],
	[TerminalVersionID]
FROM [dbo].[Terminal_History]
WHERE [IsLatestVersion] = 1
AND [TerminalID] IN (SELECT DISTINCT [TerminalID] FROM @TerminalServicePoint)

INSERT INTO [dbo].[TerminalServicePoint_History]
(
	[TerminalServicePointID],
	[ServicePointVersionID],
	[TerminalVersionID],
	[ExtraMiles],
	[IsActive],
	[VersionNum],
	[IsLatestVersion],
	[IsInactiveViewable],
	[UpdatedOn],
	[UpdatedBy],
	[Comments]
)
SELECT TSP.[TerminalServicePointID],
	 SPVID.[ServicePointVersionID],
	 TVID.[TerminalVersionID],
	 TSP.[ExtraMiles],
	 1,
	 1,
	 1,
	 1,
	 GETUTCDATE(),
	 @UpdatedBy,
	 @Comments
FROM @TerminalServicePoint TSP
INNER JOIN @TerminalVersionID TVID ON TSP.[TerminalID] = TVID.[TerminalID]
INNER JOIN @ServicePointVersionID SPVID ON TSP.[ServicePointID] = SPVID.[ServicePointID]

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
