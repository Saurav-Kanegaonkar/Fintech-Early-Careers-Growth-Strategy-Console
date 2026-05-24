# Data Sources

This folder contains deterministic synthetic data for a public fintech growth strategy portfolio artifact. It does not represent real company performance, real students, real campuses, real customers, partner records, credit outcomes, or private funnel analytics.

The structure is modeled on common growth workflows for a financial app serving students and newcomers:

- Campus and newcomer cohort sizing.
- Channel-level acquisition and activation funnels.
- No-SSN credit, checking, funding, and card activation onboarding steps.
- Referral, ambassador, webinar, creator, paid, and search-led education plays.
- Product, support, risk, compliance, RevOps, and data readiness blockers.

Generated files:

- `campus_cohorts.csv`: synthetic campus and newcomer segments with addressable-student estimates, product fit, trust gap, partner fit, and operating risk.
- `weekly_funnel_metrics.csv`: nine weeks of channel-level impressions, leads, applications, KYC steps, approvals, funding, card activation, spend, support tickets, and KYC rework.
- `growth_experiments.csv`: experiment backlog with hypothesis, incentive, expected activations, expected CAC, ICE-style scores, risk, decision, and owner.
- `product_readiness.csv`: onboarding, compliance, support, data, and RevOps blockers that must be cleared before scaling acquisition.
- `stakeholder_actions.csv`: sprint actions joining cohort focus, experiments, readiness work, owner, effort, dependency, and status.

The generator uses a fixed random seed so every run is reproducible.
