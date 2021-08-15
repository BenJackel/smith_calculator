import pandas as pd
from calculators.mortgage_calculator.mortgage_calculator import MortgageCalculator
from calculators.investment_calculator.investment_calculator import InvestmentCalculator


class SmithCalculator:
    def __init__(self, mortgage, investment, start_date, frequency):
        self.mortgage = mortgage
        self.investment = investment
        self.start_date = pd.to_datetime(start_date)
        self.frequency = frequency
        self.current_step = pd.to_datetime(start_date)

    # Refunds come out in March
    tax_refund_month = 3

    @staticmethod
    def end_of_month(date):
        year = (date + pd.DateOffset(months=1)).year
        month = (date + pd.DateOffset(months=1)).month
        return pd.Timestamp(year=year, month=month, day=1) - pd.DateOffset(days=1)

    def timestep(self):
        heloc_due_date = self.end_of_month(self.current_step)

        # Logic is:
        # If a mortgage payment is due, make_regular_payment
        # If heloc interest is due (end of month), capitalize_interest
        # If there are dividends, make a double_up_payment
        # If there are tax refunds available (in March), make a lump_sum
        # If there is available heloc_credit_balance, draw -> buy
        return self


if __name__ == "__main__":

    mortgage = MortgageCalculator(
        principle=500000,
        amortization_months=333,
        interest_rate=2.75,
        heloc_interest_rate=1.0,
        payment_freqency="bi-weekly",
        last_payment_date="2021-08-12",
        payment_amount=1000.0,
    )

    investment = InvestmentCalculator(100000, 4.45, "monthly")

    smith = SmithCalculator(
        mortgage=mortgage,
        investment=investment,
        start_date="2021-08-14",
        frequency="bi-weekly",
    )
