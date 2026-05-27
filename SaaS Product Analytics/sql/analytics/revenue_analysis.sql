select
    count(DISTINCT user_id) as paid_users,
    sum(monthly_revenue) as total_mrr,
    avg(monthly_revenue) as arpu,

    count(
        case when status = 'canceled' then 1 end
    ) as churned_users

from subscriptions