#! I am also aware that I have used a mixture of camel/snake/etc will tidy up at the end. Also why doesnt python have multi-line comments
# TODO change to classes "accounts" and "transactions"
#! Now in the console you can run "poetry run List_All Transactions2014" or other files as you like

import csv
import logging
import sys

logger = logging.getLogger()
logging.basicConfig(filename="SupportBank.log", filemode="w", level=logging.DEBUG)
logger.debug("I am in the log file")

def read_transactions(filename):
    with open(filename, mode='r') as file:
        reader = csv.DictReader(file)
        transactions = list(reader)
        logger.info(f'{filename} read and transformed to list')
        return transactions

def List_All(transactions):
    accountsList = []
    for lines in transactions:
        accountsList.append(lines["From"])
        accountsList.append(lines["To"])
    accountsList = list(set(accountsList))
    accountsDict = {}
    for account in accountsList:
        accountsDict[account] = 0

    for lines in transactions:
        accountsDict[lines["From"]] -= int(float(lines["Amount"]) * 100)
        accountsDict[lines["To"]] += int(float(lines["Amount"]) * 100)
    print(accountsList)
    print(accountsDict)

def cli_List_All():
    if len(sys.argv) < 2:
        print("Usage: poetry run List_All <csv_filename>")
        sys.exit(1)
    filename = f"./DataFiles/{sys.argv[1]}.csv"
    transactions = read_transactions(filename)
    List_All(transactions)

def List(account, transactions):
    listOfTransactions = []
    for lines in transactions:
        if lines["From"] == account or lines["To"] == account:
            listOfTransactions.append(lines)
            print(lines)