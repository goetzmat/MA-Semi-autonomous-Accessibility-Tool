import csv
import json


def Convert(lst):
    lst = lst.replace('[',"").replace("]","")
    lst = lst.split(",")
    return lst


website_csv = open("./overview.csv")
error_types = open("./error_types.csv","w+",newline='')

writer = csv.writer(error_types,delimiter=";")
writer.writerow(["Category,NoWebsites,Percentage,NoTotal"])

reader = csv.reader(website_csv,delimiter=";")
fst = True

##Data Format: ErrorType; NoWebsites; No Occurances
raw_csv = []
index = 0
no_websites = 0

## Process the input CSV File
for row in reader:
    # Check if row is the first line (with Field Names)
    if fst:
        fst = False
    else:
        list = Convert(row[3])
        no_websites += 1
        for listElement in list:
            # Check if element is an error type or number
            if "\'" in listElement:
                # If error type alreade has a number, add the occurences on Webpages, else append the List
                try:
                    index = raw_csv.index(listElement)
                    raw_csv[index+1] = raw_csv[index+1]+1
                except:
                    index = len(raw_csv)
                    raw_csv.append(listElement)
                    raw_csv.append(1)
                    raw_csv.append(0)
            else:
                raw_csv[index+2] = raw_csv[index+2] + int(listElement)
print(raw_csv)
print(no_websites)

## Write the Info to csv
while len(raw_csv) != 0:
    type = raw_csv.pop(0)
    no_websites_cat = raw_csv.pop(0)
    percentage = no_websites_cat / no_websites
    total = raw_csv.pop(0)
    writer.writerow([type,no_websites_cat,percentage,total])

