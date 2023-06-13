import os
import json
import csv

directory = 'results'
## Create Overview CSV
overview_csv = open("overview.csv","w",newline='')
writer = csv.writer(overview_csv,delimiter=";")
writer.writerow(["PageTitle","No.ErrorTypes","ErrorsTotal","ErrorDetails"])

for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    if os.path.isfile(f):
        f = open(f,"r").read()
        #print(f)
        if f != "":
            print(f"Parsing {filename}")
            json_file = json.loads(f)
            site_stats = [filename,len(json_file)]
            site_categories = []
            total_errors = 0
            print(len(json_file))
            for element in json_file:
                site_categories.append(element['id'])
                site_categories.append(len(element['nodes']))
                total_errors += len(element['nodes'])
            site_stats.append(total_errors)
            site_stats.append(site_categories)
            writer.writerow(site_stats)
        else:
            print(f"Fehler bei {filename}")