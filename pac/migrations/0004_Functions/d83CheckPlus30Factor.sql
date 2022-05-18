IF EXISTS (SELECT *
FROM sys.objects
WHERE  object_id = OBJECT_ID(N'[dbo].[d83CheckPlus30Factor]')
	AND type IN ( N'FN', N'IF', N'TF', N'FS', N'FT' ))
  DROP FUNCTION [dbo].[d83CheckPlus30Factor]
GO

CREATE FUNCTION [dbo].[d83CheckPlus30Factor](		@Orig varchar(7), @intchg varchar(7), @Dest varchar(7)		)
	RETURNS @Plus30FactorTable TABLE (
	Plus30FactorOrig decimal(9,2),
	Plus30FactorDest decimal(9,2))  AS
BEGIN
	Declare @Plus30FactorOrig int, @Plus30FactorDest int

	/*
Logic from Rocky Mountain...
IF isONPQ(origin) AND isStatesListed(destination) AND isZipsListed(interchange) 
    THEN addThirty(originTOinterchangeLeg)
ELSE
    IF  isONPQ(destination) AND isStatesListed(origin) AND isZipsListed(interchange) 
        THEN addThirty(destinationTOinterchangeLeg)
    ELSE 
        doNothing
    ENDIF    
ENDIF
*/

	-- Must be an Interchange point in the [Plus30InterchangeList]
	IF EXISTS(	SELECT *
	FROM dbo.Plus30InterchangeList
	WHERE Zip = LEFT(@intchg,3)	) 
BEGIN


		IF (	((LEFT(@Orig,1) between 'A' AND 'Z') AND (LEFT(@Dest,1) between '0' AND '9'))
			OR ((LEFT(@Dest,1) between 'A' AND 'Z') AND (LEFT(@Orig,1) between '0' AND '9'))	)
BEGIN



			IF (	(LEFT(@Orig,1) between 'A' AND 'Z') AND (LEFT(@Dest,1) between '0' AND '9')	)
	BEGIN
				-- Both the @Orig & @Dest must be within the [Plus30Factor] ranges....
				IF EXISTS(SELECT *
					FROM dbo.Plus30Factor
					WHERE LEFT(@Orig,3) BETWEEN LEFT(Zip_Range,3) AND RIGHT(Zip_Range,3))
					AND EXISTS(SELECT *
					FROM dbo.Plus30Factor
					WHERE LEFT(@Dest,5) BETWEEN LEFT(Zip_Range,5) AND RIGHT(Zip_Range,5))
		BEGIN
					--Plus30Factor applies between the Interchange and Canadian Point...
					SET @Plus30FactorOrig = (	SELECT Plus30FactorAmt
					FROM dbo.Plus30Factor
					WHERE LEFT(@Orig,3) BETWEEN LEFT(Zip_Range,3) AND RIGHT(Zip_Range,3)		)
					SET @Plus30FactorDest = 0
				END
		ELSE
		BEGIN
					-- This logic should never execute in theory but is a catchall to ensure no assumption gets missed.
					SET @Plus30FactorOrig = 0
					SET @Plus30FactorDest = 0
				END
			END
	ELSE IF (	(LEFT(@Dest,1) between 'A' AND 'Z') AND (LEFT(@Orig,1) between '0' AND '9'))
	BEGIN

				IF EXISTS(SELECT *
					FROM dbo.Plus30Factor
					WHERE LEFT(@Dest,3) BETWEEN LEFT(Zip_Range,3) AND RIGHT(Zip_Range,3))
					AND EXISTS(SELECT *
					FROM dbo.Plus30Factor
					WHERE LEFT(@Orig,5) BETWEEN LEFT(Zip_Range,5) AND RIGHT(Zip_Range,5))	
		BEGIN
					SET @Plus30FactorOrig = 0
					SET @Plus30FactorDest = (	SELECT Plus30FactorAmt
					FROM dbo.Plus30Factor
					WHERE LEFT(@Dest,3) BETWEEN LEFT(Zip_Range,3) AND RIGHT(Zip_Range,3)		)
				END
		ELSE
		BEGIN
					-- This logic should never execute in theory but is a catchall to ensure no assumption gets missed.
					SET @Plus30FactorOrig = 0
					SET @Plus30FactorDest = 0
				END
			END

		END






	END

	INSERT INTO @Plus30FactorTable
	Values( IsNull(@Plus30FactorOrig,0.00), ISNULL(@Plus30FactorDest,0.00)	)

	RETURN
END


GO


