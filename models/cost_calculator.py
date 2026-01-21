"""Core calculation logic for Davis-Bacon wage impact on housing costs."""

from dataclasses import dataclass
from typing import Optional
import numpy as np


@dataclass
class CalculationResult:
    """Results from a Davis-Bacon impact calculation."""

    # Input values
    home_price: float
    construction_cost_share: float
    labor_share: float
    wage_premium: float

    # Calculated values
    construction_cost: float
    labor_cost: float
    wage_increase: float
    new_home_price: float
    price_increase_dollars: float
    price_increase_percent: float

    # Mortgage impacts (optional)
    monthly_payment_increase: Optional[float] = None
    lifetime_cost_increase: Optional[float] = None


class DavisBaconCalculator:
    """Calculator for Davis-Bacon prevailing wage impact on housing costs."""

    def __init__(
        self,
        home_price: float,
        construction_cost_share: float = 0.644,
        labor_share: float = 0.40,
        wage_premium: float = 0.15
    ):
        """
        Initialize calculator with parameters.

        Args:
            home_price: Base home price in dollars
            construction_cost_share: Construction costs as fraction of home price (0-1)
            labor_share: Labor costs as fraction of construction costs (0-1)
            wage_premium: Davis-Bacon wage premium over market wages (can be negative)
        """
        self.home_price = home_price
        self.construction_cost_share = construction_cost_share
        self.labor_share = labor_share
        self.wage_premium = wage_premium

    def calculate(self) -> CalculationResult:
        """
        Calculate the impact of Davis-Bacon wages on home price.

        Returns:
            CalculationResult with all computed values
        """
        # Step 1: Calculate construction cost portion
        construction_cost = self.home_price * self.construction_cost_share

        # Step 2: Calculate labor cost portion
        labor_cost = construction_cost * self.labor_share

        # Step 3: Calculate wage increase from Davis-Bacon
        wage_increase = labor_cost * self.wage_premium

        # Step 4: Calculate new home price
        new_home_price = self.home_price + wage_increase

        # Step 5: Calculate percentage increase
        price_increase_percent = (wage_increase / self.home_price) * 100

        return CalculationResult(
            home_price=self.home_price,
            construction_cost_share=self.construction_cost_share,
            labor_share=self.labor_share,
            wage_premium=self.wage_premium,
            construction_cost=construction_cost,
            labor_cost=labor_cost,
            wage_increase=wage_increase,
            new_home_price=new_home_price,
            price_increase_dollars=wage_increase,
            price_increase_percent=price_increase_percent
        )

    def calculate_with_mortgage(
        self,
        interest_rate: float = 0.07,
        years: int = 30
    ) -> CalculationResult:
        """
        Calculate impact including mortgage cost implications.

        Args:
            interest_rate: Annual mortgage interest rate (e.g., 0.07 for 7%)
            years: Mortgage term in years

        Returns:
            CalculationResult with mortgage impacts included
        """
        result = self.calculate()

        # Calculate monthly payment difference
        monthly_rate = interest_rate / 12
        num_payments = years * 12

        # Monthly payment formula: M = P * [r(1+r)^n] / [(1+r)^n - 1]
        def monthly_payment(principal: float) -> float:
            if monthly_rate == 0:
                return principal / num_payments
            factor = (1 + monthly_rate) ** num_payments
            return principal * (monthly_rate * factor) / (factor - 1)

        original_payment = monthly_payment(self.home_price)
        new_payment = monthly_payment(result.new_home_price)

        result.monthly_payment_increase = new_payment - original_payment
        result.lifetime_cost_increase = result.monthly_payment_increase * num_payments

        return result

    @staticmethod
    def sensitivity_analysis(
        home_price: float,
        construction_cost_share: float,
        labor_shares: np.ndarray,
        wage_premiums: np.ndarray
    ) -> np.ndarray:
        """
        Generate a 2D array of price increase percentages for sensitivity analysis.

        Args:
            home_price: Base home price
            construction_cost_share: Construction cost share (fixed)
            labor_shares: Array of labor share values to test
            wage_premiums: Array of wage premium values to test

        Returns:
            2D numpy array of price increase percentages
        """
        results = np.zeros((len(wage_premiums), len(labor_shares)))

        for i, premium in enumerate(wage_premiums):
            for j, labor in enumerate(labor_shares):
                calc = DavisBaconCalculator(
                    home_price=home_price,
                    construction_cost_share=construction_cost_share,
                    labor_share=labor,
                    wage_premium=premium
                )
                results[i, j] = calc.calculate().price_increase_percent

        return results

    @staticmethod
    def scenario_comparison(
        home_price: float,
        construction_cost_share: float,
        scenarios: dict,
        interest_rate: float = 0.07,
        years: int = 30
    ) -> dict:
        """
        Compare multiple scenarios and return results.

        Args:
            home_price: Base home price
            construction_cost_share: Construction cost share
            scenarios: Dict of scenario names to parameter dicts
            interest_rate: Mortgage interest rate
            years: Mortgage term

        Returns:
            Dict of scenario names to CalculationResult objects
        """
        results = {}

        for name, params in scenarios.items():
            if name == "Custom Settings":
                continue
            calc = DavisBaconCalculator(
                home_price=home_price,
                construction_cost_share=construction_cost_share,
                labor_share=params["labor_share"],
                wage_premium=params["wage_premium"]
            )
            results[name] = calc.calculate_with_mortgage(interest_rate, years)

        return results
