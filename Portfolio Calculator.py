# -*- coding: utf-8 -*-
"""
Created on Thu Jan 22 20:46:49 2026

@author: erika
"""

import matplotlib.pyplot as plt

# =========================
# Core assumptions
# =========================

base_salary = 32000
years = 40
start_age = 22

growth_rate = 0.06
inflation = 0.03

# =========================
# Investment assumptions
# =========================

pension_base = 2000
isa_base = 20000
cash_base = 11000
lisa_base = 0

pension_rate = 0.08
isa_rate = 0.11
cash_rate = 0.045
lisa_rate = 0.07

# Contribution rules
pension_contribution_rate = 0.15
isa_contribution_rate = 0.15
lisa_max_contribution = 4000
lisa_bonus_rate = 0.25

# =========================
# Property assumptions
# =========================

property_price_start = 170000
deposit_rate = 0.10
house_price_growth = 0.05
mortgage_rate = 0.045
mortgage_rate_real = (1 + mortgage_rate) / (1 + inflation) - 1
mortgage_term = 30

# =========================
# Net pay function
# =========================

def net_pay(gross):
    personal_allowance = 12570
    basic_limit = 50270
    NI_lower = 12570
    NI_upper = 50270

    basic_rate = 0.20
    NI_main_rate = 0.08
    NI_upper_rate = 0.02

    loan_threshold = 28470
    loan_rate = 0.09

    pension_contrib = 0.05 * gross
    taxable = max(0, gross - pension_contrib)

    # Income tax
    if taxable <= personal_allowance:
        tax = 0
    else:
        tax = min(taxable - personal_allowance, basic_limit - personal_allowance) * basic_rate

    # NI
    if taxable <= NI_lower:
        ni = 0
    elif taxable <= NI_upper:
        ni = (taxable - NI_lower) * NI_main_rate
    else:
        ni = (NI_upper - NI_lower) * NI_main_rate + (taxable - NI_upper) * NI_upper_rate

    # Student loan
    loan = max(0, (taxable - loan_threshold) * loan_rate)

    net = gross - pension_contrib - tax - ni - loan
    return net

# =========================
# Tracking lists (year 0)
# =========================

nominal_salary = [base_salary]
real_salary = [base_salary]
net_salary = [net_pay(base_salary)]

pension = [pension_base]
isa = [isa_base]
cash = [cash_base]
lisa = [lisa_base]

property_value = [0]
mortgage_balance = [0]
home_equity = [0]

house_bought = False
annual_mortgage_payment = None
purchase_year = None

# =========================
# Simulation loop
# =========================

for year in range(1, years):

    # Salaries
    nominal_salary.append(nominal_salary[-1] * (1 + growth_rate))
    real_salary.append(real_salary[-1] * (1 + growth_rate - inflation))
    current_net = net_pay(real_salary[-1])
    net_salary.append(current_net)

    # Pension / ISA / Cash
    pension.append(
        pension[-1] * (1 + pension_rate - inflation) +
        pension_contribution_rate * real_salary[-1]
    )

    isa.append(
        isa[-1] * (1 + isa_rate - inflation) +
        isa_contribution_rate * current_net
    )

    cash.append(
        cash[-1] * (1 + cash_rate - inflation)
    )

    # ---------- LISA ----------
    if not house_bought:
        lisa_contrib = min(lisa_max_contribution, 0.2 * current_net)
        bonus = lisa_contrib * lisa_bonus_rate
    else:
        lisa_contrib = 0
        bonus = 0

    lisa.append(
        lisa[-1] * (1 + lisa_rate - inflation) +
        lisa_contrib +
        bonus
    )

    # ---------- PROPERTY ----------
    current_house_price = property_price_start * (
        (1 + house_price_growth - inflation) ** year
    )
    deposit_required = current_house_price * deposit_rate

    if not house_bought and lisa[-1] >= deposit_required:
        house_bought = True
        purchase_year = year

        property_value.append(current_house_price)

        initial_mortgage = current_house_price - deposit_required
        mortgage_balance.append(initial_mortgage)

        home_equity.append(deposit_required)

        lisa[-1] -= deposit_required
        annual_mortgage_payment = initial_mortgage / mortgage_term


    elif house_bought:
        property_value.append(
            property_value[-1] * (1 + house_price_growth - inflation)
        )

        mortgage_balance.append(
            max(
                0,
                mortgage_balance[-1] * (1 + mortgage_rate_real) - annual_mortgage_payment
            )
        )

        home_equity.append(
            property_value[-1] - mortgage_balance[-1]
        )

    else:
        property_value.append(0)
        mortgage_balance.append(0)
        home_equity.append(0)

# =========================
# Net worth
# =========================

net_worth = [
    p + i + c + l + e
    for p, i, c, l, e in zip(pension, isa, cash, lisa, home_equity)
]

# =========================
# Plot
# =========================

ages = [start_age + i for i in range(years)]

plt.figure(figsize=(10, 6))
plt.plot(ages, pension, label="Pension")
plt.plot(ages, isa, label="ISA")
plt.plot(ages, lisa, label="LISA")
plt.plot(ages, cash, label="Cash")
plt.plot(ages, home_equity, label="Home Equity")
plt.plot(ages, net_worth, label="Total Net Worth", linewidth=3)

if purchase_year is not None:
    plt.axvline(
        start_age + purchase_year,
        linestyle="--",
        label="House Purchase"
    )

plt.legend()
plt.title("Real Net Worth Growth")
plt.grid(True)
plt.show()

print(home_equity)