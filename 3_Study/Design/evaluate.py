import time
from selenium import webdriver
from axe_selenium_python import Axe
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService

# Setup Selenium Webdriver
service = ChromeService(executable_path=ChromeDriverManager().install())

# Variables
pages_list = open("./pages-100.txt")
pages_tested = 0

# Run for each Webpage
for page in pages_list:
    driver = webdriver.Chrome(service=service)
    # Get page title
    page_title = page.replace("/","").replace(".","-").replace("https:","").replace("www.","")
    print(f"Now testing:{page_title}")
    # Start axe testing
    try:
        driver.get(page)
        axe=Axe(driver)
        axe.inject()
        results = axe.run()
        axe.write_results(results["violations"], f"./results/{page_title.strip()}.json")
        pages_tested += 1
    except:
        print(f"Failed for:{page_title}")
    driver.close()
    


print(f"Total pages tested: {pages_tested}")
