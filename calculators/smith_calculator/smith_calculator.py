from numpy import divide
import pandas as pd
from calculators.mortgage_calculator.mortgage_calculator import MortgageCalculator
from calculators.investment_calculator.investment_calculator import InvestmentCalculator


class SmithCalculator:
    def __init__(
        self,
        mortgage,
        investment,
        start_date,
        n_steps,
        marginal_tax_rate,
        dividend_tax_rate,
    ):
        self.mortgage = mortgage
        self.investment = investment
        self.start_date = pd.to_datetime(start_date)
        self.n_steps = n_steps
        self.marginal_tax_rate = marginal_tax_rate
        self.dividend_tax_rate = dividend_tax_rate

    # Refunds come out in March
    tax_refund_month = 3

    def simulate(self):
        date_range = pd.date_range(
            start=self.start_date, periods=self.n_steps, freq="D"
        )

        tracker = pd.DataFrame(
            {
                "date": [self.start_date],
                "mort_interest_paid": 0,
                "mort_principle_paid": 0,
                "mort_principle": self.mortgage.principle,
                "interest_capitalized": 0,
                "credit_limit": self.mortgage.credit_limit,
                "credit_available": self.mortgage.credit_available,
                "credit_balance": self.mortgage.credit_balance,
                "investment_balance": self.investment.balance,
                "dividends": 0,
                "out_of_pocket": 0,
                "event": True,
            }
        )

        cash = 0
        new_credit = 0

        # print(f"Start Date: {self.start_date.date()}")
        for date in date_range:

            principle = 0
            interest = 0
            heloc_interest = 0
            event = False
            dividends = 0

            if date.month >= 1 and date.month < 3:
                tax_return_available = True

            mortgage_due_date = self.mortgage.mortgage_payment_date(date)
            if date == mortgage_due_date:
                interest, principle = self.mortgage.calculate_interest_and_principle()
                self.mortgage.make_regular_payment()
                # print(f"\t{date.date()}: Make mortgage payment")
                new_credit += principle
                event = True

            heloc_due_date = self.mortgage.heloc_payment_date(date)
            if date == heloc_due_date:
                # print(f"\t{date.date()}: Capitalize HELOC interest")
                if self.mortgage.credit_available > 2000000:
                    heloc_interest = self.mortgage.capitalize_heloc_interest()
                else:
                    heloc_interest = self.mortgage.heloc_interest_due()
                    self.mortgage.make_heloc_payment(heloc_interest)
                    cash -= heloc_interest
                event = True

            self.investment.issue_dividend(date)
            div_balance = self.investment.dividend_balance

            if div_balance > 0:
                # print(f"\t{date}: Dividend Issued")
                self.investment.withdraw_dividends(div_balance)
                # print(f"\t{date}: Withdraw Dividend ${div_balance}")
                dividends += div_balance
                cash += div_balance
                event = True

            if date.month == 3 and tax_return_available:
                # Tax return calculated as
                # Marginal tax rate * total interest paid this year
                tax_rate = self.marginal_tax_rate / 100
                div_tax_rate = self.dividend_tax_rate / 100
                tax_start = date - pd.DateOffset(years=1, month=1, day=1)
                tax_end = tax_start + pd.DateOffset(month=12, day=31)
                interest_paid = tracker[tracker["date"].between(tax_start, tax_end)][
                    "interest_capitalized"
                ].sum()
                tax_return = tax_rate * interest_paid
                # subtract dividend tax rate * total dividends
                dividends_earned = tracker[tracker["date"].between(tax_start, tax_end)][
                    "dividends"
                ].sum()
                dividend_tax = dividends_earned * 1.38 * div_tax_rate
                tax_return -= dividend_tax
                tax_return = round(tax_return, 2)
                if tax_return > 0:
                    amt = tax_return + max(0, cash)
                    self.mortgage.make_lump_sum_payment(amt)
                    new_credit += amt
                else:
                    cash -= tax_return
                tax_return_available = False
                event = True
                print(f"{date}: Tax Return - ${tax_return}")
                tax_return = 0
                cash = min(cash, 0)
            if cash > 0:
                amt = min(max(0, cash), self.mortgage.payment_amount)
                self.mortgage.make_double_up_payment(amt)
                # print(f"\t{date}: Double up mortgage payment ${cash}")
                new_credit += amt
                cash -= amt
                event = True

            div_balance = self.investment.dividend_balance

            new_credit_available = (
                self.mortgage.credit_limit - tracker["credit_limit"].iloc[-1]
            )

            # if new_credit_available > 0:
            if self.mortgage.credit_available > 2000 and new_credit > 0:
                if self.mortgage.credit_available > 10000:
                    new_credit += 1000
                # print(f"\t{date}: Draw from HELOC and invest")
                self.mortgage.draw_from_heloc(new_credit)
                self.investment.buy(new_credit)
                new_credit = 0
                event = True

            if not event:
                continue

            if self.mortgage.principle <= 5000:
                break

            new_row = pd.DataFrame(
                {
                    "date": [date],
                    "mort_interest_paid": interest,
                    "mort_principle_paid": principle,
                    "mort_principle": self.mortgage.principle,
                    "interest_capitalized": heloc_interest,
                    "credit_limit": self.mortgage.credit_limit,
                    "credit_available": self.mortgage.credit_available,
                    "credit_balance": self.mortgage.credit_balance,
                    "investment_balance": self.investment.balance,
                    "dividends": dividends,
                    "out_of_pocket": cash,
                    "event": event,
                }
            )
            tracker = tracker.append(new_row)

        return tracker.drop_duplicates()


if __name__ == "__main__":

    mortgage = MortgageCalculator(
        principle=486888.03,
        equity_available=795000,
        amortization_months=329,
        interest_rate=2.74,
        heloc_interest_rate=2.95,
        payment_freqency="bi-weekly",
        last_payment_date="2021-08-10",
        # payment_amount=969.58,
        payment_amount=1100,
    )

    investment = InvestmentCalculator(0, 4.45, "monthly", "2021-08-15")

    # mortgage.make_lump_sum_payment(35000)
    mortgage.draw_from_heloc(140000)
    investment.buy(140000)

    smith = SmithCalculator(
        mortgage=mortgage,
        investment=investment,
        start_date="2021-08-17",
        # n_steps=365 * 25,
        n_steps=365 * 25,
        marginal_tax_rate=40.5,
        dividend_tax_rate=(40.5 - 15.0198 - 11),  # Marginal, federal, provincial
    )

    tracker = smith.simulate()
