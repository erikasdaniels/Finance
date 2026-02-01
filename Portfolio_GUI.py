import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math

# Set appearance mode and default color theme
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class PortfolioApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window setup
        self.title("Portfolio Calculator")
        self.geometry("1400x900")

        # Layout configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left Sidebar for Inputs
        self.sidebar = ctk.CTkScrollableFrame(self, width=350, label_text="Parameters")
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Right Frame for Plot
        self.plot_frame = ctk.CTkFrame(self)
        self.plot_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.plot_frame.grid_rowconfigure(0, weight=1)
        self.plot_frame.grid_columnconfigure(0, weight=1)

        # Storage for input widgets
        self.widgets = {}

        # Create Input Fields
        self.create_inputs()

        # Execute Button
        self.calc_button = ctk.CTkButton(self.sidebar, text="Update Plot", command=self.calculate_and_plot, height=40, font=("font", 14, "bold"))
        self.calc_button.pack(pady=20, fill="x", padx=10)

        # Matplotlib Figure
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # Initial Calculation
        self.calculate_and_plot()
        
        # Connect Hover Event
        self.canvas.mpl_connect("motion_notify_event", self.on_hover)

    def add_section_header(self, text):
        label = ctk.CTkLabel(self.sidebar, text=text, font=("font", 16, "bold"), anchor="w")
        label.pack(pady=(20, 5), padx=5, fill="x")

    def add_input(self, label_text, var_name, default_value):
        frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        frame.pack(pady=2, fill="x", padx=5)
        
        lbl = ctk.CTkLabel(frame, text=label_text, width=180, anchor="w")
        lbl.pack(side="left")
        
        entry = ctk.CTkEntry(frame, width=100)
        entry.pack(side="right")
        entry.insert(0, str(default_value))
        
        self.widgets[var_name] = entry

    def add_slider(self, label_text, var_name, default_value, min_val, max_val, step=0.001, format_str="{:.1%}"):
        frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        frame.pack(pady=5, fill="x", padx=5)
        
        # Grid layout for better alignment
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=0)
        
        # Title Label
        lbl_title = ctk.CTkLabel(frame, text=label_text, anchor="w", font=("font", 12, "bold"))
        lbl_title.grid(row=0, column=0, sticky="w")
        
        # Value Label
        lbl_val = ctk.CTkLabel(frame, text=format_str.format(default_value), width=50, anchor="e")
        lbl_val.grid(row=0, column=1, sticky="e")
        
        # Callback to update label and plot
        def update_val(value):
            lbl_val.configure(text=format_str.format(value))
            self.calculate_and_plot()
            
        slider = ctk.CTkSlider(frame, from_=min_val, to=max_val, number_of_steps=(max_val-min_val)/step, command=update_val)
        slider.set(default_value)
        slider.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5,0))
        
        self.widgets[var_name] = slider

    def create_inputs(self):
        # Core Assumptions
        self.add_section_header("Core Assumptions")
        self.add_input("Base Salary (£)", "base_salary", 32000)
        self.add_input("Years to Simulate", "years", 40)
        self.add_slider("Start Age", "start_age", 22, 18, 60, 1, format_str="{:.0f}")
        self.add_slider("Salary Growth Rate", "growth_rate", 0.06, 0.0, 0.20)
        self.add_slider("Inflation Rate", "inflation", 0.03, 0.0, 0.20)

        # Retirement Goals
        self.add_section_header("Retirement Goals")
        self.add_slider("Retirement Age", "retire_age", 60, 40, 75, 1, format_str="{:.0f}")
        self.add_input("Retirement Income (£)", "retire_income", 25000)

        # Investment Starting Values
        self.add_section_header("Starting Balances")
        self.add_input("Pension Base (£)", "pension_base", 2000)
        self.add_input("ISA Base (£)", "isa_base", 20000)
        self.add_input("Cash Base (£)", "cash_base", 11000)
        self.add_input("LISA Base (£)", "lisa_base", 0)

        # Investment Growth Rates
        self.add_section_header("Investment Growth Rates")
        self.add_slider("Pension Rate", "pension_rate", 0.08, 0.0, 0.20)
        self.add_slider("ISA Rate", "isa_rate", 0.11, 0.0, 0.20)
        self.add_slider("Cash Rate", "cash_rate", 0.045, 0.0, 0.20)
        self.add_slider("LISA Rate", "lisa_rate", 0.07, 0.0, 0.20)

        # Contribution Rules
        self.add_section_header("Contribution Rules")
        self.add_input("Employee Pension %", "pension_employee_rate", 0.05)
        self.add_input("Employer Pension %", "pension_employer_rate", 0.10)
        self.add_input("ISA Contrib Rate", "isa_contribution_rate", 0.15)
        self.add_input("LISA Max Contrib (£)", "lisa_max_contribution", 4000)
        self.add_input("LISA Bonus Rate", "lisa_bonus_rate", 0.25)

        # Property Assumptions
        self.add_section_header("Property Assumptions")
        self.add_input("Property Start Price (£)", "property_price_start", 170000)
        self.add_input("Deposit Rate", "deposit_rate", 0.10)
        self.add_slider("House Price Growth", "house_price_growth", 0.05, 0.0, 0.20)
        self.add_slider("Mortgage Rate", "mortgage_rate", 0.045, 0.0, 0.20)
        self.add_input("Mortgage Term (Years)", "mortgage_term", 30)

    def get_val(self, key):
        try:
            return float(self.widgets[key].get())
        except ValueError:
            return 0.0

    def net_pay(self, gross, pension_rate=0.05):
        personal_allowance = 12570
        basic_limit = 50270
        NI_lower = 12570
        NI_upper = 50270

        basic_rate = 0.20
        NI_main_rate = 0.08
        NI_upper_rate = 0.02

        loan_threshold = 28470
        loan_rate = 0.09

        pension_contrib = pension_rate * gross
        taxable = max(0, gross - pension_contrib)

        # Income tax
        if taxable <= personal_allowance:
            tax = 0
        else:
            # Handle Higher Rate bands explicitly?
            # Basic rate logic here was: min(taxable-PA, basic_limit-PA). 
            # If taxable > basic_limit, this capped at basic band tax.
            # Missing Higher Rate Tax logic!
            # Let's add simple HRT logic:
            
            # Taxable income above Personal Allowance
            taxable_income = taxable - personal_allowance
            
            # Basic Band: £37,700 width (50270 - 12570)
            basic_band_width = basic_limit - personal_allowance
            
            if taxable_income <= basic_band_width:
                 tax = taxable_income * basic_rate
            else:
                 # Higher Rate
                 # Assuming logic is strictly BRT and HRT (40%) and ART (45%)
                 # For simplicity in this fix, let's just add the 40% band
                 # Everything above basic_limit is 40% (ignoring 100k taper and 125k limit for now to keep it simpler)
                 tax = (basic_band_width * basic_rate) + (taxable_income - basic_band_width) * 0.40

        # NI
        # NI is technically on Gross usually, but if Salary Sacrifice, it's on the reduced amount.
        # This function treats pension_contrib as Salary Sacrifice (reducing taxable and NI-able pay).
        
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

    def calculate_and_plot(self):
        # Retrieve values
        base_salary = self.get_val("base_salary")
        years = int(self.get_val("years"))
        start_age = int(self.get_val("start_age"))

        growth_rate = self.get_val("growth_rate")
        inflation = self.get_val("inflation")

        pension_base = self.get_val("pension_base")
        isa_base = self.get_val("isa_base")
        cash_base = self.get_val("cash_base")
        lisa_base = self.get_val("lisa_base")

        pension_rate = self.get_val("pension_rate")
        isa_rate = self.get_val("isa_rate")
        cash_rate = self.get_val("cash_rate")
        lisa_rate = self.get_val("lisa_rate")

        pension_employee_rate = self.get_val("pension_employee_rate")
        pension_employer_rate = self.get_val("pension_employer_rate")
        isa_contribution_rate = self.get_val("isa_contribution_rate")
        lisa_max_contribution = self.get_val("lisa_max_contribution")
        lisa_bonus_rate = self.get_val("lisa_bonus_rate")

        property_price_start = self.get_val("property_price_start")
        deposit_rate = self.get_val("deposit_rate")
        house_price_growth = self.get_val("house_price_growth")
        mortgage_rate = self.get_val("mortgage_rate")
        mortgage_term = self.get_val("mortgage_term")

        mortgage_rate_real = (1 + mortgage_rate) / (1 + inflation) - 1

        # Tracking lists (year 0)
        nominal_salary = [base_salary]
        real_salary = [base_salary]
        
        # Initial Net Pay using ONLY user's contribution
        net_salary = [self.net_pay(base_salary, pension_employee_rate)]

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

        # Simulation loop
        # Retirement Parameters
        retire_age = int(self.get_val("retire_age"))
        retire_income = self.get_val("retire_income")
        
        state_pension_age = 67
        state_pension_amount = 12000
        pension_access_age = 57
        lisa_access_age = 60

        # Simulation loop
        for year in range(1, years):
            current_age = start_age + year
            is_retired = current_age >= retire_age
            
            # --- Returns & Growth (Before Cashflows) ---
            # Calculate growth on previous balances
            pen_growth = pension[-1] * (1 + pension_rate - inflation)
            isa_growth = isa[-1] * (1 + isa_rate - inflation)
            cash_growth = cash[-1] * (1 + cash_rate - inflation)
            lisa_growth = lisa[-1] * (1 + lisa_rate - inflation)
            
            # --- Cashflows ---
            
            # Salary
            if not is_retired:
                nominal_salary.append(nominal_salary[-1] * (1 + growth_rate))
                real_salary.append(real_salary[-1] * (1 + growth_rate - inflation))
                
                # Deduct ONLY employee contribution for Net Pay calc
                current_net_pay = self.net_pay(real_salary[-1], pension_employee_rate)
                net_salary.append(current_net_pay)
                
                # Pension Pot Contribution = Employee + Employer
                total_pension_rate = pension_employee_rate + pension_employer_rate
                pen_contrib = total_pension_rate * real_salary[-1]
                
                isa_contrib = isa_contribution_rate * current_net_pay
                
                # LISA
                if not house_bought:
                    lisa_contrib = min(lisa_max_contribution, 0.2 * current_net_pay)
                    lisa_bonus = lisa_contrib * lisa_bonus_rate
                else:
                    lisa_contrib = 0
                    lisa_bonus = 0
            else:
                # Retired: No Salary, No Contributions
                nominal_salary.append(0)
                real_salary.append(0)
                net_salary.append(0)
                
                pen_contrib = 0
                isa_contrib = 0
                lisa_contrib = 0
                lisa_bonus = 0
            
            # --- Drawdown Logic (If Retired) ---
            pen_withdraw = 0
            isa_withdraw = 0
            cash_withdraw = 0
            lisa_withdraw = 0
            
            if is_retired:
                required = retire_income
                
                # Apply State Pension
                if current_age >= state_pension_age:
                    required = max(0, required - state_pension_amount)
                
                remaining_need = required
                
                # Strategy:
                # 1. Use ISA/Cash if < 57 (Mandatory)
                # 2. Use Pension if >= 57 (Preserves ISA)
                # 3. Use LISA if >= 60 (Preserves ISA)
                # 4. Fallback to ISA/Cash if Pension/LISA empty
                
                # Step A: Locked Pension Phase (< 57)
                if current_age < pension_access_age:
                    # Must use ISA/Cash
                    can_take_isa = isa_growth
                    take_isa = min(remaining_need, can_take_isa)
                    isa_withdraw += take_isa
                    remaining_need -= take_isa
                    
                    if remaining_need > 0:
                        can_take_cash = cash_growth
                        take_cash = min(remaining_need, can_take_cash)
                        cash_withdraw += take_cash
                        remaining_need -= take_cash
                        
                else:
                    # Accessible Pension Phase
                    # Prefer Pension/LISA to drain them? Or preserve ISA?
                    # Generally drawing pension is standard.
                    
                    # 1. Try Pension
                    can_take_pen = pen_growth
                    take_pen = min(remaining_need, can_take_pen)
                    pen_withdraw += take_pen
                    remaining_need -= take_pen
                    
                    # 2. Try LISA (if accessible)
                    if remaining_need > 0 and current_age >= lisa_access_age:
                        can_take_lisa = lisa_growth
                        take_lisa = min(remaining_need, can_take_lisa)
                        lisa_withdraw += take_lisa
                        remaining_need -= take_lisa
                        
                    # 3. Fallback to ISA
                    if remaining_need > 0:
                        can_take_isa = isa_growth
                        take_isa = min(remaining_need, can_take_isa)
                        isa_withdraw += take_isa
                        remaining_need -= take_isa
                        
                    # 4. Fallback to Cash
                    if remaining_need > 0:
                        can_take_cash = cash_growth
                        take_cash = min(remaining_need, can_take_cash)
                        cash_withdraw += take_cash
                        remaining_need -= take_cash
                        
                    # Note: Home Equity is intentionally NOT accessed for income. 
                    # If remaining_need > 0 here, it represents a shortfall (running out of money).

            # --- Apply Changes ---
            pension.append( max(0, pen_growth + pen_contrib - pen_withdraw) )
            isa.append( max(0, isa_growth + isa_contrib - isa_withdraw) )
            cash.append( max(0, cash_growth - cash_withdraw) ) # Cash doesn't usually get contribs in this model aside from initial? Check
            
            # LISA Update
            new_lisa = lisa_growth + lisa_contrib + lisa_bonus - lisa_withdraw
            lisa.append( max(0, new_lisa) )


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

        # Net worth calculation
        net_worth = [
            p + i + c + l + e
            for p, i, c, l, e in zip(pension, isa, cash, lisa, home_equity)
        ]

        # Plotting
        self.ax.clear()
        ages = [start_age + i for i in range(years)]
        
        self.ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'£{x/1000:,.0f}k'))
        
        lines = []
        lines.append(self.ax.plot(ages, pension, label="Pension")[0])
        lines.append(self.ax.plot(ages, isa, label="ISA")[0])
        lines.append(self.ax.plot(ages, lisa, label="LISA")[0])
        lines.append(self.ax.plot(ages, cash, label="Cash")[0])
        lines.append(self.ax.plot(ages, home_equity, label="Home Equity")[0])
        lines.append(self.ax.plot(ages, net_worth, label="Total Net Worth", linewidth=3, color="black")[0])
        
        if purchase_year is not None:
            self.ax.axvline(
                start_age + purchase_year,
                linestyle="--",
                color="gray",
                label="House Purchase"
            )

        # Minor ticks and grid
        from matplotlib.ticker import AutoMinorLocator
        self.ax.xaxis.set_minor_locator(AutoMinorLocator())
        self.ax.yaxis.set_minor_locator(AutoMinorLocator())
        self.ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
        self.ax.grid(True, which='major', linestyle='-', linewidth=0.8, alpha=1.0)

        # Annotate last points
        for line in lines:
            y_data = line.get_ydata()
            x_data = line.get_xdata()
            if len(y_data) > 0:
                last_val = y_data[-1]
                last_age = x_data[-1]
                
                # Format value
                if last_val >= 1_000_000:
                    val_str = f"£{last_val/1_000_000:.2f}M"
                else:
                    val_str = f"£{last_val/1_000:.0f}k"
                
                # Marker
                self.ax.plot(last_age, last_val, marker='o', color=line.get_color(), markersize=5)
                
                # Text annotation
                self.ax.annotate(
                    f"{val_str}",
                    xy=(last_age, last_val),
                    xytext=(5, 5),
                    textcoords="offset points",
                    fontsize=9,
                    color=line.get_color(),
                    fontweight='bold'
                )

        self.ax.set_title("Real Net Worth Growth")
        self.ax.set_xlabel("Age")
        self.ax.set_ylabel("Value")
        self.ax.legend(loc='upper left')
        
        # Redraw canvas
        self.canvas.draw()
        
        # --- Interactive Features ---
        # Save data for hover
        self.sim_data = {
            "Pension": pension,
            "ISA": isa,
            "LISA": lisa,
            "Cash": cash,
            "Equity": home_equity,
            "Total": net_worth
        }
        self.sim_ages = ages
        self.sim_start_age = start_age
        
        # Create Cursor Artists (hidden by default)
        self.cursor_line = self.ax.axvline(x=start_age, visible=False, color='gray', linestyle=':', alpha=0.8)
        
        # Create a text box for the tooltip
        # We use a fixed axis-aligned box (top-left or wherever) or a floating one. 
        # Floating is better for "analysing curves".
        self.cursor_text = self.ax.text(
            1.02, 1.0, "", 
            transform=self.ax.transAxes, 
            verticalalignment='top',
            horizontalalignment='left',
            fontdict={'size': 9},
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.9, edgecolor="gray")
        )
        self.cursor_text.set_visible(False)

    def on_hover(self, event):
        # Check if mouse is on the plot area
        if event.inaxes != self.ax:
            if hasattr(self, 'cursor_line') and self.cursor_line.get_visible():
                self.cursor_line.set_visible(False)
                self.cursor_text.set_visible(False)
                self.canvas.draw_idle()
            return

        # Get nearest age index
        # xdata is the age (float). 
        # We want to snap to the nearest integer year in our data
        try:
            hover_age = int(round(event.xdata))
            
            # Find index
            start_age = self.sim_start_age
            idx = hover_age - start_age
            
            # Bounds check
            if idx < 0 or idx >= len(self.sim_ages):
                return
                
            # Update Cursor Line
            self.cursor_line.set_xdata([hover_age])
            self.cursor_line.set_visible(True)
            
            # Build Text
            info = f"Age: {hover_age}\n"
            info += "-" * 15 + "\n"
            
            # Sort keys to be consistent or by value? 
            # Consistent order is usually better to read as you scroll.
            # Order: Total, Pension, ISA, LISA, Cash, Equity
            keys = ["Total", "Pension", "ISA", "LISA", "Cash", "Equity"]
            
            for key in keys:
                if key in self.sim_data:
                    val = self.sim_data[key][idx]
                    # Format
                    if val > 1_000_000:
                        v_str = f"£{val/1_000_000:.2f}M"
                    else:
                        v_str = f"£{val/1_000:.0f}k"
                    
                    info += f"{key}: {v_str}\n"

            self.cursor_text.set_text(info)
            # Move text box to follow cursor but stay within bounds?
            # Or just keep it fixed in a better spot?
            # User asked to "move the box... not same pos as legend". 
            # Moving to outside the plot (right side) is safest if space permits.
            # Or fixed Top-Right.
            # Let's try putting it OUTSIDE the plot to the right. 
            # The canvas might clip it. 
            # Safest is floating near cursor.
            
            # Let's Implement Floating Tooltip
            # transforming data coords to axes coords
            # x, y = event.xdata, event.ydata
            # We want to place it slightly offset.
            
            # However, simpler request: "move the box". 
            # I will move it to Top Left (offset) or Right.
            
            # Let's stick to Fixed Top Right inside axes.
            pass
            
            self.cursor_text.set_visible(True)
            
            self.canvas.draw_idle()
            
        except Exception:
            pass

if __name__ == "__main__":
    app = PortfolioApp()
    app.mainloop()
