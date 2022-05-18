CREATE OR ALTER PROCEDURE [dbo].[Request_By_ID_Select]
	@RequestID BIGINT,
	@IsNewRequest BIT
AS

SET NOCOUNT ON;

WITH UM AS (
SELECT DISTINCT UT.UserManagerID, U.UserName
FROM dbo.[User] U
INNER JOIN dbo.[User] UT ON U.UserID = UT.UserManagerID
),
UT AS 
(
SELECT U.UserID, U.UserName, UM.UserName AS UserManagerName
FROM dbo.[User] U
LEFT JOIN UM ON U.UserManagerID = UM.UserManagerID
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
		S.UserName AS submitted_by,
		SR.UserName AS sales_rep,
		SR.UserManagerName AS sales_manager,
		E.UserName AS current_editor,
		RH.VersionNum AS version_num,
		(SELECT * FROM (SELECT RIC.RequestInformationID AS request_information_id, 
		RIC.CustomerID AS customer, 
		RIC.RequestTypeID AS request_type,  
		RIC.LanguageID AS [language], 
		RIC.CurrencyID AS [currency],
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
		C.AccountID AS account, 
		NT.ParentAccountID AS parent_account_id, 
		N.AccountNumber AS parent_account_number, 
		N.AccountName AS parent_account_name, 
		A.AccountName AS account_name, 
		A.AccountNumber AS account_number, 
		C.ServiceLevelID AS service_level_id,
		SL.ServiceLevelCode AS service_level_code,
		SO.ServiceOfferingID AS service_offering_id,
		SO.ServiceOfferingName AS service_offering_name,
		C.CityID AS city,
		Y.CityName AS city_name,
		Y.ProvinceID AS province_id,
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
		) AS H FOR JSON AUTO, WITHOUT_ARRAY_WRAPPER) AS customer,
		@IsNewRequest AS is_new_request
	FROM dbo.Request R
	INNER JOIN dbo.RequestStatus RS ON R.RequestID = RS.RequestID
	INNER JOIN dbo.Request_History RH ON R.RequestID = RH.RequestID AND RH.IsLatestVersion = 1
	INNER JOIN dbo.RequestInformation RIC ON R.RequestInformationID = RIC.RequestInformationID
	INNER JOIN dbo.Customer C ON RIC.CustomerID = C.CustomerID
	INNER JOIN dbo.ServiceLevel SL ON C.ServiceLevelID = SL.ServiceLevelID
	INNER JOIN dbo.ServiceOffering SO ON SL.ServiceOfferingID = SO.ServiceOfferingID
	INNER JOIN UT I ON R.InitiatedBy = I.UserID
	LEFT JOIN UT SR ON RS.SalesRepresentativeID = SR.UserID
	LEFT JOIN UT E ON RS.CurrentEditorID = E.UserID
	LEFT JOIN dbo.Account A ON C.AccountID = A.AccountID
	LEFT JOIN dbo.AccountTree NT ON C.AccountID = NT.AccountID
	LEFT JOIN dbo.Account N ON NT.ParentAccountID = N.AccountID
	LEFT JOIN dbo.City Y ON C.CityID = Y.CityID
	LEFT JOIN UT S ON R.SubmittedBy = S.UserID
	WHERE R.RequestID = @RequestID
	) AS Q
	FOR JSON AUTO, WITHOUT_ARRAY_WRAPPER)
	AS VARCHAR(MAX))
RETURN 1

GO
