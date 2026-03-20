# Dealer MBR

A [Marimo](https://marimo.io) reactive notebook for the Dealer organization's Monthly Business Review (MBR).

## Prerequisites

- [uv](https://docs.astral.sh/uv/) — Python package and project manager

## Setup

```bash
uv sync
```

This creates a `.venv` with Python 3.13 and installs all dependencies.

## Running

**Interactive editor** (for editing and exploring the notebook):
```bash
uv run marimo edit mbr.py
```

**Read-only presentation mode** (for running the review):
```bash
uv run marimo run mbr.py
```

Both commands open the notebook in your browser.

## Organization Structure

The review covers the **Dealer** technology organization and its sub-organizations:

| Sub-org | Teams |
|---------|-------|
| DTD | Platform, Integrations, Analytics |
| FMD | Originations, Servicing, Risk |
| CLO | Lending, Operations, Compliance |
| Dealer Core | Identity, API, Data |
| DR | Recovery, Collections, Reporting |
| Fraud | Detection, Investigation, Prevention |

## Notebook Structure

### Summary Scorecard

A color-coded table showing all metrics with:
- Red / Yellow / Green threshold ranges
- Current month value with RAG status badge
- % change vs. prior month

### Deep Dives

Tabbed sections for each category — **Customer**, **Economics**, **Talent**, **Quality** — with a trend chart (Jan–Mar 2026) and a current-month breakdown bar chart for every metric.

Use the **"View by" dropdown** at the top to drill down from the Dealer level to any sub-organization. Bar charts update to show team-level performance for the selected sub-org.

## Metrics

| Category | Metrics |
|----------|---------|
| **Customer** | Deployment Frequency, Lead Time, Cycle Time |
| **Economics** | PRs per Engineer, % Time on CTD & RTE, Direct / AWS / Snowflake Expense Variance |
| **Talent** | Span of Control, Associate/Contractor Mix %, Engagement %, Enablement %, Inclusion %, People Leadership Index % |
| **Quality** | Incidents by Severity (P1/P2/P3), SLO %, Change Failure Rate %, Time to Restore, High Vulnerability Age |
