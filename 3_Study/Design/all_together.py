import os
import checker
import fixer
import traceback
import time 


## Open all log files
logging = open("./log.csv","w")
logging_fixer = open("./log_fix.csv","w")

## URL List

pages = open("./pages-100.txt","r")
pages = pages.readlines()

def geturl(name):
    for item in pages:
        if name in item:
            return item
            
## Write Header


logging.write("alt_text_missing,link_empty,h1_missing,heading_empty,heading_skipped,button_empty,lang_missing,region_missing,table_layout,noscript,alt_suspicious,event_handler,text_justified,text_small,heading_possible,internal_link_broken,link_redundant,alt_duplicate,link_suspicious,label_missing,title_redundant,alt_redundant,contrast,color_failed,text_size-failed,file\n")
logging_fixer.write("alt_text_missing,link_empty,h1_missing,heading_empty,heading_skipped,button_empty,lang_missing,region_missing,table_layout,noscript,alt_suspicious,event_handler,text_justified,text_small,heading_possible,internal_link_broken,link_redundant,alt_duplicate,link_suspicious,label_missing,title_redundant,alt_redundant,contrast,color_failed,text_size-failed,link_info_failed,alt_creation_failed,file\n")


import shutil

named_tuple = time.localtime() # get struct_time
time_string = time.strftime("Start : %m/%d/%Y, %H:%M:%S", named_tuple)
print(time_string)

rootdir = 'C:/Users/mathi/OneDrive/Dokumente/GitHub/Masterarbeit/Umsetzung/pages'
os.chdir(rootdir)

for file in os.listdir():
    if not os.path.isdir(file):
        try:
            value = checker.run(file)
            logging.write(value)
            logging.write("\n")
            url = geturl(file.replace(".html","")).replace("\n","")
            print(repr(url))
            fixed = fixer.run(file,url)
            print(fixed)
            logging_fixer.write(fixed)
            logging_fixer.write("\n")

        except Exception as ex:
            print(ex)
            print(traceback.format_exc())




logging.write("\n\nFixed\n")
logging.write("alt_text_missing,link_empty,h1_missing,heading_empty,heading_skipped,button_empty,lang_missing,region_missing,table_layout,noscript,alt_suspicious,event_handler,text_justified,text_small,heading_possible,internal_link_broken,link_redundant,alt_duplicate,link_suspicious,label_missing,title_redundant,alt_redundant,contrast,color_failed,text_size-failed,file\n")


rootdir = 'C:/Users/mathi/OneDrive/Dokumente/GitHub/Masterarbeit/Umsetzung/pages/out'
os.chdir(rootdir)

for file in os.listdir():
        try:
            value = checker.run(file)
            logging.write(value)
            logging.write("\n")

        except Exception as ex:
            print(ex)
            print(traceback.format_exc())

print(time_string)
named_tuple = time.localtime() # get struct_time
time_string = time.strftime("End: %m/%d/%Y, %H:%M:%S", named_tuple)
print(time_string)


logging.close()
logging_fixer.close()



