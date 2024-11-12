import os
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

from dotenv import load_dotenv

load_dotenv()
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

#settings
options = Options()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=options)

#login
driver.get("https://instagram.com")

username_element = WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.NAME, "username"))
)

username_element.send_keys(EMAIL)
pw_element = driver.find_element(By.NAME, "password")
pw_element.send_keys(PASSWORD)

username_element.submit()


#search
peoples = ["1hongjp"]

for name in peoples:
    url = f"https://www.instagram.com/{name}/"
    

#get: 게시물 날짜, 게시물 하트 개수, 게시물 댓글 개수

#스크롤 최대 N번??


# 날짜, 하트개수, 댓글 개수 가져옴
#1. (link, hearts, comments)
#2. link타고 들어가서 date
#3. df에 (name, link, hears, comments, date) 순으로 저장



#save
#df에 저장..

#driver.quit()

