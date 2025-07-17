import csv
#this opens the csv file and then maps each line to a dictionary with the column headers as the keys.
with open ('./DataFiles/Transactions2014.csv', mode = 'r') as file:
    Transactions2014 = csv.DictReader(file)
    Transactions2014List = list(Transactions2014)

def extractAccounts(transactions):
    accountsList = []
    #loops through transactions adding all names to a list of accounts
    for lines in transactions:
        accountsList.append(lines['From'])
        accountsList.append(lines['To'])
    #removes duplicates
    accountsList = list(set(accountsList))
    accountsDict = {}
    #sets balance to 0 in account dictionary
    for account in accountsList:
        accountsDict[account] = 0

    for lines in Transactions2014List:
        accountsDict[lines['From']] -= int(float(lines['Amount'])*100)
        accountsDict[lines['To']] += int(float(lines['Amount'])*100)
    print(accountsList)
    print(accountsDict)

extractAccounts(Transactions2014List)


#TODO deal with rounding errors