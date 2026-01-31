import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import threading

# Set appearance mode and default color theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class BacktestApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window setup
        self.title("Portfolio Backtester")
        self.geometry("1400x900")

        # Layout configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left Sidebar for Inputs
        self.sidebar = ctk.CTkFrame(self, width=300)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.sidebar.grid_propagate(False)

        # Right Frame for Plot
        self.plot_frame = ctk.CTkFrame(self)
        self.plot_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.plot_frame.grid_rowconfigure(0, weight=1)
        self.plot_frame.grid_columnconfigure(0, weight=1)
        
        # Data storage
        self.data_cache = {}

        # Tracking widgets
        self.widgets = {}

        # Create Inputs
        self.create_inputs()

        # Execute Button
        self.run_button = ctk.CTkButton(self.sidebar, text="Run Backtest", command=self.run_backtest_thread, height=40, font=("font", 14, "bold"))
        self.run_button.pack(pady=20, fill="x", padx=10)
        
        # Status Label
        self.status_label = ctk.CTkLabel(self.sidebar, text="Ready", text_color="gray")
        self.status_label.pack(pady=5)

        # Matplotlib Figure
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # Index mapping
        self.indices = {
            "S&P 500": "^GSPC",
            "Nasdaq Composite": "^IXIC", 
            "FTSE 100": "^FTSE",
            "Global (ACWI ETF)": "ACWI" 
        }

    def add_section_header(self, text):
        label = ctk.CTkLabel(self.sidebar, text=text, font=("font", 16, "bold"), anchor="w")
        label.pack(pady=(20, 5), padx=5, fill="x")

    def add_dropdown(self, label_text, var_name, values, default_value):
        frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        frame.pack(pady=5, fill="x", padx=5)
        
        lbl = ctk.CTkLabel(frame, text=label_text, anchor="w")
        lbl.pack(fill="x")
        
        menu = ctk.CTkOptionMenu(frame, values=values)
        menu.pack(fill="x", pady=(2, 0))
        menu.set(default_value)
        
        self.widgets[var_name] = menu

    def add_input(self, label_text, var_name, default_value):
        frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        frame.pack(pady=5, fill="x", padx=5)
        
        lbl = ctk.CTkLabel(frame, text=label_text, anchor="w")
        lbl.pack(fill="x")
        
        entry = ctk.CTkEntry(frame)
        entry.pack(fill="x", pady=(2, 0))
        entry.insert(0, str(default_value))
        
        self.widgets[var_name] = entry

    def create_inputs(self):
        self.add_section_header("Strategy Settings")
        
        self.add_dropdown("Select Index", "index", 
                          ["S&P 500", "Nasdaq Composite", "FTSE 100", "Global (ACWI ETF)"], 
                          "S&P 500")
        
        self.add_input("Years to Backtest", "years", 10)
        self.add_input("Initial Investment (£/$)", "initial_investment", 10000)
        self.add_input("Monthly Contribution (DCA)", "monthly_dca", 500)

    def get_val(self, key):
        val = self.widgets[key].get()
        # Try converting to float if possible
        try:
            return float(val)
        except ValueError:
            return val

    def fetch_data(self, ticker, start_date, end_date):
        # Check cache first
        cache_key = (ticker, start_date, end_date)
        if cache_key in self.data_cache:
            return self.data_cache[cache_key]
        
        self.status_label.configure(text=f"Fetching data for {ticker}...")
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        self.data_cache[cache_key] = data
        return data

    def run_backtest_thread(self):
        # Run in separate thread to keep GUI responsive
        threading.Thread(target=self.calculate_and_plot, daemon=True).start()

    def calculate_and_plot(self):
        try:
            self.status_label.configure(text="Running Backtest...", text_color="blue")
            self.run_button.configure(state="disabled")
            
            # Get inputs
            index_name = self.get_val("index")
            years = int(self.get_val("years"))
            initial_inv = self.get_val("initial_investment")
            monthly_dca = self.get_val("monthly_dca")
            
            ticker = self.indices[index_name]
            
            # Calculate dates
            end_date = datetime.now()
            start_date = end_date - timedelta(days=years*365)
            
            # Fetch data
            df = self.fetch_data(ticker, start_date, end_date)
            
            if df.empty:
                self.status_label.configure(text="Error: No data found", text_color="red")
                self.run_button.configure(state="normal")
                return

            # Prepare Backtest
            # Resample to monthly to easier handle DCA
            # We use 'Adj Close' for accurate return calculations (dividends etc if available in adj close, otherwise just price)
            # Note: Index tickers often don't include dividends in Adj Close, but ETFs (ACWI) do. 
            # For simplicity in this script we assume price return for indices unless we switch to TR indices.
            
            # Using daily data for more accuracy on volatility, but adding cash flow monthly
            
            # Determine price column (Adj Close preferred, fallback to Close)
            # Check if using MultiIndex or flat index
            price_col = 'Adj Close'
            if isinstance(df.columns, pd.MultiIndex):
                # Check top level
                if 'Adj Close' not in df.columns.get_level_values(0):
                    price_col = 'Close'
            else:
                if 'Adj Close' not in df.columns:
                    price_col = 'Close'

            # Extract the relevant price data
            if isinstance(df.columns, pd.MultiIndex):
                df = df.xs(price_col, axis=1, level=0, drop_level=True)
            else:
                df = df[[price_col]]
            
            # Now df should have tickers as columns (e.g., "^GSPC") or be a single column
            # Since we only requested one ticker, it should be a single column dataframe usually, 
            # but yfinance sometimes returns it with the ticker name.
            
            # Ensure we have just one column called 'Price'
            if df.shape[1] >= 1:
                # Take the first column regardless of name
                df = df.iloc[:, [0]]
            
            df.columns = ['Price']
            df = df.dropna()

            portfolio_value = []
            total_invested = []
            
            current_units = initial_inv / df.iloc[0]['Price']
            invested = initial_inv
            
            # Find the day of month of start date to approximate "monthly" contributions
            start_day = df.index[0].day
            last_month = df.index[0].month
            
            dates = df.index
            prices = df['Price'].values
            
            # Iterate through days
            for i, date in enumerate(dates):
                price = prices[i]
                
                # Check if new month has started for DCA
                if date.month != last_month:
                    # Buy more units
                    units_bought = monthly_dca / price
                    current_units += units_bought
                    invested += monthly_dca
                    last_month = date.month
                
                portfolio_value.append(current_units * price)
                total_invested.append(invested)

            # Plotting (must be on main thread usually, but matplotlib backend might handle it or we use after method)
            # In tkinter, it's safer to schedule the update
            self.after(0, lambda: self.update_plot(dates, portfolio_value, total_invested, index_name))

        except Exception as e:
            print(e)
            self.status_label.configure(text=f"Error: {e}", text_color="red")
        finally:
             self.after(0, lambda: self.run_button.configure(state="normal"))

    def update_plot(self, dates, portfolio_value, total_invested, index_name):
        self.ax.clear()
        
        self.ax.plot(dates, portfolio_value, label="Portfolio Value", color="#1f77b4", linewidth=2)
        self.ax.plot(dates, total_invested, label="Total Invested", color="#d62728", linestyle="--", linewidth=1.5)
        
        final_value = portfolio_value[-1]
        final_invested = total_invested[-1]
        profit = final_value - final_invested
        roi = (profit / final_invested) * 100 if final_invested > 0 else 0
        
        title = f"Backtest Results: {index_name}\nFinal Value: {final_value:,.2f} | Returns: {roi:.2f}%"
        
        self.ax.set_title(title)
        self.ax.set_xlabel("Date")
        self.ax.set_ylabel("Value")
        self.ax.legend()
        self.ax.grid(True, alpha=0.3)
        
        # Format y-axis with comma
        self.ax.get_yaxis().set_major_formatter(
            plt.FuncFormatter(lambda x, p: format(int(x), ',')))

        self.canvas.draw()
        self.status_label.configure(text="Backtest Complete", text_color="green")

if __name__ == "__main__":
    app = BacktestApp()
    app.mainloop()
