UPDATE Single_Triggers
SET
    process_status = 1,
    last_run = CURRENT_TIMESTAMP

WHERE id = '{UUID}'