CREATE OR ALTER PROCEDURE [dbo].[Request_By_Number_Select]
	@RequestNumber VARCHAR(32)
AS

SET NOCOUNT ON;

DECLARE @RequestID BIGINT

SELECT @RequestID = RequestID
FROM dbo.Request
WHERE RequestNumber = @RequestNumber;

EXEC [dbo].[Request_By_ID_Select] @RequestID, 0;

RETURN 1

GO
