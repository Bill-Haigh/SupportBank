import csv
import json
import logging
import os
from datetime import datetime
import xml.etree.ElementTree as ET

# Logging setup
logging.basicConfig(filename="SupportBank.log", filemode="w", level=logging.DEBUG)
logger = logging.getLogger()
logger.info("Logging started.")


class Transaction:
    def __init__(self, data):
        raw_date = data.get("Date") or data.get("date")
        self.date = self.normalize_date(raw_date)
        self.from_account = data.get("From") or data.get("fromAccount") or data.get("FromAccount")
        self.to_account = data.get("To") or data.get("toAccount") or data.get("ToAccount")
        self.narrative = data.get("Narrative") or data.get("narrative") or "No Narrative"
        amount = data.get("Amount") or data.get("amount") or "0"
        self.amount = float(amount)

    @staticmethod
    def normalize_date(date_str):
        known_formats = [
            "%d/%m/%Y",
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
        ]
        for fmt in known_formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%d/%m/%Y")
            except (ValueError, TypeError):
                continue
        return "01/01/1970"  # fallback


class Account:
    def __init__(self, name):
        self.name = name
        self.balance = 0
        self.transactions = []

    def apply_transaction(self, tx):
        if tx.from_account == self.name:
            self.balance -= int(tx.amount * 100)
        if tx.to_account == self.name:
            self.balance += int(tx.amount * 100)
        self.transactions.append(tx)


def read_transactions(filepath):
    transactions = []
    try:
        if filepath.endswith(".json"):
            with open(filepath, "r") as f:
                data = json.load(f)
                for item in data:
                    try:
                        transactions.append(Transaction(item))
                    except Exception as e:
                        logger.warning(f"Invalid transaction in JSON: {item} — {e}")
        elif filepath.endswith(".csv"):
            with open(filepath, "r", newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        transactions.append(Transaction(row))
                    except Exception as e:
                        logger.warning(f"Invalid transaction in CSV: {row} — {e}")
        elif filepath.endswith(".xml"):
            tree = ET.parse(filepath)
            root = tree.getroot()
            for elem in root.findall(".//SupportTransaction"):
                try:
                    transaction_data = {
                        "Date": elem.find("Date").text,
                        "From": elem.find("Parties/From").text,
                        "To": elem.find("Parties/To").text,
                        "Narrative": elem.find("Description").text,
                        "Amount": elem.find("Value").text,
                    }
                    transactions.append(Transaction(transaction_data))
                except Exception as e:
                    logger.warning(f"Invalid transaction in XML: {ET.tostring(elem)} — {e}")
        else:
            logger.warning(f"Unsupported file type: {filepath}")
    except Exception as e:
        logger.error(f"Failed to read file {filepath}: {e}")
    return transactions


def list_all(transactions):
    accounts = {}
    for tx in transactions:
        for name in [tx.from_account, tx.to_account]:
            if name and name not in accounts:
                accounts[name] = Account(name)
        if tx.from_account:
            accounts[tx.from_account].apply_transaction(tx)
        if tx.to_account:
            accounts[tx.to_account].apply_transaction(tx)

    print("\nAccount Balances:")
    for account in accounts.values():
        print(f"{account.name}: £{account.balance / 100:.2f}")


def list_transactions(account_name, transactions):
    found = False
    relevant = [tx for tx in transactions if tx.from_account == account_name or tx.to_account == account_name]
    relevant.sort(key=lambda tx: datetime.strptime(tx.date, "%d/%m/%Y"))

    for tx in relevant:
        print(f"{tx.date} | From: {tx.from_account} | To: {tx.to_account} | {tx.narrative} | £{tx.amount:.2f}")
        found = True

    if not found:
        print(f"No transactions found for account: {account_name}")


def list_available_data_files():
    try:
        data_dir = "./DataFiles"
        files = [f for f in os.listdir(data_dir) if f.endswith((".csv", ".json", ".xml"))]
        if not files:
            print("No data files found.")
        return files
    except FileNotFoundError:
        print("The ./DataFiles directory does not exist.")
        return []


def main():
    print("Welcome to SupportBank")
    while True:
        print("\n1. List all balances from a single file")
        print("2. List transactions for an account from a single file")
        print("3. List all balances across all data files")
        print("4. List all transactions for an account across all data files")
        print("5. Quit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            files = list_available_data_files()
            if not files:
                continue
            filename = input("Enter filename: ").strip()
            transactions = read_transactions(f"./DataFiles/{filename}")
            list_all(transactions)

        elif choice == "2":
            files = list_available_data_files()
            if not files:
                continue
            filename = input("Enter filename: ").strip()
            account = input("Enter account name: ").strip()
            transactions = read_transactions(f"./DataFiles/{filename}")
            list_transactions(account, transactions)

        elif choice == "3":
            files = list_available_data_files()
            all_transactions = []
            for filename in files:
                all_transactions.extend(read_transactions(f"./DataFiles/{filename}"))
            list_all(all_transactions)

        elif choice == "4":
            files = list_available_data_files()
            all_transactions = []
            for filename in files:
                all_transactions.extend(read_transactions(f"./DataFiles/{filename}"))

            account_names = set()
            for tx in all_transactions:
                if tx.from_account:
                    account_names.add(tx.from_account)
                if tx.to_account:
                    account_names.add(tx.to_account)

            if not account_names:
                print("No accounts found.")
                continue

            sorted_accounts = sorted(account_names)
            for i, name in enumerate(sorted_accounts, 1):
                print(f"{i}. {name}")

            selection = input("Select an account by number or name: ").strip()
            if selection.isdigit():
                idx = int(selection)
                if 1 <= idx <= len(sorted_accounts):
                    account = sorted_accounts[idx - 1]
                else:
                    print("Invalid number.")
                    continue
            else:
                account = selection if selection in account_names else None
                if not account:
                    print("Invalid account.")
                    continue

            print(f"\nAll transactions for '{account}':")
            list_transactions(account, all_transactions)

        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
