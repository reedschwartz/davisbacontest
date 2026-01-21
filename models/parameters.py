"""Evidence-based parameters for Davis-Bacon wage impact calculations."""

# Default parameters based on research
DEFAULT_PARAMS = {
    "home_price": 665298,  # 2024 NAHB average
    "construction_cost_share": 0.644,  # 64.4% per NAHB 2024
    "labor_share": 0.40,  # 40% of construction costs
    "wage_premium": 0.15,  # 15% national average estimate
    "mortgage_rate": 0.07,  # 7% interest rate
    "mortgage_years": 30,
}

# Parameter ranges for sliders
PARAM_RANGES = {
    "home_price": {"min": 200000, "max": 2000000, "step": 10000},
    "construction_cost_share": {"min": 0.50, "max": 0.75, "step": 0.01},
    "labor_share": {"min": 0.25, "max": 0.55, "step": 0.01},
    "wage_premium": {"min": -0.15, "max": 0.50, "step": 0.01},
    "mortgage_rate": {"min": 0.03, "max": 0.12, "step": 0.005},
}

# Pre-defined scenarios based on research
SCENARIOS = {
    "U.S. National Average": {
        "labor_share": 0.40,
        "wage_premium": 0.15,
        "description": "DB floor ~13-15% above market wages on average nationwide",
        "source": "DOL methodology studies"
    },
    "Texas, Florida & Other Right-to-Work States": {
        "labor_share": 0.35,
        "wage_premium": -0.08,
        "description": "DB floor is 8-24% BELOW market—floor has no effect, costs unchanged",
        "source": "AGM Financial 2024 research"
    },
    "New York, California & High-Union Metros": {
        "labor_share": 0.45,
        "wage_premium": 0.35,
        "description": "DB floor up to 36% above market in heavily unionized metros",
        "source": "Center for Government Research (NY study)"
    },
    "Mid-Range Estimate": {
        "labor_share": 0.40,
        "wage_premium": 0.20,
        "description": "Beacon Hill Institute's estimate of 20-22% wage premium",
        "source": "Beacon Hill Institute"
    },
    "Low-End Estimate": {
        "labor_share": 0.30,
        "wage_premium": 0.07,
        "description": "Conservative lower bound assuming 7% construction cost impact",
        "source": "Beacon Hill Institute (cost impact study)"
    },
    "High-End Estimate": {
        "labor_share": 0.50,
        "wage_premium": 0.40,
        "description": "Upper bound combining highest research estimates",
        "source": "Combined upper estimates from multiple studies"
    },
    "Custom Settings": {
        "labor_share": 0.40,
        "wage_premium": 0.15,
        "description": "Adjust all parameters manually using the sliders below",
        "source": "User-defined"
    }
}

# Sources with citations
SOURCES = {
    "nahb_2024": {
        "title": "Cost of Constructing a Home in 2024",
        "url": "https://eyeonhousing.org/2025/01/cost-of-constructing-a-home-in-2024/",
        "finding": "Construction costs = 64.4% of home sale price"
    },
    "agm_financial": {
        "title": "How Davis Bacon Wages Impact Multifamily Construction",
        "url": "https://www.agmfinancial.com/how-davis-bacon-wages-impact-multifamily-construction-enlightening-new-research/",
        "finding": "In right-to-work states, DB wages are 8.5-23.6% below market"
    },
    "beacon_hill": {
        "title": "Davis-Bacon Studies (ABC Summary)",
        "url": "https://www.abc.org/Portals/1/ABC%20Prevailing%20Wage%20Davis%20Bacon%20Studies%20Summary%20Updated%20March%202022%20031122.pdf",
        "finding": "20-22% wage premium, 7.2% construction cost increase"
    },
    "epi": {
        "title": "Prevailing Wages and Government Contracting Costs",
        "url": "https://www.epi.org/publication/bp215/",
        "finding": "78% of peer-reviewed studies show no cost increase"
    },
    "construction_physics": {
        "title": "Construction Cost Breakdown and Partial Industrialization",
        "url": "https://www.construction-physics.com/p/construction-cost-breakdown-and-partial",
        "finding": "Labor ~50% of direct construction costs"
    }
}
