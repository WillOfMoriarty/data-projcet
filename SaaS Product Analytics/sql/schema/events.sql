create table events (
    event_id int primary key,
    user_id int,
    session_id int,
    event_timestamp timestamp,
    event_name varchar(50),
    feature_name varchar(50),

    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);
