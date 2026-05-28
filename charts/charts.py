"""
Plotly chart builder functions.
Each function returns a plotly.graph_objects.Figure with a consistent dark theme.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# ── Shared theme config ──────────────────────────────────────────────────────
COLORS = [
    "#6C63FF",  # indigo
    "#00D2FF",  # cyan
    "#FF6584",  # coral
    "#44D7B6",  # mint
    "#FFD166",  # amber
    "#A78BFA",  # lavender
    "#F97316",  # orange
    "#38BDF8",  # sky
    "#FB7185",  # rose
    "#34D399",  # emerald
]

LAYOUT_DEFAULTS = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", size=13, color="#E2E8F0"),
    margin=dict(l=40, r=30, t=50, b=40),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
)


def _apply_theme(fig: go.Figure) -> go.Figure:
    """Apply consistent dark theme to a figure."""
    fig.update_layout(**LAYOUT_DEFAULTS)
    return fig


# ── Bar: Registrations vs Attendance ─────────────────────────────────────────
def bar_registrations_vs_attendance(reg_df: pd.DataFrame, att_df: pd.DataFrame) -> go.Figure:
    """Grouped bar chart comparing registrations and attendance per event."""
    merged = reg_df.merge(att_df, on="event_name", how="outer").fillna(0)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=merged["event_name"], y=merged["total_registrations"],
        name="Registrations", marker_color=COLORS[0],
        marker=dict(line=dict(width=0)),
    ))
    fig.add_trace(go.Bar(
        x=merged["event_name"], y=merged["total_attendance"],
        name="Attendance", marker_color=COLORS[1],
        marker=dict(line=dict(width=0)),
    ))
    fig.update_layout(
        title="Registrations vs Attendance by Event",
        xaxis_title="Event",
        yaxis_title="Count",
        barmode="group",
    )
    return _apply_theme(fig)


# ── Pie: Department Participation ─────────────────────────────────────────────
def pie_department_participation(dept_df: pd.DataFrame) -> go.Figure:
    """Donut chart of department participation share."""
    fig = px.pie(
        dept_df, values="total_registrations", names="department",
        color_discrete_sequence=COLORS, hole=0.45,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(title="Department Participation Share")
    return _apply_theme(fig)


# ── Bar: Attendance Percentage ────────────────────────────────────────────────
def bar_attendance_percentage(pct_df: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart of attendance percentage per event."""
    pct_df = pct_df.sort_values("attendance_pct", ascending=True)
    fig = go.Figure(go.Bar(
        x=pct_df["attendance_pct"],
        y=pct_df["event_name"],
        orientation="h",
        marker_color=COLORS[3],
        text=pct_df["attendance_pct"].apply(lambda v: f"{v}%"),
        textposition="outside",
    ))
    fig.update_layout(
        title="Attendance Rate by Event",
        xaxis_title="Attendance %",
        yaxis_title="Event",
        xaxis=dict(range=[0, 110]),
    )
    return _apply_theme(fig)


# ── Bar: Year-wise Participation ──────────────────────────────────────────────
def bar_year_wise(year_df: pd.DataFrame) -> go.Figure:
    """Bar chart of participation by academic year."""
    year_df = year_df.copy()
    year_df["academic_year"] = year_df["academic_year"].astype(str)
    fig = go.Figure(go.Bar(
        x=year_df["academic_year"],
        y=year_df["total_registrations"],
        marker_color=COLORS[4],
        text=year_df["total_registrations"],
        textposition="outside",
    ))
    fig.update_layout(
        title="Participation by Academic Year",
        xaxis_title="Year",
        yaxis_title="Registrations",
    )
    return _apply_theme(fig)


# ── Bar: Top Attended Events ─────────────────────────────────────────────────
def bar_top_events(top_df: pd.DataFrame) -> go.Figure:
    """Bar chart of top attended events."""
    top_df = top_df.sort_values("attendance_count", ascending=True)
    fig = go.Figure(go.Bar(
        x=top_df["attendance_count"],
        y=top_df["event_name"],
        orientation="h",
        marker_color=COLORS[5],
        text=top_df["attendance_count"],
        textposition="outside",
    ))
    fig.update_layout(
        title="Top Attended Events",
        xaxis_title="Attendance Count",
        yaxis_title="Event",
    )
    return _apply_theme(fig)


# ── Pie: Invalid Records Breakdown ───────────────────────────────────────────
def pie_invalid_records(inv_df: pd.DataFrame) -> go.Figure:
    """Pie chart showing breakdown of invalid record reasons."""
    fig = px.pie(
        inv_df, values="count", names="reason",
        color_discrete_sequence=COLORS, hole=0.4,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(title="Invalid Records Breakdown")
    return _apply_theme(fig)


# ── Line: Attendance Trends ──────────────────────────────────────────────────
def line_attendance_trends(trends_df: pd.DataFrame) -> go.Figure:
    """Line chart of attendance check-ins over time."""
    fig = go.Figure(go.Scatter(
        x=trends_df["checkin_date"],
        y=trends_df["checkins"],
        mode="lines+markers",
        line=dict(color=COLORS[1], width=3),
        marker=dict(size=8, color=COLORS[0]),
        fill="tozeroy",
        fillcolor="rgba(108, 99, 255, 0.15)",
    ))
    fig.update_layout(
        title="Attendance Trends Over Time",
        xaxis_title="Date",
        yaxis_title="Check-ins",
    )
    return _apply_theme(fig)


# ── Heatmap: Event × Department ──────────────────────────────────────────────
def heatmap_event_department(heatmap_df: pd.DataFrame) -> go.Figure:
    """Heatmap of registrations by event and department."""
    fig = go.Figure(go.Heatmap(
        z=heatmap_df.values,
        x=heatmap_df.columns.tolist(),
        y=heatmap_df.index.tolist(),
        colorscale="Viridis",
        text=heatmap_df.values,
        texttemplate="%{text}",
        textfont=dict(size=12),
    ))
    fig.update_layout(
        title="Event × Department Registration Heatmap",
        xaxis_title="Department",
        yaxis_title="Event",
    )
    return _apply_theme(fig)


# ── Bar: Department Leaderboard ──────────────────────────────────────────────
def bar_department_leaderboard(lb_df: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart of department attendance rates."""
    lb_df = lb_df.sort_values("attendance_rate", ascending=True)
    fig = go.Figure(go.Bar(
        x=lb_df["attendance_rate"],
        y=lb_df["department"],
        orientation="h",
        marker_color=COLORS[2],
        text=lb_df["attendance_rate"].apply(lambda v: f"{v}%"),
        textposition="outside",
    ))
    fig.update_layout(
        title="Department Leaderboard (Attendance Rate)",
        xaxis_title="Attendance Rate %",
        yaxis_title="Department",
        xaxis=dict(range=[0, 110]),
    )
    return _apply_theme(fig)


# ── Bar: Match Summary ──────────────────────────────────────────────────────
def bar_match_summary(match_df: pd.DataFrame) -> go.Figure:
    """Bar chart of attendance match categories."""
    colors_map = {
        "Registered & Attended": COLORS[3],
        "Registered but Absent": COLORS[2],
        "Attended without Registration": COLORS[4],
    }
    fig = go.Figure(go.Bar(
        x=match_df["category"],
        y=match_df["count"],
        marker_color=[colors_map.get(c, COLORS[0]) for c in match_df["category"]],
        text=match_df["count"],
        textposition="outside",
    ))
    fig.update_layout(
        title="Registration vs Attendance Match",
        xaxis_title="Category",
        yaxis_title="Count",
    )
    return _apply_theme(fig)
