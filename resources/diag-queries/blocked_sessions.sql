select cmd,* from sys.sysprocesses
where sysprocesses.cmd like 'AWAITING COMMAND%'
--       blocked > 0