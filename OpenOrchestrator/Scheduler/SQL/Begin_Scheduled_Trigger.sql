UPDATE Scheduled_Triggers
SET
    process_status = 1,
    last_run = CURRENT_TIMESTAMP,
    next_run = '{NEXT_RUN}'

WHERE id = '{UUID}'