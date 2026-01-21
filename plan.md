# Davis-Bacon Prevailing Wage Impact Calculator

## Overview
A Python + Streamlit application to calculate and visualize how requiring Davis-Bacon prevailing wages on all federally guaranteed mortgages would affect housing costs.

---

## Evidence-Based Parameters (from Research)

### 1. Labor Cost as Percentage of Construction Costs

| Construction Type | Labor % | Materials % | Source |
|-------------------|---------|-------------|--------|
| New residential (low estimate) | 30% | 50-55% | Industry benchmarks |
| New residential (mid estimate) | 40% | 45-50% | Craftsman data |
| New residential (high estimate) | 50% | 40-45% | Construction Physics |
| High-rise multifamily | 30-40% | 60-70% | Industry data |

**Default range for model: 30% - 50%** with default value of 40%

### 2. Davis-Bacon Wage Premium Over Market Rates

| Estimate Source | Premium | Notes |
|-----------------|---------|-------|
| DOL methodology studies | 13% | Average across occupations |
| Beacon Hill Institute | 20-22% | Compared to BLS OES data |
| Beacon Hill (cost impact) | 7.2% | Impact on total construction cost |
| New York State (CGR) | 36% | High-union metro regions |
| West Virginia study | 74% | Adjusted figures, rural state |
| Right-to-work states | -8.5% to -23.6% | DB wages often *below* market |

**Default range for model: -10% to +40%** (to capture regional variation)
**National average default: 15%**

### 3. Construction Cost as % of Home Price

- **2024 NAHB data: 64.4%** of home sale price is construction costs
- Remaining: lot (13.7%), profit (11%), overhead (5.7%), other (5.2%)

---

## Program Architecture

```
davis-bacon-calculator/
├── app.py                 # Main Streamlit application
├── models/
│   ├── __init__.py
│   ├── cost_calculator.py # Core calculation logic
│   └── parameters.py      # Evidence-based parameter definitions
├── visualizations/
│   ├── __init__.py
│   ├── charts.py          # Plotly/matplotlib chart generators
│   └── sensitivity.py     # Sensitivity analysis visualizations
├── data/
│   └── defaults.json      # Default parameter values with citations
├── requirements.txt
└── README.md
```

---

## Core Calculation Model

### Formula

```
Housing_Cost_Increase = Construction_Cost_Share × Labor_Share × Wage_Premium

Where:
- Construction_Cost_Share = 0.644 (64.4% of home price, from NAHB 2024)
- Labor_Share = variable (30% to 50% of construction costs)
- Wage_Premium = variable (-10% to +40% over market wages)
```

### Example Calculation

For a $665,298 home (2024 NAHB average):
- Construction costs: $665,298 × 0.644 = $428,452
- Labor costs at 40%: $428,452 × 0.40 = $171,381
- With 15% wage premium: $171,381 × 0.15 = $25,707 increase
- **Percentage home price increase: 3.86%**

---

## Streamlit Application Features

### 1. Input Panel (Sidebar)
- **Home Price**: Slider or input ($200,000 - $2,000,000)
- **Construction Cost Share**: Slider (50% - 75%, default 64.4%)
- **Labor Share of Construction**: Slider (25% - 55%, default 40%)
- **Davis-Bacon Wage Premium**: Slider (-10% to +50%, default 15%)
- **Preset scenarios**: Dropdown for regional presets (Right-to-work, Union-heavy, National average)

### 2. Results Display
- Dollar amount increase in home cost
- Percentage increase in home cost
- Monthly mortgage payment increase (at configurable interest rate)
- Lifetime mortgage cost increase (30-year)

### 3. Visualizations

#### a) Sensitivity Heatmap
- X-axis: Labor share (30-50%)
- Y-axis: Wage premium (-10% to +40%)
- Color: % increase in home cost
- Helps identify which parameter combinations have biggest impact

#### b) Regional Comparison Bar Chart
- Bars for different scenarios:
  - Right-to-work states (low/negative premium)
  - Mixed states (moderate premium)
  - High-union states (high premium)

#### c) Cost Breakdown Waterfall Chart
- Base home price
- Construction costs portion
- Labor costs portion
- Davis-Bacon premium impact
- Final adjusted price

#### d) Interactive Line Chart
- X-axis: Wage premium percentage
- Multiple lines for different labor share assumptions
- Y-axis: Total cost increase

### 4. Scenario Comparison Table
- Side-by-side comparison of multiple parameter combinations
- Export to CSV functionality

---

## Parameter Presets (Evidence-Based)

```python
SCENARIOS = {
    "National Average": {
        "labor_share": 0.40,
        "wage_premium": 0.15,
        "description": "Based on average DOL wage determination premium"
    },
    "Right-to-Work State": {
        "labor_share": 0.35,
        "wage_premium": -0.10,
        "description": "DB wages often below market in these states"
    },
    "High-Union Metro (NY, CA)": {
        "labor_share": 0.45,
        "wage_premium": 0.35,
        "description": "Based on CGR New York study findings"
    },
    "Moderate Premium": {
        "labor_share": 0.40,
        "wage_premium": 0.20,
        "description": "Beacon Hill Institute estimate"
    },
    "Conservative Estimate": {
        "labor_share": 0.30,
        "wage_premium": 0.07,
        "description": "Lower bound estimates"
    },
    "High Impact Estimate": {
        "labor_share": 0.50,
        "wage_premium": 0.40,
        "description": "Upper bound for sensitivity analysis"
    }
}
```

---

## Key Assumptions & Limitations (To Display in App)

1. **Assumes full pass-through**: All wage increases passed to home buyers
2. **Does not account for**:
   - Potential productivity improvements from higher wages
   - Reduced worker turnover costs
   - Changes in contractor bidding behavior
   - Supply chain adjustments
3. **Regional variation**: Actual impacts vary significantly by geography
4. **Data sources**: Mix of industry surveys, academic studies, and government data

---

## Implementation Plan

### Phase 1: Core Calculator
1. Create `cost_calculator.py` with basic formula
2. Create `parameters.py` with evidence-based defaults
3. Unit tests for calculation accuracy

### Phase 2: Streamlit UI
1. Basic app layout with sidebar inputs
2. Results display cards
3. Parameter presets dropdown

### Phase 3: Visualizations
1. Sensitivity heatmap (Plotly)
2. Regional comparison bar chart
3. Cost breakdown waterfall
4. Interactive line chart

### Phase 4: Polish
1. Methodology documentation in-app
2. Export functionality
3. Mobile-responsive layout
4. Citation links

---

## Sources

1. [NAHB Cost of Constructing a Home 2024](https://eyeonhousing.org/2025/01/cost-of-constructing-a-home-in-2024/)
2. [AGM Financial - Davis Bacon Impact on Multifamily](https://www.agmfinancial.com/how-davis-bacon-wages-impact-multifamily-construction-enlightening-new-research/)
3. [EPI - Prevailing Wages and Government Contracting Costs](https://www.epi.org/publication/bp215/)
4. [ABC - Davis-Bacon Studies Summary](https://www.abc.org/Portals/1/ABC%20Prevailing%20Wage%20Davis%20Bacon%20Studies%20Summary%20Updated%20March%202022%20031122.pdf)
5. [Montana Prevailing Wage Study 2021](https://archive.legmt.gov/content/Committees/Interim/2021-2022/Local-Gov/21_Nov/DuncanReport_MontanaPrevailingWageStudy2021.pdf)
6. [Construction Physics - Cost Breakdown](https://www.construction-physics.com/p/construction-cost-breakdown-and-partial)
