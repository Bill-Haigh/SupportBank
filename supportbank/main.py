#! I am also aware that I have used a mixture of camel/snake/etc will tidy up at the end. Also why doesnt python have multi-line comments

import csv
import json
import logging
from datetime import datetime
import os
import xml.etree.ElementTree as ET

logger = logging.getLogger()
logging.basicConfig(filename="SupportBank.log", filemode="w", level=logging.DEBUG)
logger.info("Logging started.")


class Transaction:
    def __init__(self, data):
        self.Date = data.get("Date") or data.get("date")
        self.From = (
            data.get("From") or data.get("fromAccount") or data.get("FromAccount")
        )
        self.To = data.get("To") or data.get("toAccount") or data.get("ToAccount")
        self.Narrative = data.get("Narrative") or data.get("narrative")
        amount = data.get("Amount") or data.get("amount")
        self.Amount = float(amount)


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
    transactions = []
    if filename.endswith(".csv"):
        with open(filename, mode="r") as file:
            reader = csv.DictReader(file)
            line_number = 2
            for row in reader:
                try:
                    float(row["Amount"])
                    datetime.strptime(row["Date"], "%d/%m/%Y")
                    transaction = Transaction(row)
                    transactions.append(transaction)
                except ValueError as e:
                    account_name = row.get("From", "UNKNOWN")
                    logger.warning(
                        f"Invalid transaction on line {line_number}: {row} — {e}"
                    )
                    print(
                        f"Skipped invalid transaction on line {line_number} involving account '{account_name}'. See log for details."
                    )
                line_number += 1
    elif filename.endswith(".json"):
        with open(filename, mode="r") as file:
            try:
                data = json.load(file)
                for idx, row in enumerate(data, start=1):
                    try:
                        amount = row.get("Amount") or row.get("amount")
                        float(amount)
                        date_val = row.get("Date") or row.get("date")
                        parsed = False
                        for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"):
                            try:
                                datetime.strptime(date_val, fmt)
                                parsed = True
                                break
                            except (ValueError, TypeError):
                                continue
                        if not parsed:
                            raise ValueError(f"Unrecognized date format: {date_val}")
                        transaction = Transaction(row)
                        transactions.append(transaction)
                    except ValueError as e:
                        account_name = (
                            row.get("From")
                            or row.get("fromAccount")
                            or row.get("FromAccount")
                            or "UNKNOWN"
                        )
                        logger.warning(
                            f"Invalid transaction in JSON at index {idx}: {row} — {e}"
                        )
                        print(
                            f"Skipped invalid transaction in JSON at index {idx} involving account '{account_name}'. See log for details."
                        )
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON file {filename}: {e}")
                print(f"Failed to parse JSON file: {e}")
    elif filename.endswith(".xml"):
        try:
            from datetime import timedelta

            tree = ET.parse(filename)
            root = tree.getroot()
            for idx, elem in enumerate(root.findall("SupportTransaction"), start=1):
                try:
                    # Date is an attribute, value is a child, parties are nested
                    date_val = elem.attrib.get("Date")
                    # Excel date serial to datetime
                    try:
                        excel_epoch = datetime(1899, 12, 30)
                        date_obj = excel_epoch + timedelta(days=int(float(date_val)))
                        date_val_fmt = date_obj.strftime("%d/%m/%Y")
                    except Exception:
                        date_val_fmt = date_val
                    amount = float(elem.find("Value").text)
                    narrative = elem.find("Description").text
                    parties = elem.find("Parties")
                    from_account = (
                        parties.find("From").text
                        if parties is not None and parties.find("From") is not None
                        else None
                    )
                    to_account = (
                        parties.find("To").text
                        if parties is not None and parties.find("To") is not None
                        else None
                    )

                    transaction_dict = {
                        "Date": date_val_fmt,
                        "date": date_val_fmt,
                        "From": from_account,
                        "fromAccount": from_account,
                        "FromAccount": from_account,
                        "To": to_account,
                        "toAccount": to_account,
                        "ToAccount": to_account,
                        "Narrative": narrative,
                        "narrative": narrative,
                        "Amount": amount,
                        "amount": amount,
                    }
                    transaction = Transaction(transaction_dict)
                    transactions.append(transaction)
                except (ValueError, AttributeError) as e:
                    logger.warning(
                        f"Invalid transaction in XML at index {idx}: {elem} — {e}"
                    )
                    print(
                        f"Skipped invalid transaction in XML at index {idx}. See log for details."
                    )
        except ET.ParseError as e:
            logger.error(f"Failed to parse XML file {filename}: {e}")
            print(f"Failed to parse XML file: {e}")
    else:
        print("Unsupported file type. Only .csv, .json, and .xml are supported.")
        logger.warning(f"Unsupported file type: {filename}")
    logger.info(f"{filename} read with {len(transactions)} valid transactions")
    return transactions


def List_All(transactions):
    accountsDict = {}
    logger.info("showing account balances")
    for tx in transactions:
        for name in [tx.From, tx.To]:
            if name is None:
                continue
            if name not in accountsDict:
                accountsDict[name] = Account(name)
        if tx.From is not None:
            accountsDict[tx.From].apply_transaction(tx)
        if tx.To is not None:
            accountsDict[tx.To].apply_transaction(tx)

    print("Balances:")
    for account in accountsDict.values():
        print(f"{account.name}: £{account.balance / 100:.2f}")

    logger.info("Accounts and balances displayed successfully")


def list_available_data_files():
    data_dir = "./DataFiles"
    try:
        files = [
            f
            for f in os.listdir(data_dir)
            if f.endswith(".csv") or f.endswith(".json") or f.endswith(".xml")
        ]
        if not files:
            print("No CSV or JSON files found in ./DataFiles/")
            logger.warning("No CSV, JSON, or XML files found in ./DataFiles/")
        else:
            print("Available data files:")
            for f in files:
                print(f" - {f}")
            logger.info("Available data files listed")
        return files
    except FileNotFoundError:
        print("The ./DataFiles directory does not exist")
        logger.warning("The ./DataFiles directory does not exist")
        return []


def List(account, transactions):
    account_found = False
    logger.info(f"listing transactions for {account}")
    for tx in transactions:
        if tx.From == account or tx.To == account:
            account_found = True
            print(
                f"{tx.Date} | From: {tx.From} | To: {tx.To} | {tx.Narrative} | £{tx.Amount:.2f}"
            )
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
            available = list_available_data_files()
            if not available:
                continue
            filename = input(
                "Enter filename (with extension .csv, .json, or .xml): "
            ).strip()
            if not (
                filename.endswith(".csv")
                or filename.endswith(".json")
                or filename.endswith(".xml")
            ):
                print(
                    "Invalid file extension. Please enter a .csv, .json, or XML file."
                )
                continue
            try:
                transactions = read_transactions(f"./DataFiles/{filename}")
                List_All(transactions)
            except FileNotFoundError:
                print("File not found.")
        elif choice == "2":
            account = input("Enter account name: ").strip()
            available = list_available_data_files()
            if not available:
                continue
            filename = input(
                "Enter filename (with extension .csv, .json, or .xml): "
            ).strip()
            if not (
                filename.endswith(".csv")
                or filename.endswith(".json")
                or filename.endswith(".xml")
            ):
                print(
                    "Invalid file extension. Please enter a .csv, .json, or XML file."
                )
                continue
            try:
                transactions = read_transactions(f"./DataFiles/{filename}")
                List(account, transactions)
            except FileNotFoundError:
                print("File not found.")

        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
