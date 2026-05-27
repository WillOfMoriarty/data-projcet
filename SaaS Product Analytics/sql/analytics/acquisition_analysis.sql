select
    u.traffic_source,
    count(distinct u.user_id) as total_users,
    count(distinct s.user_id) as paid_users,

    round(
        100.0 * count(distinct s.user_id)
        / count(distinct u.user_id),
        2
    ) as conversion_rate_pct

from user u

left join subscriptions s
    on u.user_id = s.user_id

group by u.traffic_source
order by conversion_rate_pct desc