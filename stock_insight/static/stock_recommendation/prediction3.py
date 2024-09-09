import yfinance as yf
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pickle

# List of Indian stocks with correct Yahoo Finance tickers
stocks = ["HINDUNILVR.NS", "ITC.NS", "KOTAKBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "ASIANPAINT.NS", 
          "MARUTI.NS", "LT.NS", "AXISBANK.NS", "SUNPHARMA.NS", "WIPRO.NS", "BAJFINANCE.NS", "M&M.NS", 
          "HCLTECH.NS", "ULTRACEMCO.NS", "TECHM.NS", "TITAN.NS", "HEROMOTOCO.NS", "DRREDDY.NS", 
          "POWERGRID.NS", "TATAMOTORS.NS", "NTPC.NS", "ONGC.NS", "ADANIGREEN.NS", "BPCL.NS", "GRASIM.NS", 
          "INDUSINDBK.NS", "JSWSTEEL.NS", "ADANIPORTS.NS", "HINDALCO.NS", "ADANIENT.NS", "DIVISLAB.NS", 
          "COALINDIA.NS", "BAJAJ-AUTO.NS", "SHREECEM.NS", "BRITANNIA.NS", "EICHERMOT.NS", "SBILIFE.NS", 
          "ICICIGI.NS", "HDFCLIFE.NS", "DMART.NS", "TATACONSUM.NS", "APOLLOHOSP.NS", "PIDILITIND.NS", 
          "HAVELLS.NS", "HDFCAMC.NS"]

# Function to fetch stock data using yfinance API
def get_stock_data(stock):
    ticker = yf.Ticker(stock)
    info = ticker.info

    # Extract relevant features
    eps = info.get("trailingEps", None)
    pe_ratio = info.get("trailingPE", None)
    dividend_yield = info.get("dividendYield", None)
    pb_ratio = info.get("priceToBook", None)
    debt_equity_ratio = info.get("debtToEquity", None)
    
    return {
        "Stock": stock,
        "EPS": eps,
        "P/E Ratio": pe_ratio,
        "Dividend Yield": dividend_yield,
        "P/B Ratio": pb_ratio,
        "Debt/Equity Ratio": debt_equity_ratio
    }

# Collect data for all stocks
data = [get_stock_data(stock) for stock in stocks]
df = pd.DataFrame(data)

# Clean data (handling missing values)
df = df.dropna()

# Define features for the ML model
X = df[['EPS', 'P/E Ratio', 'Dividend Yield', 'P/B Ratio', 'Debt/Equity Ratio']]

# Mock label assignment (real-world training data needed)
y = [1 if row['P/E Ratio'] < 20 else -1 if row['P/E Ratio'] > 30 else 0 for _, row in df.iterrows()]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Save the model to a pickle file
with open('stock_recommendation_model.pkl', 'wb') as file:
    pickle.dump(model, file)

# Load the model from the pickle file
with open('stock_recommendation_model.pkl', 'rb') as file:
    model = pickle.load(file)

# Accuracy for testing purposes
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model accuracy: {accuracy * 100:.2f}%")

# Function to classify stocks based on the time horizon
def classify_stock(row, horizon):
    if horizon == 'Short-term':
        if row['Debt/Equity Ratio'] < 0.5 and row['P/E Ratio'] < 15:
            return 'Buy'
        elif row['Debt/Equity Ratio'] > 1.0 or row['P/E Ratio'] > 30:
            return 'Sell'
        else:
            return 'Hold'
    elif horizon == 'Medium-term':
        if 10 <= row['P/E Ratio'] <= 25 and row['EPS'] > 5:
            return 'Buy'
        elif row['P/E Ratio'] > 30 or row['EPS'] < 1:
            return 'Sell'
        else:
            return 'Hold'
    elif horizon == 'Long-term':
        if row['Dividend Yield'] > 0.02 and row['EPS'] > 5:
            return 'Buy'
        elif row['Dividend Yield'] is None or row['EPS'] < 2:
            return 'Sell'
        else:
            return 'Hold'
    return 'Hold'

# Apply recommendations based on user-selected time horizon
def get_recommendations(horizon):
    df['Recommendation'] = df.apply(lambda row: classify_stock(row, horizon), axis=1)
    return df[['Stock', 'EPS', 'P/E Ratio', 'Dividend Yield', 'P/B Ratio', 'Debt/Equity Ratio', 'Recommendation']]

# Ask the user for the investment horizon
print("Select your investment horizon:")
print("1: Short-term (Up to 2 years)")
print("2: Medium-term (2-5 years)")
print("3: Long-term (More than 5 years)")

# Capture user input
user_choice = input("Enter the number corresponding to your choice: ")

# Map user choice to horizon string
if user_choice == '1':
    horizon = 'Short-term'
elif user_choice == '2':
    horizon = 'Medium-term'
elif user_choice == '3':
    horizon = 'Long-term'
else:
    print("Invalid choice. Defaulting to Short-term.")
    horizon = 'Short-term'

# Get stock recommendations based on user choice
recommendations = get_recommendations(horizon)

# Display the recommendations
print(f"\nStock Recommendations for {horizon} investment horizon:")
print(recommendations)
