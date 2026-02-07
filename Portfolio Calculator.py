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
lisa_contribution_rate = 0.05  # % of net pay
lisa_monthly_amount = 0        # Optional fixed monthly amount (set > 0 to override rate)
lisa_max_bonus_limit = 4000    # Only first £4k gets bonus
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

    pension_contribution = 0.05 * gross
    taxable = max(0, gross - pension_contribution)

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

    net = gross - pension_contribution - tax - ni - loan
    return net, pension_contribution, tax, ni, loan

def print_tax_receipt(gross, needs_rate=0.60, isa_rate=0.15, savings_rate=0.05, wants_rate=0.20):
    net, pension, tax, ni, loan = net_pay(gross)

    employer_pension = 0.10 * gross

    monthly_net = net / 12
    monthly_gross = gross / 12

    # Split net pay
    needs = net * needs_rate
    isa_contribution = net * isa_rate
    savings = net * savings_rate
    wants = net * wants_rate

    monthly_needs = needs / 12
    monthly_isa = isa_contribution / 12
    monthly_savings = savings / 12
    monthly_wants = wants / 12

    print("\n" + "=" * 45)
    print("           TAX & PAY RECEIPT")
    print("=" * 45)

    print(f"Gross salary (annual):      £{gross:,.2f}")
    print(f"Gross salary (monthly):     £{monthly_gross:,.2f}")
    print("-" * 45)

    print("DEDUCTIONS (EMPLOYEE)")
    print(f"Pension (5%):               £{pension:,.2f}")
    print(f"Income tax:                 £{tax:,.2f}")
    print(f"National Insurance:         £{ni:,.2f}")
    print(f"Student loan (Plan 2):      £{loan:,.2f}")
    print("-" * 45)

    print("EMPLOYER CONTRIBUTIONS")
    print(f"Employer pension (10%):     £{employer_pension:,.2f}")
    print("-" * 45)

    print(f"Net take-home (annual):     £{net:,.2f}")
    print(f"Net take-home (monthly):    £{monthly_net:,.2f}")
    print("-" * 45)

    print("NET PAY BUDGET ALLOCATION")
    print(f"Needs ({needs_rate*100:.0f}%):                £{needs:,.2f} (£{monthly_needs:,.2f}/month)")
    print(f"ISA / Investment ({isa_rate*100:.0f}%):     £{isa_contribution:,.2f} (£{monthly_isa:,.2f}/month)")
    print(f"Savings ({savings_rate*100:.0f}%):              £{savings:,.2f} (£{monthly_savings:,.2f}/month)")
    print(f"Wants / Fun ({wants_rate*100:.0f}%):          £{wants:,.2f} (£{monthly_wants:,.2f}/month)")
    print("=" * 45)

# =========================
# Tracking lists (year 0)
# =========================

nominal_salary = [base_salary]
real_salary = [base_salary]
net_salary = [net_pay(base_salary)[0]]

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
    current_net = net_pay(real_salary[-1])[0]
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
    actual_lisa_annual = 0
    lisa_bonus = 0
    
    if not house_bought:
        current_house_price = property_price_start * ((1 + house_price_growth - inflation) ** year)
        target = current_house_price * deposit_rate
        projected_with_interest = lisa[-1] * (1 + lisa_rate - inflation)
        
        if projected_with_interest < target:
            needed = target - projected_with_interest
            
            # User defined max
            if lisa_monthly_amount > 0:
                max_annual = lisa_monthly_amount * 12
            else:
                max_annual = lisa_contribution_rate * current_net
            
            # Needed contrib accounting for 25% bonus
            if needed <= 5000:
                needed_contrib = needed / 1.25
            else:
                needed_contrib = needed - 1000
                
            actual_lisa_annual = min(max_annual, needed_contrib)
            lisa_bonus = min(actual_lisa_annual, 4000) * lisa_bonus_rate

    lisa.append(
        lisa[-1] * (1 + lisa_rate - inflation) +
        actual_lisa_annual +
        lisa_bonus
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

# =========================
# Tax Receipt Interactive
# =========================

while True:
    print("\n--- Tax Receipt Viewer ---")
    try:
        user_age = int(input(f"Enter age to view receipt ({start_age} to {start_age + years - 1}) or 0 to exit: "))
        if user_age == 0:
            break
        
        index = user_age - start_age
        if 0 <= index < len(real_salary):
            current_gross = real_salary[index]
            print_tax_receipt(current_gross)
        else:
            print("Invalid age range.")
    except ValueError:
        print("Please enter a valid number.")

print(net_salary)