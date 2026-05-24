-- Example SQL checks for a fintech growth strategy workbench.

-- 1. Funnel rows should never have a later-stage count above the previous stage.
select *
from weekly_funnel_metrics
where applications > leads
   or kyc_started > applications
   or approved_accounts > kyc_started
   or funded_accounts > approved_accounts
   or activated_users > funded_accounts;

-- 2. Experiment backlog should keep launch candidates above the priority threshold.
select experiment_id, campus_name, channel_name, priority_score, decision
from experiment_backlog
where decision = 'Launch in week 1'
  and priority_score < 76;

-- 3. Readiness issues with high user impact need an owner and current status.
select issue_id, campus_name, issue, owner, status, estimated_impacted_users
from readiness_queue
where estimated_impacted_users >= 300
  and (owner is null or status is null);
