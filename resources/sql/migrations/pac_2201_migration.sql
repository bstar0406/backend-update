-- Migration Steps:

--+  Remove all constraints from SubServiceLevel
alter table SubServiceLevel
    drop constraint UQ__tmp_ms_x__4B65E9FF977AE58C
alter table SubServiceLevel
    drop constraint UQ__tmp_ms_x__1775F85B30F7C446

--+ !IMPORTANT
--+ !IMPORTANT
--+ !IMPORTANT Apply Django migrations before continuing

--+ Rename existing Service Levels:s
UPDATE ServiceLevel
SET ServiceLevelName  = CONCAT('(OLD)', ServiceLevelName),
    IsActive=0,
    IsInactiveViewable=0

--+  Rename  ServiceLevel records:
UPDATE ServiceLevel
SET ServiceLevelName  = 'Domestic LTL',
    IsActive=1,
    IsInactiveViewable=1
where ServiceLevelID = 84
UPDATE ServiceLevel
SET ServiceLevelName  = 'US LTL',
    IsActive=1,
    IsInactiveViewable=1
where ServiceLevelID = 88
UPDATE ServiceLevel
SET ServiceLevelName  = 'Residential',
    IsActive=1,
    IsInactiveViewable=1
where ServiceLevelID = 89
UPDATE ServiceLevel
SET ServiceLevelName  = 'TL',
    IsActive=1,
    IsInactiveViewable=1
where ServiceLevelID = 90

SET IDENTITY_INSERT ServiceLevel ON;
INSERT INTO ServiceLevel (IsActive, IsInactiveViewable, ServiceLevelID, ServiceLevelName, ServiceLevelCode, PricingType,
                          ServiceOfferingID)
VALUES (1, 1, 91, N'SCS', N'SO', N'Other', 1);
INSERT INTO ServiceLevel (IsActive, IsInactiveViewable, ServiceLevelID, ServiceLevelName, ServiceLevelCode, PricingType,
                          ServiceOfferingID)
VALUES (1, 1, 92, N'Flatbed', N'FB', N'Other', 1);
INSERT INTO ServiceLevel (IsActive, IsInactiveViewable, ServiceLevelID, ServiceLevelName, ServiceLevelCode, PricingType,
                          ServiceOfferingID)
VALUES (1, 1, 93, N'LTL Air', N'LA', N'DOMESTIC-LTL-SAMEDAY', 2);
SET IDENTITY_INSERT ServiceLevel OFF;

--+ Update SubServiceLevelName
UPDATE SubServiceLevel
SET SubServiceLevelName = 'General Road LTL',
    ServiceLevelID='84'
where SubServiceLevelID = 1
UPDATE SubServiceLevel
SET SubServiceLevelName = 'General Road TL',
    ServiceLevelID='90'
where SubServiceLevelID = 2
UPDATE SubServiceLevel
SET SubServiceLevelName = 'Intermodal LTL',
    ServiceLevelID='84'
where SubServiceLevelID = 3
UPDATE SubServiceLevel
SET SubServiceLevelName = 'Intermodal TL',
    ServiceLevelID='90'
where SubServiceLevelID = 4
UPDATE SubServiceLevel
SET SubServiceLevelName = 'US TL',
    ServiceLevelID='90'
where SubServiceLevelID = 5
UPDATE SubServiceLevel
SET SubServiceLevelName = 'Guaranteed Services LTL',
    ServiceLevelID='88'
where SubServiceLevelID = 6
UPDATE SubServiceLevel
SET SubServiceLevelName = 'Guaranteed Services TL',
    ServiceLevelID='90'
where SubServiceLevelID = 7
UPDATE SubServiceLevel
SET SubServiceLevelName = 'Expedited Road LTL',
    ServiceLevelID='84'
where SubServiceLevelID = 8
UPDATE SubServiceLevel
SET SubServiceLevelName = 'Expedited Road TL',
    ServiceLevelID='90'
where SubServiceLevelID = 9
UPDATE SubServiceLevel
SET SubServiceLevelName = 'SECOND DAY',
    ServiceLevelID='84'
where SubServiceLevelID = 10
UPDATE SubServiceLevel
SET SubServiceLevelName = 'US 2ND DAY',
    ServiceLevelID='84'
where SubServiceLevelID = 11
UPDATE SubServiceLevel
SET SubServiceLevelName = 'APPOINTMENT CHARGE',
    ServiceLevelID='84'
where SubServiceLevelID = 12
UPDATE SubServiceLevel
SET SubServiceLevelName = 'US NEXT PM',
    ServiceLevelID='84'
where SubServiceLevelID = 13
UPDATE SubServiceLevel
SET SubServiceLevelName = 'INTERNATIONAL AIR EXPORT',
    ServiceLevelID='93'
where SubServiceLevelID = 14
UPDATE SubServiceLevel
SET SubServiceLevelName = 'US GROUND',
    ServiceLevelID='84'
where SubServiceLevelID = 15
UPDATE SubServiceLevel
SET SubServiceLevelName = 'AFTER HOURS CHARGE',
    ServiceLevelID='84'
where SubServiceLevelID = 16
UPDATE SubServiceLevel
SET SubServiceLevelName = 'INTERNATIONAL IMPORT',
    ServiceLevelID='84'
where SubServiceLevelID = 17
UPDATE SubServiceLevel
SET SubServiceLevelName = 'US LETTER',
    ServiceLevelID='84'
where SubServiceLevelID = 18
UPDATE SubServiceLevel
SET SubServiceLevelName = 'Next Day AM (Before Noon)',
    ServiceLevelID='84'
where SubServiceLevelID = 19
UPDATE SubServiceLevel
SET SubServiceLevelName = 'US PACK',
    ServiceLevelID='84'
where SubServiceLevelID = 20
UPDATE SubServiceLevel
SET SubServiceLevelName = 'BANK RUN',
    ServiceLevelID='84'
where SubServiceLevelID = 21
UPDATE SubServiceLevel
SET SubServiceLevelName = 'Blanket Wrap',
    ServiceLevelID='84'
where SubServiceLevelID = 22
UPDATE SubServiceLevel
SET SubServiceLevelName = 'CROSS DOCKING HP',
    ServiceLevelID='84'
where SubServiceLevelID = 23
UPDATE SubServiceLevel
SET SubServiceLevelName = 'CONTRACT REVENUE',
    ServiceLevelID='84'
where SubServiceLevelID = 24
UPDATE SubServiceLevel
SET SubServiceLevelName = 'CHECK RETURN',
    ServiceLevelID='84'
where SubServiceLevelID = 25
UPDATE SubServiceLevel
SET SubServiceLevelName = '9:00 AM Guaranteed',
    ServiceLevelID='84'
where SubServiceLevelID = 26
UPDATE SubServiceLevel
SET SubServiceLevelName = 'DIRECT DRIVE',
    ServiceLevelID='84'
where SubServiceLevelID = 27
UPDATE SubServiceLevel
SET SubServiceLevelName = 'SPECIAL DELIVERY',
    ServiceLevelID='84'
where SubServiceLevelID = 28
UPDATE SubServiceLevel
SET SubServiceLevelName = 'Expedited Ground',
    ServiceLevelID='84'
where SubServiceLevelID = 29
UPDATE SubServiceLevel
SET SubServiceLevelName = 'EXTRA LABOUR CHARGE',
    ServiceLevelID='84'
where SubServiceLevelID = 30
UPDATE SubServiceLevel
SET SubServiceLevelName = 'Global Express',
    ServiceLevelID='84'
where SubServiceLevelID = 31
UPDATE SubServiceLevel
SET SubServiceLevelName = 'H1 - One Man Delivery - Bronze',
    ServiceLevelID='89'
where SubServiceLevelID = 32
UPDATE SubServiceLevel
SET SubServiceLevelName = 'H2 - One Man Delivery - Silver',
    ServiceLevelID='89'
where SubServiceLevelID = 33
UPDATE SubServiceLevel
SET SubServiceLevelName = 'H3 - One Man Delivery - Gold',
    ServiceLevelID='89'
where SubServiceLevelID = 34
UPDATE SubServiceLevel
SET SubServiceLevelName = 'H4 - Two Man Delivery - Bronze',
    ServiceLevelID='89'
where SubServiceLevelID = 35
UPDATE SubServiceLevel
SET SubServiceLevelName = 'H5 - Two Man Delivery - Silver',
    ServiceLevelID='89'
where SubServiceLevelID = 36
UPDATE SubServiceLevel
SET SubServiceLevelName = 'H6 - Two Man Delivery - Gold',
    ServiceLevelID='89'
where SubServiceLevelID = 37
UPDATE SubServiceLevel
SET SubServiceLevelName = 'H7 - One Man Delivery-Platinum',
    ServiceLevelID='89'
where SubServiceLevelID = 38
UPDATE SubServiceLevel
SET SubServiceLevelName = 'H8-Two Man Delivery - Platinum',
    ServiceLevelID='89'
where SubServiceLevelID = 39
UPDATE SubServiceLevel
SET SubServiceLevelName = 'HE - Home Electronics',
    ServiceLevelID='89'
where SubServiceLevelID = 40
UPDATE SubServiceLevel
SET SubServiceLevelName = 'Homeway',
    ServiceLevelID='89'
where SubServiceLevelID = 41
UPDATE SubServiceLevel
SET SubServiceLevelName = 'Intermodal LTL',
    ServiceLevelID='84'
where SubServiceLevelID = 42
UPDATE SubServiceLevel
SET SubServiceLevelName = 'INSTANTAIR',
    ServiceLevelID='93'
where SubServiceLevelID = 43
UPDATE SubServiceLevel
SET SubServiceLevelName = 'LTL Ground',
    ServiceLevelID='84'
where SubServiceLevelID = 44
UPDATE SubServiceLevel
SET SubServiceLevelName = 'LX',
    ServiceLevelID='84'
where SubServiceLevelID = 45
UPDATE SubServiceLevel
SET SubServiceLevelName = 'MISSED COD''S SETUP IN A/R',
    ServiceLevelID='84'
where SubServiceLevelID = 46
UPDATE SubServiceLevel
SET SubServiceLevelName = 'MESSSENGER SWO',
    ServiceLevelID='84'
where SubServiceLevelID = 47
UPDATE SubServiceLevel
SET SubServiceLevelName = 'MISC CHARGES',
    ServiceLevelID='84'
where SubServiceLevelID = 48
UPDATE SubServiceLevel
SET SubServiceLevelName = 'No Signature Required2',
    ServiceLevelID='84'
where SubServiceLevelID = 49
UPDATE SubServiceLevel
SET SubServiceLevelName = 'No Signature Required3',
    ServiceLevelID='84'
where SubServiceLevelID = 50
UPDATE SubServiceLevel
SET SubServiceLevelName = 'NO JOURNAL ENTRY NSF/WORKORDER',
    ServiceLevelID='84'
where SubServiceLevelID = 51
UPDATE SubServiceLevel
SET SubServiceLevelName = 'NON-REVENUE',
    ServiceLevelID='84'
where SubServiceLevelID = 52
UPDATE SubServiceLevel
SET SubServiceLevelName = 'No Signature Required',
    ServiceLevelID='84'
where SubServiceLevelID = 53
UPDATE SubServiceLevel
SET SubServiceLevelName = 'OCEAN EXPORT',
    ServiceLevelID='84'
where SubServiceLevelID = 54
UPDATE SubServiceLevel
SET SubServiceLevelName = 'OCEAN IMPORT',
    ServiceLevelID='84'
where SubServiceLevelID = 55
UPDATE SubServiceLevel
SET SubServiceLevelName = 'OVERTIME BILLING - HP',
    ServiceLevelID='84'
where SubServiceLevelID = 56
UPDATE SubServiceLevel
SET SubServiceLevelName = 'PM Service',
    ServiceLevelID='84'
where SubServiceLevelID = 57
UPDATE SubServiceLevel
SET SubServiceLevelName = 'PREPURCHASED - NATIONAL',
    ServiceLevelID='84'
where SubServiceLevelID = 58
UPDATE SubServiceLevel
SET SubServiceLevelName = 'PREPURCHASED -- REGIONAL',
    ServiceLevelID='84'
where SubServiceLevelID = 59
UPDATE SubServiceLevel
SET SubServiceLevelName = 'PREPURCHASED - UNITED STATES',
    ServiceLevelID='84'
where SubServiceLevelID = 60
UPDATE SubServiceLevel
SET SubServiceLevelName = 'REDELIVERY CHARGES',
    ServiceLevelID='84'
where SubServiceLevelID = 61
UPDATE SubServiceLevel
SET SubServiceLevelName = 'RENT OLD BUILDING',
    ServiceLevelID='84'
where SubServiceLevelID = 62
UPDATE SubServiceLevel
SET SubServiceLevelName = 'REGIONAL RATES (S.W.ONT)',
    ServiceLevelID='84'
where SubServiceLevelID = 63
UPDATE SubServiceLevel
SET SubServiceLevelName = 'SPECIAL AIR CONTAINERS',
    ServiceLevelID='93'
where SubServiceLevelID = 64
UPDATE SubServiceLevel
SET SubServiceLevelName = 'SATURDAY CHARGES',
    ServiceLevelID='84'
where SubServiceLevelID = 65
UPDATE SubServiceLevel
SET SubServiceLevelName = 'SAMEDAY DELIVERY (PU B4 3:00)',
    ServiceLevelID='84'
where SubServiceLevelID = 66
UPDATE SubServiceLevel
SET SubServiceLevelName = 'SERVICE INVENTORY - HP',
    ServiceLevelID='84'
where SubServiceLevelID = 67
UPDATE SubServiceLevel
SET SubServiceLevelName = 'METRO TORONTO',
    ServiceLevelID='84'
where SubServiceLevelID = 68
UPDATE SubServiceLevel
SET SubServiceLevelName = 'SPECIAL SERVICE (CUSTOMIZED)',
    ServiceLevelID='84'
where SubServiceLevelID = 69
UPDATE SubServiceLevel
SET SubServiceLevelName = 'STORAGE CHARGE',
    ServiceLevelID='84'
where SubServiceLevelID = 70
UPDATE SubServiceLevel
SET SubServiceLevelName = 'TRANSBORDER',
    ServiceLevelID='84'
where SubServiceLevelID = 71
UPDATE SubServiceLevel
SET SubServiceLevelName = 'TAIL GATE CHARGES',
    ServiceLevelID='84'
where SubServiceLevelID = 72
UPDATE SubServiceLevel
SET SubServiceLevelName = 'Urgent Letter',
    ServiceLevelID='84'
where SubServiceLevelID = 73
UPDATE SubServiceLevel
SET SubServiceLevelName = 'Urgent Pac',
    ServiceLevelID='84'
where SubServiceLevelID = 74
UPDATE SubServiceLevel
SET SubServiceLevelName = 'US Express',
    ServiceLevelID='84'
where SubServiceLevelID = 75
UPDATE SubServiceLevel
SET SubServiceLevelName = 'WAREHOUSE REVENUE',
    ServiceLevelID='84'
where SubServiceLevelID = 76
UPDATE SubServiceLevel
SET SubServiceLevelName = 'WAITING TIME EXTRA BILLING',
    ServiceLevelID='84'
where SubServiceLevelID = 77
UPDATE SubServiceLevel
SET SubServiceLevelName = 'TRANSBORDER ASSEMBLY SERVICE',
    ServiceLevelID='84'
where SubServiceLevelID = 78
UPDATE SubServiceLevel
SET SubServiceLevelName = 'TRANSBORDER CONSOLIDATION SRV',
    ServiceLevelID='84'
where SubServiceLevelID = 79
UPDATE SubServiceLevel
SET SubServiceLevelName = 'ECONOMY SERVICE TRANSBORDER',
    ServiceLevelID='84'
where SubServiceLevelID = 80
UPDATE SubServiceLevel
SET SubServiceLevelName = 'PRIME SERVICE TRANSBORDER',
    ServiceLevelID='84'
where SubServiceLevelID = 81
UPDATE SubServiceLevel
SET SubServiceLevelName = 'STANDARD SERVICE TRANSBORDER',
    ServiceLevelID='84'
where SubServiceLevelID = 82
UPDATE SubServiceLevel
SET SubServiceLevelName = 'TRANSBORDER TRUCKLOAD SERVICE',
    ServiceLevelID='84'
where SubServiceLevelID = 83
UPDATE SubServiceLevel
SET SubServiceLevelName = 'Test Child Service Level Domestic 1',
    ServiceLevelID='84'
where SubServiceLevelID = 86
UPDATE SubServiceLevel
SET SubServiceLevelName = 'Test Child Service Level Domestic 2',
    ServiceLevelID='84'
where SubServiceLevelID = 89
UPDATE SubServiceLevel
SET SubServiceLevelName = 'Test Child Service Level US 1',
    ServiceLevelID='88'
where SubServiceLevelID = 90
UPDATE SubServiceLevel
SET SubServiceLevelName = 'Test Child Service Level US 2',
    ServiceLevelID='88'
where SubServiceLevelID = 91
UPDATE SubServiceLevel
SET SubServiceLevelName = 'Test Child Service Level Sameday 1',
    ServiceLevelID='89'
where SubServiceLevelID = 92
UPDATE SubServiceLevel
SET SubServiceLevelName = 'Test Child Service Level Sameady 2',
    ServiceLevelID='89'
where SubServiceLevelID = 93
UPDATE SubServiceLevel
SET SubServiceLevelName = 'Test Child Service Level TL 1',
    ServiceLevelID='90'
where SubServiceLevelID = 94
UPDATE SubServiceLevel
SET SubServiceLevelName = 'Test Child Service Level TL 2',
    ServiceLevelID='90'
where SubServiceLevelID = 95


--+ Migrating Lane
--  Move ServiceLevelID to SubServiceLevelID:
UPDATE Lane
SET SubServiceLevelID = ServiceLevelID

--+  Make ServiceLevelID - nulluble
ALTER TABLE Lane
    ALTER COLUMN ServiceLevelID BIGINT NULL

--+  Update unique constraints for Lane table
-- possible change in the name UQ__Lane__511096C79C03E1DA, go to Lane and check for correct name
alter table Lane
    drop constraint UQ__Lane__511096C75CF45425
alter table Lane
    add unique (OriginTerminalID, DestinationTerminalID, SubServiceLevelID)
        with (fillfactor = 90)

--+  Set ServiceLevelID to null in Lane table
UPDATE Lane
SET ServiceLevelID =null

--+ Migrating BrokerContractCost
-- Move ServiceLevelID to SubServiceLevelID:

UPDATE BrokerContractCost
SET SubServiceLevelID = ServiceLevelID

--+ Update unique constraints for BrokerContractCost table
ALTER TABLE BrokerContractCost
    drop constraint UQ__BrokerCo__885DCB375E0DCC48

ALTER TABLE BrokerContractCost
    ADD UNIQUE (TerminalID, SubServiceLevelID)
        with (fillfactor = 90)

--+  Make ServiceLevelID - nulluble
ALTER TABLE BrokerContractCost
    ALTER COLUMN ServiceLevelID BIGINT NULL

--+  Set ServiceLevelID to null in BrokerContractCost table
UPDATE BrokerContractCost
SET ServiceLevelID =null

--+  Remove ServiceLevel FK from Lane table
alter table Lane
    drop constraint Lane_ServiceLevelID_FK

--+  Remove ServiceLevel FK from BrokerContractCost table
alter table BrokerContractCost
    drop constraint BrokerContractCost_ServiceLevelID_FK

--+ Detect all potential duplicates in Customer Table: (for double checking)
select AccountID, count(*) cnt
from Customer
group by AccountID
having count(1) > 1

--+ Set AccountID=null for all duplicated records

UPDATE c
SET c.AccountID=null
FROM Customer c
         INNER JOIN (select AccountID
                     from Customer
                     group by AccountID
                     HAVING count(1) > 1
                        and AccountID is not null) as s
                    ON s.AccountID = c.AccountID

--+ Move ServiceLevelID to SubServiceLevelID customet Table:

UPDATE c
SET c.ServiceLevelID=ssl.ServiceLevelID
FROM Customer c
         INNER JOIN
     SubServiceLevel ssl
     ON c.ServiceLevelID = ssl.SubServiceLevelID

-- Process LastAssignedUser
--+ Remove unique constraint
alter table LastAssignedUser
    drop constraint UQ__LastAssi__FE076743D7F52B8D

--+ make migration
UPDATE lau
SET lau.ServiceLevelID=ssl.ServiceLevelID
FROM LastAssignedUser lau
         INNER JOIN
     SubServiceLevel ssl
     ON lau.ServiceLevelID = ssl.SubServiceLevelID

--+ remove duplicates from LastAssignedUser
DELETE FROM LastAssignedUser where LastAssignedUser.LastAssignedUserID in(1,2,3,4,6,7,11,13,14,17)
--+ 22.4.
create unique index UQ__LastAssi__FE076743E07BE18D
    on LastAssignedUser (PersonaName, ServiceLevelID, IsActive)
    with (fillfactor = 90)


--+ Process UserServiceLevel
--+  Drop unique constraints
alter table UserServiceLevel drop constraint UQ__tmp_ms_x__F5A764D2A18D7E05

--+  update UserServiceLevel
UPDATE usl
SET usl.ServiceLevelID=ssl.ServiceLevelID
FROM UserServiceLevel usl
         INNER JOIN
     SubServiceLevel ssl
     ON usl.ServiceLevelID = ssl.SubServiceLevelID
--

--+  Remove record with isActive =0
DELETE
FROM UserServiceLevel
where IsActive = 0

--+  Remove duplicates
DELETE
FROM UserServiceLevel
WHERE UserServiceLevelID NOT IN
      (
          SELECT MAX(UserServiceLevelID) AS MaxUserServiceLevelID
          FROM UserServiceLevel
          GROUP BY UserID,
                   ServiceLevelID
      );


--+  add unique constraint

alter table UserServiceLevel
    add unique (UserID, ServiceLevelID)
        with (fillfactor = 90)

--+  update GriReview
UPDATE gr
SET gr.ServiceLevelID=ssl.ServiceLevelID
FROM GriReview gr
         INNER JOIN
     SubServiceLevel ssl
     ON gr.ServiceLevelID = ssl.SubServiceLevelID
--


--+  WeightBreakHeader
--+  drop unique constraint
alter table WeightBreakHeader
    drop constraint UQ__WeightBr__D7B03E5707B895FC

--+  migrate WeightBreakHeader ServiceLevel
UPDATE wbh
SET wbh.ServiceLevelID=ssl.ServiceLevelID
FROM WeightBreakHeader wbh
         INNER JOIN
     SubServiceLevel ssl
     ON wbh.ServiceLevelID = ssl.SubServiceLevelID

--+ rename WeightBreakHeaderName

update WeightBreakHeader
set WeightBreakHeaderName = Concat(WeightBreakHeaderName, '-', WeightBreakHeaderID)
where WeightBreakHeaderName like 'CCWT Weigh Break Header%'

--+ add constraint back

alter table WeightBreakHeader
    add unique (ServiceLevelID, WeightBreakHeaderName)


--+ ServiceLevel_History
--+ drop unique constraint
alter table ServiceLevel_History
    drop constraint UQ__tmp_ms_x__D36AB6AECE07C7EF
--+ drop unique index
drop index ServiceLevel_History_Unique on ServiceLevel_History


--+ update service level
UPDATE slh
SET slh.ServiceLevelID=ssl.ServiceLevelID
FROM ServiceLevel_History slh
         INNER JOIN
     SubServiceLevel ssl
     ON slh.ServiceLevelID = ssl.SubServiceLevelID

--+ update BrokerContractCost_History table
UPDATE bch
SET bch.ServiceLevelVersionID=ssh.ServiceLevelVersionID
FROM BrokerContractCost_History bch
         INNER JOIN
     SubServiceLevel_History ssh
     ON bch.ServiceLevelVersionID = ssh.ServiceLevelVersionID


--+ make duplicated records - not latest
update ServiceLevel_History
set VersionNum      = 2,
    IsLatestVersion = 0
where ServiceLevel_History.ServiceLevelVersionID not in (
    select a.min_service_ver_id
    from (
             select slh.ServiceLevelID, min(slh.ServiceLevelVersionID) as min_service_ver_id
             from dbo.ServiceLevel_History slh
             group by slh.ServiceLevelID) a)


--+ update BrokerContractCost_History
update BrokerContractCost_History
set SubServiceLevelVersionID = a.SubServiceLevelVersionID
from (
         select bcch.BrokerContractCostVersionID, sslh.SubServiceLevelVersionID
         from BrokerContractCost bcc
                  inner join BrokerContractCost_History bcch on bcc.BrokerContractCostID = bcch.BrokerContractCostID
                  inner join SubServiceLevel_History sslh
                             on bcc.SubServiceLevelID = sslh.SubServiceLevelID and sslh.IsLatestVersion = 1) a
where BrokerContractCost_History.BrokerContractCostVersionID = a.BrokerContractCostVersionID

--+
alter table BrokerContractCost_History
    alter column ServiceLevelVersionID bigint null
--+
update BrokerContractCost_History
set ServiceLevelVersionID = null
--+
alter table BrokerContractCost_History
    alter column ServiceLevelVersionID bigint


--+ update Customer_History
update Customer_History
set ServiceLevelVersionID = a.ServiceLevelVersionID
from (
         select ch.CustomerVersionID, slh.ServiceLevelVersionID
         from Customer c
                  inner join Customer_History ch on c.CustomerID = ch.CustomerID
                  inner join ServiceLevel_History slh
                             on c.ServiceLevelID = slh.ServiceLevelID and slh.IsLatestVersion = 1) a
where Customer_History.CustomerVersionID = a.CustomerVersionID


--+ update Lane_History
update Lane_History
set SubServiceLevelVersionID = a.SubServiceLevelVersionID
from (
         select lh.LaneVersionID, sslh.SubServiceLevelVersionID
         from lane l
                  inner join Lane_History lh on l.LaneID = lh.LaneID
                  inner join SubServiceLevel_History sslh
                             on l.SubServiceLevelID = sslh.SubServiceLevelID and sslh.IsLatestVersion = 1) a
where Lane_History.LaneVersionID = a.LaneVersionID

--+
alter table Lane_History
    alter column ServiceLevelVersionID bigint null
--+
update Lane_History
set ServiceLevelVersionID = null

--+
alter table Lane_History
    alter column ServiceLevelVersionID bigint

--+ update  UserServiceLevel_History
update UserServiceLevel_History
set ServiceLevelVersionID = a.ServiceLevelVersionID
from (
         select ch.UserServiceLevelVersionID, slh.ServiceLevelVersionID
         from UserServiceLevel c
                  inner join UserServiceLevel_History ch on c.UserServiceLevelID = ch.UserServiceLevelID
                  inner join ServiceLevel_History slh
                             on c.ServiceLevelID = slh.ServiceLevelID and slh.IsLatestVersion = 1) a
where UserServiceLevel_History.UserServiceLevelVersionID = a.UserServiceLevelVersionID


--+ update WeightBreakHeader_History
update WeightBreakHeader_History
set ServiceLevelVersionID = a.ServiceLevelVersionID
from (
         select ch.WeightBreakHeaderVersionID, slh.ServiceLevelVersionID
         from WeightBreakHeader c
                  inner join WeightBreakHeader_History ch on c.WeightBreakHeaderID = ch.WeightBreakHeaderID
                  inner join ServiceLevel_History slh
                             on c.ServiceLevelID = slh.ServiceLevelID and slh.IsLatestVersion = 1) a
where WeightBreakHeader_History.WeightBreakHeaderVersionID = a.WeightBreakHeaderVersionID


--+ update SubServiceLevel_History
update SubServiceLevel_History
set ServiceLevelVersionID = a.ServiceLevelVersionID
from (
         select ch.SubServiceLevelVersionID, slh.ServiceLevelVersionID
         from SubServiceLevel c
                  inner join SubServiceLevel_History ch on c.SubServiceLevelID = ch.SubServiceLevelID
                  inner join ServiceLevel_History slh
                             on c.ServiceLevelID = slh.ServiceLevelID and slh.IsLatestVersion = 1) a
where SubServiceLevel_History.SubServiceLevelVersionID = a.SubServiceLevelVersionID

--+ delete outdated records from ServiceLevel_History
delete
from ServiceLevel_History
where ServiceLevel_History.VersionNum = 2
  and ServiceLevel_History.IsLatestVersion = 0


--+ add unique constraint back
alter table ServiceLevel_History
    add unique (ServiceLevelID, VersionNum)
        with (fillfactor = 90)

-- 25.14.
create unique index ServiceLevel_History_Unique
    on ServiceLevel_History (ServiceLevelID, IsLatestVersion)
    where [IsLatestVersion] = 1
    with (fillfactor = 90)

--+ 26. delete old records from ServiceLevel
delete
from ServiceLevel
where ServiceLevel.IsActive = 0
  and ServiceLevel.IsInactiveViewable = 0
  and ServiceLevel.ServiceLevelName like '(OLD)%'

-- SET IDENTITY_INSERT SubServiceLevel_History OFF;
INSERT INTO SubServiceLevel_History (VersionNum, IsLatestVersion, UpdatedOn, UpdatedBy, BaseVersion, Comments, IsActive, IsInactiveViewable, SubServiceLevelName, SubServiceLevelCode, SubServiceLevelID, ServiceLevelVersionID) VALUES (1, 1, N'2021-06-04 06:05:13.6700000', N'P&C System', null, N'Created first version.', 1, 1, N'Test Child Service Level US 1', N'U1', 90, 6);
INSERT INTO SubServiceLevel_History (VersionNum, IsLatestVersion, UpdatedOn, UpdatedBy, BaseVersion, Comments, IsActive, IsInactiveViewable, SubServiceLevelName, SubServiceLevelCode, SubServiceLevelID, ServiceLevelVersionID) VALUES (1, 1, N'2020-06-04 06:05:13.6700000', N'P&C Syste``````m', null, N'Created first version.', 1, 1, N'Test Child Service Level US 2', N'U2', 91, 6);
INSERT INTO SubServiceLevel_History (VersionNum, IsLatestVersion, UpdatedOn, UpdatedBy, BaseVersion, Comments, IsActive, IsInactiveViewable, SubServiceLevelName, SubServiceLevelCode, SubServiceLevelID, ServiceLevelVersionID) VALUES (1, 1, N'2020-06-04 06:05:13.6700000', N'P&C System', null, N'Created first version.', 1, 1, N'Test Child Service Level Domestic 1', N'D1', 86, 1);
INSERT INTO SubServiceLevel_History (VersionNum, IsLatestVersion, UpdatedOn, UpdatedBy, BaseVersion, Comments, IsActive, IsInactiveViewable, SubServiceLevelName, SubServiceLevelCode, SubServiceLevelID, ServiceLevelVersionID) VALUES (1, 1, N'2020-06-04 06:05:13.6700000', N'P&C System', null, N'Created first version.', 1, 1, N'Test Child Service Level Domestic 2', N'D2', 89, 1);
INSERT INTO SubServiceLevel_History (VersionNum, IsLatestVersion, UpdatedOn, UpdatedBy, BaseVersion, Comments, IsActive, IsInactiveViewable, SubServiceLevelName, SubServiceLevelCode, SubServiceLevelID, ServiceLevelVersionID) VALUES (1, 1, N'2020-06-04 06:05:13.6700000', N'P&C System', null, N'Created first version.', 1, 1, N'Test Child Service Level Sameday 1', N'C1', 92, 32);
INSERT INTO SubServiceLevel_History (VersionNum, IsLatestVersion, UpdatedOn, UpdatedBy, BaseVersion, Comments, IsActive, IsInactiveViewable, SubServiceLevelName, SubServiceLevelCode, SubServiceLevelID, ServiceLevelVersionID) VALUES (1, 1, N'2020-06-04 06:05:13.6700000', N'P&C System', null, N'Created first version.', 1, 1, N'Test Child Service Level Sameady 2', N'C2', 93, 32);
INSERT INTO SubServiceLevel_History (VersionNum, IsLatestVersion, UpdatedOn, UpdatedBy, BaseVersion, Comments, IsActive, IsInactiveViewable, SubServiceLevelName, SubServiceLevelCode, SubServiceLevelID, ServiceLevelVersionID) VALUES (1, 1, N'2020-06-04 06:05:13.6700000', N'P&C System', null, N'Created first version.', 1, 1, N'Test Child Service Level TL 1', N'T1', 94, 2);
INSERT INTO SubServiceLevel_History (VersionNum, IsLatestVersion, UpdatedOn, UpdatedBy, BaseVersion, Comments, IsActive, IsInactiveViewable, SubServiceLevelName, SubServiceLevelCode, SubServiceLevelID, ServiceLevelVersionID) VALUES (1, 1, N'2020-06-04 06:05:13.6700000', N'P&C System', null, N'Created first version.', 1, 1, N'Test Child Service Level TL 2', N'T2', 95, 2);

INSERT INTO SubServiceLevel_History (VersionNum, IsLatestVersion, UpdatedOn, UpdatedBy, BaseVersion, Comments, IsActive, IsInactiveViewable, SubServiceLevelName, SubServiceLevelCode, SubServiceLevelID, ServiceLevelVersionID) VALUES (1, 1, N'2021-06-04 06:05:13.6700000', N'P&C System', null, N'Created first version.', 1, 1, N'Test Child Service Level US 1', N'U1', 90, 6);

-- SET IDENTITY_INSERT SubServiceLevel_History ON;


select SubServiceLevel.SubServiceLevelCode, SubServiceLevel.SubServiceLevelID, SubServiceLevel.ServiceLevelID, SSLH.SubServiceLevelID  from SubServiceLevel left join SubServiceLevel_History SSLH on SubServiceLevel.SubServiceLevelID = SSLH.SubServiceLevelID