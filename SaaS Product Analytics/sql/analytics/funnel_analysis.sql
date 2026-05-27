with funnel as (
    select
        count(distinct case when event_name = 'landing_page_view' then user_id end) as landing_users,
        count(distinct case when event_name = 'signup_started' then user_id end) as signup_started_users,
        count(distinct case when event_name = 'signup_completed' then user_id end) as signup_completed_users,
        count(distinct case when event_name = 'workspace_created' then user_id end) as activated_users,
        count(distinct case when event_name = 'payment_completed' then user_id end) as paid_users

    from events
)

select
    landing_users,
    signup_started_users,
    signup_completed_users,
    activated_users,
    paid_users,

    round(100.0 * signup_started_users / landing_users, 2) as landing_to_signup_pct,
    round(100.0 * signup_completed_users / signup_started_users, 2) as signup_completion_pct,
    round(100.0 * activated_users / signup_completed_users, 2) as activation_pct,
    round(100.0 * paid_users / activated_users, 2) as paid_convertion_pct

from funnel;