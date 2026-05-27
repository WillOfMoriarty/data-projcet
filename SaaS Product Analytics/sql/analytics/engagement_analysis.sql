with feature_users as (
    select distinct user_id
    from events

    where event_name = 'feature_used'
),

paid_users as (
    select distinct user_id
    from subscriptions
)

select 
    case
        when fu.user_id is not null then 'Used Feature'
        else 'Did Not Use Feature'
    end as feature_segment,

    count(distinct e.user_id) as users,
    count(distinct pu.user_id) as paid_users,
    round(
        100.0 * count(distinct pu.user_id)
        / count(distinct e.user_id), 2
    ) as conversion_rate_pct

from events e

left join feature_users fu
    on e.user_id = fu.user_id

left join paid_users pu
    on e.user_id = pu.user_id

group by feature_segment