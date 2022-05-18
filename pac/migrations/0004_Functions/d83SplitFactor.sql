IF EXISTS (SELECT *
FROM sys.objects
WHERE  object_id = OBJECT_ID(N'[dbo].[d83SplitFactor]')
	AND type IN ( N'FN', N'IF', N'TF', N'FS', N'FT' ))
  DROP FUNCTION [dbo].[d83SplitFactor]
GO

CREATE FUNCTION [dbo].[d83SplitFactor]
(	
	-- Previous Fiscal Q1 Reveneue (by Tier)
	@zip1 varchar(7)
	, @zip2 varchar(7)
)
RETURNS @FactorTable TABLE (
	Factor decimal(9,2))
AS
BEGIN
	Declare @Factor int
	/*
	**************************************************************
	First, 
		Look up EACH pair of ZIP Codes in Section 4 
				(origin ZIP		to		interline ZIP) 
				(interline ZIP	to		destination ZIP) 
		...If the pair is found, save the EXCEPTION FACTOR.
				
	Next,
		IF NO EXCEPTION
		...lookup "FACTOR" from Section 3
	****************************************************************************************************	
	NOTE:  
		Section 3/4 tables are "BETWEEN/AND" as well as being both 3 digit and 5 digit ZIP codes.
		Any 3 digit ZIP Code includes all ZIP Codes contained within the range of [xxx00] thru [xxx99].
		This configuration results in the need to make multiple passes against the data.  
		If the "zip pair" is NOT found in Section 4, look them up in Section 3.
	****************************************************************************************************	
*/



	/*
	Modification:  20180524
	Section 3 data is storing partial HiZipCodes (first 3 digits)
	Section 4 data is storing full HiZipCodes (all 5 digits).

	Hence some ranges and logic below don't apply on Section 4 table...so removing specific Lookups for ranges on 3 digit values....
*/

	/********************************/
	-- Lookup Exceptions
	------------------------------------------------------------
	-- LookupX1	(ZIP1 to ZIP2)
	Set @Factor = (Select Factor_Exception
	from dbo.Section4
	where LowZipCode = @zip1 AND HiZipCode = @zip2)
	IF @Factor IS NULL
	BEGIN
		------------------------------------------------------------
		-- LookupX2(	ZIP2	 to	ZIP1)
		Set @Factor = (Select Factor_Exception
		from dbo.Section4
		where LowZipCode = @zip2 AND HiZipCode = @zip1)
		IF @Factor IS NULL
		BEGIN
			------------------------------------------------------------
			-- LookupX3 (	LEFT(ZIP1,3)	to	ZIP2)
			Set @Factor = (Select Factor_Exception
			from dbo.Section4
			where LowZipCode = Left(@zip1,3) AND HiZipCode = @zip2)
			IF @Factor IS NULL
			BEGIN
				------------------------------------------------------------
				-- LookupX4 (	LEFT(ZIP2,3)	to	ZIP1)
				Set @Factor = (Select Factor_Exception
				from dbo.Section4
				where LowZipCode = Left(@zip2,3) AND HiZipCode = @zip1)
				IF @Factor IS NULL
				BEGIN
					------------------------------------------------------------
					-- LookupX5 (	ZIP1	to	LEFT(ZIP2,3)	)
					Set @Factor = (Select Factor_Exception
					from dbo.Section4
					where LowZipCode = @zip1 AND HiZipCode = Left(@zip2,3))
					IF @Factor IS NULL
					BEGIN
						------------------------------------------------------------
						-- LookupX6 (	ZIP2	to	LEFT(ZIP1,3)	)
						Set @Factor = (Select Factor_Exception
						from dbo.Section4
						where LowZipCode = @zip2 AND HiZipCode = Left(@zip1,3))
						IF @Factor IS NULL
						BEGIN
							------------------------------------------------------------
							-- LookupX7 (	Left(ZIP1,3)	to	LEFT(ZIP2,3)	)
							Set @Factor = (Select Factor_Exception
							from dbo.Section4
							where LowZipCode = Left(@zip1,3) AND HiZipCode = Left(@zip2,3))
							IF @Factor IS NULL
							BEGIN
								------------------------------------------------------------
								-- LookupX8 (	Left(ZIP2,3)	to	LEFT(ZIP1,3)	)
								Set @Factor = (Select Factor_Exception
								from dbo.Section4
								where LowZipCode = Left(@zip2,3) AND HiZipCode = Left(@zip1,3))
								IF @Factor IS NULL
								BEGIN

									/*********************************************************************************************/
									-- check ranges
									/*********************************************************************************************/
									------------------------------------------------------------
									-- LookupXR9 (	"LOW-RANGE"	to	ZIP2	)
									Set @Factor = (Select Factor_Exception
									from dbo.Section4
									where Left(@zip1,3) BETWEEN Left(LowZipCode,3) AND Right(LowZipCode,3)
										AND HiZipCode = @zip2)
									IF @Factor IS NULL
									BEGIN
										------------------------------------------------------------
										-- LookupXR10 (	"LOW-RANGE"	to	ZIP1	)
										Set @Factor = (Select Factor_Exception
										from dbo.Section4
										where Left(@zip2,3) BETWEEN Left(LowZipCode,3) AND Right(LowZipCode,3)
											AND HiZipCode = @zip1)
										IF @Factor IS NULL
										BEGIN
											------------------------------------------------------------
											-- LookupXR11 (	"LOW-RANGE"	to	Left(ZIP2,3)	)
											Set @Factor = (Select Factor_Exception
											from dbo.Section4
											where Left(@zip1,3) BETWEEN Left(LowZipCode,3) AND Right(LowZipCode,3)
												AND HiZipCode = Left(@zip2,3))
											IF @Factor IS NULL
											BEGIN
												------------------------------------------------------------
												-- LookupXR12 (	"LOW-RANGE"	to	Left(ZIP1,3)	)
												Set @Factor = (Select Factor_Exception
												from dbo.Section4
												where Left(@zip2,3) BETWEEN Left(LowZipCode,3) AND Right(LowZipCode,3)
													AND HiZipCode = Left(@zip1,3))
											--IF @Factor IS NULL
											--BEGIN
											--	------------------------------------------------------------
											--	-- LookupXR13 (	ZIP1	to	"HI-RANGE"	)
											--	Set @Factor = (Select Factor_Exception from dbo.Section4
											--					where LowZipCode = @zip1 
											--						AND Left(@zip2,3) BETWEEN Left(HiZipCode,3) AND Right(HiZipCode,3))
											--	IF @Factor IS NULL
											--	BEGIN
											--		------------------------------------------------------------
											--		-- LookupXR14 (	ZIP2	to	"HI-RANGE"	)
											--		Set @Factor = (Select Factor_Exception from dbo.Section4
											--						where LowZipCode = @zip2 
											--							AND Left(@zip1,3) BETWEEN Left(HiZipCode,3) AND Right(HiZipCode,3))
											--		IF @Factor IS NULL
											--		BEGIN
											--			------------------------------------------------------------
											--			-- LookupXR15 (	Left(ZIP1,3)	to	"HI-RANGE"	)
											--			Set @Factor = (Select Factor_Exception from dbo.Section4
											--							where LowZipCode = Left(@zip1,3)
											--								AND Left(@zip2,3) BETWEEN Left(HiZipCode,3) AND Right(HiZipCode,3))
											--			IF @Factor IS NULL
											--			BEGIN
											--				------------------------------------------------------------
											--				-- LookupXR16 (	Left(ZIP1,3)	to	"HI-RANGE"	)
											--				Set @Factor = (Select Factor_Exception from dbo.Section4
											--								where LowZipCode = Left(@zip2,3)
											--									AND Left(@zip1,3) BETWEEN Left(HiZipCode,3) AND Right(HiZipCode,3))
											--				IF @Factor IS NULL
											--				BEGIN
											--					------------------------------------------------------------
											--					-- LookupXR17 (	Z1"LOW-RANGE"   to	Z2"HI-RANGE"	)
											--					Set @Factor = (Select Factor_Exception from dbo.Section4
											--									where Left(@zip1,3) BETWEEN Left(LowZipCode,3) AND Right(LowZipCode,3)
											--										AND Left(@zip2,3) BETWEEN Left(HiZipCode,3) AND Right(HiZipCode,3))
											--					IF @Factor IS NULL
											--					BEGIN
											--						------------------------------------------------------------
											--						-- LookupXR1 (	Z1"HI-RANGE"   to	Z2"LOW-RANGE"	)
											--						Set @Factor = (Select Factor_Exception from dbo.Section4
											--										where Left(@zip2,3) BETWEEN Left(LowZipCode,3) AND Right(LowZipCode,3)
											--											AND Left(@zip1,3) BETWEEN Left(HiZipCode,3) AND Right(HiZipCode,3))

											--					END --xR17
											--				END --xR16
											--			END --xR15
											--		END --xR14
											--	END --xR13
											--END --xR12
											END
										--xR11
										END
									--xR10
									END
								--xR9
								/*********************************************************************************************/
								-- end of check ranges
								/*********************************************************************************************/
								END
							--x8
							END--x7
						END--x6
					END--x5
				END--x4
			END--x3
		END--x2
	END--x1
	-- Lookup Exceptions
	/********************************/



	/********************************/
	-- Lookup Primary	
	IF (@Factor IS NULL)
	BEGIN
		Set @Factor = (SELECT Factor
		FROM dbo.Section3
		where LowZipCode = @zip1 AND HiZipCode = @zip2)
		IF @Factor IS NULL
		BEGIN
			------------------------------------------------------------
			-- LookupP2(	ZIP2	 to	ZIP1)
			Set @Factor = (SELECT Factor
			FROM dbo.Section3
			where LowZipCode = @zip2 AND HiZipCode = @zip1)
			IF @Factor IS NULL
			BEGIN
				------------------------------------------------------------
				-- LookupP3 (	LEFT(ZIP1,3)	to	ZIP2)
				Set @Factor = (SELECT Factor
				FROM dbo.Section3
				where LowZipCode = Left(@zip1,3) AND HiZipCode = @zip2)
				IF @Factor IS NULL
				BEGIN
					------------------------------------------------------------
					-- LookupP4 (	LEFT(ZIP2,3)	to	ZIP1)
					Set @Factor = (SELECT Factor
					FROM dbo.Section3
					where LowZipCode = Left(@zip2,3) AND HiZipCode = @zip1)
					IF @Factor IS NULL
					BEGIN
						------------------------------------------------------------
						-- LookupP5 (	ZIP1	to	LEFT(ZIP2,3)	)
						Set @Factor = (SELECT Factor
						FROM dbo.Section3
						where LowZipCode = @zip1 AND HiZipCode = Left(@zip2,3))
						IF @Factor IS NULL
						BEGIN
							------------------------------------------------------------
							-- LookupP6 (	ZIP2	to	LEFT(ZIP1,3)	)
							Set @Factor = (SELECT Factor
							FROM dbo.Section3
							where LowZipCode = @zip2 AND HiZipCode = Left(@zip1,3))
							IF @Factor IS NULL
							BEGIN
								------------------------------------------------------------
								-- LookupP7 (	Left(ZIP1,3)	to	LEFT(ZIP2,3)	)
								Set @Factor = (SELECT Factor
								FROM dbo.Section3
								where LowZipCode = Left(@zip1,3) AND HiZipCode = Left(@zip2,3))
								IF @Factor IS NULL
								BEGIN
									------------------------------------------------------------
									-- LookupP8 (	Left(ZIP2,3)	to	LEFT(ZIP1,3)	)
									Set @Factor = (SELECT Factor
									FROM dbo.Section3
									where LowZipCode = Left(@zip2,3) AND HiZipCode = Left(@zip1,3))
									IF @Factor IS NULL
									BEGIN

										/*********************************************************************************************/
										-- check ranges
										/*********************************************************************************************/
										------------------------------------------------------------
										-- LookupPR9 (	"LOW-RANGE"	to	ZIP2	)
										Set @Factor = (Select Factor
										from dbo.Section3
										where Left(@zip1,3) BETWEEN Left(LowZipCode,3) AND Right(LowZipCode,3)
											AND HiZipCode = @zip2)
										IF @Factor IS NULL
										BEGIN
											------------------------------------------------------------
											-- LookupPR10 (	"LOW-RANGE"	to	ZIP1	)
											Set @Factor = (Select Factor
											from dbo.Section3
											where Left(@zip2,3) BETWEEN Left(LowZipCode,3) AND Right(LowZipCode,3)
												AND HiZipCode = @zip1)
											IF @Factor IS NULL
											BEGIN
												------------------------------------------------------------
												-- LookupPR11 (	"LOW-RANGE"	to	Left(ZIP2,3)	)
												Set @Factor = (Select Factor
												from dbo.Section3
												where Left(@zip1,3) BETWEEN Left(LowZipCode,3) AND Right(LowZipCode,3)
													AND HiZipCode = Left(@zip2,3))
												IF @Factor IS NULL
												BEGIN
													------------------------------------------------------------
													-- LookupPR12 (	"LOW-RANGE"	to	Left(ZIP1,3)	)
													Set @Factor = (Select Factor
													from dbo.Section3
													where Left(@zip2,3) BETWEEN Left(LowZipCode,3) AND Right(LowZipCode,3)
														AND HiZipCode = Left(@zip1,3))
													IF @Factor IS NULL
													BEGIN
														------------------------------------------------------------
														-- LookupPR13 (	ZIP1	to	"HI-RANGE"	)
														Set @Factor = (Select Factor
														from dbo.Section3
														where LowZipCode = @zip1
															AND Left(@zip2,3) BETWEEN Left(HiZipCode,3) AND Right(HiZipCode,3))
														IF @Factor IS NULL
														BEGIN
															------------------------------------------------------------
															-- LookupPR14 (	ZIP2	to	"HI-RANGE"	)
															Set @Factor = (Select Factor
															from dbo.Section3
															where LowZipCode = @zip2
																AND Left(@zip1,3) BETWEEN Left(HiZipCode,3) AND Right(HiZipCode,3))
															IF @Factor IS NULL
															BEGIN
																------------------------------------------------------------
																-- LookupPR15 (	Left(ZIP1,3)	to	"HI-RANGE"	)
																Set @Factor = (Select Factor
																from dbo.Section3
																where LowZipCode = Left(@zip1,3)
																	AND Left(@zip2,3) BETWEEN Left(HiZipCode,3) AND Right(HiZipCode,3))
																IF @Factor IS NULL
																BEGIN
																	------------------------------------------------------------
																	-- LookupPR16 (	Left(ZIP1,3)	to	"HI-RANGE"	)
																	Set @Factor = (Select Factor
																	from dbo.Section3
																	where LowZipCode = Left(@zip2,3)
																		AND Left(@zip1,3) BETWEEN Left(HiZipCode,3) AND Right(HiZipCode,3))
																	IF @Factor IS NULL
																	BEGIN
																		------------------------------------------------------------
																		-- LookupPR17 (	Z1"LOW-RANGE"   to	Z2"HI-RANGE"	)
																		Set @Factor = (Select Factor
																		from dbo.Section3
																		where Left(@zip1,3) BETWEEN Left(LowZipCode,3) AND Right(LowZipCode,3)
																			AND Left(@zip2,3) BETWEEN Left(HiZipCode,3) AND Right(HiZipCode,3))
																		IF @Factor IS NULL
																		BEGIN
																			------------------------------------------------------------
																			-- LookupPR18 (	Z1"HI-RANGE"   to	Z2"LOW-RANGE"	)
																			Set @Factor = (Select Factor
																			from dbo.Section3
																			where Left(@zip2,3) BETWEEN Left(LowZipCode,3) AND Right(LowZipCode,3)
																				AND Left(@zip1,3) BETWEEN Left(HiZipCode,3) AND Right(HiZipCode,3))

																		END
																	--xP17
																	END
																--xP16
																END
															--xP15
															END
														--xP14
														END
													--xP13
													END
												--xP12
												END
											--xP11
											END
										--xP10
										END
									--xR9
									/*********************************************************************************************/
									-- end of check ranges
									/*********************************************************************************************/
									END
								--x8
								END--x7
							END--x6
						END--x5
					END--x4
				END--x3
			END--x2
		END--x1
	END--IsNull?
	-- Lookup Primary
	/********************************/


	IF (@Factor IS NULL)
	BEGIN
		--PRINT ' Unable to extract factor'
		INSERT INTO @FactorTable
		Values(0)
	-- "Is there.." a DEFAULT FACTOR IF THERE IS NO MATCHING RESULT??
	END
	ELSE
	BEGIN
		INSERT INTO @FactorTable
		Values(@Factor)
	END

	RETURN
END

/*****************************************************************************************/
/*
Use to lookup a pCode range with we have A1A-A2X values on Section3

	Declare @varX char(3) = 'A1D'
	Select * from Section3  
	where HiZipCode = 'A1K' and Len(LowZipCode) > 3
	and @varX between LEFT(LowZipCode,3) and RIGHT(LowZIpCode,3)
*/
/*****************************************************************************************/



/*	
SELECT Max(Len(LowZipCode)) from dbo.Section3
SELECT * from dbo.Section3 where LEN(LowZipCode) > 3 and LEFT(LowZipCode,1) NOT BETWEEN 'A' and 'Z'
 
Select * from Section4 where LEN(LowZipCode) > 3

SELECt * from dbo.Section3 where LowZipCode = '594'
SELECt * from dbo.Section3 where LowZipCode = '594 1)'

	Select Factor from dbo.Section3 where (LEFT('L6T4H6',3) between LEFT(HiZipCode,3) and RIGHT(HiZipCode,3))		
	AND Left('48198',3) = LowZipCode

*/
--Select * from d83SplitFactor('L6T4H6','48198')
--Select * from d83SplitFactor('48198','047')



GO
