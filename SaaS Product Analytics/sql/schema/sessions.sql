create table sessions(
    session_id int primary key,
    user_id int,
    session_start timestamp,
    session_end timestamp,
    session_duration_min int,
    user_type varchar(20)
);