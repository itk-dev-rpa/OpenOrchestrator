SELECT log_time, log_level, process_name, log_message 
FROM Logs
WHERE '{FROM_DATE}' <= log_time and log_time <= '{TO_DATE}'
ORDER BY log_time DESC
OFFSET {OFFSET} ROWS
FETCH NEXT {FETCH} ROWS ONLY
