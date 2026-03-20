"""
seed_data.py — Generate sample MBR metric data and write to data/mbr_metrics.csv.

Run once (or whenever you want to refresh sample data):
    uv run python seed_data.py

─────────────────────────────────────────────────────────────────────────────
REAL-BACKEND SQL REFERENCE
─────────────────────────────────────────────────────────────────────────────
When connected to a real data warehouse, replace this file with SQL queries
that populate (or are read directly by) the notebook.

The notebook expects a single DataFrame with these columns:

  month       TEXT        -- 'YYYY-MM', e.g. '2026-03'
  org_level   TEXT        -- 'team' | 'sub_org' | 'dealer'
  org_name    TEXT        -- team/sub-org/org display name
  parent_org  TEXT        -- parent org name; NULL for the top-level org
  metric      TEXT        -- metric key (see METRIC KEYS below)
  value       REAL        -- numeric value for the metric
  severity    TEXT        -- sub-dimension label; NULL for simple scalar metrics
                          --   incidents  → 'P1' | 'P2' | 'P3'
                          --   work_type_pct → 'Investment' | 'RTE' | 'CTD' | 'Tech Mod'

METRIC KEYS
  deployment_frequency    lead_time              cycle_time
  prs_per_engineer        pct_time_ctd_rte
  work_type_pct           (sub-dimensioned by work type; see severity column)
  direct_expense_variance aws_expense_variance   snowflake_expense_variance
  span_of_control         contractor_mix_pct
  engagement_pct          enablement_pct         inclusion_pct   pli_pct
  incidents               (sub-dimensioned by severity; see severity column)
  slo_pct                 change_failure_rate
  time_to_restore         high_vuln_age

─────────────────────────────────────────────────────────────────────────────
Suggested table / view structure
─────────────────────────────────────────────────────────────────────────────

-- Raw team-level fact table (populated by pipelines / HRIS / DORA tooling)
CREATE TABLE team_metrics (
    month       VARCHAR(7)     NOT NULL,   -- 'YYYY-MM'
    team_name   VARCHAR(100)   NOT NULL,
    sub_org     VARCHAR(50)    NOT NULL,
    metric      VARCHAR(50)    NOT NULL,
    value       DECIMAL(12, 4) NOT NULL,
    severity    VARCHAR(20)    NULL,       -- sub-dimension; NULL for scalar metrics
    PRIMARY KEY (month, team_name, metric, COALESCE(severity, ''))
);

-- Sub-org rollup
--   incidents    → SUM per severity
--   work_type_pct → AVG per work type  (each org's % allocation; avg preserves 100% total)
--   all others   → AVG
CREATE VIEW sub_org_metrics AS
SELECT
    month,
    'sub_org'  AS org_level,
    sub_org    AS org_name,
    'Dealer'   AS parent_org,
    metric,
    CASE metric
        WHEN 'incidents' THEN SUM(value)
        ELSE AVG(value)
    END        AS value,
    severity
FROM team_metrics
GROUP BY month, sub_org, metric, severity;

-- Dealer-level rollup from sub-orgs (same aggregation rules)
CREATE VIEW dealer_metrics AS
SELECT
    month,
    'dealer'   AS org_level,
    'Dealer'   AS org_name,
    NULL       AS parent_org,
    metric,
    CASE metric
        WHEN 'incidents' THEN SUM(value)
        ELSE AVG(value)
    END        AS value,
    severity
FROM sub_org_metrics
GROUP BY month, metric, severity;

-- Unified view — this is what the notebook queries
CREATE VIEW mbr_metrics AS
    SELECT month, 'team' AS org_level,
           team_name AS org_name, sub_org AS parent_org,
           metric, value, severity
    FROM   team_metrics
UNION ALL
    SELECT month, org_level, org_name, parent_org, metric, value, severity
    FROM   sub_org_metrics
UNION ALL
    SELECT month, org_level, org_name, parent_org, metric, value, severity
    FROM   dealer_metrics;

─────────────────────────────────────────────────────────────────────────────
Primary notebook query (replace pd.read_csv with something like this)
─────────────────────────────────────────────────────────────────────────────

    SELECT month, org_level, org_name, parent_org, metric, value, severity
    FROM   mbr_metrics
    WHERE  month BETWEEN :start_month AND :end_month   -- e.g. '2026-01'..'2026-03'
    ORDER  BY month, org_level, org_name, metric, severity;

─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import pathlib

import numpy as np
import pandas as pd

# ── Configuration ─────────────────────────────────────────────────────────────

MONTHS = ["2026-01", "2026-02", "2026-03"]

ORG_HIERARCHY: dict[str, list[str]] = {
    "Dealer":      ["DTD", "FMD", "CLO", "Dealer Core", "DR", "Fraud"],
    "DTD":         ["DTD - Platform", "DTD - Integrations", "DTD - Analytics"],
    "FMD":         ["FMD - Originations", "FMD - Servicing", "FMD - Risk"],
    "CLO":         ["CLO - Lending", "CLO - Operations", "CLO - Compliance"],
    "Dealer Core": ["Core - Identity", "Core - API", "Core - Data"],
    "DR":          ["DR - Recovery", "DR - Collections", "DR - Reporting"],
    "Fraud":       ["Fraud - Detection", "Fraud - Investigation", "Fraud - Prevention"],
}

# Metric aggregation rules when rolling up team → sub-org → dealer.
# work_type_pct uses "mean" like other % metrics; special multi-row handling
# is done explicitly in generate() so only the aggregation rule matters here.
METRIC_AGG: dict[str, str] = {
    "deployment_frequency":      "mean",
    "lead_time":                 "mean",
    "cycle_time":                "mean",
    "prs_per_engineer":          "mean",
    "pct_time_ctd_rte":          "mean",
    "work_type_pct":             "mean",   # sub-dimensioned; see generate()
    "direct_expense_variance":   "mean",
    "aws_expense_variance":      "mean",
    "snowflake_expense_variance": "mean",
    "span_of_control":           "mean",
    "contractor_mix_pct":        "mean",
    "engagement_pct":            "mean",
    "enablement_pct":            "mean",
    "inclusion_pct":             "mean",
    "pli_pct":                   "mean",
    "incidents":                 "sum",    # severity breakdown kept separate
    "slo_pct":                   "mean",
    "change_failure_rate":       "mean",
    "time_to_restore":           "mean",
    "high_vuln_age":             "mean",
}

# ── Generation parameters ─────────────────────────────────────────────────────

# (base_value, coefficient_of_variation, [delta_jan, delta_feb, delta_mar])
PARAMS: dict[str, tuple[float, float, list[float]]] = {
    "deployment_frequency":      (1.8,   0.25, [0.00,  0.10,  0.20]),
    "lead_time":                 (5.0,   0.25, [0.50,  0.00, -0.30]),
    "cycle_time":                (3.5,   0.25, [0.30,  0.00, -0.25]),
    "prs_per_engineer":          (6.0,   0.25, [0.00,  0.50,  0.40]),
    "direct_expense_variance":   (3.0,   1.00, [0.00,  0.50,  1.00]),
    "aws_expense_variance":      (6.5,   0.50, [0.00,  0.50,  1.50]),
    "snowflake_expense_variance": (-3.0, 0.80, [0.00, -0.50, -0.50]),
    "span_of_control":           (7.2,   0.20, [0.00,  0.00,  0.10]),
    "contractor_mix_pct":        (34.0,  0.15, [2.00, -1.00, -2.00]),
    "engagement_pct":            (70.0,  0.08, [-1.00, 0.00,  1.50]),
    "enablement_pct":            (72.0,  0.08, [-0.50, 0.00,  1.00]),
    "inclusion_pct":             (76.0,  0.07, [0.00,  0.50,  1.00]),
    "pli_pct":                   (74.0,  0.08, [0.00,  0.50,  1.50]),
    "slo_pct":                   (99.25, 0.002, [-0.10, 0.00,  0.10]),
    "change_failure_rate":       (9.0,   0.30, [1.00,  0.00, -1.00]),
    "time_to_restore":           (2.8,   0.30, [0.30,  0.00, -0.30]),
    "high_vuln_age":             (45.0,  0.25, [5.00,  0.00, -5.00]),
}

# Metrics whose values must stay in [0, 100]
PCT_METRICS = {
    "engagement_pct", "enablement_pct", "inclusion_pct",
    "pli_pct", "slo_pct", "contractor_mix_pct",
}

# Poisson λ per severity for incident generation
INCIDENT_LAMBDAS = {"P1": 0.25, "P2": 1.2, "P3": 3.0}

# ── Work-type allocation parameters ──────────────────────────────────────────
# The four work types always sum to 100% (normalized after generation).
# Stacking order used in charts: Investment (bottom) → Tech Mod → CTD → RTE (top).
# Monthly deltas mirror the desired trend: CTD+RTE decreasing, Investment recovering.
#
# (base_pct, [delta_jan, delta_feb, delta_mar])
WORK_TYPES = ["Investment", "Tech Mod", "CTD", "RTE"]
WORK_TYPE_BASE: dict[str, tuple[float, list[float]]] = {
    "Investment": (52.0, [-2.0, 0.0,  1.5]),
    "Tech Mod":   (16.0, [ 0.0, 0.0,  0.0]),
    "CTD":        (14.0, [ 1.0, 0.0, -0.75]),
    "RTE":        (18.0, [ 1.0, 0.0, -0.75]),
}

# The scorecard metric pct_time_ctd_rte = CTD + RTE (derived below).
# Target ≈ 32% in Jan, declining to ~30% in Mar to match the scorecard thresholds.


# ── Data generation ───────────────────────────────────────────────────────────

def generate() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    sub_orgs = ORG_HIERARCHY["Dealer"]
    all_teams = [t for so in sub_orgs for t in ORG_HIERARCHY[so]]

    # Stable per-org multipliers so each org has a consistent character over time
    so_mod = {so: rng.uniform(0.85, 1.15) for so in sub_orgs}
    team_mod = {team: rng.uniform(0.82, 1.18) for team in all_teams}

    # Per-team, per-work-type modifiers so allocations vary across teams
    wt_mod = {
        team: {wt: rng.uniform(0.88, 1.12) for wt in WORK_TYPES}
        for team in all_teams
    }

    # ── 1. Team-level rows ────────────────────────────────────────────────────
    rows: list[dict] = []
    # Store work-type allocations keyed by (team, month) to derive pct_time_ctd_rte
    work_type_vals: dict[tuple[str, str], dict[str, float]] = {}

    for so in sub_orgs:
        for team in ORG_HIERARCHY[so]:
            tm = team_mod[team] * so_mod[so]
            for m_idx, month in enumerate(MONTHS):

                # ── Work-type allocation (4 rows, normalized to 100%) ─────────
                raw_wt: dict[str, float] = {}
                for wt in WORK_TYPES:
                    base_val, deltas = WORK_TYPE_BASE[wt]
                    raw_wt[wt] = max(
                        0.1,
                        (base_val + deltas[m_idx]) * wt_mod[team][wt]
                        + rng.normal(0, base_val * 0.05),
                    )
                total_wt = sum(raw_wt.values())
                norm_wt = {wt: v / total_wt * 100.0 for wt, v in raw_wt.items()}
                work_type_vals[(team, month)] = norm_wt

                for wt, pct_val in norm_wt.items():
                    rows.append({
                        "month":      month,
                        "org_level":  "team",
                        "org_name":   team,
                        "parent_org": so,
                        "metric":     "work_type_pct",
                        "value":      pct_val,
                        "severity":   wt,
                    })

                # ── pct_time_ctd_rte derived from CTD + RTE allocation ────────
                rows.append({
                    "month":      month,
                    "org_level":  "team",
                    "org_name":   team,
                    "parent_org": so,
                    "metric":     "pct_time_ctd_rte",
                    "value":      norm_wt["CTD"] + norm_wt["RTE"],
                    "severity":   None,
                })

                # ── All other scalar metrics ──────────────────────────────────
                for mk in PARAMS:
                    base, cv, deltas = PARAMS[mk]
                    v = base * tm + deltas[m_idx] + rng.normal(0, abs(base * cv * 0.35))
                    v = max(0.0, v)
                    if mk in PCT_METRICS:
                        v = min(100.0, v)
                    rows.append({
                        "month":      month,
                        "org_level":  "team",
                        "org_name":   team,
                        "parent_org": so,
                        "metric":     mk,
                        "value":      v,
                        "severity":   None,
                    })

                # ── Incidents (3 severity rows) ───────────────────────────────
                for sev, lam in INCIDENT_LAMBDAS.items():
                    rows.append({
                        "month":      month,
                        "org_level":  "team",
                        "org_name":   team,
                        "parent_org": so,
                        "metric":     "incidents",
                        "value":      float(int(rng.poisson(lam * team_mod[team]))),
                        "severity":   sev,
                    })

    tdf = pd.DataFrame(rows)

    # ── 2. Sub-org rows (aggregate from teams) ────────────────────────────────
    so_rows: list[dict] = []
    for so in sub_orgs:
        teams = ORG_HIERARCHY[so]
        for month in MONTHS:
            for mk in METRIC_AGG:

                if mk == "incidents":
                    for sev in INCIDENT_LAMBDAS:
                        mask = (
                            tdf["org_name"].isin(teams) &
                            (tdf["month"] == month) &
                            (tdf["metric"] == mk) &
                            (tdf["severity"] == sev)
                        )
                        so_rows.append({
                            "month": month, "org_level": "sub_org",
                            "org_name": so, "parent_org": "Dealer",
                            "metric": mk, "value": tdf[mask]["value"].sum(),
                            "severity": sev,
                        })

                elif mk == "work_type_pct":
                    # Average % allocation across teams (avg of values summing to 100
                    # also sums to 100, so the sub-org totals remain 100%)
                    for wt in WORK_TYPES:
                        mask = (
                            tdf["org_name"].isin(teams) &
                            (tdf["month"] == month) &
                            (tdf["metric"] == mk) &
                            (tdf["severity"] == wt)
                        )
                        so_rows.append({
                            "month": month, "org_level": "sub_org",
                            "org_name": so, "parent_org": "Dealer",
                            "metric": mk, "value": tdf[mask]["value"].mean(),
                            "severity": wt,
                        })

                else:
                    mask = (
                        tdf["org_name"].isin(teams) &
                        (tdf["month"] == month) &
                        (tdf["metric"] == mk) &
                        tdf["severity"].isna()
                    )
                    agg = METRIC_AGG[mk]
                    agg_val = tdf[mask]["value"].sum() if agg == "sum" else tdf[mask]["value"].mean()
                    so_rows.append({
                        "month": month, "org_level": "sub_org",
                        "org_name": so, "parent_org": "Dealer",
                        "metric": mk, "value": agg_val, "severity": None,
                    })

    sodf = pd.DataFrame(so_rows)

    # ── 3. Dealer rows (aggregate from sub-orgs) ──────────────────────────────
    d_rows: list[dict] = []
    for month in MONTHS:
        for mk in METRIC_AGG:

            if mk == "incidents":
                for sev in INCIDENT_LAMBDAS:
                    mask = (
                        (sodf["month"] == month) &
                        (sodf["metric"] == mk) &
                        (sodf["severity"] == sev)
                    )
                    d_rows.append({
                        "month": month, "org_level": "dealer",
                        "org_name": "Dealer", "parent_org": None,
                        "metric": mk, "value": sodf[mask]["value"].sum(),
                        "severity": sev,
                    })

            elif mk == "work_type_pct":
                for wt in WORK_TYPES:
                    mask = (
                        (sodf["month"] == month) &
                        (sodf["metric"] == mk) &
                        (sodf["severity"] == wt)
                    )
                    d_rows.append({
                        "month": month, "org_level": "dealer",
                        "org_name": "Dealer", "parent_org": None,
                        "metric": mk, "value": sodf[mask]["value"].mean(),
                        "severity": wt,
                    })

            else:
                mask = (
                    (sodf["month"] == month) &
                    (sodf["metric"] == mk) &
                    sodf["severity"].isna()
                )
                agg = METRIC_AGG[mk]
                agg_val = sodf[mask]["value"].sum() if agg == "sum" else sodf[mask]["value"].mean()
                d_rows.append({
                    "month": month, "org_level": "dealer",
                    "org_name": "Dealer", "parent_org": None,
                    "metric": mk, "value": agg_val, "severity": None,
                })

    ddf = pd.DataFrame(d_rows)
    return pd.concat([tdf, sodf, ddf], ignore_index=True)


# ── Write CSV ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    out = pathlib.Path(__file__).parent / "data" / "mbr_metrics.csv"
    out.parent.mkdir(exist_ok=True)

    df = generate()
    df.to_csv(out, index=False)

    print(f"Wrote {len(df):,} rows → {out}")
    print(df.dtypes.to_string())
    print(f"\nOrg levels:  {sorted(df['org_level'].unique())}")
    print(f"Months:      {sorted(df['month'].unique())}")
    print(f"Metrics:     {sorted(df['metric'].unique())}")
    print(f"Severities:  {df['severity'].dropna().unique().tolist()}")

    # Sanity check: work type allocations should sum to ~100% per org/month
    wt = df[df["metric"] == "work_type_pct"].groupby(
        ["month", "org_level", "org_name"]
    )["value"].sum()
    print(f"\nWork type totals (should all be ~100):")
    print(f"  min={wt.min():.2f}  max={wt.max():.2f}  mean={wt.mean():.2f}")
