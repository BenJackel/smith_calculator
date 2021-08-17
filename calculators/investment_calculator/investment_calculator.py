from datetime import date
import pandas as pd
import numpy as np


class InvestmentCalculator:
    def __init__(self, balance, dividend_yield, frequency, dividend_issue_date):
        self.balance = balance
        self.dividend_yield = dividend_yield
        self.frequency = frequency
        self.dividend_balance = 0.0
        self.dividend_issue_day = pd.to_datetime(dividend_issue_date).date()

    def __repr__(self):
        df = pd.DataFrame({"balance": [self.balance]})
        return repr(df)

    def buy(self, amount):
        if amount < 0:
            raise ValueError("Can't buy a negative amount")

        self.balance += amount
        return self

    def sell(self, amount):
        if amount < 0:
            raise ValueError("Can't sell a negative amount")
        if amount > self.balance:
            raise ValueError("Insufficient balance")

        self.balance -= amount
        return self

    @staticmethod
    def custom_date_range(start, end, freq, known_date):
        """
        Custom date range function
        Specifies a start and an end range. That must contain start, end
        Then, finds the next business day incase they land on a weekend

        For example, quarterly frequency
        start = 2021-08-10
        end = 2022-08-10
        2021-08-10, 2021-11-10, 2022-02-10, ..., 2022-08-10

        """
        day = known_date.day
        month_abbr = pd.to_datetime(known_date).strftime("%b")
        freqs = {
            "monthly": "m",
            "quarterly": f"Q-{month_abbr}",
            "semi-annually" "annualy": f"A-{month_abbr}",
        }
        date_range = pd.date_range(
            start=start, end=end + pd.DateOffset(years=1), freq=freqs.get(freq)
        )
        date_range = pd.Series(date_range).apply(lambda x: x + pd.DateOffset(day=day))
        date_range = date_range + 0 * pd.offsets.BDay()
        return date_range

    def next_dividend_date(self, current_date):
        this_date = pd.to_datetime(current_date).date()
        dividend_date = self.dividend_issue_day

        if this_date < dividend_date:
            start = this_date
            end = dividend_date
        else:
            start = dividend_date
            end = this_date

        dr = self.custom_date_range(
            start=start, end=end, freq=self.frequency, known_date=dividend_date
        )

        return dr[dr >= np.datetime64(this_date)].min().date()

    def issue_dividend(self, current_date):
        if pd.to_datetime(current_date).date() == self.next_dividend_date(current_date):
            self.dividend_balance += round(
                self.balance * self.dividend_yield / 100 / 12.0, 2
            )

        return self

    def withdraw_dividends(self, amount):
        if amount > self.dividend_balance:
            raise ValueError("Insufficient dividend balance.")
        if amount < 0:
            raise ValueError("amount must be greater than 0")

        self.dividend_balance -= amount

        return self


if __name__ == "__main__":

    investment = InvestmentCalculator(
        balance=120000,
        dividend_yield=10,
        frequency="monthly",
        dividend_issue_date="2021-10-10",
    )
