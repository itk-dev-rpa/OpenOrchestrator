SELECT a.process_name, a.cron_expr, a.last_run, a.next_run, a.process_path, b.status_text, a.is_git_repo, a.blocking, a.id
FROM Scheduled_Triggers a JOIN Trigger_Status b
ON a.process_status = b.id