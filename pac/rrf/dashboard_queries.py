ColumnMapping = {
    "account_number": {"sortColumn": 'A.AccountNumber', "filter": " AND A.AccountNumber LIKE '%{0}%' "},
    "approvals_completed": {"sortColumn": 'ISNULL(D1.NumApprovalsCompleted, 0)', "filter": " AND (ISNULL(D1.NumApprovalsCompleted, 0) IN ({0})) "},
    "business_type_name": {"sortColumn": 'A.AccountID',
        "filter": """ AND ('Expanded' IN ('{0}') AND A.AccountID IS NOT NULL OR 'New' IN ('{0}') AND A.AccountID IS NULL) """},
    "customer_name": {"sortColumn": 'C.CustomerName', "filter": " AND C.CustomerID IN ({0}) "},
    "date_initiated": {"sortColumn": '', "filter": " "},
    "days_in_queue": {"sortColumn": 'ISNULL(G4.ElapsedTime, 0)', "filter": " AND A.AccountNumber LIKE '%{0}%' "},
    "pricing_analyst_name": {"sortColumn": 'ISNULL(UPA.UserName,'')', "filter": " AND RSU.PricingAnalystID IN ({0}) "},
    "priority": {"sortColumn": 'I.[Priority]', "filter": " AND ( I.[Priority] IN ({0})) "},
    "request_code": {"sortColumn": 'R.requestCode', "filter": " AND R.RequestCode LIKE '%{0}%' "},
    "request_status_type_name": {"sortColumn": 'RST.RequestStatusTypeName', "filter": " AND RSU.RequestStatusTypeID IN ({0}) "},
    "sales_representative_name": {"sortColumn": 'ISNULL(USR.UserName,'')', "filter": " AND RSU.SalesRepresentativeID IN ({0}) "},
    "service_level_code": {"sortColumn": 'SL.ServiceLevelCode', "filter": " AND SL.ServiceLevelID IN ({0}) "},
}

GET_FILTERED_QUERY = """
DECLARE @UserID BIGINT = {user_id};
DECLARE @UserPersona VARCHAR(50);
SELECT @UserPersona = P.PersonaName FROM dbo.[User] U INNER JOIN dbo.Persona P ON U.PersonaID = P.PersonaID WHERE U.UserID = @UserID;

With A1 AS (
SELECT DISTINCT RequestID
FROM dbo.RequestQueue
WHERE CompletedOn IS NULL AND IsActive = 1 AND IsInactiveViewable = 1 AND (
UserID = @UserID OR
UserID IN (SELECT UserID FROM dbo.[User] WHERE UserManagerID = @UserID)
)),

A3 AS (
SELECT Q.RequestID, Q.UserID, Q.AssignedOn, Q.CompletedOn, RST.AssignedPersona
FROM dbo.RequestQueue Q
INNER JOIN dbo.RequestStatusType RST ON Q.RequestStatusTypeID = RST.RequestStatusTypeID
WHERE Q.RequestID IN (SELECT RequestID FROM A1) AND Q.IsActive = 1 AND Q.IsInactiveViewable = 1 AND Q.IsActionable = 1
AND RST.AssignedPersona IN ('Pricing Analyst', 'Credit Analyst', 'Credit Manager', 'Partner Carrier')
),
B1 AS (
SELECT DISTINCT Q.RequestID, Q.RequestStatusTypeID, Q.AssignedOn, U.UserName, Q.UserID
FROM dbo.RequestQueue Q
INNER JOIN dbo.[User] U ON Q.UserID = U.UserID
WHERE Q.RequestID IN (SELECT RequestID FROM A1) AND Q.IsSecondary = 1 AND Q.IsActive = 1 AND Q.IsInactiveViewable = 1
),
C1 AS (
SELECT B1.RequestID, COUNT(DISTINCT B1.RequestStatusTypeID) AS NumApprovalsRequested
FROM B1
INNER JOIN dbo.RequestStatusType RST ON RST.RequestStatusTypeID = B1.RequestStatusTypeID
WHERE RST.RequestStatusTypeName IN ('Pending DRM Approval', 'Pending EPT Approval', 'Pending PC Approval', 'Pending PCR Approval')
GROUP BY B1.RequestID
),
D1 AS (
SELECT B1.RequestID, COUNT(DISTINCT B1.RequestStatusTypeID) AS NumApprovalsCompleted
FROM B1
INNER JOIN dbo.RequestStatusType RST ON RST.RequestStatusTypeID = B1.RequestStatusTypeID
WHERE RST.RequestStatusTypeName IN ('DRM Approved', 'DRM Declined', 'EPT Approved', 'EPT Declined', 'PC Approved', 'PC Declined', 'PCR Approved', 'PCR Declined')
GROUP BY B1.RequestID
),
E1 AS (
SELECT RequestID, [secondary_approval], [status], [date], [user], [is_actionable] FROM (
SELECT B1.RequestID, 'Deal Review' AS [secondary_approval],
    CASE WHEN RST.RequestStatusTypeName = 'Pending DRM Approval' THEN 'Requested' WHEN RST.RequestStatusTypeName = 'DRM Approved' THEN 'Approved' WHEN RST.RequestStatusTypeName = 'DRM Declined' THEN 'Declined' ELSE NULL END AS [status],
    B1.UserName AS [user],
    CASE WHEN RST.RequestStatusTypeName = 'Pending DRM Approval' AND B1.UserID = @UserID THEN 1 ELSE 0 END AS [is_actionable],
    B1.AssignedOn AS [date],
ROW_NUMBER() OVER(PARTITION BY B1.RequestID ORDER BY AssignedOn DESC) AS RN
FROM B1
INNER JOIN dbo.RequestStatusType RST ON RST.RequestStatusTypeID = B1.RequestStatusTypeID
WHERE RST.RequestStatusTypeName IN ('Pending DRM Approval', 'DRM Approved', 'DRM Declined')) AS T
WHERE RN = 1

UNION

SELECT RequestID, [secondary_approval], [status], [date], [user], [is_actionable] FROM (
SELECT B1.RequestID, 'Pricing Committee' AS [secondary_approval],
    CASE WHEN RST.RequestStatusTypeName = 'Pending PCR Approval' THEN 'Requested' WHEN RST.RequestStatusTypeName = 'PCR Approved' THEN 'Approved' WHEN RST.RequestStatusTypeName = 'PCR Declined' THEN 'Declined' ELSE NULL END AS [status],
    B1.UserName AS [user],
    CASE WHEN RST.RequestStatusTypeName = 'Pending PCR Approval' AND B1.UserID = @UserID THEN 1 ELSE 0 END AS [is_actionable],
    B1.AssignedOn AS [date],
ROW_NUMBER() OVER(PARTITION BY B1.RequestID ORDER BY AssignedOn DESC) AS RN
FROM B1
INNER JOIN dbo.RequestStatusType RST ON RST.RequestStatusTypeID = B1.RequestStatusTypeID
WHERE RST.RequestStatusTypeName IN ('Pending PCR Approval', 'PCR Approved', 'PCR Declined')) AS T
WHERE RN = 1

UNION

SELECT RequestID, [secondary_approval], [status], [date], [user], [is_actionable] FROM (
SELECT B1.RequestID, 'Priority Change' AS [secondary_approval],
    CASE WHEN RST.RequestStatusTypeName = 'Pending PC Approval' THEN 'Requested' WHEN RST.RequestStatusTypeName = 'PC Approved' THEN 'Approved' WHEN RST.RequestStatusTypeName = 'PC Declined' THEN 'Declined' ELSE NULL END AS [status],
    B1.UserName AS [user],
    CASE WHEN RST.RequestStatusTypeName = 'Pending PC Approval' AND B1.UserID = @UserID THEN 1 ELSE 0 END AS [is_actionable],
    B1.AssignedOn AS [date],
ROW_NUMBER() OVER(PARTITION BY B1.RequestID ORDER BY AssignedOn DESC) AS RN
FROM B1
INNER JOIN dbo.RequestStatusType RST ON RST.RequestStatusTypeID = B1.RequestStatusTypeID
WHERE RST.RequestStatusTypeName IN ('Pending PC Approval', 'PC Approved', 'PC Declined')) AS T
WHERE RN = 1

UNION

SELECT RequestID, [secondary_approval], [status], [date], [user], [is_actionable] FROM (
SELECT B1.RequestID, 'Extended Payment' AS [secondary_approval],
    CASE WHEN RST.RequestStatusTypeName = 'Pending EPT Approval' THEN 'Requested' WHEN RST.RequestStatusTypeName = 'EPT Approved' THEN 'Approved' WHEN RST.RequestStatusTypeName = 'EPT Declined' THEN 'Declined' ELSE NULL END AS [status],
    B1.UserName AS [user],
    CASE WHEN RST.RequestStatusTypeName = 'Pending EPT Approval' AND B1.UserID = @UserID THEN 1 ELSE 0 END AS [is_actionable],
    B1.AssignedOn AS [date],
ROW_NUMBER() OVER(PARTITION BY B1.RequestID ORDER BY AssignedOn DESC) AS RN
FROM B1
INNER JOIN dbo.RequestStatusType RST ON RST.RequestStatusTypeID = B1.RequestStatusTypeID
WHERE RST.RequestStatusTypeName IN ('Pending EPT Approval', 'EPT Approved', 'EPT Declined')) AS T
WHERE RN = 1
),
F1 AS
(
SELECT E1.RequestID, (SELECT E2.[secondary_approval], E2.[status], E2.[date], E2.[user], E2.[is_actionable] FROM E1 AS E2 WHERE E1.RequestID = E2.RequestID FOR JSON AUTO) AS approvals
FROM E1
GROUP BY E1.RequestID),
G1 AS (
SELECT * FROM (
SELECT RequestID, AssignedOn,
ROW_NUMBER() OVER(PARTITION BY A3.RequestID ORDER BY A3.AssignedOn DESC) AS RN
FROM A3 WHERE AssignedPersona = 'Credit Analyst') AS T
WHERE RN = 1
),
G2 AS (
SELECT * FROM (
SELECT RequestID, AssignedOn,
ROW_NUMBER() OVER(PARTITION BY A3.RequestID ORDER BY A3.AssignedOn DESC) AS RN
FROM A3 WHERE AssignedPersona = 'Credit Manager') AS T
WHERE RN = 1
),
G3 AS (
SELECT * FROM (
SELECT RequestID, AssignedOn,
ROW_NUMBER() OVER(PARTITION BY A3.RequestID ORDER BY A3.AssignedOn DESC) AS RN
FROM A3 WHERE AssignedPersona = 'Partner Carrier') AS T
WHERE RN = 1
),
G4 AS (
SELECT * FROM (
SELECT RequestID, UserID, SUM(DATEDIFF(MINUTE, AssignedOn, ISNULL(CompletedON, GETUTCDATE()))) / (24*60) AS ElapsedTime
FROM A3 WHERE AssignedPersona = 'Pricing Analyst'
GROUP BY RequestID, UserID) AS T
)

{{opening_clause}}
SELECT R.RequestNumber AS request_number,
    R.RequestID AS request,
    R.RequestCode AS request_code,
    ISNULL(A.AccountNumber,'') AS account_number,
    ISNULL(C.CustomerName,'') AS customer_name,
    C.ServiceLevelID AS service_level_id,
    SL.ServiceLevelCode AS service_level_code,
    ISNULL(RSU.PricingAnalystID,'') AS pricing_analyst_id,
    ISNULL(UPA.UserName,'') AS pricing_analyst_name,
    ISNULL(RSU.SalesRepresentativeID,'') AS sales_representative_id,
    ISNULL(USR.UserName,'') AS sales_representative_name,
    ISNULL(RSU.CurrentEditorID,'') AS current_editor_id,
    ISNULL(CUE.UserName,'') AS current_editor_name,
    ISNULL(I.[Priority],'') AS [priority],
    RSU.RequestStatusTypeID AS request_status_type_id,
    RST.RequestStatusTypeName AS request_status_type_name,
    R.InitiatedOn AS date_initiated,
    ISNULL(R.SubmittedON,'') AS date_submitted,
    R.InitiatedBy AS initiated_by_id,
    IBY.UserName AS initiated_by_name,
    ISNULL(R.SubmittedBy,'') AS submitted_by_id,
    ISNULL(SBY.UserName,'') AS submitted_by_name,
    I.IsNewBusiness AS is_new_business,
    CASE WHEN A.AccountID IS NULL THEN 'New' ELSE 'Expanded' END AS business_type_name,
    ISNULL(G4.ElapsedTime, 0) AS days_in_queue,
    ISNULL(C1.NumApprovalsRequested, 0) AS approvals_requested,
    ISNULL(D1.NumApprovalsCompleted, 0) approvals_completed,
    ISNULL(F1.Approvals, '[]') AS approvals,
    ISNULL(G1.AssignedOn, '') AS date_submitted_credit_analyst,
    ISNULL(G2.AssignedOn, '') AS date_submitted_credit_manager,
    ISNULL(G3.AssignedOn, '') AS date_submitted_partner_carrier,
    RT.RequestTypeName AS request_type_name,
    CASE WHEN RSU.CurrentEditorID = @UserID THEN 1 ELSE 0 END AS is_current_editor,
    R.SpeedsheetName AS speedsheet_name,
    (select LanguageCode from Language where LanguageId = I.LanguageID) AS language_code
FROM dbo.Request R
INNER JOIN dbo.RequestStatus RSU ON R.RequestID = RSU.RequestID
INNER JOIN dbo.RequestStatusType RST ON RSU.RequestStatusTypeID = RST.RequestStatusTypeID
INNER JOIN dbo.RequestInformation I ON R.RequestInformationID = I.RequestInformationID
INNER JOIN dbo.Customer C ON I.CustomerID = C.CustomerID
INNER JOIN dbo.ServiceLevel SL ON C.ServiceLevelID = SL.ServiceLevelID
LEFT JOIN A1 ON R.RequestID = A1.RequestID
LEFT JOIN dbo.RequestType RT ON I.RequestTypeID = RT.RequestTypeID
LEFT JOIN dbo.Account A ON C.AccountID = A.AccountID
LEFT JOIN dbo.[User] UPA ON RSU.PricingAnalystID = UPA.UserID
LEFT JOIN dbo.[User] USR ON RSU.SalesRepresentativeID = USR.UserID
LEFT JOIN dbo.[User] CUE ON RSU.CurrentEditorID = CUE.UserID
LEFT JOIN dbo.[User] IBY ON R.InitiatedBy = IBY.UserID
LEFT JOIN dbo.[User] SBY ON R.SubmittedBy = SBY.UserID
LEFT JOIN C1 ON R.RequestID = C1.RequestID
LEFT JOIN D1 ON R.RequestID = D1.RequestID
LEFT JOIN F1 ON R.RequestID = F1.RequestID
LEFT JOIN G1 ON R.RequestID = G1.RequestID
LEFT JOIN G2 ON R.RequestID = G2.RequestID
LEFT JOIN G3 ON R.RequestID = G3.RequestID
LEFT JOIN G4 ON R.RequestID = G4.RequestID AND G4.UserID = @UserID
WHERE 1 = 1 {type_filter}
AND R.IsInactiveViewable = 1 AND (A1.RequestID IS NOT NULL OR @UserPersona IN ('Pricing Analyst', 'Pricing Manager'))
{{where_clauses}}
{{sort_clause}}
{{page_clause}}
{{closing_clause}}
"""