import csv
from datetime import datetime
import os
import pandas as pd
import matplotlib.pyplot as plt
#initialze data file
FILE = "expenses.csv"

# Create file if not exists
if not os.path.exists(FILE):
    with open(FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Category", "Amount", "Note"])
#add and view expenses
#add expenses
def add_expense():
    category = input("Enter category (Food/Travel/Shopping/etc): ")
    amount = float(input("Enter amount: "))
    note = input("Enter a short note: ")
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([date, category, amount, note])
    print("✅ Expense added successfully!\n")
#view expenses
def view_expenses():
    df = pd.read_csv(FILE)
    if df.empty:
        print("No expenses found.")
        return
    print("\n--- All Expenses ---")
    print(df)
#Show Summary by Category
def show_summary():
    df = pd.read_csv(FILE)
    if df.empty:
        print("No expenses to summarize.")
        return

    summary = df.groupby("Category")["Amount"].sum()
    print("\n--- Expense Summary ---")
    print(summary)
    print(f"\nTotal Spent: ₹{summary.sum():.2f}")
#Graph Visualization
def plot_category_chart():
    df = pd.read_csv(FILE)
    if df.empty:
        print("No expenses to visualize.")
        return

    summary = df.groupby("Category")["Amount"].sum()
    plt.figure(figsize=(6,6))
    plt.pie(summary, labels=summary.index, autopct='%1.1f%%', startangle=140)
    plt.title("Expenses by Category")
    plt.show()
def plot_expense_over_time():
    df = pd.read_csv(FILE)
    if df.empty:
        print("No expenses to visualize.")
        return

    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")
    plt.figure(figsize=(8,5))
    plt.plot(df["Date"], df["Amount"], marker="o", linestyle="-")
    plt.title("Expenses Over Time")
    plt.xlabel("Date")
    plt.ylabel("Amount (₹)")
    plt.grid(True)
    plt.show()
#main menu
def main():
    while True:
        print("\n===== EXPENSE TRACKER MENU =====")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Show Summary")
        print("4. Plot Category Chart (Pie)")
        print("5. Plot Expense Over Time")
        print("6. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            add_expense()
        elif choice == "2":
            view_expenses()
        elif choice == "3":
            show_summary()
        elif choice == "4":
            plot_category_chart()
        elif choice == "5":
            plot_expense_over_time()
        elif choice == "6":
            print("Goodbye 👋")
            break
        else:
            print("Invalid choice, try again!")
if __name__ == "__main__":
    main()