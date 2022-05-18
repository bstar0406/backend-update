SELECT login_name ,COUNT(session_id) AS session_count
FROM sys.dm_exec_sessions
GROUP BY login_name;