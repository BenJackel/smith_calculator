import pandas as pd
import calendar


class MortgageCalculator:
    def __init__(
        self,
        principle,
        equity_available,
        amortization_months,
        interest_rate,
        heloc_interest_rate,
        payment_freqency,
        last_payment_date,
        payment_amount=None,
    ):
        self.principle = principle
        self.equity_available = equity_available
        self.amortization_months = amortization_months
        self.interest_rate = interest_rate
        self.heloc_interest_rate = heloc_interest_rate
        self.payment_frequency = payment_freqency
        self.last_payment_date = pd.to_datetime(last_payment_date)
        if payment_amount is not None:
            self.payment_amount = payment_amount
        else:
            self.payment_amount = self.calculate_payment_amount()
        self.credit_limit = self.calculate_heloc_credit_limit()
        self.credit_balance = 0.0
        self.credit_available = self.calculate_credit_available()

    payment_periods = {
        "monthly": {"num": 12, "denom": 12},
        "bi-weekly": {"num": 12, "denom": 26},
        "weekly": {"num": 12, "denom": 52},
        "accelerated bi-weekly": {"num": 13, "denom": 26},
        "accelerated weekly": {"num": 13, "denom": 52},
    }

    def __repr__(self):
        df = self.data()
        return repr(df)

    def next_payment_date(self):
        return self.last_payment_date + pd.Timedelta("14 days")

    def data(self):
        df = pd.DataFrame(
            {
                "principle": [self.principle],
                "interest_rate": self.interest_rate,
                "payment_amount": self.payment_amount,
                "next_payment_date": self.next_payment_date(),
            }
        )
        return df

    def calculate_payment_amount(self):
        # Calculate the monthly from the amortization months
        # Canada uses semi-annual compounding, so we need to get the effective rate
        # P * [(i (i + 1) ^ n) / ((i + 1) ^ n - 1)]
        # P = principle
        # i = monthly interest rate
        # n = number of amortization months
        P = self.principle
        semi_annual_rate = self.interest_rate / 100.0 / 2
        # pif = monthly interest factor
        pif = ((1 + semi_annual_rate) ** 2) ** (1 / 12) - 1
        n = self.amortization_months
        payment = P * pif
        payment = payment / (1 - (1 + pif) ** (-n))

        num = self.payment_periods[self.payment_frequency]["num"]
        denom = self.payment_periods[self.payment_frequency]["denom"]
        return round(payment * num / denom, 2)

    def calculate_heloc_credit_limit(self):
        return round(self.equity_available - self.principle, 2)

    def calculate_credit_available(self):
        return self.credit_limit - self.credit_balance

    def calculate_interest_and_principle(self):
        semi_annual_rate = self.interest_rate / 100.0 / 2
        # pif = monthly interest factor
        denom = self.payment_periods[self.payment_frequency]["denom"]
        if "accelerated" in self.payment_frequency:
            pif = ((1 + semi_annual_rate) ** 2) ** (1 / denom) - 1
        else:
            pif = ((1 + semi_annual_rate) ** 2) ** (1 / 12) - 1
            num = self.payment_periods[self.payment_frequency]["num"]
            pif = pif * num / denom
        payment = self.payment_amount
        interest_payment = round(pif * self.principle, 2)
        principle_payment = round(self.payment_amount - interest_payment, 2)
        return interest_payment, principle_payment

    def make_regular_payment(self):
        interest_payment, principle_payment = self.calculate_interest_and_principle()
        self.principle -= principle_payment
        self.credit_limit = self.calculate_heloc_credit_limit()
        return self

    def make_double_up_payment(self, amount=0):
        # Need to check if amount > 0 and < payment_amount
        if amount < 0 or amount > self.payment_amount:
            raise ValueError("Amount needs to be > 0 and < payment amount")

        self.principle -= amount
        self.credit_limit = self.calculate_heloc_credit_limit()
        return self

    def make_lump_sum_payment(self, amount=0):
        # Need to check if amount > 0 and < 10% of equity
        if amount < 0 or amount > self.equity_available * 0.1:
            raise ValueError("Amount needs to be > 0 and < 10% of equity")

        self.principle -= amount
        self.credit_limit = self.calculate_heloc_credit_limit()
        return self

    def draw_from_heloc(self, amount):
        if amount > self.credit_available:
            raise ValueError("Can't draw more than available credit")
        if amount < 0:
            raise ValueError("Can't draw negative funds")

        self.credit_balance += amount
        self.credit_available = self.calculate_credit_available()
        return self

    def make_heloc_payment(self, amount):
        if amount < 0:
            raise ValueError("Can't make a negative payment")
        if amount > self.credit_balance:
            raise ValueError("Can't make a payment larger than the balance")

        self.credit_balance -= amount
        self.credit_available = self.calculate_credit_available()
        return self

    def capitalize_heloc_interest(self):
        interest = self.heloc_interest_rate / 100 / 12.0 * self.credit_balance
        if interest > self.credit_available:
            raise ValueError(
                "Can not capitalize interest. Not enough credit available."
            )

        self.draw_from_heloc(interest)
        return self


if __name__ == "__main__":

    frequencies = [
        "monthly",
        "bi-weekly",
        "weekly",
        "accelerated bi-weekly",
        "accelerated weekly",
    ]

    for freq in frequencies:

        mortgage = MortgageCalculator(
            principle=500000,
            equity_available=500000 / 0.8,
            amortization_months=25 * 12,
            interest_rate=2.5,
            heloc_interest_rate=3.0,
            payment_freqency=freq,
            last_payment_date="2021-08-10",
        )

        print(
            freq, mortgage.payment_amount, mortgage.calculate_interest_and_principle()
        )
