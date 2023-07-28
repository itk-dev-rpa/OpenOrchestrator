CREATE TABLE Log_Level (
    id          TINYINT         NOT NULL    PRIMARY KEY,
    level_text  VARCHAR(10)     NOT NULL
);

INSERT INTO Log_Level
VALUES 
    (0, 'Trace'),
    (1, 'Info'),
    (2, 'Error');

CREATE TABLE Logs (
    id              UNIQUEIDENTIFIER    NOT NULL    PRIMARY KEY,
    log_time        DATETIME            NOT NULL,
    log_level       TINYINT             NOT NULL    FOREIGN KEY REFERENCES Log_Level(id),
    process_name    VARCHAR(100)        NOT NULL,
    log_message     VARCHAR(8000)
);

CREATE TABLE Trigger_Status (
    id              TINYINT         NOT NULL    PRIMARY KEY,
    status_text     VARCHAR(10)     NOT NULL
);

INSERT INTO Trigger_Status
VALUES
    (0, 'Idle'),
    (1, 'Running'),
    (2, 'Failed'),
    (3, 'Done');

CREATE TABLE Scheduled_Triggers (
    id              UNIQUEIDENTIFIER     NOT NULL    PRIMARY KEY,
    process_name    VARCHAR(100)         NOT NULL,
    cron_expr       VARCHAR(200)         NOT NULL,
    last_run        DATETIME,
    next_run        DATETIME             NOT NULL,
    process_path    VARCHAR(250)         NOT NULL,
    process_status  TINYINT              NOT NULL    FOREIGN KEY REFERENCES Trigger_Status(id),
    is_git_repo     BIT                  NOT NULL,
    blocking        BIT                  NOT NULL
);

CREATE TABLE Single_Triggers (
    id              UNIQUEIDENTIFIER     NOT NULL    PRIMARY KEY,
    process_name    VARCHAR(100)         NOT NULL,
    last_run        DATETIME,
    next_run        DATETIME             NOT NULL,
    process_path    VARCHAR(250)         NOT NULL,
    process_status  TINYINT              NOT NULL    FOREIGN KEY REFERENCES Trigger_Status(id),
    is_git_repo     BIT                  NOT NULL,
    blocking        BIT                  NOT NULL
);

CREATE TABLE Email_Triggers (
    id              UNIQUEIDENTIFIER     NOT NULL    PRIMARY KEY,
    process_name    VARCHAR(100)         NOT NULL,
    email_folder    VARCHAR(250)         NOT NULL,
    last_run        DATETIME,
    process_path    VARCHAR(250)         NOT NULL,
    process_status  TINYINT              NOT NULL    FOREIGN KEY REFERENCES Trigger_Status(id),
    is_git_repo     BIT                  NOT NULL,
    blocking        BIT                  NOT NULL
);

CREATE TABLE Credentials (
    cred_name        VARCHAR(255)     NOT NULL    PRIMARY KEY,
    cred_username    VARCHAR(255)     NOT NULL,
    cred_password    VARCHAR(255)     NOT NULL,    
);

CREATE TABLE Constants (
    constant_name   VARCHAR(255)     NOT NULL    PRIMARY KEY,
    constant_value  VARCHAR(1000)    NOT NULL
);