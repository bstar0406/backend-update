CREATE OR ALTER PROCEDURE [dbo].[Request_History_By_Number_Select]
	@RequestNumber VARCHAR(32), @VersionNum INT
AS

SET NOCOUNT ON;

WITH UM AS (
SELECT UT.UserManagerVersionID, U.UserName
FROM dbo.[User_History] U
INNER JOIN dbo.[User_History] UT ON U.UserVersionID = UT.UserManagerVersionID
),
UT AS 
(
SELECT U.UserVersionID, 
	U.UserName, 
	UM.UserName AS UserManagerName
FROM dbo.[User_History] U
LEFT JOIN UM ON U.UserManagerVersionID = UM.UserManagerVersionID
)

SELECT CAST(
(SELECT *
FROM
(
	SELECT R.RequestID AS request_id,
		R.RequestNumber AS request_number,
		R.RequestCode AS request_code,
		R.[IsReview] AS is_review,
		R.IsActive AS is_active,
		R.IsInactiveViewable AS is_inactive_viewable,
		R.IsValidData AS is_valid_data,
		R.InitiatedOn AS initiated_on,
		I.UserName AS initiated_by,
		R.SubmittedOn AS submitted_on,
		B.UserName AS submitted_by,
		S.UserName AS sales_rep,
		S.UserManagerName AS sales_manager,
		E.UserName AS current_editor,
		R.VersionNum AS version_num,
		(SELECT * FROM (SELECT RIC.RequestInformationID AS request_information_id, 
		C.CustomerID AS customer, 
		YP.RequestTypeID AS request_type,  
		L.LanguageID AS [language], 
		Y.CurrencyID AS [currency],
		RIC.RequestNumber AS request_number,
		RIC.IsValidData AS is_valid_data,
		RIC.IsNewBusiness AS is_new_business, 
		CASE WHEN A.AccountID IS NULL THEN 'New' ELSE 'Expanded' END AS business_type_name,
		RIC.IsPayingByCreditCard AS is_paying_by_credit_card, 
		RIC.IsExtendedPayment AS is_extended_payment, 
		RIC.ExtendedPaymentDays AS extended_payment_days, 
		RIC.ExtendedPaymentTermsMargin AS extended_payment_terms_margin,
		RIC.[Priority] AS [priority]) AS G FOR JSON AUTO, WITHOUT_ARRAY_WRAPPER) AS request_information,
		(SELECT * FROM (SELECT C.CustomerID AS customer_id,  
		A.AccountID AS account,
		N.AccountID AS parent_account_id, 
		N.AccountNumber AS parent_account_number, 
		N.AccountName AS parent_account_name, 
		A.AccountName AS account_name, 
		A.AccountNumber AS account_number, 
		SL.ServiceLevelID AS service_level_id,
		SL.ServiceLevelCode AS service_level_code,
		SO.ServiceOfferingID AS service_offering_id,
		SO.ServiceOfferingName AS service_offering_name,
		TY.CityID AS city,
		TY.CityName AS city_name,
		VY.ProvinceID AS province_id,
		C.CustomerName AS customer_name, 
		C.CustomerAlias AS customer_alias,  
		C.CustomerAddressLine1 AS customer_address_line_1, 
		C.CustomerAddressLine2 AS customer_address_line_2, 
		C.PostalCode AS postal_code, 
		C.ContactName AS contact_name,  
		C.ContactTitle AS contact_title, 
		C.Phone AS phone, 
		C.Email AS email, 
		C.Website AS website, 
		C.IsValidData AS is_valid_data
		) AS H FOR JSON AUTO, WITHOUT_ARRAY_WRAPPER) AS customer
	FROM dbo.Request_History R
	LEFT JOIN UT I ON R.InitiatedByVersion = I.UserVersionID
	LEFT JOIN dbo.RequestStatus RST ON RST.RequestID = R.RequestID
	LEFT JOIN dbo.RequestStatus_History RS ON RST.RequestStatusID = RS.RequestStatusID AND RS.IsLatestVersion = 1
	LEFT JOIN dbo.RequestInformation_History RIC ON R.RequestInformationVersionID = RIC.RequestInformationVersionID
	LEFT JOIN dbo.Customer_History C ON RIC.CustomerVersionID = C.CustomerVersionID
	LEFT JOIN dbo.ServiceLevel_History SL ON C.ServiceLevelVersionID = SL.ServiceLevelVersionID
	LEFT JOIN dbo.ServiceOffering_History SO ON SL.ServiceOfferingVersionID = SO.ServiceOfferingVersionID
	LEFT JOIN UT AS S ON RS.SalesRepresentativeVersionID = S.USerVersionID
	LEFT JOIN UT AS E ON RS.CurrentEditorVersionID = E.USerVersionID
	LEFT JOIN dbo.Account_History A ON C.AccountVersionID = A.AccountVersionID
	LEFT JOIN dbo.AccountTree_History NT ON C.AccountVersionID = NT.AccountVersionID
	LEFT JOIN dbo.Account_History N ON NT.ParentAccountVersionID = N.AccountVersionID
	LEFT JOIN dbo.City_History TY ON C.CityVersionID = TY.CityVersionID
	LEFT JOIN dbo.Province_History VY ON TY.ProvinceVersionID = VY.ProvinceVersionID
	LEFT JOIN UT B ON R.SubmittedByVersion = B.USerVersionID
	LEFT JOIN dbo.Language_History L ON RIC.LanguageVersionID = L.LanguageVersionID
	LEFT JOIN dbo.Currency_History Y ON RIC.CurrencyVersionID = Y.CurrencyVersionID
	LEFT JOIN dbo.RequestType_History YP ON RIC.RequestTypeVersionID = YP.RequestTypeVersionID
	WHERE R.RequestNumber = @RequestNumber AND R.VersionNum = @VersionNum
	) AS Q
	FOR JSON AUTO, WITHOUT_ARRAY_WRAPPER)
	AS VARCHAR(MAX))
RETURN 1

GO
