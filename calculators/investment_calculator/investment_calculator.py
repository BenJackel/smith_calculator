import pandas as pd


class InvestmentCalculator:
    def __init__(self, balance, dividend_yield, frequency):
        self.balance = balance
        self.dividend_yield = dividend_yield
        self.frequency = frequency

    def __repr__(self):
        df = pd.DataFrame({"balance": [self.balance]})
        return repr(df)

    def buy(self, amount):
        return self

    def sell(self, amount):
        return self

    def extract_dividends(self, amount):
        return self
