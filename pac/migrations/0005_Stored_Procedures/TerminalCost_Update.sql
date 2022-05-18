CREATE OR ALTER PROCEDURE [dbo].[TerminalCost_Update]
	@TerminalCostTableType_Update TerminalCostTableType_Update READONLY
AS

SET NOCOUNT ON;

BEGIN TRAN

DECLARE @ERROR1 INT, @ERROR2 INT, @ERROR3 INT;

UPDATE dbo.TerminalCost
SET Cost = dbo.FormatJsonField(A.[Cost]),
[IsIntraRegionMovementEnabled] = A.[IsIntraRegionMovementEnabled],
[IntraRegionMovementFactor] = A.[IntraRegionMovementFactor]
FROM @TerminalCostTableType_Update AS A
WHERE dbo.TerminalCost.TerminalCostID = A.TerminalCostID

SELECT @ERROR1 = @@ERROR;

DECLARE @TerminalNewCost_History table
(
	[TerminalCostVersionID] [BIGINT] NOT NULL,
	[TerminalCostID] [BIGINT] NOT NULL,
	[TerminalVersionID]         BIGINT          NOT NULL,
	[Cost] [NVARCHAR](MAX) NOT NULL,
	[ServiceOfferingVersionID]           BIGINT NOT NULL,
    [VersionNum]            INT             NOT NULL,
    [IsActive]              BIT             NOT NULL,
    [IsInactiveViewable]    BIT             NOT NULL,
	[IsIntraRegionMovementEnabled] BIT             NOT NULL,
    [IntraRegionMovementFactor]    NUMERIC (19, 6) NOT NULL
)

INSERT INTO @TerminalNewCost_History
(
	[TerminalCostVersionID],
	[TerminalCostID],
	[TerminalVersionID],
	[Cost],
	[ServiceOfferingVersionID],
    [VersionNum],
    [IsActive],
    [IsInactiveViewable],
	[IsIntraRegionMovementEnabled],
	[IntraRegionMovementFactor]
)
SELECT LCH.[TerminalCostVersionID],
	LC.[TerminalCostID],
	LCH.[TerminalVersionID],
	dbo.FormatJsonField(LC.[Cost]),
	LCH.[ServiceOfferingVersionID],
	LCH.[VersionNum],
	LCH.[IsActive],
	LCH.[IsInactiveViewable],
	LC.[IsIntraRegionMovementEnabled],
	LC.[IntraRegionMovementFactor]
FROM dbo.[TerminalCost_History] LCH
INNER JOIN @TerminalCostTableType_Update LC ON LCH.TerminalCostID = LC.TerminalCostID AND LCH.[IsLatestVersion] = 1

UPDATE dbo.[TerminalCost_History]
SET [IsLatestVersion] = 0
FROM @TerminalNewCost_History AS A
WHERE dbo.[TerminalCost_History].[TerminalCostVersionID] = A.[TerminalCostVersionID]

SELECT @ERROR2 = @@ERROR;

INSERT INTO [dbo].[TerminalCost_History]
(
	[TerminalCostID],
	[TerminalVersionID],
	[ServiceOfferingVersionID],
	[Cost],
	[IsActive],
	[VersionNum],
	[IsLatestVersion],
	[IsInactiveViewable],
	[UpdatedOn],
	[UpdatedBy],
	[Comments],
	[IsIntraRegionMovementEnabled],
	[IntraRegionMovementFactor]
)
SELECT LCH.[TerminalCostID],
	 LCH.[TerminalVersionID],
	 LCH.[ServiceOfferingVersionID],
	 LCH.[Cost],
	 LCH.[IsActive],
	 LCH.[VersionNum] + 1,
	 1,
	 LCH.[IsInactiveViewable],
	 GETUTCDATE(),
	 'P&C System',
	 'Added Weight break levels',
	 LCH.[IntraRegionMovementFactor],
	 LCH.[IntraRegionMovementFactor]
FROM @TerminalNewCost_History LCH

SELECT @ERROR3 = @@ERROR;

IF (@ERROR1 <> 0) OR (@ERROR2 <> 0) OR (@ERROR3 <> 0) 

	BEGIN
	ROLLBACK TRAN
	RAISERROR('Insert Procedure Failed!', 16, 1)
	RETURN 0
	END

COMMIT TRAN

RETURN 1
GO
