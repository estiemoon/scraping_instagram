import pandas as pd
import os
import time
from datetime import datetime
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

from selenium.common.exceptions import NoSuchElementException, TimeoutException

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


def get_post_date(driver, p):
    
    p.click()
    time.sleep(1)
    
    element = p.find_element(By.XPATH, "//article[@role='presentation']")
    date = element.find_element(By.CSS_SELECTOR, 'time').get_attribute('datetime')
    date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')
    
    driver.back()
    time.sleep(1)
    
    return date

def binary_search_dates(driver, posts, target):
    left, right = 0,len(posts)-1

    while left < right:
        mid = (left+right)//2
        d = get_post_date(driver,posts[mid])
        if d <= target:
            right = mid
        else:
            left = mid + 1
    
    return left


def find_post_in_date(posts, before, after):
    
    start_idx = binary_search_dates(driver,posts,before)
    end_idx  = binary_search_dates(driver, posts,after)
    
    return start_idx, end_idx

def check_date(driver, all_posts,s,e):
    print("checkdate s e", s,e)
    end = all_posts[s]
    start = all_posts[e]
    
    end_date = get_post_date(driver, end)
    start_date = get_post_date(driver, start)
    
    return end_date, start_date
    
    
#e after,s before
def sum_likes_counts(driver,all_posts, e,s):
    posts = all_posts[s:e+1]
    result = [0,0,0]
    for p in posts:
        values = []
        attrs = p.find_elements(By.CSS_SELECTOR, 'span.html-span')
        for t in attrs:
            values.append(t.get_attribute('textContent').strip())
        
        for i,attr in enumerate(result):
            try:
                v = list(values[i])
                if '만' in v:
                    values[i] = int(float(values[i].replace("만", "")) * 10000)
            
                result[i] += int(values[i])
            except IndexError:
                result[i] += 0  
                
    likes, comments, watches = result[0],result[1],result[2]
        
    return likes, comments, watches
        
def scraping(df, before, after):    
    ids = []
    likes = []
    comments = []
    watches = []
    followers = []
    cnt = []
    start_dates = []
    end_dates = []
    
    peoples = df.iloc[:,0]
    
    for idx, name in enumerate(peoples):
        print(name)
        
        if name =='없음':
            ids.append("none")
            likes.append("none")
            comments.append("none")
            watches.append("none")
            followers.append("none")
            start_dates.append("none")
            end_dates.append("none")
            cnt.append("none")
            continue
        elif df.iloc[idx,6]:
            continue

        
        ids.append(name)
        url = f"https://www.instagram.com/{name}/reels"
        driver.get(url)
        time.sleep(1)
        
        headers = driver.find_elements(By.CSS_SELECTOR, 'header span.html-span')
        f = headers[1].get_attribute('textContent').strip()

        n = 12 #스크롤 몇번 
        for _ in range(n):
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            time.sleep(2)
            
        all_posts = driver.find_elements(By.CSS_SELECTOR,'div._aajz')
        
        print(len(all_posts))
        s, e = find_post_in_date(all_posts,before, after) #start index=before, end index=after
        print("index" ,s,e)
        time.sleep(1)
        
        end_date, start_date = check_date(driver,all_posts, s,e)
        time.sleep(1)
        
        l, c, w = sum_likes_counts(driver,all_posts, e,s)
        
        start_dates.append(start_date)
        end_dates.append(end_date)
        
        followers.append(f)
        likes.append(l)
        comments.append(c)
        watches.append(w)
        cnt.append(s-e)
    
        print(name, l, c, w, f, s-e, start_date, end_date)
        

    return ids, likes, comments, watches, followers, cnt, start_dates, end_dates


def main():
    try:
        peoples = pd.read_excel("files/ids.xlsx",sheet_name ="main sheet")
        df = pd.DataFrame()
        
        login()
        time.sleep(5)
        
        ##수정
        before = '2024-04-10'
        after = '2023-12-12'
        before = datetime.strptime(before, "%Y-%m-%d")
        after = datetime.strptime(after, "%Y-%m-%d")
            
        ids, likes, comments, watches, followers, cnt, start_date, end_date = scraping(peoples, before, after)

    except NoSuchElementException:
        df["id"] = ids
        df["릴스 개수"] = cnt
        df["좋아요 총개수"] = likes
        df["댓글 총개수"] = comments
        df["릴스 조회수"] = watches
        df["팔로워 수"] = followers
        df["수집 시작 날짜"] = start_date
        df["수집 마지막 날짜"] = end_date
        
        df.to_excel('output.xlsx')
        return
    except TimeoutException:
        df["id"] = ids
        df["릴스 개수"] = cnt
        df["좋아요 총개수"] = likes
        df["댓글 총개수"] = comments
        df["릴스 조회수"] = watches
        df["팔로워 수"] = followers
        df["수집 시작 날짜"] = start_date
        df["수집 마지막 날짜"] = end_date
        
        df.to_excel('output.xlsx')
        
    driver.quit()
    
    df["id"] = ids
    df["릴스 개수"] = cnt
    df["좋아요 총개수"] = likes
    df["댓글 총개수"] = comments
    df["릴스 조회수"] = watches
    df["팔로워 수"] = followers
    df["수집 시작 날짜"] = start_date
    df["수집 마지막 날짜"] = end_date

    print(df)
    
    df.to_excel('output.xlsx')


if __name__ == "__main__":
    main()