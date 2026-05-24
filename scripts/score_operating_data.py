import csv
import json
import math
import random
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "analysis" / "outputs"
ANALYSIS_DIR = ROOT / "analysis"
SEED = 20260615

random.seed(SEED)


def clamp(value, low, high):
    return max(low, min(high, value))


def pct(numerator, denominator):
    if denominator == 0:
        return 0
    return numerator / denominator * 100


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def money(value):
    return f"${value:,.0f}"


def number(value):
    return f"{value:,.0f}"


regions = [
    ("Northeast", 1.08, 1.12),
    ("Mid-Atlantic", 1.02, 1.06),
    ("Southeast", 0.95, 0.98),
    ("Midwest", 0.92, 0.93),
    ("Texas Corridor", 1.05, 1.04),
    ("West Coast", 1.18, 1.15),
    ("Mountain West", 0.88, 0.90),
    ("Canada Bridge", 0.98, 1.02),
]

segments = [
    ("Incoming graduate students", 1.20, 1.10, 0.88),
    ("Incoming undergraduate students", 1.00, 0.98, 0.82),
    ("STEM masters cohorts", 1.26, 1.16, 0.91),
    ("MBA and professional programs", 1.14, 1.18, 0.86),
    ("Early career visa holders", 0.86, 1.05, 0.80),
    ("Family and partner movers", 0.72, 0.92, 0.74),
]

channels = [
    ("campus_ambassador", "Campus ambassadors", 0.075, 0.61, 22, 0.91),
    ("partner_webinar", "Partner webinars", 0.108, 0.67, 34, 0.87),
    ("referral", "Student referral loops", 0.086, 0.70, 18, 0.96),
    ("creator_content", "Creator content", 0.052, 0.52, 30, 0.78),
    ("paid_social", "Paid social", 0.044, 0.48, 46, 0.71),
    ("search_content", "Search and explainer content", 0.068, 0.58, 26, 0.83),
]

campus_names = [
    "Atlantic Gateway University",
    "Metro Tech Institute",
    "Lakeview State",
    "Pacific Design College",
    "Northern Engineering School",
    "Capital City University",
    "Great Plains Tech",
    "Summit Business School",
    "Bay Area Graduate Institute",
    "Central Research University",
    "South Coast University",
    "Pioneer STEM College",
    "Great Lakes Business Institute",
    "Canyon State University",
    "Hudson Applied Sciences",
    "Lone Star Polytechnic",
    "Riverbend University",
    "Northwest Innovation School",
    "Queen City College",
    "Desert Valley University",
    "Union Graduate School",
    "Harbor Analytics Institute",
    "Keystone International College",
    "Prairie Data University",
    "Redwood Professional School",
    "Magnolia Technical University",
    "Front Range Institute",
    "Gulf Coast Business School",
    "Maple Bridge University",
    "Liberty Urban University",
    "Twin Cities Applied College",
    "Sunrise Engineering University",
]

hypotheses = {
    "campus_ambassador": "Student ambassador office hours will lift trust before arrival.",
    "partner_webinar": "Visa and housing partner webinars will convert high-intent applicants.",
    "referral": "Peer referral credits will shorten the path from application to activation.",
    "creator_content": "Creator explainers will reduce confusion around no-SSN credit access.",
    "paid_social": "Paid social retargeting will recover students who dropped before KYC.",
    "search_content": "Search-led guides will capture users comparing banking options.",
}

owners = ["Growth", "Community", "Product", "RevOps", "Data", "Operations", "Compliance"]


def build_campuses():
    campuses = []
    for index, campus_name in enumerate(campus_names, 1):
        region_name, region_scale, cost_scale = regions[(index - 1) % len(regions)]
        segment_name, demand_scale, activation_scale, trust_scale = segments[(index + 1) % len(segments)]
        addressable = int(random.triangular(850, 8500, 3100) * region_scale * demand_scale)
        community_density = round(clamp(random.gauss(72, 12) * demand_scale, 35, 96), 1)
        partner_fit = round(clamp(random.gauss(68, 14) * region_scale, 28, 98), 1)
        trust_gap = round(clamp(random.gauss(38, 14) / trust_scale, 12, 82), 1)
        compliance_complexity = round(clamp(random.gauss(44, 12) / activation_scale, 18, 78), 1)
        product_fit = round(clamp(random.gauss(74, 10) * activation_scale, 45, 96), 1)
        cost_index = round(clamp(random.gauss(100, 16) * cost_scale, 62, 150), 1)
        focus = random.choice(["pre-arrival", "orientation", "first 30 days", "credit building"])
        campuses.append({
            "campus_id": f"CMP{index:03d}",
            "campus_name": campus_name,
            "region": region_name,
            "student_segment": segment_name,
            "primary_start_window": focus,
            "estimated_addressable_students": addressable,
            "community_density_score": community_density,
            "partner_fit_score": partner_fit,
            "trust_gap_score": trust_gap,
            "compliance_complexity_score": compliance_complexity,
            "product_fit_score": product_fit,
            "cost_index": cost_index,
            "owner": owners[index % len(owners)],
        })
    return campuses


def build_weekly_metrics(campuses):
    rows = []
    start = date(2026, 6, 15)
    for week_index in range(9):
        week_start = start + timedelta(days=week_index * 7)
        seasonality = 0.82 + week_index * 0.045 + math.sin(week_index / 2) * 0.08
        for campus in campuses:
            for channel_id, channel_name, lead_rate, activation_rate, base_cac, trust_factor in channels:
                addressable = campus["estimated_addressable_students"]
                density = campus["community_density_score"] / 100
                partner_fit = campus["partner_fit_score"] / 100
                product_fit = campus["product_fit_score"] / 100
                trust_penalty = campus["trust_gap_score"] / 130
                complexity_penalty = campus["compliance_complexity_score"] / 160
                channel_multiplier = random.uniform(0.78, 1.25)
                impressions = int(addressable * random.uniform(0.10, 0.28) * seasonality * channel_multiplier)
                leads = int(impressions * lead_rate * (0.72 + density * 0.46 + partner_fit * 0.18))
                applications = int(leads * random.uniform(0.24, 0.42) * (1.08 - trust_penalty))
                kyc_started = int(applications * random.uniform(0.72, 0.88))
                approved = int(kyc_started * random.uniform(0.58, 0.77) * (1.04 - complexity_penalty))
                funded = int(approved * random.uniform(0.50, 0.71) * product_fit)
                activated = int(funded * activation_rate * random.uniform(0.86, 1.12))
                spend = round((leads * base_cac * campus["cost_index"] / 100) * random.uniform(0.72, 1.18), 2)
                rows.append({
                    "week_start": week_start.isoformat(),
                    "campus_id": campus["campus_id"],
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "impressions": impressions,
                    "leads": leads,
                    "applications": applications,
                    "kyc_started": kyc_started,
                    "approved_accounts": approved,
                    "funded_accounts": funded,
                    "activated_users": activated,
                    "spend": spend,
                    "support_tickets": int(max(0, random.gauss(approved * 0.08, 4))),
                    "kyc_rework_cases": int(max(0, random.gauss(kyc_started * campus["compliance_complexity_score"] / 900, 3))),
                })
    return rows


def aggregate_by_campus(campuses, weekly_rows):
    campus_lookup = {row["campus_id"]: row for row in campuses}
    buckets = defaultdict(lambda: defaultdict(float))
    for row in weekly_rows:
        bucket = buckets[row["campus_id"]]
        for key in [
            "impressions",
            "leads",
            "applications",
            "kyc_started",
            "approved_accounts",
            "funded_accounts",
            "activated_users",
            "spend",
            "support_tickets",
            "kyc_rework_cases",
        ]:
            bucket[key] += float(row[key])

    queue = []
    for campus_id, metrics in buckets.items():
        campus = campus_lookup[campus_id]
        cac = metrics["spend"] / max(1, metrics["activated_users"])
        activation_rate = pct(metrics["activated_users"], metrics["applications"])
        approval_rate = pct(metrics["approved_accounts"], metrics["kyc_started"])
        lead_to_apply = pct(metrics["applications"], metrics["leads"])
        readiness = (
            campus["product_fit_score"] * 0.36
            + campus["partner_fit_score"] * 0.24
            + campus["community_density_score"] * 0.18
            + (100 - campus["compliance_complexity_score"]) * 0.14
            + (100 - campus["trust_gap_score"]) * 0.08
        )
        opportunity = math.sqrt(campus["estimated_addressable_students"]) * activation_rate * 0.82
        efficiency = clamp(100 - cac * 1.3, 0, 100)
        risk_penalty = campus["compliance_complexity_score"] * 0.18 + campus["trust_gap_score"] * 0.16
        priority = clamp(opportunity * 0.44 + readiness * 0.30 + efficiency * 0.26 - risk_penalty, 0, 100)
        if priority >= 78:
            decision = "Sprint focus"
        elif priority >= 67:
            decision = "Test next"
        elif priority >= 56:
            decision = "Nurture"
        else:
            decision = "Hold"
        queue.append({
            "campus_id": campus_id,
            "campus_name": campus["campus_name"],
            "region": campus["region"],
            "student_segment": campus["student_segment"],
            "primary_start_window": campus["primary_start_window"],
            "addressable_students": campus["estimated_addressable_students"],
            "leads": int(metrics["leads"]),
            "applications": int(metrics["applications"]),
            "approved_accounts": int(metrics["approved_accounts"]),
            "activated_users": int(metrics["activated_users"]),
            "spend": round(metrics["spend"], 2),
            "cac": round(cac, 2),
            "lead_to_apply_pct": round(lead_to_apply, 1),
            "approval_rate_pct": round(approval_rate, 1),
            "activation_rate_pct": round(activation_rate, 1),
            "readiness_score": round(readiness, 1),
            "priority_score": round(priority, 1),
            "decision": decision,
            "recommended_focus": focus_for(campus),
            "owner": campus["owner"],
        })
    return sorted(queue, key=lambda row: row["priority_score"], reverse=True)


def focus_for(campus):
    if campus["trust_gap_score"] > 56:
        return "trust proof and peer stories"
    if campus["compliance_complexity_score"] > 58:
        return "KYC pre-check and document guidance"
    if campus["partner_fit_score"] > 78:
        return "partner webinar and campus ops"
    if campus["community_density_score"] > 80:
        return "ambassador and referral loop"
    return "orientation activation bundle"


def build_experiments(campuses, campus_queue):
    queue_lookup = {row["campus_id"]: row for row in campus_queue}
    experiments = []
    experiment_id = 1
    top_campuses = sorted(campuses, key=lambda row: queue_lookup[row["campus_id"]]["priority_score"], reverse=True)[:18]
    incentives = ["fee waiver", "cashback boost", "peer challenge", "office hours", "arrival checklist", "credit education"]
    for campus in top_campuses:
        base = queue_lookup[campus["campus_id"]]
        for channel_id, channel_name, lead_rate, activation_rate, base_cac, trust_factor in random.sample(channels, 4):
            impact = clamp(base["priority_score"] + random.gauss(0, 8), 35, 98)
            confidence = clamp(58 + campus["partner_fit_score"] * 0.22 + campus["community_density_score"] * 0.18 + random.gauss(0, 8), 32, 94)
            ease = clamp(86 - base_cac * 0.72 - campus["compliance_complexity_score"] * 0.18 + random.gauss(0, 7), 24, 94)
            risk = clamp(campus["trust_gap_score"] * 0.44 + campus["compliance_complexity_score"] * 0.36 + random.gauss(0, 6), 12, 82)
            expected_activations = int(max(18, base["activated_users"] * random.uniform(0.035, 0.11) * trust_factor))
            expected_spend = expected_activations * base_cac * campus["cost_index"] / 100 * random.uniform(0.82, 1.18)
            rice = (expected_activations * impact / 100 * confidence / 100 * ease / 100) / max(1, risk / 45)
            priority = clamp(rice * 2.2, 0, 100)
            if priority >= 76:
                decision = "Launch in week 1"
            elif priority >= 62:
                decision = "Design test"
            elif priority >= 48:
                decision = "Backlog"
            else:
                decision = "Do not pursue"
            experiments.append({
                "experiment_id": f"EXP{experiment_id:03d}",
                "campus_id": campus["campus_id"],
                "campus_name": campus["campus_name"],
                "channel_id": channel_id,
                "channel_name": channel_name,
                "hypothesis": hypotheses[channel_id],
                "incentive": random.choice(incentives),
                "expected_activations": expected_activations,
                "expected_spend": round(expected_spend, 2),
                "expected_cac": round(expected_spend / expected_activations, 2),
                "impact_score": round(impact, 1),
                "confidence_score": round(confidence, 1),
                "ease_score": round(ease, 1),
                "risk_score": round(risk, 1),
                "priority_score": round(priority, 1),
                "decision": decision,
                "owner": random.choice(["Growth", "Community", "RevOps", "Product"]),
            })
            experiment_id += 1
    return sorted(experiments, key=lambda row: row["priority_score"], reverse=True)


def build_readiness(campuses):
    issue_templates = [
        ("KYC", "Passport image rework", "application to KYC", "Operations"),
        ("KYC", "Address proof mismatch", "KYC to approval", "Compliance"),
        ("Product", "First deposit setup confusion", "approval to funding", "Product"),
        ("Product", "Virtual card education gap", "funding to card activation", "Product"),
        ("Support", "Arrival week support spike", "application to activation", "Operations"),
        ("RevOps", "Campus partner attribution gap", "lead to application", "RevOps"),
        ("Data", "Referral source missing", "lead to application", "Data"),
        ("Risk", "Thin-file review queue", "KYC to approval", "Risk"),
    ]
    rows = []
    for index, campus in enumerate(random.sample(campuses, 28), 1):
        source_domain, issue, stage, owner = random.choice(issue_templates)
        impact_users = int(random.triangular(45, 820, 180) * campus["estimated_addressable_students"] / 3500)
        fix_hours = int(random.triangular(8, 92, 28))
        severity_score = clamp(
            campus["compliance_complexity_score"] * 0.42
            + campus["trust_gap_score"] * 0.32
            + impact_users / 18
            + random.gauss(0, 7),
            15,
            98,
        )
        readiness_score = clamp(100 - severity_score * 0.52 - fix_hours * 0.18 + random.gauss(0, 4), 18, 96)
        if severity_score >= 74:
            severity = "High"
        elif severity_score >= 55:
            severity = "Medium"
        else:
            severity = "Watch"
        rows.append({
            "issue_id": f"RDY{index:03d}",
            "campus_id": campus["campus_id"],
            "campus_name": campus["campus_name"],
            "source_domain": source_domain,
            "issue": issue,
            "affected_stage": stage,
            "severity": severity,
            "estimated_impacted_users": impact_users,
            "fix_hours": fix_hours,
            "readiness_score": round(readiness_score, 1),
            "status": random.choice(["Open", "In review", "Ready to fix", "Blocked"]),
            "owner": owner,
            "recommendation": readiness_recommendation(source_domain, stage),
        })
    return sorted(rows, key=lambda row: (row["severity"] == "High", row["estimated_impacted_users"]), reverse=True)


def readiness_recommendation(source_domain, stage):
    recommendations = {
        "KYC": "Publish document examples before application handoff.",
        "Product": "Add onboarding copy and checklist to the activation step.",
        "Support": "Pre-staff arrival week macro coverage and escalation paths.",
        "RevOps": "Standardize partner and campaign source fields.",
        "Data": "Add required referral source validation before weekly readout.",
        "Risk": "Route thin-file reviews into a named operating queue.",
    }
    return recommendations[source_domain]


def build_actions(campus_queue, experiments, readiness):
    top_campuses = campus_queue[:8]
    top_experiments = experiments[:8]
    readiness_hot = readiness[:8]
    rows = []
    action_id = 1
    for campus in top_campuses:
        rows.append({
            "action_id": f"ACT{action_id:03d}",
            "workstream": "Cohort focus",
            "owner": campus["owner"],
            "sprint_week": f"Week {min(9, max(1, action_id))}",
            "action": f"Build {campus['recommended_focus']} for {campus['student_segment']}.",
            "expected_lift": round(campus["activated_users"] * 0.09, 1),
            "effort_hours": random.randint(14, 42),
            "dependency": "weekly campus funnel readout",
            "status": "Planned" if action_id <= 4 else "Backlog",
        })
        action_id += 1
    for experiment in top_experiments:
        rows.append({
            "action_id": f"ACT{action_id:03d}",
            "workstream": "Experiment",
            "owner": experiment["owner"],
            "sprint_week": f"Week {random.randint(1, 7)}",
            "action": f"{experiment['decision']}: {experiment['channel_name']} at {experiment['campus_name']}.",
            "expected_lift": experiment["expected_activations"],
            "effort_hours": random.randint(10, 34),
            "dependency": experiment["incentive"],
            "status": "Planned" if experiment["decision"] != "Backlog" else "Backlog",
        })
        action_id += 1
    for issue in readiness_hot:
        rows.append({
            "action_id": f"ACT{action_id:03d}",
            "workstream": "Readiness",
            "owner": issue["owner"],
            "sprint_week": f"Week {random.randint(1, 9)}",
            "action": issue["recommendation"],
            "expected_lift": round(issue["estimated_impacted_users"] * 0.18, 1),
            "effort_hours": issue["fix_hours"],
            "dependency": issue["affected_stage"],
            "status": "Ready to fix" if issue["severity"] == "High" else "In review",
        })
        action_id += 1
    return rows


def channel_summary(weekly_rows):
    buckets = defaultdict(lambda: defaultdict(float))
    for row in weekly_rows:
        bucket = buckets[row["channel_name"]]
        for key in ["leads", "applications", "activated_users", "spend", "kyc_rework_cases", "support_tickets"]:
            bucket[key] += float(row[key])
    rows = []
    for channel_name, metrics in buckets.items():
        rows.append({
            "channel_name": channel_name,
            "leads": int(metrics["leads"]),
            "applications": int(metrics["applications"]),
            "activated_users": int(metrics["activated_users"]),
            "spend": round(metrics["spend"], 2),
            "cac": round(metrics["spend"] / max(1, metrics["activated_users"]), 2),
            "apply_rate_pct": round(pct(metrics["applications"], metrics["leads"]), 1),
            "activation_rate_pct": round(pct(metrics["activated_users"], metrics["applications"]), 1),
            "ops_load": int(metrics["kyc_rework_cases"] + metrics["support_tickets"]),
        })
    return sorted(rows, key=lambda row: row["activated_users"], reverse=True)


def weekly_focus(weekly_rows):
    buckets = defaultdict(lambda: defaultdict(float))
    for row in weekly_rows:
        bucket = buckets[row["week_start"]]
        for key in ["applications", "activated_users", "spend", "support_tickets", "kyc_rework_cases"]:
            bucket[key] += float(row[key])
    rows = []
    for week, metrics in sorted(buckets.items()):
        rows.append({
            "week_start": week,
            "applications": int(metrics["applications"]),
            "activated_users": int(metrics["activated_users"]),
            "spend": round(metrics["spend"], 2),
            "cac": round(metrics["spend"] / max(1, metrics["activated_users"]), 2),
            "ops_cases": int(metrics["support_tickets"] + metrics["kyc_rework_cases"]),
        })
    return rows


def write_docs(summary, top_campus, top_experiment, top_readiness):
    executive = f"""# Executive Findings

## What I analyzed

I modeled a nine-week fintech growth sprint for students and newcomers, joining campus cohorts, weekly funnel metrics, growth experiments, product-readiness blockers, and stakeholder actions.

## Findings

- The synthetic sprint includes {number(summary["campus_count"])} campus cohorts, {number(summary["modeled_weekly_rows"])} weekly funnel rows, {number(summary["experiment_count"])} experiments, and {number(summary["readiness_issue_count"])} readiness checks.
- The highest-priority cohort is {top_campus["campus_name"]}, with {top_campus["activated_users"]} modeled activated users, {top_campus["activation_rate_pct"]}% application-to-activation, and a {top_campus["priority_score"]} priority score.
- The strongest experiment is {top_experiment["channel_name"]} at {top_experiment["campus_name"]}, with {top_experiment["expected_activations"]} expected activations and {money(top_experiment["expected_spend"])} modeled spend.
- The highest readiness risk is {top_readiness["issue"]} at {top_readiness["campus_name"]}, affecting an estimated {top_readiness["estimated_impacted_users"]} users.

## Recommendation

Treat the summer sprint as an integrated growth operating cadence. Prioritize high-fit campus cohorts, launch only the experiments with strong activation economics, and clear onboarding blockers before scaling acquisition volume.
"""
    (ANALYSIS_DIR / "executive_findings.md").write_text(executive)

    plan = f"""# Analysis Plan

## Objective

Prioritize a nine-week fintech growth sprint for students and newcomers by connecting acquisition, activation, product readiness, and stakeholder action planning.

## Method

1. Generate synthetic campus cohorts with addressable-student estimates, community density, partner fit, trust gap, product fit, compliance complexity, and regional cost assumptions.
2. Simulate weekly funnel performance across campus ambassadors, partner webinars, referrals, creator content, paid social, and search-led education.
3. Rank campus cohorts by opportunity size, activation quality, CAC efficiency, readiness, and operating risk.
4. Score experiments using expected activations, impact, confidence, ease, CAC, and readiness risk.
5. Separate growth recommendations from product, RevOps, risk, compliance, support, and data blockers.

## Current Run Summary

- Activated users: {number(summary["activated_users"])}
- Applications: {number(summary["applications"])}
- Modeled spend: {money(summary["modeled_spend"])}
- Blended CAC: {money(summary["blended_cac"])}
- Sprint focus: {top_campus["campus_name"]}, {top_campus["student_segment"]}
"""
    (ANALYSIS_DIR / "analysis_plan.md").write_text(plan)

    sql = """-- Example SQL checks for a fintech growth strategy workbench.

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
"""
    (ANALYSIS_DIR / "sql_checks.sql").write_text(sql)


def main():
    DATA_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    campuses = build_campuses()
    weekly_rows = build_weekly_metrics(campuses)
    campus_queue = aggregate_by_campus(campuses, weekly_rows)
    experiments = build_experiments(campuses, campus_queue)
    readiness = build_readiness(campuses)
    actions = build_actions(campus_queue, experiments, readiness)
    channels_out = channel_summary(weekly_rows)
    weeks = weekly_focus(weekly_rows)

    summary = {
        "campus_count": len(campuses),
        "modeled_weekly_rows": len(weekly_rows),
        "experiment_count": len(experiments),
        "readiness_issue_count": len(readiness),
        "applications": sum(row["applications"] for row in campus_queue),
        "activated_users": sum(row["activated_users"] for row in campus_queue),
        "modeled_spend": round(sum(row["spend"] for row in campus_queue), 2),
        "blended_cac": round(sum(row["spend"] for row in campus_queue) / max(1, sum(row["activated_users"] for row in campus_queue)), 2),
        "avg_activation_rate_pct": round(sum(row["activation_rate_pct"] for row in campus_queue) / len(campus_queue), 1),
        "launch_experiments": sum(1 for row in experiments if row["decision"] == "Launch in week 1"),
        "high_readiness_risks": sum(1 for row in readiness if row["severity"] == "High"),
    }

    write_csv(DATA_DIR / "campus_cohorts.csv", campuses, list(campuses[0].keys()))
    write_csv(DATA_DIR / "weekly_funnel_metrics.csv", weekly_rows, list(weekly_rows[0].keys()))
    write_csv(DATA_DIR / "growth_experiments.csv", experiments, list(experiments[0].keys()))
    write_csv(DATA_DIR / "product_readiness.csv", readiness, list(readiness[0].keys()))
    write_csv(DATA_DIR / "stakeholder_actions.csv", actions, list(actions[0].keys()))

    write_csv(OUTPUT_DIR / "cohort_priority_queue.csv", campus_queue, list(campus_queue[0].keys()))
    write_csv(OUTPUT_DIR / "experiment_backlog.csv", experiments, list(experiments[0].keys()))
    write_csv(OUTPUT_DIR / "readiness_queue.csv", readiness, list(readiness[0].keys()))
    write_csv(OUTPUT_DIR / "stakeholder_action_plan.csv", actions, list(actions[0].keys()))
    (OUTPUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2))

    payload = {
        "summary": summary,
        "cohort_queue": campus_queue[:14],
        "channel_summary": channels_out,
        "experiments": experiments[:18],
        "readiness_queue": readiness[:18],
        "actions": actions[:18],
        "weekly_focus": weeks,
    }
    (OUTPUT_DIR / "app_payload.json").write_text(json.dumps(payload, indent=2))

    write_docs(summary, campus_queue[0], experiments[0], readiness[0])

    print(json.dumps({
        "campuses": len(campuses),
        "weekly_rows": len(weekly_rows),
        "experiments": len(experiments),
        "readiness_issues": len(readiness),
        "top_cohort": campus_queue[0]["campus_name"],
        "top_experiment": experiments[0]["experiment_id"],
    }, indent=2))


if __name__ == "__main__":
    main()
