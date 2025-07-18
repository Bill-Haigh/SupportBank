#! I am also aware that I have used a mixture of camel/snake/etc will tidy up at the end. Also why doesnt python have multi-line comments

import csv
import logging
import sys
import os

logger = logging.getLogger()
logging.basicConfig(filename="SupportBank.log", filemode="w", level=logging.DEBUG)
logger.info("Logging started.")

class Transaction:
    def __init__(self, data):
        self.Date = data["Date"]
        self.From = data["From"]
        self.To = data["To"]
        self.Narrative = data["Narrative"]
        self.Amount = float(data["Amount"])

class Account:
    def __init__(self, name):
        self.name = name
        self.balance = 0
        self.transactions = []

    def apply_transaction(self, transaction):
        if transaction.From == self.name:
            self.balance -= int(transaction.Amount * 100)
        if transaction.To == self.name:
            self.balance += int(transaction.Amount * 100)
        self.transactions.append(transaction)

def read_transactions(filename):
    try:
        with open(filename, mode='r') as file:
            reader = csv.DictReader(file)
            transactions = [Transaction(row) for row in reader]
            logger.info(f'{filename} read and transformed to list')
            return transactions
    except Exception as e:
        logger.error(f"failed to read {filename}: {e}")

def list_available_csv_files():
    data_dir = "./DataFiles"
    try:
        files = [f[:-4] for f in os.listdir(data_dir) if f.endswith(".csv")]
        if not files:
            print("No CSV files found in ./DataFiles/")
            logger.warning("No CSV files found in ./DataFiles/")
        else:
            print("Available CSV files:")
            for f in files:
                print(f" - {f}")
            logger.info("available CSV files listed")
        return files
    except FileNotFoundError:
        print("The ./DataFiles directory does not exist")
        logger.warning("The ./DataFiles directory does not exist")
        return []

def List_All(transactions):
    accountsDict = {}
    logger.info("showing account balances")
    for tx in transactions:
        for name in [tx.From, tx.To]:
            if name not in accountsDict:
                accountsDict[name] = Account(name)
        accountsDict[tx.From].apply_transaction(tx)
        accountsDict[tx.To].apply_transaction(tx)

    print("Balances:")
    for account in accountsDict.values():
        print(f"{account.name}: £{account.balance / 100:.2f}")
    logger.info("Accounts and balances displayed successfully")

def List(account, transactions):
    account_found = False
    logger.info(f"listing transactions for {account}")
    for tx in transactions:
        if tx.From == account or tx.To == account:
            account_found = True
            print(f"{tx.Date} | From: {tx.From} | To: {tx.To} | {tx.Narrative} | £{tx.Amount:.2f}")
    if not account_found:
        print(f"Account '{account}' not found in any transactions.")
        logger.warning(f"Account '{account}' not found in any transactions.")

def main():
    print("Welcome to SupportBank")
    while True:
        print("\nWhat would you like to do?")
        print("1. List all balances")
        print("2. List transactions for an account")
        print("3. Quit")
        choice = input("Enter the number of your choice: ").strip()
        logger.info(f"User selected choice: {choice}")

        if choice == "1":
            available = list_available_csv_files()
            if not available:
                continue
            filename = input("Enter CSV filename (without .csv): ").strip()
            try:
                transactions = read_transactions(f"./DataFiles/{filename}.csv")
                List_All(transactions)
            except FileNotFoundError:
                print("File not found.")
        elif choice == "2":
            account = input("Enter account name: ").strip()
            available = list_available_csv_files()
            if not available:
                continue
            filename = input("Enter CSV filename (without .csv): ").strip()
            try:
                transactions = read_transactions(f"./DataFiles/{filename}.csv")
                List(account, transactions)
            except FileNotFoundError:
                print("File not found.")

        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
