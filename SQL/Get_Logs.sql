SELECT log_time, log_level, process_name, log_message 
FROM Logs
{filter}
ORDER BY log_time DESC
OFFSET {offset} ROWS
FETCH NEXT {fetch} ROWS ONLY
