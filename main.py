import csv
#this opens the csv file and then maps each line to a dictionary with the column headers as the keys.
with open ('./DataFiles/Transactions2014.csv', mode = 'r') as file:
    Transactions2014 = csv.DictReader(file)
    accountsList = []
    #loops through transactions adding all names to a list of accounts
    for lines in Transactions2014:
       accountsList.append(lines['From'])
       accountsList.append(lines['To'])
    #removes duplicates
    accountsList = list(set(accountsList))
    accountsDict = {}
    #sets balance to 0 in account dictionary
    for account in accountsList:
        accountsDict[account] = 0

#i am unsure why it requires me to open a with block again
#adds the transactions to the accounts in the dictionary
with open ('./DataFiles/Transactions2014.csv', mode = 'r') as file:
    Transactions2014 = csv.DictReader(file)
    for lines in Transactions2014:
        accountsDict[lines['From']] -= float(lines['Amount'])
        accountsDict[lines['To']] += float(lines['Amount'])


print(accountsList)
print(accountsDict)

#TODO deal with rounding errors