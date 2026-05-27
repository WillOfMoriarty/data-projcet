with first_activity as (
    select
        user_id,
        min(date(event_timestamp)) as first_date
    from events
    group by user_id
)

return_activity as (
    SELECT
        e.user_id,
        DATE(e.event_timestamp) AS activity_date,
        f.first_date,

        DATE(e.event_timestamp) - f.first_date AS days_since_signup

    FROM events e

    JOIN first_activity f
        ON e.user_id = f.user_id

)

SELECT

    days_since_signup,

    COUNT(DISTINCT user_id) AS retained_users

FROM return_activity

GROUP BY days_since_signup

ORDER BY days_since_signup;