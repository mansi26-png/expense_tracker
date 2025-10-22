import csv
from datetime import datetime
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

CSV_FILE = "expenses.csv"
CSV_HEADER = ["Date", "Category", "Amount", "Description"]

# --- Ensure CSV exists with header ---
def ensure_csv():
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=CSV_HEADER)
        df.to_csv(CSV_FILE, index=False)
        print(f"Created new file: {CSV_FILE} with header.")

# --- Read CSV safely (skip bad lines) ---
def read_expenses():
    ensure_csv()
    try:
        # on_bad_lines='skip' will ignore malformed lines instead of crashing
        df = pd.read_csv(CSV_FILE, on_bad_lines='skip')
        # If file exists but has no columns (empty), return empty DataFrame with correct columns
        if df.shape[1] == 0 or df.empty:
            return pd.DataFrame(columns=CSV_HEADER)
        # If the CSV contains no proper headers (e.g., user manually created), ensure columns
        df.columns = [c if c in CSV_HEADER else CSV_HEADER[i] if i < len(CSV_HEADER) else c
                      for i, c in enumerate(df.columns)]
        # Ensure correct dtypes
        if "Amount" in df.columns:
            # coerce Amount to numeric, invalid -> NaN then drop or fill
            df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
        return df
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=CSV_HEADER)
    except Exception as e:
        print("Error reading CSV:", e)
        return pd.DataFrame(columns=CSV_HEADER)
# AI MODEL FOR CATEGORIZATION
def train_category_model():
    data = {
        "Description": [
            "bus ticket", "train fare", "taxi ride", "flight ticket", "petrol", "car wash",
            "movie ticket", "netflix", "concert", "dinner", "lunch", "coffee", "snacks",
            "groceries", "milk", "vegetables", "fruits", "t-shirt", "jeans", "shoes",
            "mobile recharge", "electricity bill", "internet bill", "water bill", "rent"
        ],
        "Category": [
            "Travel", "Travel", "Travel", "Travel", "Travel", "Travel",
            "Entertainment", "Entertainment", "Entertainment", "Food", "Food", "Food", "Food",
            "Groceries", "Groceries", "Groceries", "Groceries", "Shopping", "Shopping", "Shopping",
            "Utilities", "Utilities", "Utilities", "Utilities", "Rent"
        ]
    }

    df = pd.DataFrame(data)
    X = df["Description"]
    y = df["Category"]

    vectorizer = CountVectorizer()
    X_vec = vectorizer.fit_transform(X)

    model = MultinomialNB()
    model.fit(X_vec, y)

    return model, vectorizer

model, vectorizer = train_category_model()

def predict_category(description):
    if not description or str(description).strip()=="":
        return "Misc"
    desc_vec = vectorizer.transform([description])
    return model.predict(desc_vec)[0]
# ADD EXPENSE
def add_expense():
    ensure_csv()
    date = input("Enter date (YYYY-MM-DD) [press Enter for today]: ").strip()
    if not date:
        date = pd.Timestamp.now().strftime("%Y-%m-%d")
    description = input("Enter description: ").strip()

    # Predict category using AI model
    category = predict_category(description)
    print(f"🤖 Predicted Category: {category}")

    # amount input with validation
    while True:
        amt_raw = input("Enter amount (₹): ").strip()
        try:
            amount = float(amt_raw)
            break
        except:
            print("Please enter a valid numeric amount (e.g., 250 or 99.50).")

    # Append safely using pandas
    new_row = pd.DataFrame([[date, category, amount, description]], columns=CSV_HEADER)
    try:
        # If file empty, write header; else append without header
        if os.path.getsize(CSV_FILE) == 0:
            new_row.to_csv(CSV_FILE, mode="a", index=False)
        else:
            new_row.to_csv(CSV_FILE, mode="a", index=False, header=False)
        print("✅ Expense added successfully!")
    except Exception as e:
        print("Error saving expense:", e)
# VIEW EXPENSES
def view_expenses():
    df = read_expenses()
    if df.empty:
        print("No expenses found.")
        return
    # show last 50 rows to avoid huge prints
    pd.set_option('display.max_rows', 200)
    print("\n=== All Expenses ===")
    print(df.tail(200).to_string(index=False))
# SHOW MONTHLY TREND GRAPH
def show_monthly_trend():
    df = read_expenses()
    if df.empty:
        print("No data to plot.")
        return
    try:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])
        df["Month"] = df["Date"].dt.strftime("%b-%Y")
        monthly_expense = df.groupby("Month")["Amount"].sum().sort_index()
        if monthly_expense.empty:
            print("No numeric amount data to plot.")
            return
        monthly_expense.plot(kind="bar")
        plt.title("Monthly Expense Trend")
        plt.xlabel("Month")
        plt.ylabel("Total Expense (₹)")
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print("⚠️ Unable to plot graph:", e)
# AI: PREDICT NEXT MONTH EXPENSE
def predict_next_month_expense():
    df = read_expenses()
    if df.empty:
        print("No data to predict.")
        return
    try:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])
        df["MonthNum"] = df["Date"].dt.year * 12 + df["Date"].dt.month  # continuous month index
        monthly_expense = df.groupby("MonthNum")["Amount"].sum().reset_index().sort_values("MonthNum")

        if monthly_expense.shape[0] < 2:
            print("Need at least 2 months of data to make a reasonable prediction.")
            return

        X = monthly_expense["MonthNum"].values.reshape(-1, 1)
        y = monthly_expense["Amount"].values

        lr = LinearRegression()
        lr.fit(X, y)

        next_month_num = monthly_expense["MonthNum"].max() + 1
        prediction = lr.predict(np.array([[next_month_num]]))[0]
        print(f"\n🧠 Predicted total expense for next month: ₹{prediction:.2f}\n")
    except Exception as e:
        print("⚠️ Error predicting expenses:", e)
# QUICK FIX: Repair CSV (optional)
def repair_csv_instruction():
    print("\nIf you previously had a ParserError, open expenses.csv in a text editor and:")
    print("- look for lines with extra commas (e.g., notes containing commas).")
    print("- remove or replace commas inside the Description field (use spaces).")
    print("Alternatively, run the following quick script to show problematic lines (printed here):")
    try:
        with open(CSV_FILE, "r", errors="replace") as f:
            for i, line in enumerate(f, 1):
                # count commas (should be 3 for 4 fields)
                if line.count(",") != 3:
                    print(f"Line {i}: has {line.count(',')} commas -> {line.strip()}")
    except Exception as e:
        print("Could not inspect file:", e)
# MAIN MENU
def main():
    ensure_csv()
    print("\n💰 Welcome to the AI-Based Expense Tracker (robust) 💰")
    while True:
        print("\n======= MENU =======")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Show Monthly Expense Graph")
        print("4. Predict Next Month Expense (AI)")
        print("5. Check CSV formatting issues (helper)")
        print("6. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            add_expense()
        elif choice == "2":
            view_expenses()
        elif choice == "3":
            show_monthly_trend()
        elif choice == "4":
            predict_next_month_expense()
        elif choice == "5":
            repair_csv_instruction()
        elif choice == "6":
            print("👋 Exiting... Goodbye!")
            break
        else:
            print("❌ Invalid choice, please try again.")

if __name__ == "__main__":
    main()
