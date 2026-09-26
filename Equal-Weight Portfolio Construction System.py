import numpy as np
import pandas as pd
import yfinance as yf
import math
import tkinter as tk
from tkinter import filedialog


# =========================================================
# 1. SELECT CSV FILE
# =========================================================

root = tk.Tk()
root.withdraw()

print("Please select your CSV file...")

file_path = filedialog.askopenfilename(
    title="Select your stock CSV file",
    filetypes=[
        ("CSV files", "*.csv"),
        ("All files", "*.*")
    ]
)

# If the user cancels the file selection
if not file_path:
    print("\nNo file selected. Program stopped.")
    exit()

print(f"\nSelected file:")
print(file_path)


# =========================================================
# 2. READ CSV FILE
# =========================================================

try:

    tickers = pd.read_csv(file_path)

except Exception as e:

    print(f"\nCould not read the CSV file: {e}")
    exit()


# =========================================================
# 3. CHECK FOR TICKER COLUMN
# =========================================================

if "Ticker" not in tickers.columns:

    print("\nERROR: Your CSV file must contain a column called 'Ticker'.")

    print("\nColumns found in your CSV:")
    print(tickers.columns.tolist())

    exit()


# =========================================================
# 4. DISPLAY STOCK LIST
# =========================================================

print("\nTickers from CSV:")
print(tickers)


# =========================================================
# 5. CREATE TICKER LIST
# =========================================================

ticker_list = tickers["Ticker"].dropna().tolist()

print("\nTicker list:")
print(ticker_list)


# =========================================================
# 6. DOWNLOAD LATEST STOCK PRICES
# =========================================================

print("\nDownloading stock prices...")

data = yf.download(
    ticker_list,
    period="1d",
    group_by="ticker",
    auto_adjust=False,
    threads=False
)

print("\nPrice download completed.")


# =========================================================
# 7. GET PRICE + MARKET CAP
# =========================================================

stocks_data = []

print("\nGetting stock information...\n")

for i, ticker in enumerate(ticker_list, start=1):

    print(f"Processing {i}/{len(ticker_list)}: {ticker}")

    try:

        # Get latest closing price
        latest_price = data[ticker]["Close"].dropna().iloc[-1]

        # Get market capitalization
        ticker_object = yf.Ticker(ticker)

        info = ticker_object.info

        market_cap = info.get("marketCap", np.nan)

        # Store information
        stocks_data.append({
            "Ticker": ticker,
            "Market Cap": market_cap,
            "Latest Price": latest_price
        })

    except Exception as e:

        print(f"Skipping {ticker}: {e}")


# =========================================================
# 8. CREATE DATAFRAME
# =========================================================

df = pd.DataFrame(stocks_data)

print("\nStock data:")
print(df)


# =========================================================
# 9. REMOVE STOCKS WITH MISSING DATA
# =========================================================

df = df.dropna(
    subset=["Market Cap", "Latest Price"]
)


# =========================================================
# 10. SORT BY MARKET CAP
# =========================================================

df = df.sort_values(
    by="Market Cap",
    ascending=False
)


# =========================================================
# 11. SELECT TOP 10
# =========================================================

df = df.head(10)

df = df.reset_index(drop=True)


print("\n==============================================")
print("       TOP 10 STOCKS BY MARKET CAP")
print("==============================================")

print(
    df[
        ["Ticker", "Market Cap", "Latest Price"]
    ].to_string(index=False)
)


# =========================================================
# 12. CHECK THAT STOCKS WERE FOUND
# =========================================================

if len(df) == 0:

    print("\nERROR: No stocks could be processed.")

    exit()


# =========================================================
# 13. ASK FOR PORTFOLIO SIZE
# =========================================================

while True:

    try:

        portfolio_size = float(
            input("\nEnter the amount you want to invest: ₹")
        )

        if portfolio_size <= 0:

            print("Please enter an amount greater than zero.")

        else:

            break

    except ValueError:

        print("Please enter a valid number.")


# =========================================================
# 14. CALCULATE EQUAL POSITION SIZE
# =========================================================

number_of_stocks = len(df)

position_size = (
    portfolio_size / number_of_stocks
)


print("\n==============================================")
print("           PORTFOLIO CALCULATION")
print("==============================================")

print(
    f"Total portfolio size: ₹{portfolio_size:,.2f}"
)

print(
    f"Number of stocks: {number_of_stocks}"
)

print(
    f"Amount allocated to each stock: "
    f"₹{position_size:,.2f}"
)


# =========================================================
# 15. CALCULATE NUMBER OF SHARES
# =========================================================

df["Number of Shares to Buy"] = df[
    "Latest Price"
].apply(
    lambda price: math.floor(
        position_size / price
    )
)


# =========================================================
# 16. CALCULATE ACTUAL INVESTMENT
# =========================================================

df["Actual Investment"] = (
    df["Number of Shares to Buy"]
    * df["Latest Price"]
)


# =========================================================
# 17. CALCULATE CASH REMAINING
# =========================================================

total_invested = df[
    "Actual Investment"
].sum()

cash_remaining = (
    portfolio_size - total_invested
)


# =========================================================
# 18. DISPLAY FINAL PORTFOLIO
# =========================================================

print("\n==============================================")
print("          FINAL EQUAL-WEIGHT PORTFOLIO")
print("==============================================")

print(
    df[
        [
            "Ticker",
            "Latest Price",
            "Number of Shares to Buy",
            "Actual Investment"
        ]
    ].to_string(index=False)
)


# =========================================================
# 19. DISPLAY SUMMARY
# =========================================================

print("\n==============================================")
print("               SUMMARY")
print("==============================================")

print(
    f"Total portfolio: ₹{portfolio_size:,.2f}"
)

print(
    f"Total actually invested: ₹{total_invested:,.2f}"
)

print(
    f"Cash remaining: ₹{cash_remaining:,.2f}"
)

print("==============================================")