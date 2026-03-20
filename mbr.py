import marimo

__generated_with = "0.21.0"
app = marimo.App(width="full")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import pandas as pd
    import altair as alt

    return alt, mo, pd


@app.cell(hide_code=True)
def _():
    MONTHS = ["2026-01", "2026-02", "2026-03"]
    CURRENT_MONTH = "2026-03"
    PRIOR_MONTH = "2026-02"
    CATEGORIES = ["Customer", "Economics", "Talent", "Quality"]

    ORG_HIERARCHY = {
        "Dealer": ["DTD", "FMD", "CLO", "Dealer Core", "DR", "Fraud"],
        "DTD": ["DTD - Platform", "DTD - Integrations", "DTD - Analytics"],
        "FMD": ["FMD - Originations", "FMD - Servicing", "FMD - Risk"],
        "CLO": ["CLO - Lending", "CLO - Operations", "CLO - Compliance"],
        "Dealer Core": ["Core - Identity", "Core - API", "Core - Data"],
        "DR": ["DR - Recovery", "DR - Collections", "DR - Reporting"],
        "Fraud": ["Fraud - Detection", "Fraud - Investigation", "Fraud - Prevention"],
    }

    METRICS = {
        # ── Customer ────────────────────────────────────────────────────────────
        "deployment_frequency": {
            "label": "Deployment Frequency",
            "category": "Customer",
            "unit": "deploys/day",
            "direction": "higher_is_better",
            "aggregate": "mean",
            "thresholds": {
                "green": (2.0, None),
                "yellow": (1.0, 2.0),
                "red": (None, 1.0),
            },
        },
        "lead_time": {
            "label": "Lead Time",
            "category": "Customer",
            "unit": "days",
            "direction": "lower_is_better",
            "aggregate": "mean",
            "thresholds": {
                "green": (None, 3.0),
                "yellow": (3.0, 7.0),
                "red": (7.0, None),
            },
        },
        "cycle_time": {
            "label": "Cycle Time",
            "category": "Customer",
            "unit": "days",
            "direction": "lower_is_better",
            "aggregate": "mean",
            "thresholds": {
                "green": (None, 2.0),
                "yellow": (2.0, 5.0),
                "red": (5.0, None),
            },
        },
        # ── Economics ───────────────────────────────────────────────────────────
        "prs_per_engineer": {
            "label": "PRs per Engineer",
            "category": "Economics",
            "unit": "PRs/engineer",
            "direction": "higher_is_better",
            "aggregate": "mean",
            "thresholds": {
                "green": (8.0, None),
                "yellow": (4.0, 8.0),
                "red": (None, 4.0),
            },
        },
        "pct_time_ctd_rte": {
            "label": "% Time on CTD & RTE",
            "category": "Economics",
            "unit": "%",
            "direction": "lower_is_better",
            "aggregate": "mean",
            "thresholds": {
                "green": (None, 20.0),
                "yellow": (20.0, 35.0),
                "red": (35.0, None),
            },
        },
        "direct_expense_variance": {
            "label": "Direct Expense Variance",
            "category": "Economics",
            "unit": "%",
            "direction": "bidirectional",
            "aggregate": "mean",
            "thresholds": {"green": 5.0, "yellow": 10.0},
        },
        "aws_expense_variance": {
            "label": "AWS Expense Variance",
            "category": "Economics",
            "unit": "%",
            "direction": "bidirectional",
            "aggregate": "mean",
            "thresholds": {"green": 5.0, "yellow": 10.0},
        },
        "snowflake_expense_variance": {
            "label": "Snowflake Expense Variance",
            "category": "Economics",
            "unit": "%",
            "direction": "bidirectional",
            "aggregate": "mean",
            "thresholds": {"green": 5.0, "yellow": 10.0},
        },
        # ── Talent ──────────────────────────────────────────────────────────────
        "span_of_control": {
            "label": "Span of Control",
            "category": "Talent",
            "unit": "reports/mgr",
            "direction": "range",
            "aggregate": "mean",
            "thresholds": {
                "green": (5.0, 10.0),
                "yellow_low": 3.0,
                "yellow_high": 12.0,
            },
        },
        "contractor_mix_pct": {
            "label": "Associate/Contractor Mix %",
            "category": "Talent",
            "unit": "%",
            "direction": "lower_is_better",
            "aggregate": "mean",
            "thresholds": {
                "green": (None, 30.0),
                "yellow": (30.0, 45.0),
                "red": (45.0, None),
            },
        },
        "engagement_pct": {
            "label": "Engagement %",
            "category": "Talent",
            "unit": "%",
            "direction": "higher_is_better",
            "aggregate": "mean",
            "thresholds": {
                "green": (75.0, None),
                "yellow": (60.0, 75.0),
                "red": (None, 60.0),
            },
        },
        "enablement_pct": {
            "label": "Enablement %",
            "category": "Talent",
            "unit": "%",
            "direction": "higher_is_better",
            "aggregate": "mean",
            "thresholds": {
                "green": (75.0, None),
                "yellow": (60.0, 75.0),
                "red": (None, 60.0),
            },
        },
        "inclusion_pct": {
            "label": "Inclusion %",
            "category": "Talent",
            "unit": "%",
            "direction": "higher_is_better",
            "aggregate": "mean",
            "thresholds": {
                "green": (80.0, None),
                "yellow": (65.0, 80.0),
                "red": (None, 65.0),
            },
        },
        "pli_pct": {
            "label": "People Leadership Index %",
            "category": "Talent",
            "unit": "%",
            "direction": "higher_is_better",
            "aggregate": "mean",
            "thresholds": {
                "green": (80.0, None),
                "yellow": (65.0, 80.0),
                "red": (None, 65.0),
            },
        },
        # ── Quality ─────────────────────────────────────────────────────────────
        "incidents": {
            "label": "Incidents by Severity",
            "category": "Quality",
            "unit": "count",
            "direction": "lower_is_better",
            "aggregate": "sum",
            "thresholds": {
                "P1": {"green": 0, "yellow": 1},
                "P2": {"green": 2, "yellow": 5},
                "P3": {"green": 5, "yellow": 10},
            },
        },
        "slo_pct": {
            "label": "SLO %",
            "category": "Quality",
            "unit": "%",
            "direction": "higher_is_better",
            "aggregate": "mean",
            "thresholds": {
                "green": (99.5, None),
                "yellow": (99.0, 99.5),
                "red": (None, 99.0),
            },
        },
        "change_failure_rate": {
            "label": "Change Failure Rate %",
            "category": "Quality",
            "unit": "%",
            "direction": "lower_is_better",
            "aggregate": "mean",
            "thresholds": {
                "green": (None, 5.0),
                "yellow": (5.0, 15.0),
                "red": (15.0, None),
            },
        },
        "time_to_restore": {
            "label": "Time to Restore",
            "category": "Quality",
            "unit": "hours",
            "direction": "lower_is_better",
            "aggregate": "mean",
            "thresholds": {
                "green": (None, 1.0),
                "yellow": (1.0, 4.0),
                "red": (4.0, None),
            },
        },
        "high_vuln_age": {
            "label": "High Vulnerability Age",
            "category": "Quality",
            "unit": "days",
            "direction": "lower_is_better",
            "aggregate": "mean",
            "thresholds": {
                "green": (None, 30.0),
                "yellow": (30.0, 60.0),
                "red": (60.0, None),
            },
        },
    }
    return (
        CATEGORIES,
        CURRENT_MONTH,
        METRICS,
        MONTHS,
        ORG_HIERARCHY,
        PRIOR_MONTH,
    )


@app.cell(hide_code=True)
def _():
    def classify_threshold(val, meta):
        direction = meta["direction"]
        thresholds = meta["thresholds"]

        if direction == "bidirectional":
            abs_val = abs(val)
            if abs_val <= thresholds["green"]:
                return "green"
            elif abs_val <= thresholds["yellow"]:
                return "yellow"
            return "red"

        elif direction == "range":
            g_lo, g_hi = thresholds["green"]
            if g_lo <= val <= g_hi:
                return "green"
            y_lo = thresholds["yellow_low"]
            y_hi = thresholds["yellow_high"]
            if y_lo <= val <= y_hi:
                return "yellow"
            return "red"

        elif direction == "higher_is_better":
            g_min = thresholds["green"][0]
            y_min = thresholds["yellow"][0]
            if val >= g_min:
                return "green"
            elif val >= y_min:
                return "yellow"
            return "red"

        elif direction == "lower_is_better":
            g_max = thresholds["green"][1]
            y_max = thresholds["yellow"][1]
            if val <= g_max:
                return "green"
            elif val <= y_max:
                return "yellow"
            return "red"

        return "yellow"

    def classify_incidents(p1, p2, thresholds):
        t1 = thresholds["P1"]
        t2 = thresholds["P2"]
        if p1 > t1["yellow"]:
            return "red"
        elif p1 > t1["green"]:
            return "yellow"
        elif p2 > t2["yellow"]:
            return "red"
        elif p2 > t2["green"]:
            return "yellow"
        return "green"

    def fmt_val(val, meta):
        unit = meta["unit"]
        if unit == "%":
            return f"{val:.1f}%"
        elif unit == "days":
            return f"{val:.1f}d"
        elif unit == "hours":
            return f"{val:.1f}h"
        elif unit == "deploys/day":
            return f"{val:.2f}/day"
        elif unit == "PRs/engineer":
            return f"{val:.1f}"
        elif unit == "reports/mgr":
            return f"{val:.1f}"
        elif unit == "count":
            return str(int(round(val)))
        return f"{val:.2f}"

    def fmt_num(v):
        if v is None:
            return "—"
        if v == int(v):
            return f"{int(v)}"
        return f"{v:.1f}"

    def range_strings(meta):
        """Return (red_str, yellow_str, green_str) for a metric."""
        direction = meta["direction"]
        t = meta["thresholds"]

        if direction == "bidirectional":
            g, y = t["green"], t["yellow"]
            return (f"> ±{fmt_num(y)}%", f"±{fmt_num(g)}–±{fmt_num(y)}%", f"within ±{fmt_num(g)}%")

        elif direction == "range":
            g_lo, g_hi = t["green"]
            y_lo, y_hi = t["yellow_low"], t["yellow_high"]
            return (
                f"< {fmt_num(y_lo)} or > {fmt_num(y_hi)}",
                f"{fmt_num(y_lo)}–{fmt_num(g_lo)} or {fmt_num(g_hi)}–{fmt_num(y_hi)}",
                f"{fmt_num(g_lo)} – {fmt_num(g_hi)}",
            )

        elif direction == "higher_is_better":
            g_min = t["green"][0]
            y_min, y_max = t["yellow"]
            r_max = t["red"][1]
            return (f"< {fmt_num(r_max)}", f"{fmt_num(y_min)} – {fmt_num(y_max)}", f"≥ {fmt_num(g_min)}")

        elif direction == "lower_is_better":
            g_max = t["green"][1]
            y_min, y_max = t["yellow"]
            r_min = t["red"][0]
            return (f"> {fmt_num(r_min)}", f"{fmt_num(y_min)} – {fmt_num(y_max)}", f"< {fmt_num(g_max)}")

        return ("—", "—", "—")

    def pct_change_html(pct, direction):
        if pct is None:
            return "<span style='color:#6c757d;'>—</span>"
        abs_p = abs(pct)
        if abs_p < 0.05:
            return f"<span style='color:#6c757d;'>→ 0.0%</span>"
        if direction == "higher_is_better":
            favorable = pct > 0
        elif direction == "lower_is_better":
            favorable = pct < 0
        else:
            color = "#6c757d"
            arrow = "↑" if pct > 0 else "↓"
            return f"<span style='color:{color};'>{arrow} {abs_p:.1f}%</span>"
        color = "#28a745" if favorable else "#dc3545"
        arrow = "↑" if pct > 0 else "↓"
        return f"<span style='color:{color}; font-weight:600;'>{arrow} {abs_p:.1f}%</span>"

    return (
        classify_incidents,
        classify_threshold,
        fmt_val,
        pct_change_html,
        range_strings,
    )


@app.cell(hide_code=True)
def _(pd):
    # Load pre-generated metric data.
    # To switch to a real backend, replace this read_csv call with a database
    # query using the SQL in seed_data.py as a reference.  The DataFrame must
    # have columns: month, org_level, org_name, parent_org, metric, value, severity
    df = pd.read_csv(
        "data/mbr_metrics.csv",
        dtype={
            "month":      "str",
            "org_level":  "str",
            "org_name":   "str",
            "parent_org": "str",
            "metric":     "str",
            "value":      "float64",
            "severity":   "str",
        },
        # pandas reads empty cells as NaN, which is correct for parent_org
        # (top-level org) and severity (non-incident metrics)
        keep_default_na=True,
        na_values=[""],
    )
    return (df,)


@app.cell(hide_code=True)
def _(ORG_HIERARCHY, mo):
    org_selector = mo.ui.dropdown(
        options=list(ORG_HIERARCHY.keys()),
        value="Dealer",
        label="View by:",
    )
    return (org_selector,)


@app.cell(hide_code=True)
def _(ORG_HIERARCHY, org_selector):
    selected_org = org_selector.value
    if selected_org == "Dealer":
        bar_orgs = ORG_HIERARCHY["Dealer"]
        bar_level = "sub_org"
    else:
        bar_orgs = ORG_HIERARCHY.get(selected_org, [])
        bar_level = "team"
    return bar_level, bar_orgs, selected_org


@app.cell(hide_code=True)
def _(
    CURRENT_MONTH,
    METRICS,
    PRIOR_MONTH,
    classify_incidents,
    classify_threshold,
    df,
    fmt_val,
    range_strings,
    selected_org,
):
    def _build_scorecard():
        org_df = df[df["org_name"] == selected_org]
        CATEGORY_ORDER = ["Customer", "Economics", "Talent", "Quality"]
        rows = []

        for mk, meta in METRICS.items():
            cat = meta["category"]

            if mk == "incidents":
                def _inc_row(month, _odf=org_df, _mk=mk):
                    sub = _odf[
                        (_odf["month"] == month) &
                        (_odf["metric"] == _mk) &
                        _odf["severity"].notna()
                    ]
                    return {
                        sev: int(sub[sub["severity"] == sev]["value"].sum())
                        for sev in ["P1", "P2", "P3"]
                    }

                cur = _inc_row(CURRENT_MONTH)
                pri = _inc_row(PRIOR_MONTH)
                cur_total = sum(cur.values())
                pri_total = sum(pri.values())
                pct = ((cur_total - pri_total) / max(pri_total, 1) * 100) if pri_total else None
                color = classify_incidents(cur["P1"], cur["P2"], meta["thresholds"])
                rows.append({
                    "metric": meta["label"],
                    "category": cat,
                    "red_range": "P1>1 or P2>5",
                    "yellow_range": "P1=1 or P2 3-5",
                    "green_range": "P1=0, P2≤2",
                    "current_formatted": f"P1:{cur['P1']} P2:{cur['P2']} P3:{cur['P3']}",
                    "current_value": cur_total,
                    "color": color,
                    "pct_change": pct,
                    "direction": meta["direction"],
                })
            else:
                def _row(month, _odf=org_df, _mk=mk):
                    return _odf[
                        (_odf["month"] == month) &
                        (_odf["metric"] == _mk) &
                        _odf["severity"].isna()
                    ]["value"]

                cur_s = _row(CURRENT_MONTH)
                pri_s = _row(PRIOR_MONTH)
                if cur_s.empty:
                    continue
                cur_v = float(cur_s.iloc[0])
                pri_v = float(pri_s.iloc[0]) if not pri_s.empty else None
                pct = ((cur_v - pri_v) / abs(pri_v) * 100) if pri_v else None
                red_s, yel_s, grn_s = range_strings(meta)
                rows.append({
                    "metric": meta["label"],
                    "category": cat,
                    "red_range": red_s,
                    "yellow_range": yel_s,
                    "green_range": grn_s,
                    "current_formatted": fmt_val(cur_v, meta),
                    "current_value": cur_v,
                    "color": classify_threshold(cur_v, meta),
                    "pct_change": pct,
                    "direction": meta["direction"],
                })

        rows.sort(key=lambda r: (
            CATEGORY_ORDER.index(r["category"]),
            list(METRICS.keys()).index(
                next(k for k, v in METRICS.items() if v["label"] == r["metric"])
            ),
        ))
        return rows

    scorecard_rows = _build_scorecard()
    return (scorecard_rows,)


@app.cell(hide_code=True)
def _(mo, pct_change_html, scorecard_rows, selected_org):
    _COLOR_STYLE = {
        "green":  "background:#d4edda; color:#155724;",
        "yellow": "background:#fff3cd; color:#856404;",
        "red":    "background:#f8d7da; color:#721c24;",
    }
    _BADGE = {"green": "🟢", "yellow": "🟡", "red": "🔴"}

    _hdr = f"""
    <div style="overflow-x:auto; margin:16px 0;">
    <table style="width:100%; border-collapse:collapse;
                  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
                  font-size:13px;">
      <thead>
        <tr style="background:#1a252f; color:#ecf0f1;">
          <th style="padding:10px 14px; text-align:left; white-space:nowrap;">Category</th>
          <th style="padding:10px 14px; text-align:left; white-space:nowrap;">Metric</th>
          <th style="padding:10px 14px; text-align:center; white-space:nowrap;">🔴 Red</th>
          <th style="padding:10px 14px; text-align:center; white-space:nowrap;">🟡 Yellow</th>
          <th style="padding:10px 14px; text-align:center; white-space:nowrap;">🟢 Green</th>
          <th style="padding:10px 14px; text-align:center; white-space:nowrap; min-width:140px;">Current (Mar) — {selected_org}</th>
          <th style="padding:10px 14px; text-align:center; white-space:nowrap;">vs. Feb</th>
        </tr>
      </thead>
      <tbody>
    """

    _body = ""
    _prev_cat = None
    for _r in scorecard_rows:
        _border_top = "border-top:2px solid #dee2e6;" if _r["category"] != _prev_cat else "border-top:1px solid #f0f0f0;"
        if _r["category"] != _prev_cat:
            _cat_td = f'<td style="padding:8px 14px; font-weight:700; vertical-align:top; {_border_top}">{_r["category"]}</td>'
            _prev_cat = _r["category"]
        else:
            _cat_td = f'<td style="padding:8px 14px; {_border_top}"></td>'

        _cs = _COLOR_STYLE[_r["color"]]
        _badge = _BADGE[_r["color"]]
        _pct_html = pct_change_html(_r.get("pct_change"), _r["direction"])

        _body += f"""
        <tr>
          {_cat_td}
          <td style="padding:8px 14px; white-space:nowrap; {_border_top}">{_r['metric']}</td>
          <td style="padding:8px 14px; text-align:center; color:#721c24; white-space:nowrap; {_border_top}">{_r['red_range']}</td>
          <td style="padding:8px 14px; text-align:center; color:#856404; white-space:nowrap; {_border_top}">{_r['yellow_range']}</td>
          <td style="padding:8px 14px; text-align:center; color:#155724; white-space:nowrap; {_border_top}">{_r['green_range']}</td>
          <td style="padding:8px 14px; text-align:center; {_cs} font-weight:700;
                     border-radius:4px; white-space:nowrap; {_border_top}">
            {_badge} {_r['current_formatted']}
          </td>
          <td style="padding:8px 14px; text-align:center; white-space:nowrap; {_border_top}">{_pct_html}</td>
        </tr>
        """

    _footer = "</tbody></table></div>"
    scorecard_html = mo.Html(_hdr + _body + _footer)
    return (scorecard_html,)


@app.cell(hide_code=True)
def _(MONTHS, alt, classify_threshold, df, pd):
    CHART_W = 430
    CHART_H = 230

    RAG_SCALE = alt.Scale(
        domain=["green", "yellow", "red"],
        range=["#28a745", "#e6a817", "#dc3545"],
    )
    SEV_SCALE = alt.Scale(
        domain=["P1", "P2", "P3"],
        range=["#dc3545", "#fd7e14", "#ffc107"],
    )

    # Work-type stacking order (bottom → top) and colours
    _WORK_TYPES_ORDER = ["Investment", "Tech Mod", "CTD", "RTE"]
    _WORK_TYPE_ORDER_MAP = {wt: i for i, wt in enumerate(_WORK_TYPES_ORDER)}
    WORK_TYPE_SCALE = alt.Scale(
        domain=_WORK_TYPES_ORDER,
        range=["#2196F3", "#4CAF50", "#FF9800", "#F44336"],
    )

    def _threshold_rules(meta):
        direction = meta["direction"]
        t = meta["thresholds"]
        rules = []

        def _rule(y_val, color):
            return (
                alt.Chart(pd.DataFrame({"y": [y_val]}))
                .mark_rule(color=color, strokeDash=[4, 4], strokeWidth=1.5, opacity=0.75)
                .encode(y=alt.Y("y:Q"))
            )

        if direction == "higher_is_better":
            rules.append(_rule(t["green"][0], "#28a745"))
            rules.append(_rule(t["yellow"][0], "#e6a817"))
        elif direction == "lower_is_better":
            rules.append(_rule(t["green"][1], "#28a745"))
            rules.append(_rule(t["yellow"][1], "#e6a817"))
        elif direction == "bidirectional":
            g, y = t["green"], t["yellow"]
            for v in [g, -g]:
                rules.append(_rule(v, "#28a745"))
            for v in [y, -y]:
                rules.append(_rule(v, "#e6a817"))
        elif direction == "range":
            g_lo, g_hi = t["green"]
            rules.append(_rule(g_lo, "#28a745"))
            rules.append(_rule(g_hi, "#28a745"))
            rules.append(_rule(t["yellow_low"], "#e6a817"))
            rules.append(_rule(t["yellow_high"], "#e6a817"))
        return rules

    def build_trend_chart(metric_key, meta, selected_org):
        title = f"{meta['label']} — {selected_org} Trend"

        if metric_key == "incidents":
            filt = df[
                (df["org_name"] == selected_org) &
                (df["metric"] == metric_key) &
                df["severity"].notna()
            ].copy()
            chart = (
                alt.Chart(filt)
                .mark_line(point=True, strokeWidth=2)
                .encode(
                    x=alt.X("month:N", title="", sort=MONTHS, axis=alt.Axis(labelAngle=0)),
                    y=alt.Y("value:Q", title="Count"),
                    color=alt.Color("severity:N", scale=SEV_SCALE,
                                    legend=alt.Legend(title="Severity")),
                    tooltip=["month:N", "severity:N", alt.Tooltip("value:Q", format=".0f")],
                )
                .properties(title=title, width=CHART_W, height=CHART_H)
            )

        elif metric_key == "pct_time_ctd_rte":
            # Show all four work types as a stacked area chart
            filt = df[
                (df["org_name"] == selected_org) &
                (df["metric"] == "work_type_pct") &
                df["severity"].notna()
            ].copy()
            filt["wt_order"] = filt["severity"].map(_WORK_TYPE_ORDER_MAP)
            chart = (
                alt.Chart(filt)
                .mark_area()
                .encode(
                    x=alt.X("month:N", title="", sort=MONTHS, axis=alt.Axis(labelAngle=0)),
                    y=alt.Y("value:Q", title="%", stack="zero"),
                    color=alt.Color("severity:N", scale=WORK_TYPE_SCALE,
                                    legend=alt.Legend(title="Work Type")),
                    order=alt.Order("wt_order:O"),
                    tooltip=[
                        "month:N",
                        alt.Tooltip("severity:N", title="Work Type"),
                        alt.Tooltip("value:Q", format=".1f", title="%"),
                    ],
                )
                .properties(
                    title=f"Work Type Distribution — {selected_org} Trend",
                    width=CHART_W, height=CHART_H,
                )
            )

        else:
            filt = df[
                (df["org_name"] == selected_org) &
                (df["metric"] == metric_key) &
                df["severity"].isna()
            ].copy()
            line = (
                alt.Chart(filt)
                .mark_line(point=True, color="#2c3e50", strokeWidth=2)
                .encode(
                    x=alt.X("month:N", title="", sort=MONTHS, axis=alt.Axis(labelAngle=0)),
                    y=alt.Y("value:Q", title=meta["unit"]),
                    tooltip=["month:N", alt.Tooltip("value:Q", format=".2f")],
                )
            )
            rules = _threshold_rules(meta)
            chart = (
                alt.layer(line, *rules)
                .properties(title=title, width=CHART_W, height=CHART_H)
            )
        return chart.configure_view(strokeWidth=0).configure_axis(grid=True, gridColor="#f0f0f0")

    def build_bar_chart(metric_key, meta, current_month, selected_org, bar_orgs, bar_level):
        level_label = "Sub-Organization" if bar_level == "sub_org" else "Team"
        title = f"{meta['label']} — by {level_label}"

        if metric_key == "incidents":
            filt = df[
                (df["month"] == current_month) &
                (df["metric"] == metric_key) &
                df["org_name"].isin(bar_orgs) &
                (df["org_level"] == bar_level) &
                df["severity"].notna()
            ].copy()
            chart = (
                alt.Chart(filt)
                .mark_bar()
                .encode(
                    x=alt.X("org_name:N", title="", sort=bar_orgs,
                            axis=alt.Axis(labelAngle=-25)),
                    y=alt.Y("value:Q", title="Count", stack="zero"),
                    color=alt.Color("severity:N", scale=SEV_SCALE,
                                    legend=alt.Legend(title="Severity")),
                    order=alt.Order("severity:N", sort="ascending"),
                    tooltip=["org_name:N", "severity:N", alt.Tooltip("value:Q", format=".0f")],
                )
                .properties(title=title, width=CHART_W, height=CHART_H)
            )

        elif metric_key == "pct_time_ctd_rte":
            # Show all four work types as a stacked bar chart
            filt = df[
                (df["month"] == current_month) &
                (df["metric"] == "work_type_pct") &
                df["org_name"].isin(bar_orgs) &
                (df["org_level"] == bar_level) &
                df["severity"].notna()
            ].copy()
            filt["wt_order"] = filt["severity"].map(_WORK_TYPE_ORDER_MAP)
            chart = (
                alt.Chart(filt)
                .mark_bar()
                .encode(
                    x=alt.X("org_name:N", title="", sort=bar_orgs,
                            axis=alt.Axis(labelAngle=-25)),
                    y=alt.Y("value:Q", title="%", stack="zero"),
                    color=alt.Color("severity:N", scale=WORK_TYPE_SCALE,
                                    legend=alt.Legend(title="Work Type")),
                    order=alt.Order("wt_order:O"),
                    tooltip=[
                        "org_name:N",
                        alt.Tooltip("severity:N", title="Work Type"),
                        alt.Tooltip("value:Q", format=".1f", title="%"),
                    ],
                )
                .properties(
                    title=f"Work Type Distribution — by {level_label}",
                    width=CHART_W, height=CHART_H,
                )
            )

        else:
            filt = df[
                (df["month"] == current_month) &
                (df["metric"] == metric_key) &
                df["org_name"].isin(bar_orgs) &
                (df["org_level"] == bar_level) &
                df["severity"].isna()
            ].copy()
            filt["status"] = filt["value"].apply(lambda v: classify_threshold(v, meta))
            chart = (
                alt.Chart(filt)
                .mark_bar()
                .encode(
                    x=alt.X("org_name:N", title="", sort=bar_orgs,
                            axis=alt.Axis(labelAngle=-25)),
                    y=alt.Y("value:Q", title=meta["unit"]),
                    color=alt.Color("status:N", scale=RAG_SCALE, legend=None),
                    tooltip=["org_name:N", alt.Tooltip("value:Q", format=".2f"), "status:N"],
                )
                .properties(title=title, width=CHART_W, height=CHART_H)
            )
        return chart.configure_view(strokeWidth=0).configure_axis(grid=True, gridColor="#f0f0f0")

    return build_bar_chart, build_trend_chart


@app.cell(hide_code=True)
def _(
    CATEGORIES,
    CURRENT_MONTH,
    METRICS,
    bar_level,
    bar_orgs,
    build_bar_chart,
    build_trend_chart,
    mo,
    selected_org,
):
    def _make_category_content(category):
        cat_metrics = [
            (mk, meta)
            for mk, meta in METRICS.items()
            if meta["category"] == category
        ]
        sections = []
        for mk, meta in cat_metrics:
            trend = build_trend_chart(mk, meta, selected_org)
            bar   = build_bar_chart(mk, meta, CURRENT_MONTH, selected_org, bar_orgs, bar_level)
            row = mo.hstack(
                [mo.ui.altair_chart(trend), mo.ui.altair_chart(bar)],
                justify="start",
                gap="2rem",
            )
            deep_dive_label = "Work Type Distribution" if mk == "pct_time_ctd_rte" else meta["label"]
            sections.append(
                mo.vstack([
                    mo.md(f"### {deep_dive_label}"),
                    row,
                ])
            )
        return mo.vstack(sections)

    category_tabs = mo.ui.tabs(
        {cat: _make_category_content(cat) for cat in CATEGORIES}
    )
    return (category_tabs,)


@app.cell(hide_code=True)
def _(category_tabs, mo, org_selector, scorecard_html):
    mo.vstack([
        mo.md("""
    # Dealer Monthly Business Review
    ## March 2026
        """),
        mo.hstack(
            [mo.md("**Drill-down level:**"), org_selector],
            justify="start",
            gap="1rem",
            align="center",
        ),
        mo.md("---"),
        mo.md("## Summary Scorecard"),
        scorecard_html,
        mo.md("---"),
        mo.md("## Deep Dives"),
        category_tabs,
    ])
    return


if __name__ == "__main__":
    app.run()
