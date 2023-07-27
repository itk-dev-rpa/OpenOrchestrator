DELETE FROM Scheduled_Triggers
WHERE id = '{UUID}';

DELETE FROM Email_Triggers
WHERE id = '{UUID}';

DELETE FROM Single_Triggers
WHERE id = '{UUID}';