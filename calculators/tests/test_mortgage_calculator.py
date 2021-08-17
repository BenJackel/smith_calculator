import pytest
import pandas as pd
from calculators.mortgage_calculator.mortgage_calculator import MortgageCalculator


@pytest.fixture
def this_mortgage():
    return MortgageCalculator(
        principle=500000,
        equity_available=800000,
        amortization_months=25 * 12,
        interest_rate=2.5,
        heloc_interest_rate=3.0,
        payment_freqency="bi-weekly",
        last_payment_date="2021-08-10",
    )


def test_mortgage_payment_date():
    mortgage = MortgageCalculator(
        principle=500000,
        equity_available=500000 / 0.8,
        amortization_months=25 * 12,
        interest_rate=2.5,
        heloc_interest_rate=3.0,
        payment_freqency="monthly",
        last_payment_date="2021-08-10",
    )

    due_date = mortgage.mortgage_payment_date("2021-08-9")
    actual = pd.to_datetime("2021-08-10")
    assert due_date == actual

    due_date = mortgage.mortgage_payment_date("2021-08-10")
    actual = pd.to_datetime("2021-08-10")
    assert due_date == actual

    mortgage = MortgageCalculator(
        principle=500000,
        equity_available=500000 / 0.8,
        amortization_months=25 * 12,
        interest_rate=2.5,
        heloc_interest_rate=3.0,
        payment_freqency="bi-weekly",
        last_payment_date="2021-08-10",
    )

    due_date = mortgage.mortgage_payment_date("2021-08-9")
    actual = pd.to_datetime("2021-08-10")
    assert due_date == actual

    due_date = mortgage.mortgage_payment_date("2021-08-25")
    actual = pd.to_datetime("2021-09-07")
    assert due_date == actual

    mortgage = MortgageCalculator(
        principle=500000,
        equity_available=500000 / 0.8,
        amortization_months=25 * 12,
        interest_rate=2.5,
        heloc_interest_rate=3.0,
        payment_freqency="weekly",
        last_payment_date="2021-08-10",
    )

    due_date = mortgage.mortgage_payment_date("2021-08-9")
    actual = pd.to_datetime("2021-08-10")
    assert due_date == actual

    due_date = mortgage.mortgage_payment_date("2021-09-01")
    actual = pd.to_datetime("2021-09-07")
    assert due_date == actual


def test_heloc_payment_date(this_mortgage):
    mortgage = this_mortgage

    due_date = mortgage.heloc_payment_date("2021-08-10")
    actual = pd.to_datetime("2021-08-31")
    assert due_date == actual

    due_date = mortgage.heloc_payment_date("2021-08-31")
    actual = pd.to_datetime("2021-08-31")
    assert due_date == actual

    due_date = mortgage.heloc_payment_date("2100-02-10")
    actual = pd.to_datetime("2100-02-28")
    assert due_date == actual

    due_date = mortgage.heloc_payment_date("2000-02-10")
    actual = pd.to_datetime("2000-02-29")
    assert due_date == actual


def test_calculate_payment_amount():
    # Test monthly, bi-weekly, weekly, accelerated bi-weekly, accelerated weekly
    frequencies = [
        "monthly",
        "bi-weekly",
        "weekly",
        "accelerated bi-weekly",
        "accelerated weekly",
    ]
    actuals = [2239.83, 1033.77, 516.88, 1119.92, 559.96]
    for freq, actual in zip(frequencies, actuals):
        mortgage = MortgageCalculator(
            principle=500000,
            equity_available=500000 / 0.8,
            amortization_months=25 * 12,
            interest_rate=2.5,
            heloc_interest_rate=3.0,
            payment_freqency=freq,
            last_payment_date="2021-08-10",
        )
        predicted = mortgage.payment_amount
        assert predicted == actual


def test_calculate_heloc_credit_limit(this_mortgage):
    mortgage = this_mortgage
    assert mortgage.calculate_heloc_credit_limit() == 140000.0


def test_calculated_interest_and_principle():
    frequencies = [
        "monthly",
        "bi-weekly",
        "weekly",
        "accelerated bi-weekly",
        "accelerated weekly",
    ]
    interest_actuals = [1036.28, 478.28, 239.14, 478.02, 238.95]
    principle_actuals = [1203.55, 555.49, 277.74, 641.90, 321.01]
    for freq, act_interest, act_principle in zip(
        frequencies, interest_actuals, principle_actuals
    ):
        mortgage = MortgageCalculator(
            principle=500000,
            equity_available=500000 / 0.8,
            amortization_months=25 * 12,
            interest_rate=2.5,
            heloc_interest_rate=3.0,
            payment_freqency=freq,
            last_payment_date="2021-08-10",
        )
        pred_interest, pred_principle = mortgage.calculate_interest_and_principle()
        assert pred_interest == act_interest and pred_principle == act_principle


def test_make_regular_payment(this_mortgage):
    mortgage = this_mortgage
    mortgage.make_regular_payment()
    pred_principle = mortgage.principle
    pred_cred_limit = mortgage.credit_limit
    actual_principle = 500000 - 555.49
    actual_cred_limit = 140555.49
    assert pred_principle == actual_principle and pred_cred_limit == actual_cred_limit


def test_make_double_up_payment(this_mortgage):
    mortgage = this_mortgage
    mortgage.make_double_up_payment(500.0)
    pred_principle = mortgage.principle
    pred_cred_limit = mortgage.credit_limit
    actual_principle = 500000 - 500.0
    actual_cred_limit = 140500.00
    assert pred_principle == actual_principle and pred_cred_limit == actual_cred_limit

    with pytest.raises(ValueError):
        mortgage.make_double_up_payment(-10)

    with pytest.raises(ValueError):
        mortgage.make_double_up_payment(9000)


def test_make_lump_sum_payment(this_mortgage):
    mortgage = this_mortgage
    mortgage.make_lump_sum_payment(5000.0)
    pred_principle = mortgage.principle
    pred_cred_limit = mortgage.credit_limit
    actual_principle = 500000 - 5000.0
    actual_cred_limit = 145000.00
    assert pred_principle == actual_principle and pred_cred_limit == actual_cred_limit

    with pytest.raises(ValueError):
        mortgage.make_lump_sum_payment(-10)

    with pytest.raises(ValueError):
        mortgage.make_lump_sum_payment(100000)


def test_draw_from_heloc(this_mortgage):
    mortgage = this_mortgage
    mortgage.draw_from_heloc(5000.0)
    pred_cred_limit = mortgage.credit_limit
    pred_cred_balance = mortgage.credit_balance
    pred_cred_available = mortgage.credit_available
    actual_cred_limit = 140000.00
    actual_cred_balance = 5000.0
    actual_cred_available = 140000 - 5000
    assert pred_cred_limit == actual_cred_limit
    assert pred_cred_balance == actual_cred_balance
    assert pred_cred_available == actual_cred_available

    with pytest.raises(ValueError):
        mortgage.draw_from_heloc(-10)

    with pytest.raises(ValueError):
        mortgage.draw_from_heloc(200000)

    # Make sure we can draw twice
    mortgage.draw_from_heloc(100000.0)
    pred_cred_limit = mortgage.credit_limit
    pred_cred_balance = mortgage.credit_balance
    pred_cred_available = mortgage.credit_available
    actual_cred_limit = 140000.00
    actual_cred_balance = 105000.0
    actual_cred_available = 140000 - 105000
    assert pred_cred_limit == actual_cred_limit
    assert pred_cred_balance == actual_cred_balance
    assert pred_cred_available == actual_cred_available


def test_make_heloc_payment(this_mortgage):
    mortgage = this_mortgage
    mortgage.draw_from_heloc(10000.0)
    mortgage.make_heloc_payment(5000.0)
    pred_cred_limit = mortgage.credit_limit
    pred_cred_balance = mortgage.credit_balance
    pred_cred_available = mortgage.credit_available
    actual_cred_limit = 140000.00
    actual_cred_balance = 5000.0
    actual_cred_available = 140000 - 5000
    assert pred_cred_limit == actual_cred_limit
    assert pred_cred_balance == actual_cred_balance
    assert pred_cred_available == actual_cred_available

    with pytest.raises(ValueError):
        mortgage.make_heloc_payment(-10)

    with pytest.raises(ValueError):
        mortgage.make_heloc_payment(200000)


def test_capitalize_heloc_interest(this_mortgage):
    mortgage = this_mortgage
    mortgage.capitalize_heloc_interest()
    assert mortgage.credit_balance == 0

    mortgage.draw_from_heloc(10000.0)
    mortgage.capitalize_heloc_interest()

    pred_cred_limit = mortgage.credit_limit
    pred_cred_balance = mortgage.credit_balance
    pred_cred_available = mortgage.credit_available
    actual_cred_limit = 140000.00
    actual_cred_balance = 10025.0
    actual_cred_available = 140000 - 10025
    assert pred_cred_limit == actual_cred_limit
    assert pred_cred_balance == actual_cred_balance
    assert pred_cred_available == actual_cred_available

    mortgage.draw_from_heloc(129900)
    with pytest.raises(ValueError):
        mortgage.capitalize_heloc_interest()
