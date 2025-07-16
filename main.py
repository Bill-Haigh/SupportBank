import csv
#this opens the csv file and then maps each line to a dictionary with the column headers as the keys.
with open ('./DataFiles/Transactions2014.csv', mode = 'r') as file:
    Transactions2014 = csv.DictReader(file)
    for lines in Transactions2014:
        print(lines)