import pandas as pd
import os
import time
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
from selenium import webdriver
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

def get_post_date(driver, url):
    driver.get(url)
    time.sleep(1)
    elements = driver.find_element(By.XPATH, "//time[@class='x1p4m5qa']")
    date = elements.get_attribute('title') #2024년 11월 12일
    
    return datetime.strptime(date, '%Y년 %m월 %d일') 

def binary_search_dates(driver, posts, target):
    left, right = 0,len(posts)-1
    urls = list(posts.values())

    while left < right:
        mid = (left+right)//2
        d = get_post_date(driver,urls[mid])
        if d <= target:
            right = mid
        else:
            left = mid + 1
    
    return left

def find_post_in_date(posts,before,after): #
    before = datetime.strptime(before, "%Y-%m-%d")
    after = datetime.strptime(after, "%Y-%m-%d")
    
    start_idx = binary_search_dates(driver,posts, after)
    #✋🏿: start_idx 다음부터 찾는걸로 리스트를 줄여도 될 듯
    end_idx = binary_search_dates(driver,posts, before)

    return (start_idx, end_idx)

def sum_likes_counts(driver,sr,sc,er,ec):
    total_likes = 0
    total_comments = 0
    
    for i in range(sr, er+1):  
        for j in range(sc if i == sr else 0, 3):  
            if i == er and j > ec:
                break
            
            focus = driver.find_element(By.XPATH, f'/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/div[2]/div/div[{i+1}]/div[{j+1}]')
            
            act = ActionChains(driver)
            act.move_to_element(focus).perform()
            time.sleep(1)
        
            both = focus.find_elements(By.XPATH, './a/div[3]/ul/li/span[1]/span')
            total_likes += int(both[0].text)
            total_comments += int(both[1].text)
    
    return (total_likes, total_comments)


def scraping(peoples, before, after):    
    ids = []
    likes = []
    comments = []
    followers = []
    
    for name in peoples:
        ids.append(name)
        url = f"https://www.instagram.com/{name}/reels"
        driver.get(url)
        time.sleep(1)
        
        #✋🏿: followers 수 추가

        #####✋🏿 urls scraping - def로 변환
        posts = {}
        
        n = 2 #스크롤 몇번 
        for _ in range(n):
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            time.sleep(1)
            #맨 아래면 break
        
        row_posts =  driver.find_elements(By.XPATH, '/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/div[2]/div/div')

        for r, row in enumerate(row_posts):
            threes_link = row.find_elements(By.XPATH, './div/a')
            for c, p in enumerate(threes_link):
                posts[(r,c)] = p.get_attribute('href')
        #####
        
        
        ##### 기간 내 div들 가져오기.
        start_idx, end_idx = find_post_in_date(posts,before, after)
        keys = list(posts.keys())
        print(start_idx, end_idx)
        sr,sc = keys[end_idx]
        er,ec = keys[start_idx]
        print(sr,sc,er,ec)
        #####
                
        #####받아온 (r,c)~(r,c) 좋아요 수, 댓글 수 얻기
        driver.get(url)
        total_likes, total_comments = sum_likes_counts(driver,sr,sc,er,ec)
        print(total_likes,total_comments)
        likes.append(total_likes)
        comments.append(total_comments)
        #####


    return (ids,likes,comments,followers)


def main():
    
    # ids = load_ids()
    ids = ["kwak_sang_eon"] #example1
    login()
    time.sleep(5)
    
    before = '2024-11-14'
    after = '2024-11-12'
    
    results = scraping(ids, before, after)
    ids, likes, comments, followers = results
    
    df = pd.DataFrame(data={
    'id' : ids,
    'likes' : likes,
    'comments' : comments,
    })
    
    print(df)


if __name__ == "__main__":
    main()