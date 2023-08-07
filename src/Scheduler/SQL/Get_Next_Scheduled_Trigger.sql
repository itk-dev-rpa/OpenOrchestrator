SELECT TOP(1) process_name, next_run, id
FROM Scheduled_Triggers
WHERE process_status = 0
ORDER BY next_run