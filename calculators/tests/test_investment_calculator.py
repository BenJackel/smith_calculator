import pytest
import pandas as pd
from calculators.investment_calculator.investment_calculator import InvestmentCalculator


def test_buy():
    investment = InvestmentCalculator(
        balance=0.0,
        dividend_yield=10.0,
        frequency="monthly",
        dividend_issue_date="2021-10-10",
    )
    investment.buy(10000)
    predicted = investment.balance
    actual = 10000
    assert predicted == actual

    # Buy again
    investment.buy(5000)
    predicted = investment.balance
    actual = 15000
    assert predicted == actual

    # Try to buy a negative amount
    with pytest.raises(ValueError):
        investment.buy(-100.0)

    # Buy 0 should do nothing
    investment.buy(0)
    predicted = investment.balance
    actual = 15000
    assert predicted == actual


def test_sell():
    investment = InvestmentCalculator(
        balance=10000.0,
        dividend_yield=10.0,
        frequency="monthly",
        dividend_issue_date="2021-10-10",
    )

    investment.sell(5000)
    predicted = investment.balance
    actual = 5000
    assert predicted == actual

    # Sell again
    investment.sell(1000)
    predicted = investment.balance
    actual = 4000
    assert predicted == actual

    # Try to buy a negative amount
    with pytest.raises(ValueError):
        investment.sell(-100.0)

    # Buy 0 should do nothing
    investment.sell(0)
    predicted = investment.balance
    actual = 4000
    assert predicted == actual

    # Try to sell more than there is
    with pytest.raises(ValueError):
        investment.sell(5000)


def test_next_dividend_date():
    investment = InvestmentCalculator(
        balance=100000.0,
        dividend_yield=10.0,
        frequency="monthly",
        dividend_issue_date="2021-10-10",
    )

    next_date = investment.next_dividend_date("2021-08-09")
    actual = pd.to_datetime("2021-08-10").date()
    assert next_date == actual

    next_date = investment.next_dividend_date("2021-08-10")
    actual = pd.to_datetime("2021-08-10").date()
    assert next_date == actual

    next_date = investment.next_dividend_date("2021-08-11")
    actual = pd.to_datetime("2021-09-10").date()
    assert next_date == actual

    investment = InvestmentCalculator(
        balance=100000.0,
        dividend_yield=10.0,
        frequency="quarterly",
        dividend_issue_date="2021-10-10",
    )

    next_date = investment.next_dividend_date("2021-08-09")
    actual = pd.to_datetime("2021-10-11").date()  # Oct 10th is a sunday
    assert next_date == actual

    next_date = investment.next_dividend_date("2021-10-10")
    actual = pd.to_datetime("2021-10-11").date()
    assert next_date == actual

    next_date = investment.next_dividend_date("2021-11-11")
    actual = pd.to_datetime("2022-01-10").date()
    assert next_date == actual


def test_issue_dividend():
    investment = InvestmentCalculator(
        balance=120000.0,
        dividend_yield=10.0,
        frequency="monthly",
        dividend_issue_date="2021-10-10",
    )

    investment.issue_dividend("2021-08-09")
    balance = investment.dividend_balance
    actual = 0.0
    assert balance == actual

    investment.issue_dividend("2021-08-10")
    balance = investment.dividend_balance
    actual = 1000.0
    assert balance == actual

    investment.issue_dividend("2021-08-11")
    balance = investment.dividend_balance
    actual = 1000.0
    assert balance == actual

    investment.issue_dividend("2021-09-10")
    balance = investment.dividend_balance
    actual = 2000.0
    assert balance == actual

    investment.issue_dividend("2021-10-11")
    balance = investment.dividend_balance
    actual = 3000.0
    assert balance == actual


def test_withdraw_dividends():
    investment = InvestmentCalculator(
        balance=120000.0,
        dividend_yield=10.0,
        frequency="monthly",
        dividend_issue_date="2021-10-10",
    )

    investment.issue_dividend("2021-10-11")

    investment.withdraw_dividends(10)
    balance = investment.dividend_balance
    actual = 990
    assert balance == actual

    with pytest.raises(ValueError):
        investment.withdraw_dividends(-100)

    with pytest.raises(ValueError):
        investment.withdraw_dividends(10000)
