#! I am also aware that I have used a mixture of camel/snake/etc will tidy up at the end. Also why doesnt python have multi-line comments
# TODO change to classes "accounts" and "transactions"
#! Now in the console you can run "poetry run List_All Transactions2014" or other files as you like

import csv
import logging
import sys

logger = logging.getLogger()
logging.basicConfig(filename="SupportBank.log", filemode="w", level=logging.DEBUG)
logger.debug("I am in the log file")

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
    with open(filename, mode='r') as file:
        reader = csv.DictReader(file)
        transactions = [Transaction(row) for row in reader]
        logger.info(f'{filename} read and transformed to list')
        return transactions

def List_All(transactions):
    accountsDict = {}

    for tx in transactions:
        for name in [tx.From, tx.To]:
            if name not in accountsDict:
                accountsDict[name] = Account(name)
        accountsDict[tx.From].apply_transaction(tx)
        accountsDict[tx.To].apply_transaction(tx)

    print("Balances:")
    for account in accountsDict.values():
        print(f"{account.name}: £{account.balance / 100:.2f}")
    print("If you wish to see a detailed list of transactions do the following:")
    print("poetry run list_account <account> <csv_filename>")

def cli_List_All():
    if len(sys.argv) < 2:
        print("Usage: poetry run List_All <csv_filename>")
        sys.exit(1)
    filename = f"./DataFiles/{sys.argv[1]}.csv"
    transactions = read_transactions(filename)
    List_All(transactions)

def List(account, transactions):
    for tx in transactions:
        if tx.From == account or tx.To == account:
            print(f"{tx.Date} | From: {tx.From} | To: {tx.To} | {tx.Narrative} | £{tx.Amount:.2f}")

def cli_List():
    if len(sys.argv) < 3:
        print("Usage: poetry run list_account <account> <csv_filename>")
        sys.exit(1)
    account = sys.argv[1]
    filename = f"./DataFiles/{sys.argv[2]}.csv"
    transactions = read_transactions(filename)
    List(account, transactions)
