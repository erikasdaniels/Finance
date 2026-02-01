import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys

# Set theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class PensionLogic:
    def __init__(self):
        # 2024/25 Tax Years parameters
        self.personal_allowance = 12570
        self.basic_rate_limit = 50270
        self.additional_rate_limit = 125140
        self.taper_threshold = 100000
        
        # Rates
        self.tax_basic = 0.20
        self.tax_higher = 0.40
        self.tax_additional = 0.45
        
        # NI Rates (Jan 2024 update: 10% -> 8% from April 2024)
        # However, the user linked an article that says "Updated for 8% NI".
        self.ni_lower_limit = 12570
        self.ni_upper_limit = 50270
        self.ni_rate_main = 0.08
        self.ni_rate_upper = 0.02
        
    def get_marginal_rates(self, gross_salary):
        """
        Returns (income_tax_rate, ni_rate) for the marginal £1 earned at this salary.
        Handles Personal Allowance Taper (60% effective rate).
        """
        # Income Tax
        if gross_salary < self.personal_allowance:
            tax_rate = 0.0
        elif gross_salary < self.basic_rate_limit:
            tax_rate = self.tax_basic
        elif gross_salary < self.taper_threshold:
            tax_rate = self.tax_higher
        elif gross_salary < self.additional_rate_limit:
            # Between 100k and 125k, PA tapers £1 for every £2.
            # Effective rate = 40% + 20% (lost PA) = 60%.
            # Strictly, for every £1 earned, you pay £0.40 tax and lose £0.50 allowance (which is taxed at 40%, so £0.20 extra tax).
            if gross_salary < 125140:
                tax_rate = 0.60
            else:
                tax_rate = self.tax_additional # 45%
        else:
            tax_rate = self.tax_additional

        # NI
        if gross_salary < self.ni_lower_limit:
            ni_rate = 0.0
        elif gross_salary < self.ni_upper_limit:
            ni_rate = self.ni_rate_main
        else:
            ni_rate = self.ni_rate_upper
            
        return tax_rate, ni_rate

    def calculate_efficiency(self, current_salary, retire_tax_band="Basic", 
                             employee_pct=5.0, employer_pct=3.0):
        """
        Calculates the value of £1000 Net Pay sacrificed/invested.
        """
        NET_INVESTMENT = 1000.0
        
        # 1. Determine Marginal Rates
        marg_tax, marg_ni = self.get_marginal_rates(current_salary)
        total_deduction = marg_tax + marg_ni
        retention_rate = 1 - total_deduction
        
        # 2. Determine Retirement Tax Rate
        if retire_tax_band == "Zero":
            retire_tax = 0.0
        elif retire_tax_band == "Basic":
            retire_tax = 0.20
        elif retire_tax_band == "Higher":
            retire_tax = 0.40
        elif retire_tax_band == "Additional":
            retire_tax = 0.45
        else:
            retire_tax = 0.20

        results = {}

        # --- OPTION 1: ISA ---
        # Baseline. £1000 Net -> £1000 Pot. No Tax on way out.
        results['ISA'] = {
            'pot': NET_INVESTMENT,
            'net_withdrawal': NET_INVESTMENT,
            'label': 'ISA'
        }
        
        # --- OPTION 2: LISA ---
        # £1000 Net -> +25% Bonus.
        # Withdrawal Tax Free (if >60).
        lisa_pot = NET_INVESTMENT * 1.25
        results['LISA'] = {
            'pot': lisa_pot,
            'net_withdrawal': lisa_pot,
            'label': 'LISA'
        }

        # --- Share Function for Pension Withdrawal ---
        def calc_pension_withdrawal(pot_value):
            tax_free_cash = pot_value * 0.25
            taxable_cash = pot_value * 0.75
            net_taxable = taxable_cash * (1 - retire_tax)
            return tax_free_cash + net_taxable

        # --- OPTION 3: PENSION (Salary Sacrifice) ---
        # To get £1000 Net, you needed Gross = 1000 / retention_rate
        # That Gross goes entirely into Pension.
        ss_gross_needed = NET_INVESTMENT / retention_rate if retention_rate > 0 else 0
        ss_pot = ss_gross_needed
        results['Pension (SS)'] = {
            'pot': ss_pot,
            'net_withdrawal': calc_pension_withdrawal(ss_pot),
            'label': 'Pension (Sal. Sac.)'
        }
        
        # --- OPTION 4: PENSION (Workplace Match) ---
        # Same as SS, but for every £1 Gross I put in (Employee%), Employer adds £(Employer%/Employee%).
        # Match Ratio
        if employee_pct > 0:
            match_ratio = employer_pct / employee_pct
        else:
            match_ratio = 0
            
        matched_pot = ss_gross_needed * (1 + match_ratio)
        results['Workplace (Match)'] = {
            'pot': matched_pot,
            'net_withdrawal': calc_pension_withdrawal(matched_pot),
            'label': 'Workplace (Matched)'
        }
        
        # --- OPTION 5: PENSION (SIPP / Relief at Source) ---
        if marg_tax < 0.2:
             # Non-taxpayer relief logic
            sipp_pot = NET_INVESTMENT / 0.8
        else:
            sipp_pot = NET_INVESTMENT / (1 - marg_tax)
            
        results['Pension (SIPP)'] = {
            'pot': sipp_pot,
            'net_withdrawal': calc_pension_withdrawal(sipp_pot),
            'label': 'Pension (SIPP)'
        }
        
        return results, marg_tax, marg_ni

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.logic = PensionLogic()
        self.title("Pension Tax Efficiency Calculator")
        self.geometry("1400x800")
        
        # Grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3) # More space for charts
        self.grid_rowconfigure(0, weight=1)
        
        # -- Sidebar --
        self.sidebar = ctk.CTkFrame(self, width=350, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.lbl_title = ctk.CTkLabel(self.sidebar, text="Configuration", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_title.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Sidebar Form
        self.create_sidebar_inputs()
        
        # -- Main Content --
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=4)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Results Cards
        self.cards_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.cards_frame.grid(row=0, column=0, sticky="new")
        
        self.create_results_cards()

        # Chart
        self.chart_frame = ctk.CTkFrame(self.main_frame)
        self.chart_frame.grid(row=1, column=0, sticky="nsew", pady=20)
        
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
        self.calculate()
        
    def create_sidebar_inputs(self):
        # Salary Input
        self.lbl_salary = ctk.CTkLabel(self.sidebar, text="Current Gross Salary (£)", anchor="w")
        self.lbl_salary.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="ew")
        self.entry_salary = ctk.CTkEntry(self.sidebar)
        self.entry_salary.grid(row=2, column=0, padx=20, pady=(5, 10), sticky="ew")
        self.entry_salary.insert(0, "55000")
        
        # Retirement Tax Band
        self.lbl_retire = ctk.CTkLabel(self.sidebar, text="Expected Retirement Tax Band", anchor="w")
        self.lbl_retire.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="ew")
        self.opt_retire = ctk.CTkOptionMenu(self.sidebar, values=["Basic", "Higher", "Additional", "Zero"])
        self.opt_retire.grid(row=4, column=0, padx=20, pady=(5, 10), sticky="ew")
        
        # Workplace Match Section
        self.lbl_match_title = ctk.CTkLabel(self.sidebar, text="Workplace Match Settings", font=ctk.CTkFont(size=14, weight="bold"))
        self.lbl_match_title.grid(row=5, column=0, padx=20, pady=(20, 5), sticky="w")
        
        self.lbl_emp_cont = ctk.CTkLabel(self.sidebar, text="My Contribution (%)", anchor="w")
        self.lbl_emp_cont.grid(row=6, column=0, padx=20, pady=(5, 0), sticky="ew")
        self.entry_emp_cont = ctk.CTkEntry(self.sidebar)
        self.entry_emp_cont.grid(row=7, column=0, padx=20, pady=(2, 10), sticky="ew")
        self.entry_emp_cont.insert(0, "5")
        
        self.lbl_employer_cont = ctk.CTkLabel(self.sidebar, text="Employer Match (%)", anchor="w")
        self.lbl_employer_cont.grid(row=8, column=0, padx=20, pady=(5, 0), sticky="ew")
        self.entry_employer_cont = ctk.CTkEntry(self.sidebar)
        self.entry_employer_cont.grid(row=9, column=0, padx=20, pady=(2, 10), sticky="ew")
        self.entry_employer_cont.insert(0, "3")

        # Calculate Button
        self.btn_calc = ctk.CTkButton(self.sidebar, text="Calculate ROI", command=self.calculate)
        self.btn_calc.grid(row=10, column=0, padx=20, pady=20, sticky="ew")
        
        # Info Box
        self.info_box = ctk.CTkTextbox(self.sidebar, height=180)
        self.info_box.grid(row=11, column=0, padx=20, pady=10, sticky="ew")
        self.info_box.insert("0.0", "Compares value of £1000 net income sacrificed.\n\nWorkplace Matching:\nAssumes matched portion is added on top of your contribution.")

    def create_results_cards(self):
        self.cards = {}
        # Included 'Workplace (Match)' in list
        vehicle_list = ['Workplace (Match)', 'Pension (SS)', 'Pension (SIPP)', 'LISA', 'ISA']
        
        for i, vehicle in enumerate(vehicle_list):
            card = ctk.CTkFrame(self.cards_frame, border_width=2, border_color="#3B8ED0")
            card.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            self.cards_frame.grid_columnconfigure(i, weight=1)
            
            # Label
            lbl_v = ctk.CTkLabel(card, text=vehicle, font=ctk.CTkFont(size=12, weight="bold"))
            lbl_v.pack(pady=(10,5))
            
            # Value
            lbl_val = ctk.CTkLabel(card, text="£0", font=ctk.CTkFont(size=18, weight="bold"))
            lbl_val.pack(pady=5)
            
            # ROI
            lbl_roi = ctk.CTkLabel(card, text="+0%", text_color="green", font=ctk.CTkFont(size=12))
            lbl_roi.pack(pady=(0, 10))
            
            self.cards[vehicle] = {'val': lbl_val, 'roi': lbl_roi, 'frame': card}

    def calculate(self):
        try:
            salary = float(self.entry_salary.get())
            emp_pct = float(self.entry_emp_cont.get())
            employer_pct = float(self.entry_employer_cont.get())
        except ValueError:
            return

        retire_band = self.opt_retire.get()
        
        results, marg_tax, marg_ni = self.logic.calculate_efficiency(
            salary, retire_band, emp_pct, employer_pct
        )
        
        # Update info
        marg_total = marg_tax + marg_ni
        self.info_box.delete("0.0", "end")
        self.info_box.insert("0.0", f"Salary: £{salary:,.0f}\n")
        self.info_box.insert("end", f"Ded: {marg_total*100:.1f}% (Tx:{marg_tax*100:.0f} NI:{marg_ni*100:.0f})\n")
        
        # Find winner
        winner = max(results.items(), key=lambda x: x[1]['net_withdrawal'])
        self.info_box.insert("end", f"Best: {winner[0]}\n")
        
        # Update Cards & Plot
        vehicles = ['Workplace (Match)', 'Pension (SS)', 'Pension (SIPP)', 'LISA', 'ISA']
        values = []
        colors = []
        
        base_investment = 1000.0
        
        for v in vehicles:
            res = results[v]
            val = res['net_withdrawal']
            roi = (val - base_investment) / base_investment
            
            self.cards[v]['val'].configure(text=f"£{val:,.0f}")
            self.cards[v]['roi'].configure(text=f"+{roi*100:.1f}%")
            
            if v == winner[0]:
                self.cards[v]['frame'].configure(border_color="#2CC985")
                colors.append("#2CC985")
            else:
                self.cards[v]['frame'].configure(border_color="#3B8ED0")
                colors.append("#3B8ED0")
                
            values.append(val)

        # Plot
        self.ax.clear()
        bars = self.ax.bar(vehicles, values, color=colors)
        self.ax.set_title("Net Value of £1,000 (Post-Tax Income) Invested")
        self.ax.set_ylabel("Net Withdrawal (£)")
        self.ax.axhline(y=1000, color='gray', linestyle='--', label="Original Net Cash")
        
        # Wrap labels for the chart axis
        wrapped_labels = [v.replace(" ", "\n") for v in vehicles]
        self.ax.set_xticks(range(len(vehicles)))
        self.ax.set_xticklabels(wrapped_labels, fontsize=9)
        
        for bar in bars:
            height = bar.get_height()
            self.ax.annotate(f'£{height:.0f}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha='center', va='bottom')
                            
        self.ax.set_ylim(bottom=0, top=max(values)*1.15)
        self.canvas.draw()

if __name__ == "__main__":
    app = App()
    app.mainloop()
