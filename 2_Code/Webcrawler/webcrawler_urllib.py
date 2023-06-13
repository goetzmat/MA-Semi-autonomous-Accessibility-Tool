## Webcrawler pulling index.html from webpages defined in "pages.txt"
## M. Götz 2023
import requests
from bs4 import BeautifulSoup
pages_list = open("./pages-100.txt","r")


i = 0

for page in pages_list:
    filename = page[page.find(".")+1:]
    filename = filename[:filename.find(".")]
    print(filename)
    file = open(f"./Webcrawler/pages/{filename}.html","w",encoding="utf-8")
    i += 1
    page = page.strip()
    try:
        r = requests.get(page)
        soup = BeautifulSoup(r.content, "html.parser")

        file.write(soup.prettify())
        file.close()


    except Exception as ex:
        print(f"Download failed: {page} because {ex}")


