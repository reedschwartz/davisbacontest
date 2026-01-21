"""Sensitivity analysis visualization for Davis-Bacon impact."""

import plotly.graph_objects as go
import numpy as np
from typing import Tuple


def create_sensitivity_heatmap(
    home_price: float,
    construction_cost_share: float,
    labor_range: Tuple[float, float] = (0.25, 0.55),
    premium_range: Tuple[float, float] = (-0.15, 0.50),
    resolution: int = 20
) -> go.Figure:
    """
    Create a heatmap showing price increase sensitivity to labor share and wage premium.

    Args:
        home_price: Base home price
        construction_cost_share: Construction cost share (fixed for this analysis)
        labor_range: Tuple of (min, max) labor share values
        premium_range: Tuple of (min, max) wage premium values
        resolution: Number of points along each axis

    Returns:
        Plotly Figure object
    """
    # Create arrays for the axes
    labor_shares = np.linspace(labor_range[0], labor_range[1], resolution)
    wage_premiums = np.linspace(premium_range[0], premium_range[1], resolution)

    # Calculate price increase percentages for each combination
    results = np.zeros((resolution, resolution))

    for i, premium in enumerate(wage_premiums):
        for j, labor in enumerate(labor_shares):
            increase = home_price * construction_cost_share * labor * premium
            results[i, j] = (increase / home_price) * 100

    # Create custom colorscale: green for negative, white for zero, red for positive
    colorscale = [
        [0.0, '#00CC96'],      # Green for negative (cost savings)
        [0.23, '#00CC96'],     # Green
        [0.23, '#FFFFFF'],     # White at zero
        [0.25, '#FFFFFF'],     # White at zero
        [0.25, '#FFF5F5'],     # Light red
        [0.5, '#FFAAAA'],      # Medium red
        [1.0, '#EF553B']       # Dark red for high positive
    ]

    # Normalize colorscale based on actual data range
    min_val = results.min()
    max_val = results.max()

    # Find where zero falls in the range
    if min_val < 0 and max_val > 0:
        zero_position = abs(min_val) / (max_val - min_val)
        colorscale = [
            [0.0, '#00CC96'],
            [zero_position - 0.02, '#90EE90'],
            [zero_position, '#FFFFFF'],
            [zero_position + 0.02, '#FFCCCC'],
            [1.0, '#EF553B']
        ]

    fig = go.Figure(go.Heatmap(
        z=results,
        x=labor_shares * 100,  # Convert to percentage
        y=wage_premiums * 100,  # Convert to percentage
        colorscale=colorscale,
        colorbar=dict(
            title="Price<br>Change (%)",
            ticksuffix="%"
        ),
        hovertemplate=(
            "Labor Share: %{x:.0f}%<br>"
            "Wage Premium: %{y:.0f}%<br>"
            "Price Change: %{z:.2f}%<extra></extra>"
        )
    ))

    # Add contour lines
    fig.add_trace(go.Contour(
        z=results,
        x=labor_shares * 100,
        y=wage_premiums * 100,
        contours=dict(
            showlabels=True,
            labelfont=dict(size=10, color='black'),
            start=-4,
            end=14,
            size=2
        ),
        line=dict(color='rgba(0,0,0,0.3)', width=1),
        showscale=False,
        hoverinfo='skip'
    ))

    # Add markers for key scenarios
    scenarios = [
        {"name": "U.S. Avg", "labor": 40, "premium": 15},
        {"name": "TX/FL", "labor": 35, "premium": -8},
        {"name": "NY/CA", "labor": 45, "premium": 35},
    ]

    for scenario in scenarios:
        fig.add_trace(go.Scatter(
            x=[scenario["labor"]],
            y=[scenario["premium"]],
            mode='markers+text',
            marker=dict(size=14, color='black', symbol='x', line=dict(width=2)),
            text=[scenario["name"]],
            textposition='top center',
            textfont=dict(size=12, color='black', family='Arial Black'),
            showlegend=False,
            hoverinfo='skip'
        ))

    fig.update_layout(
        title=dict(text="How Different Assumptions Change the Result", font=dict(size=18)),
        xaxis_title="Labor as % of Construction Cost",
        yaxis_title="DB Floor vs. Market Wages",
        height=600,
        font=dict(size=13),
        xaxis=dict(ticksuffix="%", tickfont=dict(size=12), title_font=dict(size=14)),
        yaxis=dict(ticksuffix="%", tickfont=dict(size=12), title_font=dict(size=14)),
        coloraxis_colorbar=dict(tickfont=dict(size=11))
    )

    # Add horizontal line at 0% premium with annotation
    fig.add_hline(y=0, line_dash="dash", line_color="black", line_width=2,
                  annotation_text="Floor = Market (no effect below this line)",
                  annotation_position="right",
                  annotation_font_size=11)

    return fig


def create_dollar_sensitivity_heatmap(
    home_price: float,
    construction_cost_share: float,
    labor_range: Tuple[float, float] = (0.25, 0.55),
    premium_range: Tuple[float, float] = (-0.15, 0.50),
    resolution: int = 20
) -> go.Figure:
    """
    Create a heatmap showing dollar amount changes (not percentages).

    Args:
        home_price: Base home price
        construction_cost_share: Construction cost share
        labor_range: Tuple of (min, max) labor share values
        premium_range: Tuple of (min, max) wage premium values
        resolution: Number of points along each axis

    Returns:
        Plotly Figure object
    """
    labor_shares = np.linspace(labor_range[0], labor_range[1], resolution)
    wage_premiums = np.linspace(premium_range[0], premium_range[1], resolution)

    results = np.zeros((resolution, resolution))

    for i, premium in enumerate(wage_premiums):
        for j, labor in enumerate(labor_shares):
            results[i, j] = home_price * construction_cost_share * labor * premium

    # Find where zero falls in the range
    min_val = results.min()
    max_val = results.max()

    if min_val < 0 and max_val > 0:
        zero_position = abs(min_val) / (max_val - min_val)
        colorscale = [
            [0.0, '#00CC96'],
            [zero_position - 0.02, '#90EE90'],
            [zero_position, '#FFFFFF'],
            [zero_position + 0.02, '#FFCCCC'],
            [1.0, '#EF553B']
        ]
    else:
        colorscale = 'RdYlGn_r'

    fig = go.Figure(go.Heatmap(
        z=results,
        x=labor_shares * 100,
        y=wage_premiums * 100,
        colorscale=colorscale,
        colorbar=dict(
            title="Price<br>Change ($)",
            tickprefix="$",
            tickformat=",.0f"
        ),
        hovertemplate=(
            "Labor Share: %{x:.0f}%<br>"
            "Wage Premium: %{y:.0f}%<br>"
            "Price Change: $%{z:,.0f}<extra></extra>"
        )
    ))

    fig.update_layout(
        title=dict(text=f"Dollar Impact on a ${home_price:,.0f} Home", font=dict(size=18)),
        xaxis_title="Labor as % of Construction Cost",
        yaxis_title="DB Floor vs. Market Wages",
        height=600,
        font=dict(size=13),
        xaxis=dict(ticksuffix="%", tickfont=dict(size=12), title_font=dict(size=14)),
        yaxis=dict(ticksuffix="%", tickfont=dict(size=12), title_font=dict(size=14))
    )

    fig.add_hline(y=0, line_dash="dash", line_color="black", line_width=2,
                  annotation_text="Floor = Market",
                  annotation_position="right",
                  annotation_font_size=11)

    return fig
