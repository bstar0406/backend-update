IF EXISTS (SELECT *
FROM sys.objects
WHERE  object_id = OBJECT_ID(N'[dbo].[getD83SPLIT]')
	AND type IN ( N'FN', N'IF', N'TF', N'FS', N'FT' ))
  DROP FUNCTION [dbo].[getD83SPLIT]
GO

CREATE FUNCTION [dbo].[getD83SPLIT] (		@orig_Zip varchar(7), @intl_Zip varchar(7), @dest_Zip varchar(7), @revenue decimal(11,2)	) 
RETURNS @SplitPercents TABLE (
	Percent1 decimal(8,5),
	Percent2 decimal(8,5)) AS
BEGIN

	Declare @factor1 decimal(9,2), @factor2 decimal(9,2)
	Declare @Plus30FactorOrig decimal(9,2)-- Plus30Factor Origin to Interchange 
	Declare @Plus30FactorDest decimal(9,2)-- Plus30Factor Interchange to Destination
	Declare @Plus10FactorOrig decimal(9,2)-- Plus10Factor 
	Declare @Plus10FactorDest decimal(9,2)-- Plus10Factor 
	Declare @splitPercent1 decimal(8,5), @splitPercent2 decimal(8,5)
	Declare @revenue1 decimal(11,2), @revenue2 decimal(11,2)
	Declare @revenue1MIN decimal(11,2), @revenue2MIN decimal(11,2)
	Declare @IsMinimumSplit bit = 0
	Declare @IsFactor1Priority bit = 0

	SET @factor1 = (Select Factor
	FROM dbo.d83SplitFactor(@orig_Zip, @intl_Zip))
	-- Get [FACTOR1]		(Origin to Intl)
	SET @factor2 = (Select Factor
	FROM dbo.d83SplitFactor(@intl_Zip, @dest_Zip))
	-- Get [FACTOR2]		(Intl to Destination)

	-- If @f1 or @f2 is 0...return ZEROS...
	IF NOT (ISNULL(@factor1,0) = 0 OR ISNULL(@factor2,0) = 0)
	BEGIN

		/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/
		/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/
		-- Check "Plus30" 
		Select @Plus30FactorOrig = IsNull(Plus30FactorOrig,0.00) 
			, @Plus30FactorDest = ISNULL(Plus30FactorDest,0.00)
		FROM dbo.d83CheckPlus30Factor(@orig_Zip, @intl_Zip, @dest_Zip)

		If @Plus30FactorOrig > 0
		BEGIN
			SET @factor1 = @factor1 + @Plus30FactorOrig
		END

		If @Plus30FactorDest > 0
		BEGIN
			SET @factor2 = @factor2 + @Plus30FactorDest
		END




		/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/
		/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/
		-- CHECK FOR "PLUS FACTORS"...before calculating splits....
		/*
			If
		*/
		Select @Plus10FactorOrig = PlusFactor1, @Plus10FactorDest = PlusFactor2
		FROM dbo.d83CheckPlusFactor(@orig_Zip, @intl_Zip, @dest_Zip)


		-- Only check Plus10 (if Plus30 is not already applied...)
		If (@Plus30FactorOrig= 0.00 AND @Plus10FactorOrig > 0)
		BEGIN
			--Destination/Interchange are zips;      Origin is Cdn prov.
			--SET @factor1 = @factor1 + IsNull(	(Select PlusFactor FROM dbo.d83CheckPlusFactor(@intl_Zip, @orig_Zip, @dest_Zip))	,0.00)
			SET @factor1 = @factor1 + @Plus10FactorOrig
		END


		IF (@Plus30FactorDest = 0.00 AND @Plus10FactorDest > 0)
		BEGIN
			--Origin /Interchange are zips;     Destination is Cdn prov.
			--SET @factor2 = @factor2 + IsNull(	(Select PlusFactor FROM dbo.d83CheckPlusFactor(@intl_Zip, @dest_Zip, @orig_Zip))	,0.00)
			SET @factor2 = @factor2 + @Plus10FactorDest
		END

		/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/
		/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/




		/*****************************************************************************************************/
		-- CALCULATE SPLITS	
		IF (@factor1 < @factor2)
			BEGIN
			Set @IsFactor1Priority = 1
			Set @splitPercent1 = (@factor1 / (@factor1 + @factor2)) * 100
			Set @splitPercent2 = 100 - @splitPercent1
		END
			ELSE
			BEGIN
			Set @IsFactor1Priority = 0
			Set @splitPercent2 = (@factor2 / (@factor1 + @factor2)) * 100
			Set @splitPercent1 = 100 - @splitPercent2
		END

		SET @revenue1 = @revenue * @splitPercent1 / Cast(100 As decimal(5,2))
		SET @revenue2 = @revenue * @splitPercent2 / Cast(100 As decimal(5,2))
		/*****************************************************************************************************/

		/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/
		-- CHECK FOR MINIMUMS...
		SET @revenue1MIN = (SELECT MinFactorRevenue
		FROM dbo.d83CheckMinimums(@orig_Zip))
		-- Get [FACTOR1]		(Origin to Intl)
		SET @revenue2MIN = (SELECt MinFactorRevenue
		FROM dbo.d83CheckMinimums(@dest_Zip))
		-- Get [FACTOR2]		(Intl to Destination)
		/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/

		IF (	(@revenue1MIN + @revenue2MIN) > @revenue	)			-- IF Minimums exceed total revenue..split 50%/50%
		BEGIN
			SET @splitPercent1 = 50
			SET @splitPercent2 = 50
		END
		ELSE
		BEGIN
			IF 
			(
				@revenue1MIN > @revenue1
				OR
				@revenue1MIN > (CAST(@splitPercent1 as decimal(3,0))	/ 100	* @revenue)
			)
			BEGIN
				SET @splitPercent1 = (@revenue1MIN / @revenue) * 100
				SET @splitPercent2 = 100 - @splitPercent1
				SET @IsMinimumSplit = 1
			END
			ELSE IF 
			(
				@revenue2MIN > @revenue2
				OR
				@revenue2MIN > (CAST(@splitPercent2 as decimal(3,0))	/ 100	* @revenue)
			)
			BEGIN
				SET @splitPercent2 = (@revenue2MIN / @revenue) * 100
				SET @splitPercent1 = 100 - @splitPercent2
				SET @IsMinimumSplit = 1
			END
		END

		-- Only when we have a minimum split do we need to pass back the precision of the "PERCENT SPLIT"
		-- ...otherwise simply round the splits up to whole percentages (e.g. 57/43)
		IF (@IsMinimumSplit = 0)
		BEGIN
			-- Round split percents to whole percentages.
			If (@IsFactor1Priority = 1)
			BEGIN
				SET @splitPercent1 = CAST(@splitPercent1 as decimal(3,0))
				Set @splitPercent2 = 100 - @splitPercent1
			END
			ELSE
			BEGIN
				SET @splitPercent2 = CAST(@splitPercent2 as decimal(3,0))
				SET @splitPercent1 = 100 - @splitPercent2
			END
		END


		INSERT INTO @SplitPercents
		VALUES(@splitPercent1, @splitPercent2)
	-- If the minimums exceed the available revenue...split 50/50...
	END
	ELSE
	BEGIN
		INSERT INTO @SplitPercents
		VALUES(0, 0)
	-- If the minimums exceed the available revenue...split 50/50...
	END
	RETURN
END

GO