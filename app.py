"""
Davis-Bacon Prevailing Wage Impact Calculator

A Streamlit application to calculate and visualize how requiring Davis-Bacon
prevailing wages on federally guaranteed mortgages would affect housing costs.
"""

import streamlit as st
import pandas as pd

# Import local modules
from models.parameters import SCENARIOS, DEFAULT_PARAMS, PARAM_RANGES, SOURCES
from models.cost_calculator import DavisBaconCalculator
from visualizations.charts import (
    create_waterfall_chart,
    create_regional_comparison,
    create_premium_impact_line_chart,
    create_mortgage_impact_chart,
    create_cost_breakdown_pie
)
from visualizations.sensitivity import (
    create_sensitivity_heatmap,
    create_dollar_sensitivity_heatmap
)

# Page configuration
st.set_page_config(
    page_title="Davis-Bacon Wage Impact Calculator",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and introduction
st.title("🏠 Davis-Bacon Prevailing Wage Impact Calculator")

st.markdown("""
This tool models how requiring **Davis-Bacon prevailing wages** on all federally guaranteed
mortgages could affect housing costs. The Davis-Bacon Act sets a **wage floor** (minimum wage)
for workers on federal projects, requiring at least the locally "prevailing wage" be paid.

In some regions, this floor is **above** current market rates (increasing costs). In others,
especially right-to-work states, the floor may already be **below** what contractors pay.

**Use the sidebar** to adjust parameters and explore different scenarios.
""")

# Sidebar for inputs
st.sidebar.header("📊 Parameters")

# Scenario selector
selected_scenario = st.sidebar.selectbox(
    "Quick Scenario",
    options=list(SCENARIOS.keys()),
    index=0,
    help="Select a pre-defined scenario based on research, or choose 'Custom' to set your own values"
)

# Show scenario description
if selected_scenario != "Custom Settings":
    st.sidebar.caption(f"*{SCENARIOS[selected_scenario]['description']}*")
    st.sidebar.caption(f"Source: {SCENARIOS[selected_scenario]['source']}")

st.sidebar.divider()

# Parameter inputs
st.sidebar.subheader("Home & Construction")

home_price = st.sidebar.slider(
    "Home Price ($)",
    min_value=PARAM_RANGES["home_price"]["min"],
    max_value=PARAM_RANGES["home_price"]["max"],
    value=DEFAULT_PARAMS["home_price"],
    step=PARAM_RANGES["home_price"]["step"],
    format="$%d",
    help="Average new home price. Default is $665,298 (NAHB 2024 average)"
)

construction_cost_share = st.sidebar.slider(
    "Construction Cost Share",
    min_value=int(PARAM_RANGES["construction_cost_share"]["min"] * 100),
    max_value=int(PARAM_RANGES["construction_cost_share"]["max"] * 100),
    value=int(DEFAULT_PARAMS["construction_cost_share"] * 100),
    step=1,
    format="%d%%",
    help="Construction costs as percentage of home price. Default is 64% (NAHB 2024)"
) / 100

st.sidebar.subheader("Labor & Wages")

# Set defaults based on scenario
if selected_scenario != "Custom Settings":
    default_labor = SCENARIOS[selected_scenario]["labor_share"]
    default_premium = SCENARIOS[selected_scenario]["wage_premium"]
else:
    default_labor = DEFAULT_PARAMS["labor_share"]
    default_premium = DEFAULT_PARAMS["wage_premium"]

labor_share = st.sidebar.slider(
    "Labor Share of Construction",
    min_value=int(PARAM_RANGES["labor_share"]["min"] * 100),
    max_value=int(PARAM_RANGES["labor_share"]["max"] * 100),
    value=int(default_labor * 100),
    step=1,
    format="%d%%",
    help="Labor costs as percentage of construction costs (30-50% typical)"
) / 100

wage_premium = st.sidebar.slider(
    "DB Floor vs. Market Wages",
    min_value=int(PARAM_RANGES["wage_premium"]["min"] * 100),
    max_value=int(PARAM_RANGES["wage_premium"]["max"] * 100),
    value=int(default_premium * 100),
    step=1,
    format="%+d%%",
    help="How much the Davis-Bacon wage floor is above (+) or below (-) current market wages. Negative means the floor has no effect."
) / 100

st.sidebar.subheader("Mortgage Settings")

mortgage_rate = st.sidebar.slider(
    "Mortgage Interest Rate",
    min_value=3.0,
    max_value=12.0,
    value=7.0,
    step=0.25,
    format="%.2f%%",
    help="Annual mortgage interest rate"
) / 100

mortgage_years = st.sidebar.selectbox(
    "Mortgage Term",
    options=[15, 20, 30],
    index=2,
    help="Mortgage term in years"
)

# Run calculations
calculator = DavisBaconCalculator(
    home_price=home_price,
    construction_cost_share=construction_cost_share,
    labor_share=labor_share,
    wage_premium=wage_premium
)

result = calculator.calculate_with_mortgage(
    interest_rate=mortgage_rate,
    years=mortgage_years
)

# Main content area
st.header("📈 Results")

# Key metrics in columns
col1, col2, col3, col4 = st.columns(4)

with col1:
    delta_color = "inverse" if result.price_increase_dollars < 0 else "normal"
    impact_sign = "+" if result.price_increase_dollars >= 0 else "-"
    st.metric(
        "Home Price Change",
        f"{impact_sign}${abs(result.price_increase_dollars):,.0f}",
        delta=f"{result.price_increase_percent:+.2f}%",
        delta_color=delta_color
    )

with col2:
    st.metric(
        "Adjusted Home Price",
        f"${result.new_home_price:,.0f}",
        delta=f"was ${home_price:,.0f}",
        delta_color="off"
    )

with col3:
    if result.monthly_payment_increase is not None:
        monthly_sign = "+" if result.monthly_payment_increase >= 0 else "-"
        st.metric(
            "Monthly Payment Change",
            f"{monthly_sign}${abs(result.monthly_payment_increase):,.0f}/mo",
            delta=f"{result.monthly_payment_increase:+,.0f} per month",
            delta_color="inverse" if result.monthly_payment_increase < 0 else "normal"
        )

with col4:
    if result.lifetime_cost_increase is not None:
        lifetime_sign = "+" if result.lifetime_cost_increase >= 0 else "-"
        st.metric(
            f"Total {mortgage_years}-Year Impact",
            f"{lifetime_sign}${abs(result.lifetime_cost_increase):,.0f}",
            delta="over life of mortgage",
            delta_color="off"
        )

# Visualization tabs
st.divider()
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Cost Breakdown",
    "🗺️ Regional Comparison",
    "🔥 Sensitivity Analysis",
    "📈 Premium vs Impact"
])

with tab1:
    col_a, col_b = st.columns([2, 1])

    with col_a:
        waterfall_fig = create_waterfall_chart(
            home_price=home_price,
            construction_cost=result.construction_cost,
            labor_cost=result.labor_cost,
            wage_increase=result.wage_increase,
            new_home_price=result.new_home_price
        )
        st.plotly_chart(waterfall_fig, use_container_width=True)

    with col_b:
        pie_fig = create_cost_breakdown_pie(
            construction_cost_share=construction_cost_share,
            labor_share=labor_share
        )
        st.plotly_chart(pie_fig, use_container_width=True)

        st.markdown("""
        **Key Insight:** Only the labor portion of construction costs
        (shown in red) is affected by a Davis-Bacon wage floor.
        The floor only increases costs where it's set *above* current
        market wages—otherwise it has no effect.
        """)

with tab2:
    # Calculate all scenarios
    scenario_results = DavisBaconCalculator.scenario_comparison(
        home_price=home_price,
        construction_cost_share=construction_cost_share,
        scenarios=SCENARIOS,
        interest_rate=mortgage_rate,
        years=mortgage_years
    )

    col_c, col_d = st.columns(2)

    with col_c:
        regional_fig = create_regional_comparison(scenario_results, SCENARIOS)
        st.plotly_chart(regional_fig, use_container_width=True)

    with col_d:
        mortgage_fig = create_mortgage_impact_chart(scenario_results, SCENARIOS)
        st.plotly_chart(mortgage_fig, use_container_width=True)

    # Scenario comparison table
    st.subheader("All Scenarios at a Glance")

    table_data = []
    for name, res in scenario_results.items():
        table_data.append({
            "Scenario": name,
            "Labor %": f"{res.labor_share*100:.0f}%",
            "Wage Premium": f"{res.wage_premium*100:+.0f}%",
            "Home Price Change": f"${res.price_increase_dollars:+,.0f}",
            "% Change": f"{res.price_increase_percent:+.2f}%",
            "Monthly Change": f"${res.monthly_payment_increase:+,.0f}",
            f"{mortgage_years}-Year Total": f"${res.lifetime_cost_increase:+,.0f}"
        })

    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

with tab3:
    st.markdown("""
    This heatmap shows how the **home price impact varies** based on different assumptions
    about labor's share of construction costs and the Davis-Bacon wage premium.

    **X marks** indicate key research-based scenarios.
    """)

    heatmap_type = st.radio(
        "Display as:",
        ["Percentage Change", "Dollar Amount"],
        horizontal=True
    )

    if heatmap_type == "Percentage Change":
        heatmap_fig = create_sensitivity_heatmap(
            home_price=home_price,
            construction_cost_share=construction_cost_share
        )
    else:
        heatmap_fig = create_dollar_sensitivity_heatmap(
            home_price=home_price,
            construction_cost_share=construction_cost_share
        )

    st.plotly_chart(heatmap_fig, use_container_width=True)

with tab4:
    line_fig = create_premium_impact_line_chart(
        home_price=home_price,
        construction_cost_share=construction_cost_share
    )
    st.plotly_chart(line_fig, use_container_width=True)

    st.markdown("""
    This chart shows how the **percentage increase in home price** varies with how far the
    Davis-Bacon wage floor is above current market rates.

    **Key observations:**
    - The relationship is linear: doubling the floor-to-market gap doubles the price impact
    - Higher labor shares amplify the impact of wage floors
    - **When the floor is below market wages (negative %)**, requiring Davis-Bacon has
      **no effect**—contractors already pay above the floor, so costs don't change
    - Cost increases only occur where the floor *raises* wages above what would otherwise be paid
    """)

# Methodology and sources
st.divider()
with st.expander("📚 Methodology & Sources"):
    st.markdown("""
    ### Calculation Formula

    ```
    Price_Impact = Home_Price × Construction_Share × Labor_Share × Wage_Premium
    ```

    ### Key Assumptions

    1. **Full pass-through**: All wage increases are passed to home buyers
    2. **Static analysis**: Does not account for:
       - Productivity changes from higher wages
       - Reduced worker turnover
       - Changes in contractor bidding behavior
       - Supply chain adjustments
    3. **Regional variation**: Actual impacts vary significantly by geography

    ### Research Sources

    | Source | Key Finding |
    |--------|-------------|
    | NAHB 2024 | Construction = 64.4% of home price |
    | AGM Financial | In right-to-work states, DB wages 8-24% below market |
    | Beacon Hill Institute | 20-22% wage premium, 7.2% cost increase |
    | EPI Review | 78% of peer-reviewed studies show no cost increase |
    | Construction Physics | Labor ≈ 50% of direct construction costs |

    ### Important Context

    Research on Davis-Bacon wage impacts is **highly contested**. Industry groups tend to find
    significant cost increases, while labor-affiliated researchers often find minimal impact.
    This tool allows you to explore the range of estimates and form your own conclusions.
    """)

    st.subheader("Full Source Links")
    for key, source in SOURCES.items():
        st.markdown(f"- [{source['title']}]({source['url']}): {source['finding']}")

# Footer
st.divider()
st.caption("""
**Disclaimer:** This tool is for educational and analytical purposes only.
Actual policy impacts depend on many factors not captured in this simplified model.
Parameter estimates are drawn from research studies with varying methodologies and potential biases.
""")
