SELECT
(SELECT [text]
FROM sys.dm_exec_sql_text(sql_handle)
) AS SqlCommand,
spid AS [Process ID], status AS [Status],
hostname AS [Host Name], hostprocess AS [Host Process], SPACE(3) AS [Company],
0 AS [Task], SPACE(64) AS [Description],
loginame AS [User], open_tran AS [Open Trans], cmd AS [Command],
blocked AS [Blocked], CONVERT(VARCHAR(19), waittime) AS [Wait Time],
[Waiting] =
Case waittype
WHEN 0x0000 THEN SPACE(256)
Else waitresource
END, login_time AS [Login Time],
SPACE(64) AS [WTS Client], SPACE(12) AS [WTS ID],
program_name AS [Application]
FROM sys.sysprocesses WITH (NOLOCK)
WHERE
spid = ##