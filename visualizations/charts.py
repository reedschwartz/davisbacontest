"""Chart generators for Davis-Bacon impact visualization."""

import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List
import pandas as pd


def create_waterfall_chart(
    home_price: float,
    construction_cost: float,
    labor_cost: float,
    wage_increase: float,
    new_home_price: float
) -> go.Figure:
    """
    Create a waterfall chart showing cost breakdown.

    Args:
        home_price: Original home price
        construction_cost: Construction cost portion
        labor_cost: Labor cost portion of construction
        wage_increase: Davis-Bacon wage impact
        new_home_price: Final adjusted price

    Returns:
        Plotly Figure object
    """
    # Format wage increase text based on positive/negative
    if wage_increase >= 0:
        wage_text = f"+${wage_increase:,.0f}"
    else:
        wage_text = f"-${abs(wage_increase):,.0f}"

    fig = go.Figure(go.Waterfall(
        name="Cost Breakdown",
        orientation="v",
        measure=["absolute", "relative", "relative", "total"],
        x=[
            "Starting<br>Home Price",
            f"Construction Costs<br>({construction_cost/home_price*100:.0f}% of price)",
            f"Davis-Bacon<br>Wage Impact",
            "Final<br>Home Price"
        ],
        y=[
            home_price,
            0,  # Construction costs are already included in home price
            wage_increase,
            0  # Will be calculated as total
        ],
        text=[
            f"${home_price:,.0f}",
            f"${construction_cost:,.0f}<br>(already included)",
            wage_text,
            f"${new_home_price:,.0f}"
        ],
        textposition="outside",
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        increasing={"marker": {"color": "#EF553B"}},
        decreasing={"marker": {"color": "#00CC96"}},
        totals={"marker": {"color": "#636EFA"}}
    ))

    fig.update_layout(
        title=dict(text="How the Davis-Bacon Wage Floor Affects Home Price", font=dict(size=18)),
        showlegend=False,
        height=500,
        yaxis_title="Price",
        yaxis_tickprefix="$",
        yaxis_tickformat=",.0f",
        font=dict(size=14),
        xaxis=dict(tickfont=dict(size=12)),
        yaxis=dict(tickfont=dict(size=12)),
        margin=dict(t=60, b=40)
    )

    return fig


def create_regional_comparison(
    scenario_results: Dict,
    scenarios: Dict
) -> go.Figure:
    """
    Create a bar chart comparing regional scenarios.

    Args:
        scenario_results: Dict of scenario name to CalculationResult
        scenarios: Dict of scenario parameters for descriptions

    Returns:
        Plotly Figure object
    """
    names = []
    increases = []
    colors = []
    descriptions = []

    for name, result in scenario_results.items():
        names.append(name)
        increases.append(result.price_increase_percent)
        descriptions.append(scenarios[name]["description"])

        # Color based on positive/negative impact
        if result.price_increase_percent < 0:
            colors.append("#00CC96")  # Green for cost reduction
        elif result.price_increase_percent < 3:
            colors.append("#FFA15A")  # Orange for moderate
        else:
            colors.append("#EF553B")  # Red for high impact

    # Shorten names for better display
    short_names = []
    for name in names:
        if "Texas" in name:
            short_names.append("TX, FL &<br>Right-to-Work")
        elif "New York" in name:
            short_names.append("NY, CA &<br>High-Union")
        elif "National" in name:
            short_names.append("U.S.<br>Average")
        elif "Mid-Range" in name:
            short_names.append("Mid-Range")
        elif "Low-End" in name:
            short_names.append("Low-End")
        elif "High-End" in name:
            short_names.append("High-End")
        else:
            short_names.append(name)

    fig = go.Figure(go.Bar(
        x=short_names,
        y=increases,
        marker_color=colors,
        text=[f"{v:+.1f}%" for v in increases],
        textposition="outside",
        textfont=dict(size=14),
        hovertext=descriptions,
        hovertemplate="<b>%{x}</b><br>Price Change: %{y:.2f}%<br>%{hovertext}<extra></extra>"
    ))

    fig.update_layout(
        title=dict(text="Home Price Change by Scenario", font=dict(size=18)),
        xaxis_title="",
        yaxis_title="Change in Home Price",
        height=500,
        yaxis_ticksuffix="%",
        yaxis_tickformat="+.1f",
        showlegend=False,
        font=dict(size=13),
        xaxis=dict(tickfont=dict(size=11)),
        yaxis=dict(tickfont=dict(size=12)),
        margin=dict(t=60, b=80)
    )

    # Add a horizontal line at 0
    fig.add_hline(y=0, line_dash="dash", line_color="gray", line_width=2,
                  annotation_text="No change", annotation_position="right")

    return fig


def create_premium_impact_line_chart(
    home_price: float,
    construction_cost_share: float,
    labor_shares: List[float] = [0.30, 0.35, 0.40, 0.45, 0.50]
) -> go.Figure:
    """
    Create an interactive line chart showing price increase vs wage premium.

    Args:
        home_price: Base home price
        construction_cost_share: Construction cost share
        labor_shares: List of labor share values to plot

    Returns:
        Plotly Figure object
    """
    import numpy as np

    premiums = np.linspace(-0.15, 0.50, 50)

    fig = go.Figure()

    colors = px.colors.qualitative.Set2

    for i, labor_share in enumerate(labor_shares):
        price_increases = []
        for premium in premiums:
            increase = home_price * construction_cost_share * labor_share * premium
            increase_pct = (increase / home_price) * 100
            price_increases.append(increase_pct)

        fig.add_trace(go.Scatter(
            x=premiums * 100,  # Convert to percentage
            y=price_increases,
            mode='lines',
            name=f"Labor: {labor_share*100:.0f}%",
            line=dict(color=colors[i % len(colors)], width=2),
            hovertemplate=(
                f"Labor Share: {labor_share*100:.0f}%<br>"
                "Wage Premium: %{x:.0f}%<br>"
                "Price Increase: %{y:.2f}%<extra></extra>"
            )
        ))

    fig.update_layout(
        title=dict(text="How the Wage Floor Gap Affects Home Price", font=dict(size=18)),
        xaxis_title="DB Floor Above (+) or Below (-) Market Wages",
        yaxis_title="Change in Home Price",
        xaxis_ticksuffix="%",
        yaxis_ticksuffix="%",
        height=500,
        hovermode="x unified",
        legend_title="Labor as %<br>of Construction",
        font=dict(size=13),
        xaxis=dict(tickfont=dict(size=12)),
        yaxis=dict(tickfont=dict(size=12)),
        legend=dict(font=dict(size=12))
    )

    # Add vertical line at 0 premium with annotation
    fig.add_vline(x=0, line_dash="dash", line_color="gray", line_width=2)
    fig.add_hline(y=0, line_dash="dash", line_color="gray", line_width=1)

    # Add shaded region for "no effect" zone
    fig.add_vrect(x0=-15, x1=0, fillcolor="lightgreen", opacity=0.15,
                  annotation_text="Floor below market<br>(no cost impact)",
                  annotation_position="top left",
                  annotation_font_size=11)

    # Add annotation for national average
    fig.add_annotation(
        x=15, y=0,
        text="U.S. Avg<br>(+15%)",
        showarrow=True,
        arrowhead=2,
        ax=0, ay=-50,
        font=dict(size=11)
    )

    return fig


def create_mortgage_impact_chart(
    scenario_results: Dict,
    scenarios: Dict
) -> go.Figure:
    """
    Create a grouped bar chart showing monthly and lifetime mortgage impacts.

    Args:
        scenario_results: Dict of scenario name to CalculationResult
        scenarios: Dict of scenario parameters

    Returns:
        Plotly Figure object
    """
    names = list(scenario_results.keys())
    monthly = [r.monthly_payment_increase for r in scenario_results.values()]
    lifetime = [r.lifetime_cost_increase for r in scenario_results.values()]

    fig = go.Figure()

    # Shorten names for better display
    short_names = []
    for name in names:
        if "Texas" in name:
            short_names.append("TX, FL &<br>Right-to-Work")
        elif "New York" in name:
            short_names.append("NY, CA &<br>High-Union")
        elif "National" in name:
            short_names.append("U.S.<br>Average")
        elif "Mid-Range" in name:
            short_names.append("Mid-Range")
        elif "Low-End" in name:
            short_names.append("Low-End")
        elif "High-End" in name:
            short_names.append("High-End")
        else:
            short_names.append(name)

    # Color bars based on positive/negative
    bar_colors = ["#00CC96" if v < 0 else "#636EFA" for v in monthly]

    fig.add_trace(go.Bar(
        name='Monthly Payment Change',
        x=short_names,
        y=monthly,
        text=[f"${v:+,.0f}/mo" for v in monthly],
        textposition='outside',
        textfont=dict(size=13),
        marker_color=bar_colors
    ))

    fig.update_layout(
        title=dict(text="Monthly Mortgage Payment Change", font=dict(size=18)),
        xaxis_title="",
        yaxis_title="Change per Month",
        yaxis_tickprefix="$",
        yaxis_tickformat="+,.0f",
        height=450,
        showlegend=False,
        font=dict(size=13),
        xaxis=dict(tickfont=dict(size=11)),
        yaxis=dict(tickfont=dict(size=12)),
        margin=dict(t=60, b=80)
    )

    fig.add_hline(y=0, line_dash="dash", line_color="gray", line_width=2)

    return fig


def create_cost_breakdown_pie(
    construction_cost_share: float,
    labor_share: float
) -> go.Figure:
    """
    Create a pie chart showing the cost breakdown.

    Args:
        construction_cost_share: Construction as fraction of home price
        labor_share: Labor as fraction of construction

    Returns:
        Plotly Figure object
    """
    # Calculate all components
    other_costs = 1 - construction_cost_share
    construction_labor = construction_cost_share * labor_share
    construction_materials = construction_cost_share * (1 - labor_share)

    labels = [
        'Construction Labor',
        'Materials & Equipment',
        'Land, Profit, Overhead'
    ]
    values = [construction_labor, construction_materials, other_costs]
    colors = ['#EF553B', '#636EFA', '#00CC96']

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        marker_colors=colors,
        textinfo='label+percent',
        textposition='auto',
        textfont=dict(size=12),
        hole=0.35,
        hovertemplate="<b>%{label}</b><br>%{percent}<extra></extra>"
    ))

    fig.update_layout(
        title=dict(text="What Makes Up Home Price?", font=dict(size=16)),
        height=400,
        showlegend=False,
        annotations=[dict(
            text=f'<b>{construction_labor*100:.0f}%</b><br>is labor<br>(affected by<br>DB floor)',
            x=0.5, y=0.5,
            font_size=11,
            showarrow=False
        )],
        margin=dict(t=50, b=20, l=20, r=20)
    )

    return fig
