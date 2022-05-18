IF EXISTS (SELECT *
FROM sys.objects
WHERE  object_id = OBJECT_ID(N'[dbo].[d83CheckMinimums]')
	AND type IN ( N'FN', N'IF', N'TF', N'FS', N'FT' ))
  DROP FUNCTION [dbo].[d83CheckMinimums]
GO

CREATE FUNCTION [dbo].[d83CheckMinimums](@zip varchar(7))
RETURNS @MinFactorRevenueTable TABLE (
	MinFactorRevenue decimal(11,2))
AS
BEGIN
	Declare @MinFactor int

	/********************************/
	-- Lookup Minimums
	IF	(Len(@zip) = 5 AND Left(@zip,1) BETWEEN '0' AND '9'	)
	BEGIN
		------------------------------------------------------------
		-- #2a		CHECK USA RANGES #1
		Set @MinFactor = 
		(
			Select Factor_Minimum
		from dbo.Section6
		where (Len(ZipCode1) = 8 AND SUBSTRING(ZipCode1,6,1) = '-')
			AND @zip between LEFT(ZipCode1,5) AND (LEFT(ZipCode1,3) + RIGHT(ZipCode1,2)) 
		)
	END

	IF @MinFactor IS NULL
	BEGIN
		------------------------------------------------------------
		-- #1	(FULL - e.g. 04730 or A1A1A1
		Set @MinFactor = (Select Factor_Minimum
		from dbo.Section6
		where ZipCode1 = @zip)
		IF @MinFactor IS NULL
		BEGIN
			-- #1	LEFT(Zip,3)
			Set @MinFactor = (Select Factor_Minimum
			from dbo.Section6
			where ZipCode1 = Left(@zip,3))
		END
	END



	IF (@MinFactor IS NULL)
	BEGIN
		-- Default to lowest..
		Set @MinFactor = 0
	END

	INSERT INTO @MinFactorRevenueTable
	SELECT Isnull(MinDivisionAmt,0.00)
	FROM dbo.MinimumDivision
	WHERE 
		@MinFactor Between LowFactor and HiFactor

		-- Only select the most recent effective date for the matching factor
		-- NOTE:  This logic works fine for minimum changes...based on effective dates only.
		--....if Factor ranges changed...may need to alter logic.
		AND EffectiveDate = 
	(
		Select MAX(EffectiveDate)
		FROM dbo.MinimumDivision
		WHERE @MinFactor Between LowFactor and HiFactor
			AND EffectiveDate <= GetDate()
	)




	RETURN
END


/*
Select * from Section6 where Len(ZipCode1) = 8 and Len(ZipCode2) <> 5
Select *, LEFT(ZipCode1,5) As Range1, (LEFT(ZipCode1,3) + RIGHT(ZipCode1,2)) As Range2 from Section6 where Len(ZipCode1) = 8 AND Factor_Minimum > 80
*/

GO


