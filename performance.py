import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import pandas as pd
    import altair as alt

    return alt, mo, pd


@app.cell(hide_code=True)
def _():
    REVIEW_PERIODS = ["2025-Q3", "2025-Q4", "2026-Q1"]
    CURRENT_PERIOD = "2026-Q1"
    PRIOR_PERIOD   = "2025-Q4"

    ORG_HIERARCHY = {
        "Dealer":      ["DTD", "FMD", "CLO", "Dealer Core", "DR", "Fraud"],
        "DTD":         ["DTD - Platform", "DTD - Integrations", "DTD - Analytics"],
        "FMD":         ["FMD - Originations", "FMD - Servicing", "FMD - Risk"],
        "CLO":         ["CLO - Lending", "CLO - Operations", "CLO - Compliance"],
        "Dealer Core": ["Core - Identity", "Core - API", "Core - Data"],
        "DR":          ["DR - Recovery", "DR - Collections", "DR - Reporting"],
        "Fraud":       ["Fraud - Detection", "Fraud - Investigation", "Fraud - Prevention"],
    }

    # Each entry: col, label, competency, unit, fmt, direction ("higher"|"lower"),
    #             scale_max, green threshold, yellow threshold
    IC_METRICS = [
        {
            "col": "throughput_consistency", "label": "Throughput Consistency",
            "competency": "Results Focus", "unit": "ratio (0–1)", "fmt": ".2f",
            "direction": "higher", "scale_max": 1.0, "green": 0.85, "yellow": 0.65,
        },
        {
            "col": "scope_of_impact", "label": "Scope of Impact",
            "competency": "Job-Specific Skills", "unit": "unique repos", "fmt": ".0f",
            "direction": "higher", "scale_max": 15.0, "green": 6.0, "yellow": 3.0,
        },
        {
            "col": "cycle_time", "label": "Cycle Time",
            "competency": "Problem Solving", "unit": "days", "fmt": ".1f",
            "direction": "lower", "scale_max": 15.0, "green": 3.0, "yellow": 7.0,
        },
        {
            "col": "change_failure_rate", "label": "Change Failure Rate",
            "competency": "Judgment", "unit": "%", "fmt": ".1f",
            "direction": "lower", "scale_max": 30.0, "green": 5.0, "yellow": 15.0,
        },
        {
            "col": "review_influence_index", "label": "Review Influence Index",
            "competency": "Communication", "unit": "influential reviews", "fmt": ".0f",
            "direction": "higher", "scale_max": 30.0, "green": 15.0, "yellow": 8.0,
        },
    ]

    LEADER_METRICS = [
        {
            "col": "ai_tool_penetration", "label": "AI Tool Penetration",
            "competency": "Influence", "unit": "%", "fmt": ".0f",
            "direction": "higher", "scale_max": 100.0, "green": 70.0, "yellow": 40.0,
        },
        {
            "col": "slo_health", "label": "SLO Health",
            "competency": "Customer Focus", "unit": "%", "fmt": ".1f",
            "direction": "higher", "scale_max": 100.0, "green": 99.0, "yellow": 97.0,
        },
        {
            "col": "knowledge_contribution_rate", "label": "Knowledge Contribution Rate",
            "competency": "Teamwork", "unit": "contributions", "fmt": ".0f",
            "direction": "higher", "scale_max": 20.0, "green": 8.0, "yellow": 4.0,
        },
        {
            "col": "say_do_ratio", "label": "Say/Do Ratio",
            "competency": "Results Focus", "unit": "%", "fmt": ".0f",
            "direction": "higher", "scale_max": 110.0, "green": 85.0, "yellow": 70.0,
        },
        {
            "col": "innovation_vs_maintenance_ratio", "label": "Innovation vs Maintenance",
            "competency": "Judgment", "unit": "ratio", "fmt": ".2f",
            "direction": "lower", "scale_max": 3.0, "green": 0.5, "yellow": 1.0,
        },
    ]

    # (min_value_inclusive, label) — first match wins
    RATING_BANDS = [
        (4.5, "Outstanding"),
        (3.5, "Exceeds Expectations"),
        (2.5, "Meets Expectations"),
        (1.5, "Developing"),
        (0.0, "Needs Improvement"),
    ]
    RATING_LABEL_ORDER = [
        "Needs Improvement", "Developing", "Meets Expectations",
        "Exceeds Expectations", "Outstanding",
    ]
    RATING_COLORS = {
        "Outstanding":          "#1b5e20",
        "Exceeds Expectations": "#388e3c",
        "Meets Expectations":   "#f9a825",
        "Developing":           "#e65100",
        "Needs Improvement":    "#b71c1c",
    }

    GOAL_STATUS_ORDER  = ["Not Started", "At Risk", "On Track", "Complete"]
    GOAL_STATUS_COLORS = {
        "Complete":    "#388e3c",
        "On Track":    "#1565c0",
        "At Risk":     "#e65100",
        "Not Started": "#9e9e9e",
    }

    CHART_W, CHART_H = 400, 210
    return (
        CURRENT_PERIOD,
        IC_METRICS,
        LEADER_METRICS,
        ORG_HIERARCHY,
        RATING_BANDS,
        RATING_COLORS,
        REVIEW_PERIODS,
    )


@app.cell(hide_code=True)
def _(pd):
    # To switch to a real backend, replace these read_csv calls with
    # database queries. See seed_performance_data.py for the SQL reference.
    people_df = pd.read_csv(
        "data/people.csv",
        dtype={
            "employee_id": "str", "full_name": "str", "title": "str",
            "level": "str", "employee_type": "str", "is_leader": "int64",
            "sub_org": "str", "team": "str",
            "manager_id": "str", "start_date": "str",
        },
        keep_default_na=True,
        na_values=[""],
    )
    reviews_df = pd.read_csv(
        "data/individual_reviews.csv",
        dtype={
            "employee_id": "str", "review_period": "str",
            "overall_rating": "float64", "goal_completion_pct": "float64",
            "manager_notes": "str",
            # IC metrics (NaN for people leaders)
            "throughput_consistency":          "float64",
            "scope_of_impact":                 "float64",
            "cycle_time":                      "float64",
            "change_failure_rate":             "float64",
            "review_influence_index":          "float64",
            # People-leader metrics (NaN for ICs)
            "ai_tool_penetration":             "float64",
            "slo_health":                      "float64",
            "knowledge_contribution_rate":     "float64",
            "say_do_ratio":                    "float64",
            "innovation_vs_maintenance_ratio": "float64",
        },
        keep_default_na=True,
        na_values=[""],
    )
    goals_df = pd.read_csv(
        "data/individual_goals.csv",
        dtype={
            "goal_id": "int64", "employee_id": "str", "review_period": "str",
            "title": "str", "category": "str", "status": "str",
            "completion_pct": "float64",
        },
        keep_default_na=True,
        na_values=[""],
    )
    return goals_df, people_df, reviews_df


@app.cell(hide_code=True)
def _(RATING_BANDS, RATING_COLORS):
    def get_rating_label(r: float) -> str:
        for threshold, label in RATING_BANDS:
            if r >= threshold:
                return label
        return "Needs Improvement"

    def rating_badge_html(r: float) -> str:
        label = get_rating_label(r)
        color = RATING_COLORS[label]
        return (
            f'<span style="background:{color};color:#fff;padding:3px 12px;'
            f'border-radius:12px;font-size:0.85rem;font-weight:600">'
            f'{r:.1f} — {label}</span>'
        )

    return (rating_badge_html,)


@app.cell(hide_code=True)
def _(ORG_HIERARCHY, mo):
    all_orgs = (
        ["Dealer"]
        + ORG_HIERARCHY["Dealer"]
        + [t for so in ORG_HIERARCHY["Dealer"] for t in ORG_HIERARCHY[so]]
    )
    org_selector = mo.ui.dropdown(
        options=all_orgs, value="Dealer", label="Organization",
    )
    return (org_selector,)


@app.cell(hide_code=True)
def _(CURRENT_PERIOD, ORG_HIERARCHY, org_selector, people_df, reviews_df):
    from datetime import date as _date

    _sel = org_selector.value
    if _sel == "Dealer":
        _mask = people_df["employee_id"].notna()
    elif _sel in ORG_HIERARCHY["Dealer"]:
        _mask = people_df["sub_org"] == _sel
    else:
        _mask = people_df["team"] == _sel

    _fp = people_df[_mask].copy()
    _fp["tenure_years"] = _fp["start_date"].apply(
        lambda s: (_date(2026, 3, 18) - _date.fromisoformat(s)).days / 365.25
    )
    # Merge ALL current-period metric columns (drop review_period and manager_notes
    # which are only needed in the individual profile cell via reviews_df directly).
    _cur = reviews_df[reviews_df["review_period"] == CURRENT_PERIOD].drop(
        columns=["review_period", "manager_notes"], errors="ignore"
    )
    filtered_people     = _fp
    people_with_ratings = _fp.merge(_cur, on="employee_id", how="left")
    return (filtered_people,)


@app.cell(hide_code=True)
def _(filtered_people, mo):
    # Build the dropdown. _opts is cell-private (underscore prefix = not exported,
    # not rendered). person_selector is the only export — Marimo embeds it in
    # the nav header so it won't appear as a separate standalone cell output.
    _opts = {"— select a person —": None} | {
        f"{r['full_name']}  ({r['title']})": r["employee_id"]
        for _, r in filtered_people.sort_values("full_name").iterrows()
    }
    person_selector = mo.ui.dropdown(
        options=list(_opts.keys()),
        value="— select a person —",
        label="Person",
    )
    return (person_selector,)


@app.cell(hide_code=True)
def _(filtered_people, person_selector):
    # Rebuild the lookup here (cell-private) so we can call .value safely.
    # Marimo forbids reading widget.value in the same cell that created it.
    _opts = {"— select a person —": None} | {
        f"{r['full_name']}  ({r['title']})": r["employee_id"]
        for _, r in filtered_people.sort_values("full_name").iterrows()
    }
    selected_employee_id = _opts.get(person_selector.value)
    return (selected_employee_id,)


@app.cell(hide_code=True)
def _(
    CURRENT_PERIOD,
    REVIEW_PERIODS,
    goals_df,
    people_df,
    reviews_df,
    selected_employee_id,
):
    from datetime import date as _d2

    if selected_employee_id is not None:
        person_record = people_df[
            people_df["employee_id"] == selected_employee_id
        ].iloc[0]

        person_reviews = reviews_df[
            (reviews_df["employee_id"] == selected_employee_id) &
            reviews_df["review_period"].isin(REVIEW_PERIODS)
        ].sort_values("review_period")

        person_goals = goals_df[
            (goals_df["employee_id"] == selected_employee_id) &
            (goals_df["review_period"] == CURRENT_PERIOD)
        ].copy()

        # Resolve manager name
        mgr_id = person_record.get("manager_id")
        if mgr_id and str(mgr_id) != "nan":
            _mgr_rows = people_df[people_df["employee_id"] == mgr_id]
            manager_name = _mgr_rows.iloc[0]["full_name"] if len(_mgr_rows) else "—"
        else:
            manager_name = "—"

        tenure_years = (
            _d2(2026, 3, 18) - _d2.fromisoformat(person_record["start_date"])
        ).days / 365.25
    else:
        person_record  = None
        person_reviews = None
        person_goals   = None
        manager_name   = None
        tenure_years   = None
    return manager_name, person_record, person_reviews, tenure_years


@app.cell(hide_code=True)
def _(mo, org_selector, person_selector):
    nav = mo.hstack(
        [
            mo.md("## Individual Performance Tracker"),
            mo.hstack([org_selector, person_selector], gap="1rem"),
        ],
        justify="space-between",
        align="end",
    )
    return (nav,)


@app.cell(hide_code=True)
def _(
    CURRENT_PERIOD,
    IC_METRICS,
    LEADER_METRICS,
    alt,
    mo,
    people_df,
    person_record,
    reviews_df,
):
    import pandas as _pd3

    if person_record is None:
        metrics_section = mo.md("")
    else:
        # ── One-time data prep (all employees, current period) ─────────────────
        _cur       = reviews_df[reviews_df["review_period"] == CURRENT_PERIOD]
        _all_data  = people_df.merge(_cur, on="employee_id", how="inner")
        _role_data = _all_data[
            _all_data["is_leader"] == person_record["is_leader"]
        ].copy()

        _emp_id   = person_record["employee_id"]
        _emp_team = person_record["team"]

        _team_df = _role_data[_role_data["team"] == _emp_team]
        _lob_df  = _role_data   # LoB = Dealer = all in dataset
        _div_df  = _role_data   # Division = Financial Services = same in mock

        _metrics_def = LEADER_METRICS if bool(person_record["is_leader"]) else IC_METRICS

        _ALT_SORT   = ["Team", "Line of Business", "Division"]
        _ALT_COLORS = ["#4299e1", "#48bb78", "#9f7aea"]

        # Panel geometry — _CX must equal _PW/2 so alt.value(_CX) always hits
        # the exact center of the violin (density=0 with padding=0 on x scale).
        _PW = 150   # panel width in pixels
        _PH = 280   # panel height in pixels
        _CX = _PW // 2   # 75 — violin center in pixels
        _BW = 12         # half-width of IQR box in pixels

        def _box_stats(series):
            _s   = series.dropna()
            _q1  = float(_s.quantile(0.25))
            _q2  = float(_s.quantile(0.50))
            _q3  = float(_s.quantile(0.75))
            _iqr = _q3 - _q1
            return _pd3.DataFrame([{
                "q1":  _q1, "q2": _q2, "q3": _q3,
                "wlo": float(max(float(_s.min()), _q1 - 1.5 * _iqr)),
                "whi": float(min(float(_s.max()), _q3 + 1.5 * _iqr)),
            }])

        def _make_panel(grp_series, altitude, color, show_y, vmin, vmax,
                        emp_val, metric_label):
            _s    = grp_series.dropna()
            _ys   = alt.Scale(domain=[vmin, vmax])
            _dist = _pd3.DataFrame({"value": _s.values})
            _box  = _box_stats(_s)
            _emp  = _pd3.DataFrame({"value": [emp_val]})

            _y_axis = (
                alt.Axis(title=metric_label)
                if show_y else
                alt.Axis(labels=False, ticks=False, title=None, domain=False)
            )

            # Violin: density mirrored around x=0; padding=0 guarantees
            # density=0 maps to exactly pixel _CX (= _PW/2).
            _violin = (
                alt.Chart(_dist)
                .transform_density(
                    "value", as_=["value", "density"], extent=[vmin, vmax]
                )
                .mark_area(orient="horizontal", color=color, opacity=0.5)
                .encode(
                    alt.X("density:Q")
                        .stack("center").impute(None).title(None)
                        .scale(alt.Scale(padding=0, nice=False))
                        .axis(labels=False, values=[0], grid=False, ticks=True),
                    alt.Y("value:Q", scale=_ys, axis=_y_axis),
                )
            )

            # Whisker: vertical rule from wlo to whi at the violin center
            _whisker = (
                alt.Chart(_box)
                .mark_rule(color=color, strokeWidth=1.5)
                .encode(
                    x=alt.value(_CX),
                    y=alt.Y("wlo:Q", scale=_ys),
                    y2=alt.Y2("whi:Q"),
                )
            )

            # IQR box: filled rect Q1→Q3, centered on the violin
            _iqr = (
                alt.Chart(_box)
                .mark_rect(color=color)
                .encode(
                    x=alt.value(_CX - _BW),
                    x2=alt.value(_CX + _BW),
                    y=alt.Y("q1:Q", scale=_ys),
                    y2=alt.Y2("q3:Q"),
                )
            )

            # Median: wide white rule drawn on top of the IQR box
            _median = (
                alt.Chart(_box)
                .mark_rule(color="white", strokeWidth=3)
                .encode(
                    x=alt.value(_CX - _BW),
                    x2=alt.value(_CX + _BW),
                    y=alt.Y("q2:Q", scale=_ys),
                )
            )

            # Employee line: dashed, spans full panel width (no x encoding)
            _emp_line = (
                alt.Chart(_emp)
                .mark_rule(color="#1a1a2e", strokeWidth=2, strokeDash=[6, 3])
                .encode(y=alt.Y("value:Q", scale=_ys))
            )

            return (
                alt.layer(_violin, _whisker, _iqr, _median, _emp_line)
                .properties(
                    title=alt.TitleParams(
                        altitude, anchor="middle",
                        fontSize=11, color="#666", fontWeight="normal",
                    ),
                    width=_PW,
                    height=_PH,
                )
            )

        def _build_dist_chart(meta):
            _col     = meta["col"]
            _emp_row = _all_data[_all_data["employee_id"] == _emp_id]
            if len(_emp_row) == 0 or _pd3.isna(_emp_row.iloc[0][_col]):
                return mo.md(f"*No data available for {meta['label']}.*")

            _emp_val      = float(_emp_row.iloc[0][_col])
            # Use the actual data ceiling rather than the fixed scale_max so
            # the KDE tail is never clipped at the top of the chart.  Add 10%
            # headroom; also floor at scale_max so the axis isn't too cramped
            # when all values are well below the threshold.
            _all_vals = _pd3.concat(
                [_team_df[_col], _lob_df[_col], _div_df[_col]]
            ).dropna()
            _vmin = 0.0
            _vmax = max(meta["scale_max"], float(_all_vals.max())) * 1.10
            _metric_label = f"{meta['label']} ({meta['unit']})"
            _grp_series   = [
                _team_df[_col], _lob_df[_col], _div_df[_col]
            ]

            _panels = [
                _make_panel(
                    grp_series   = _grp_series[i],
                    altitude     = _ALT_SORT[i],
                    color        = _ALT_COLORS[i],
                    show_y       = (i == 0),
                    vmin         = _vmin,
                    vmax         = _vmax,
                    emp_val      = _emp_val,
                    metric_label = _metric_label,
                )
                for i in range(3)
            ]

            # spacing=0 makes the dashed employee line continuous across panels
            return mo.ui.altair_chart(
                alt.hconcat(*_panels, spacing=0)
                .resolve_scale(y="shared")
                .properties(
                    title=alt.TitleParams(
                        f"{meta['competency']}  ·  {meta['label']}",
                        anchor="middle",
                        fontSize=13,
                        fontWeight="bold",
                    )
                )
                .configure_view(stroke=None)
                .configure_axis(grid=True, gridColor="#e8e8e8")
            )

        metrics_section = mo.vstack(
            [_build_dist_chart(m) for m in _metrics_def],
            gap="2rem",
        )
    return (metrics_section,)


@app.cell(hide_code=True)
def _(
    CURRENT_PERIOD,
    manager_name,
    mo,
    person_record,
    person_reviews,
    rating_badge_html,
    tenure_years,
):
    if person_record is None:
        profile_section = mo.callout(
            mo.md("Select a person from the **Person** dropdown above to view their profile."),
            kind="info",
        )
    else:
        _cur_review = person_reviews[
            person_reviews["review_period"] == CURRENT_PERIOD
        ]
        _cur_rating = (
            _cur_review.iloc[0]["overall_rating"]
            if len(_cur_review) > 0 else None
        )
        _badge = rating_badge_html(_cur_rating) if _cur_rating is not None else "—"

        _tenure_str = (
            f"{tenure_years:.1f} yr{'s' if tenure_years >= 2 else ''}"
            if tenure_years is not None else "—"
        )

        profile_section = mo.Html(f"""
        <div style="background:#fff;border:1px solid #dee2e6;border-radius:10px;
                    padding:1.25rem 1.75rem;margin-bottom:1rem">
          <div style="display:flex;justify-content:space-between;align-items:flex-start">
            <div>
              <div style="font-size:1.4rem;font-weight:700;color:#1a1a2e">
                {person_record["full_name"]}
              </div>
              <div style="color:#555;margin-top:2px">{person_record["title"]}</div>
            </div>
            <div style="text-align:right">
              <div style="font-size:0.8rem;color:#888;margin-bottom:4px">Current Rating</div>
              {_badge}
            </div>
          </div>
          <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0.5rem;
                      margin-top:1rem;font-size:0.85rem;color:#444">
            <div><span style="color:#999">Level</span><br><strong>{person_record["level"]}</strong></div>
            <div><span style="color:#999">Type</span><br><strong>{person_record["employee_type"]}</strong></div>
            <div><span style="color:#999">Team</span><br><strong>{person_record["team"]}</strong></div>
            <div><span style="color:#999">Manager</span><br><strong>{manager_name or "—"}</strong></div>
            <div><span style="color:#999">Sub-org</span><br><strong>{person_record["sub_org"]}</strong></div>
            <div><span style="color:#999">Tenure</span><br><strong>{_tenure_str}</strong></div>
            <div><span style="color:#999">Employee ID</span><br><strong>{person_record["employee_id"]}</strong></div>
            <div><span style="color:#999">Start Date</span><br><strong>{person_record["start_date"]}</strong></div>
          </div>
        </div>
        """)
    return (profile_section,)


@app.cell(hide_code=True)
def _(metrics_section, mo, nav, profile_section):
    mo.vstack(
        [nav, mo.md("---"), profile_section, metrics_section],
        gap="1.5rem",
    )
    return


if __name__ == "__main__":
    app.run()
