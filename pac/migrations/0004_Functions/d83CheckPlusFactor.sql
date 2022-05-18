IF EXISTS (SELECT *
FROM sys.objects
WHERE  object_id = OBJECT_ID(N'[dbo].[d83CheckPlusFactor]')
	AND type IN ( N'FN', N'IF', N'TF', N'FS', N'FT' ))
  DROP FUNCTION [dbo].[d83CheckPlusFactor]
GO

CREATE FUNCTION [dbo].[d83CheckPlusFactor]
(		
	@orig varchar(7)		-- Origin
	, @IntZip varchar(7)	-- Interchange zip
	, @dest varchar(7)		-- Destination
)
	RETURNS @PlusFactorTable TABLE (
	PlusFactor1 decimal(9,2),
	PlusFactor2 decimal(9,2))  AS
BEGIN
	Declare @PlusFactor1 decimal(9,2), @PlusFactor2 decimal(9,2)


	/*
	Shipments moving between points in the United States assigned MI Zip Codes 480-483, on the one hand,
	and, points in Canada assigned Canadian Postal Codes as shown in Note 1 on the other, which are
	interchanged at MI Zip Codes 480-483, the factor to apply between MI Zip Codes 480-483 and the
	Canadian origin or destination shall be as published in D83, plus ten (10) factors.
	Note 1 - Canada Postal Codes are as follows:
	N0J-N0R		N4S-N4V		N4Z-N5B		N5P-N5R		N5V-N6N		N7L-N7M		N7S-N7X		N8N-N9K
	N5C		N4G		N5H		N7A		N7G		N8A		N8H		N8M		N9V		N9Y

	IF @Interchange in [480-483]	AND		(@Orig in [480-483]	OR	@Dest in [480-483])
*/







	/*
	Interchange must be a zip in the range defined within the PlusFactor table ...[480-483]
	At least the origin or destination must also be in the same zip range....
	And then the Origin or destination must also be a province code matching the "PCode" in the PlusFactor table...
*/


	IF LEFT(@orig,1) BETWEEN 'A' AND 'Z'    
	BEGIN

		SELECT
			@PlusFactor1 = IsNull(PlusFactorAmt,0.00)
		FROM dbo.PlusFactor
		WHERE 
			LEFT(@IntZip,3) BETWEEN	LEFT(Zip,3) AND RIGHT(Zip,3)
			AND LEFT(@orig,3) BETWEEN LEFT(PCode,3) AND RIGHT(PCode,3)
			AND LEFT(@dest,3) BETWEEN	LEFT(Zip,3) AND RIGHT(Zip,3) -- If Origin is Canada, @dest must match Interchange
			AND EffectiveDate = 
		(
			SELECT Max(EffectiveDate)
			FROM dbo.PlusFactor
			WHERE 
				LEFT(@IntZip,3) BETWEEN	LEFT(Zip,3) AND RIGHT(Zip,3)
				AND LEFT(@orig,3) BETWEEN LEFT(PCode,3) AND RIGHT(PCode,3)
				AND LEFT(@dest,3) BETWEEN	LEFT(Zip,3) AND RIGHT(Zip,3) -- If Origin is Canada, @dest must match Interchange
				AND EffectiveDate <= GETDATE()
			GROUP BY Zip, Pcode
		)

	END

	IF LEFT(@dest,1) BETWEEN 'A' AND 'Z'
	BEGIN

		SELECT
			@PlusFactor2 = IsNull(PlusFactorAmt,0.00)
		FROM dbo.PlusFactor
		WHERE 
			LEFT(@IntZip,3) BETWEEN	LEFT(Zip,3) AND RIGHT(Zip,3)
			AND LEFT(@dest,3) BETWEEN LEFT(PCode,3) AND RIGHT(PCode,3)
			AND LEFT(@orig,3) BETWEEN	LEFT(Zip,3) AND RIGHT(Zip,3) -- If Destination is Canada, @orig must match Interchange
			AND EffectiveDate = 
		(
			SELECT Max(EffectiveDate)
			FROM dbo.PlusFactor
			WHERE 
				LEFT(@IntZip,3) BETWEEN	LEFT(Zip,3) AND RIGHT(Zip,3)
				AND LEFT(@dest,3) BETWEEN LEFT(PCode,3) AND RIGHT(PCode,3)
				AND LEFT(@orig,3) BETWEEN	LEFT(Zip,3) AND RIGHT(Zip,3) -- If Origin is Canada, @dest must match Interchange
				AND EffectiveDate <= GETDATE()
			GROUP BY Zip, Pcode
		)

	END

	INSERT INTO @PlusFactorTable
	Values( Isnull(@PlusFactor1,0.00), IsNull(@PlusFactor2,0.00)		)

	RETURN
END

GO


