"""
seed_performance_data.py — Generate sample individual performance data.

Run:
    uv run python seed_performance_data.py

CSVs written:
    data/people.csv              — employee roster
    data/individual_reviews.csv  — per-employee review scores for the current period

─────────────────────────────────────────────────────────────────────────────
REAL-BACKEND SQL REFERENCE
─────────────────────────────────────────────────────────────────────────────

CREATE TABLE employees (
    employee_id    VARCHAR(8)    PRIMARY KEY,
    full_name      VARCHAR(100)  NOT NULL,
    title          VARCHAR(100)  NOT NULL,
    level          VARCHAR(4)    NOT NULL,     -- 'L3' .. 'L8'
    employee_type  VARCHAR(15)   NOT NULL,     -- 'Associate' | 'Contractor'
    is_leader      SMALLINT      NOT NULL,     -- 1 = people leader, 0 = IC
    sub_org        VARCHAR(50)   NOT NULL,
    team           VARCHAR(100)  NOT NULL,
    manager_id     VARCHAR(8)    REFERENCES employees(employee_id),
    start_date     DATE          NOT NULL
);

CREATE TABLE performance_reviews (
    employee_id          VARCHAR(8)    REFERENCES employees(employee_id),
    review_period        VARCHAR(7)    NOT NULL,   -- 'YYYY-QN'
    overall_rating       DECIMAL(3,1)  NOT NULL,   -- 1.0 – 5.0
    -- IC metrics (NULL for people leaders)
    throughput_consistency         DECIMAL(5,4)  NULL,  -- 0–1  ratio; higher is better
    scope_of_impact                DECIMAL(5,1)  NULL,  -- count of unique repos; higher
    cycle_time                     DECIMAL(6,2)  NULL,  -- median days first-commit→merge; lower
    change_failure_rate            DECIMAL(5,2)  NULL,  -- rollbacks / deploys %; lower
    review_influence_index         DECIMAL(5,1)  NULL,  -- influential review comments; higher
    -- People-leader metrics (NULL for ICs)
    ai_tool_penetration            DECIMAL(5,1)  NULL,  -- % team members w/ >10 AI prompts; higher
    slo_health                     DECIMAL(6,3)  NULL,  -- % time services met SLO; higher
    knowledge_contribution_rate    DECIMAL(5,1)  NULL,  -- wiki/ADR/show-and-tell count; higher
    say_do_ratio                   DECIMAL(5,1)  NULL,  -- points completed / committed %; higher
    innovation_vs_maintenance_ratio DECIMAL(5,3) NULL,  -- CTD+RTE hrs / Innovation+Mod hrs; lower
    PRIMARY KEY (employee_id, review_period)
);

Primary notebook queries:

  -- 1. Full roster for a given scope
  SELECT * FROM employees WHERE sub_org = :sub_org;          -- sub-org view
  SELECT * FROM employees WHERE team   = :team;              -- team view
  SELECT * FROM employees;                                   -- org-wide

  -- 2. Current-period scores joined to roster
  SELECT e.*, r.*
  FROM   employees e
  JOIN   performance_reviews r
         ON r.employee_id = e.employee_id
         AND r.review_period = :current_period
  WHERE  e.sub_org = :sub_org;
"""

from __future__ import annotations

import pathlib
from datetime import date, timedelta

import numpy as np
import pandas as pd

# ── Name pools ────────────────────────────────────────────────────────────────

FIRST_NAMES = [
    "Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Avery", "Quinn",
    "Skyler", "Dakota", "Reese", "Finley", "Sage", "River", "Blake", "Cameron",
    "Drew", "Emery", "Hayden", "Jamie", "Kendall", "Logan", "Mackenzie", "Parker",
    "Peyton", "Rowan", "Sawyer", "Spencer", "Sydney", "Tanner", "Tyler", "Wiley",
    "Addison", "Bailey", "Charlie", "Devon", "Ellis", "Frankie", "Glenn", "Harper",
    "Indigo", "Jesse", "Kai", "Lane", "Marley", "Nash", "Oakley", "Phoenix",
    "Remi", "Sterling",
]

LAST_NAMES = [
    "Anderson", "Brooks", "Campbell", "Davies", "Evans", "Foster", "Garcia",
    "Harris", "Irving", "Johnson", "Kim", "Lewis", "Martin", "Nguyen", "O'Brien",
    "Patel", "Quinn", "Roberts", "Singh", "Thompson", "Ueda", "Vasquez", "Williams",
    "Xu", "Young", "Zhang", "Adams", "Baker", "Carter", "Dixon", "Edwards",
    "Fleming", "Green", "Hudson", "Ingram", "Jackson", "Knox", "Lambert",
    "Mason", "Nelson", "Oliver", "Price", "Reed", "Stone", "Turner", "Underwood",
    "Vance", "Walsh", "Xavier", "York",
]

# ── Org structure ─────────────────────────────────────────────────────────────

ORG_HIERARCHY: dict[str, list[str]] = {
    "Dealer":      ["DTD", "FMD", "CLO", "Dealer Core", "DR", "Fraud"],
    "DTD":         ["DTD - Platform", "DTD - Integrations", "DTD - Analytics"],
    "FMD":         ["FMD - Originations", "FMD - Servicing", "FMD - Risk"],
    "CLO":         ["CLO - Lending", "CLO - Operations", "CLO - Compliance"],
    "Dealer Core": ["Core - Identity", "Core - API", "Core - Data"],
    "DR":          ["DR - Recovery", "DR - Collections", "DR - Reporting"],
    "Fraud":       ["Fraud - Detection", "Fraud - Investigation", "Fraud - Prevention"],
}

# ── IC title/level options and weights ────────────────────────────────────────

IC_TITLES = [
    ("Software Engineer I",       "L3"),
    ("Software Engineer II",      "L4"),
    ("Senior Software Engineer",  "L5"),
    ("Staff Engineer",            "L6"),
    ("Principal Engineer",        "L7"),
]
IC_WEIGHTS = [0.10, 0.35, 0.35, 0.15, 0.05]

# ── Review configuration ──────────────────────────────────────────────────────

CURRENT_PERIOD = "2026-Q1"
AS_OF_DATE     = date(2026, 3, 18)

# Base rating distributions per role type: (mean, std) clipped to [1, 5]
BASE_RATING_PARAMS: dict[str, tuple[float, float]] = {
    "org_lead":     (4.4, 0.15),
    "sub_org_lead": (4.1, 0.25),
    "team_lead":    (3.7, 0.40),
    "ic":           (3.2, 0.60),
}


# ── Generation functions ──────────────────────────────────────────────────────

def _unique_name(rng: np.random.Generator, used: set[str]) -> str:
    for _ in range(10_000):
        name = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
        if name not in used:
            used.add(name)
            return name
    raise RuntimeError("Name pool exhausted")


def _start_date(rng: np.random.Generator, min_years: float, max_years: float) -> str:
    days = int(rng.integers(int(min_years * 365), int(max_years * 365)))
    return (AS_OF_DATE - timedelta(days=days)).strftime("%Y-%m-%d")


def generate_people(rng: np.random.Generator) -> pd.DataFrame:
    used_names: set[str] = set()
    rows: list[dict] = []
    counter = [1]

    def pid() -> str:
        val = f"E{counter[0]:03d}"
        counter[0] += 1
        return val

    def add(title: str, level: str, etype: str, sub_org: str, team: str,
            manager_id: str | None, role_type: str) -> str:
        min_y, max_y = {
            "org_lead":     (4.0, 12.0),
            "sub_org_lead": (3.0, 10.0),
            "team_lead":    (2.0,  8.0),
            "ic":           (0.5,  6.0),
        }[role_type]
        emp_id = pid()
        rows.append({
            "employee_id":   emp_id,
            "full_name":     _unique_name(rng, used_names),
            "title":         title,
            "level":         level,
            "employee_type": etype,
            "is_leader":     0 if role_type == "ic" else 1,
            "sub_org":       sub_org,
            "team":          team,
            "manager_id":    manager_id,
            "start_date":    _start_date(rng, min_y, max_y),
        })
        return emp_id

    org_lead_id = add("VP of Engineering", "L8", "Associate",
                       "Dealer", "Dealer", None, "org_lead")

    for so in ORG_HIERARCHY["Dealer"]:
        so_lead_id = add("Director of Engineering", "L7", "Associate",
                          so, so, org_lead_id, "sub_org_lead")

        for team in ORG_HIERARCHY[so]:
            tl_id = add("Engineering Manager", "L6", "Associate",
                         so, team, so_lead_id, "team_lead")

            for _ in range(4):
                idx = rng.choice(len(IC_TITLES), p=IC_WEIGHTS)
                ic_title, ic_level = IC_TITLES[idx]
                etype = rng.choice(["Associate", "Contractor"], p=[0.66, 0.34])
                add(ic_title, ic_level, etype, so, team, tl_id, "ic")

    return pd.DataFrame(rows)


def generate_reviews(people_df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    role_map = {}
    for _, row in people_df.iterrows():
        if row["team"] == "Dealer":
            role_map[row["employee_id"]] = "org_lead"
        elif row["team"] == row["sub_org"]:
            role_map[row["employee_id"]] = "sub_org_lead"
        elif row["title"] == "Engineering Manager":
            role_map[row["employee_id"]] = "team_lead"
        else:
            role_map[row["employee_id"]] = "ic"

    rows: list[dict] = []
    for _, person in people_df.iterrows():
        eid       = person["employee_id"]
        role      = role_map[eid]
        is_leader = role != "ic"

        mu, sigma = BASE_RATING_PARAMS[role]
        rating = float(np.clip(rng.normal(mu, sigma), 1.0, 5.0))
        rating = round(rating * 2) / 2  # snap to nearest 0.5

        row: dict = {
            "employee_id":    eid,
            "review_period":  CURRENT_PERIOD,
            "overall_rating": rating,
        }

        if not is_leader:
            # ── IC metrics ───────────────────────────────────────────────────
            row.update({
                # Results Focus: weeks with ≥1 merged PR / total weeks
                "throughput_consistency": round(
                    float(np.clip(rng.normal(0.55 + rating * 0.09, 0.05), 0.0, 1.0)), 3
                ),
                # Job-Specific Skills: unique ASV repos with merged code
                "scope_of_impact": float(max(1, int(rng.normal(rating * 2.0, 1.5)))),
                # Problem Solving: median cycle time (days)
                "cycle_time": round(
                    float(np.clip(rng.normal(10.0 - rating * 1.4, 1.5), 0.5, 20.0)), 1
                ),
                # Judgment: rollbacks / deploys %
                "change_failure_rate": round(
                    float(np.clip(rng.normal(22.0 - rating * 3.8, 3.0), 0.0, 40.0)), 1
                ),
                # Communication: PR comments that led to code changes
                "review_influence_index": float(
                    max(0, int(rng.normal(rating * 4.0 - 2.0, 3.0)))
                ),
                # Leader metrics — not applicable
                "ai_tool_penetration":             None,
                "slo_health":                      None,
                "knowledge_contribution_rate":     None,
                "say_do_ratio":                    None,
                "innovation_vs_maintenance_ratio": None,
            })
        else:
            # ── People-leader metrics ────────────────────────────────────────
            row.update({
                # IC metrics — not applicable
                "throughput_consistency":  None,
                "scope_of_impact":         None,
                "cycle_time":              None,
                "change_failure_rate":     None,
                "review_influence_index":  None,
                # Influence: % of team with >10 AI-assisted prompts/month
                "ai_tool_penetration": round(
                    float(np.clip(rng.normal(rating * 12.0 + 18.0, 8.0), 0.0, 100.0)), 1
                ),
                # Customer Focus: % time services met SLO targets
                "slo_health": round(
                    float(np.clip(rng.normal(94.0 + rating * 1.0, 1.2), 88.0, 100.0)), 2
                ),
                # Teamwork: count of wiki/ADR/show-and-tell contributions
                "knowledge_contribution_rate": float(
                    max(0, int(rng.normal(rating * 2.5, 2.0)))
                ),
                # Results Focus: story points completed / committed %
                "say_do_ratio": round(
                    float(np.clip(rng.normal(68.0 + rating * 7.0, 8.0), 30.0, 120.0)), 1
                ),
                # Judgment: (CTD+RTE hrs) / (Innovation+Modernization hrs)
                "innovation_vs_maintenance_ratio": round(
                    float(np.clip(rng.normal(2.8 - rating * 0.45, 0.35), 0.1, 4.0)), 2
                ),
            })

        rows.append(row)

    return pd.DataFrame(rows)


# ── Write CSVs ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    rng = np.random.default_rng(42)
    out = pathlib.Path(__file__).parent / "data"
    out.mkdir(exist_ok=True)

    people  = generate_people(rng)
    reviews = generate_reviews(people, rng)

    people.to_csv(out / "people.csv", index=False)
    reviews.to_csv(out / "individual_reviews.csv", index=False)

    print(f"people:  {len(people):>4} rows  →  data/people.csv")
    print(f"reviews: {len(reviews):>4} rows  →  data/individual_reviews.csv")
    print()
    print("Level distribution:")
    print(people["level"].value_counts().sort_index().to_string())
    print("\nEmployee type distribution:")
    print(people["employee_type"].value_counts().to_string())
    print("\nRating distribution (2026-Q1):")
    print(reviews["overall_rating"].value_counts().sort_index().to_string())
