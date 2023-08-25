SELECT TOP(1) process_name, next_run, id, process_path, is_git_repo, blocking
FROM Single_Triggers
WHERE process_status = 0
ORDER BY next_run