
#! I am aware that I havent quite got there with making the scripts run correctly. WIP.
#! I am also aware that I have used a mixture of camel/snake/etc will tidy up at the end.

import csv
import logging
logger = logging.getLogger()
logging.basicConfig(filename='SupportBank.log', filemode='w', level=logging.DEBUG)
logger.debug('I am in the log file')

with open ('./DataFiles/Transactions2014.csv', mode = 'r') as file:
    Transactions2014 = csv.DictReader(file)
    Transactions2014List = list(Transactions2014)
    logger.info('Transactions2014 read and transoformed to list')

with open ('./DataFiles/DodgyTransactions2015.csv', mode = 'r') as file:
    Transactions2015 = csv.DictReader(file)
    Transactions2015List = list(Transactions2015)
    logger.info('Transactions2015 read and transoformed to list')

def List_All(transactions):
    accountsList = []
    for lines in transactions:
        accountsList.append(lines['From'])
        accountsList.append(lines['To'])
    accountsList = list(set(accountsList))
    accountsDict = {}
    for account in accountsList:
        accountsDict[account] = 0

    for lines in Transactions2014List:
        accountsDict[lines['From']] -= int(float(lines['Amount'])*100)
        accountsDict[lines['To']] += int(float(lines['Amount'])*100)
    print(accountsList)
    print(accountsDict)

def List(account, transactions):
    listOfTransactions = []
    for lines in transactions:
        if lines['From'] == account or lines['To'] == account:
            listOfTransactions.append(lines)
            print(lines)
    #print(listOfTransactions)


def Test():
    print("that worked")




#List_All(Transactions2014List)
#List('Rob S', Transactions2014List)
List_All(Transactions2015List)
List('Sarah T', Transactions2015List)



