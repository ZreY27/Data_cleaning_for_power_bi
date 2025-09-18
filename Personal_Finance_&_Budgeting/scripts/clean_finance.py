import pandas as pd
import numpy as np

# ----------------- LOAD DATA -----------------
transactions = pd.read_csv("Personal_Finance_&_Budgeting/data/raw/personal_transactions.csv")
budget = pd.read_csv("Personal_Finance_&_Budgeting/data/raw/Budget.csv")

# ----------------- CLEAN TRANSACTIONS -----------------
# 1. Standardize column names
transactions.columns = [c.strip().replace(" ", "_").lower() for c in transactions.columns]

# 2. Parse dates
transactions["date"] = pd.to_datetime(transactions["date"], errors="coerce")

# 3. Parse amounts (force numeric, replace commas if needed)
transactions["amount"] = pd.to_numeric(transactions["amount"], errors="coerce")

# 4. Normalize transaction type
transactions["type"] = transactions["transaction_type"].str.lower().map(
    {"credit": "Income", "debit": "Expense"}
)

# 5. Add derived columns
transactions["year"] = transactions["date"].dt.year
transactions["month"] = transactions["date"].dt.month
transactions["monthyear"] = transactions["date"].dt.to_period("M").astype(str)
transactions["abs_amount"] = transactions["amount"].abs()

# 6. Remove duplicates
transactions = transactions.drop_duplicates(subset=["date", "description", "amount"])

# 7. Add a flag for large transactions (e.g. > 1000)
transactions["is_large"] = np.where(transactions["abs_amount"] > 1000, 1, 0)

# 8. Categorize transactions
transactions['IsBankMovement'] = transactions['category'].isin([
    "Credit Card Payment",
    "Bank Transfer",
    "Loan Payment"
])


# ----------------- CLEAN BUDGET -----------------
budget.columns = [c.strip().replace(" ", "_").lower() for c in budget.columns]
budget["budget"] = pd.to_numeric(budget["budget"], errors="coerce")

# ----------------- EXPORT CLEAN FILES -----------------
transactions.to_csv("Personal_Finance_&_Budgeting/data/processed/personal_transactions_clean.csv", index=False, encoding="utf-8-sig")
budget.to_csv("Personal_Finance_&_Budgeting/data/processed/budget_clean.csv", index=False, encoding="utf-8-sig")

print("✅ Cleaned files saved in data/processed/")
print(transactions.head())
print(budget.head())
