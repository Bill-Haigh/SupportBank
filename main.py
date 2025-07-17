import csv
#this opens the csv file and then maps each line to a dictionary with the column headers as the keys.
with open ('./DataFiles/Transactions2014.csv', mode = 'r') as file:
    Transactions2014 = csv.DictReader(file)
    Transactions2014List = list(Transactions2014)
    accountsList = []
    #loops through transactions adding all names to a list of accounts
    for lines in Transactions2014List:
       accountsList.append(lines['From'])
       accountsList.append(lines['To'])
    #removes duplicates
    accountsList = list(set(accountsList))
    accountsDict = {}
    #sets balance to 0 in account dictionary
    for account in accountsList:
        accountsDict[account] = 0

    for lines in Transactions2014List:
        accountsDict[lines['From']] -= float(lines['Amount'])
        accountsDict[lines['To']] += float(lines['Amount'])


print(accountsList)
print(accountsDict)

#TODO deal with rounding errors