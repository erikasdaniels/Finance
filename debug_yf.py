import yfinance as yf
import pandas as pd

print(f"YFinance Version: {yf.__version__}")
print(f"Pandas Version: {pd.__version__}")

ticker = "^GSPC"
print(f"Downloading {ticker}...")
try:
    df = yf.download(ticker, period="1mo", progress=False)
    print("Download complete.")
    print("Columns:", df.columns)
    print("Head:\n", df.head())
    
    print("\nAttempting to access 'Adj Close'...")
    try:
        if isinstance(df.columns, pd.MultiIndex):
            print("MultiIndex columns detected")
            if 'Adj Close' in df.columns.get_level_values(0):
                 print("'Adj Close' found in level 0")
        elif 'Adj Close' in df.columns:
            print("'Adj Close' found in columns")
        else:
            print("'Adj Close' NOT found")

        df_adj = df[['Adj Close']].copy()
        print("Success accessing df[['Adj Close']]")
    except Exception as e:
        print(f"Error accessing 'Adj Close': {e}")

except Exception as e:
    print(f"Download failed: {e}")
