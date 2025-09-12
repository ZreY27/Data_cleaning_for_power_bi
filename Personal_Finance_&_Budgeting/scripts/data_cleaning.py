import pandas as pd
import numpy as np

# ----------------- LOAD DATA -----------------
transactions = pd.read_csv("Personal_Finance_&_Budgeting/data/raw/personal_transactions.csv")
budget = pd.read_csv("Personal_Finance_&_Budgeting/data/raw/Budget.csv")

# 1) Standardize column names
transactions.columns = [c.strip() for c in transactions.columns]

# 2) Parse dates
transactions['Date'] = pd.to_datetime(transactions['Date'], format='%m/%d/%Y', errors='coerce')

# 3) Parse amounts
transactions['Amount'] = pd.to_numeric(transactions['Amount'], errors='coerce')

# 4) Normalize transaction type
transactions['Type'] = transactions['Transaction Type'].apply(lambda x: 'Income' if str(x).lower()=='credit' else 'Expense')

# 5) Add derived columns
transactions['Month'] = transactions['Date'].dt.month
transactions['Year'] = transactions['Date'].dt.year
transactions['MonthYear'] = transactions['Date'].dt.to_period('M').astype(str)
transactions['AbsAmount'] = transactions['Amount'].abs()

# 6) Remove duplicates (if any)
transactions = transactions.drop_duplicates(subset=['Date', 'Description', 'Amount'])

# 7) Compute cumulative balance (assuming starting balance = 0)
transactions = transactions.sort_values(by='Date')
transactions['CumulativeBalance'] = transactions['Amount'].cumsum()

# 8) Merge with budget to compute % of budget used
merged = pd.merge(transactions, budget, how='left', left_on='Category', right_on='Category')
merged['BudgetUsedPct'] = np.where(merged['Budget']>0, merged['Amount']/merged['Budget']*100, np.nan)

# 9) Export cleaned CSV for Power BI
merged.to_csv("Personal_Finance_&_Budgeting/data/processed/finance_clean.csv", index=False, encoding='utf-8-sig')
print("✅ Cleaned file saved: finance_clean.csv")
print(merged.head())
