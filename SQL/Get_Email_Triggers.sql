SELECT a.process_name, a.email_folder, a.last_run, a.process_path, b.status_text, a.is_git_repo, a.force_update, a.blocking, a.id
FROM Email_Triggers a JOIN Trigger_Status b
ON a.process_status = b.id