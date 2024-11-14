import pandas as pd
import os
import time

from dotenv import load_dotenv
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

load_dotenv()
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

#settings
options = Options()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=options)

#login
def login():
    driver.get("https://instagram.com")

    username_element = WebDriverWait(driver, 50).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )

    username_element.send_keys(EMAIL)
    pw_element = driver.find_element(By.NAME, "password")
    pw_element.send_keys(PASSWORD)

    username_element.submit()


#search
def load_ids():
    xlsx = pd.read_excel("peoples.xlsx",sheet_name ="main sheet")
    ids = xlsx.iloc[:,6] 
    instagram_ids = ids[ids != "없음"]
    
    return list(instagram_ids)

def scraping(peoples):    
    ids = []
    likes = []
    comments = []
    
    for name in peoples:
        ids.append(name)
        links = []
        total_likes = 0
        total_comments = 0
        time.sleep(1)
        
        url = f"https://www.instagram.com/{name}"
        driver.get(url)

        n = 2 #스크롤 몇번 
        for _ in range(n):
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
            time.sleep(1)
        
        row_posts =  driver.find_elements(By.XPATH, '/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/div[2]/div/div')

        for row in row_posts:
            threes_link = row.find_elements(By.XPATH, './div/a')
            for p in threes_link:
                links.append(p.get_attribute('href'))
                
                
            
            threes = row.find_elements(By.XPATH, './div')
            for p in threes:
                act = ActionChains(driver)
                act.move_to_element(p).perform()
                time.sleep(1)
                
                both = p.find_elements(By.XPATH, './a/div[3]/ul/li/span[1]/span')
                total_likes += int(both[0].text)
                total_comments += int(both[1].text)


        likes.append(total_likes)
        comments.append(total_comments)

        driver.quit()

    return (ids,likes,comments)


def main():
    
    # ids = load_ids()
    ids = ["kwak_sang_eon"]
    login()
    time.sleep(5)
    results = scraping(ids)
    ids, likes, comments = results
    
    df = pd.DataFrame(data={
    'id' : ids,
    'likes' : likes,
    'comments' : comments,
    })
    
    print(df)


if __name__ == "__main__":
    main()