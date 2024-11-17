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
EMAIL = os.getenv("EMAIL3")
PASSWORD = os.getenv("PASSWORD3")

#settings
options = Options()
options.add_experimental_option("detach", True)
# options.add_argument("headless")
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
    element = WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.XPATH, '//article[@role="presentation"]'))
)
    date = element.find_element(By.CSS_SELECTOR, 'time').get_attribute('datetime')
    date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')
    
    driver.back()
    time.sleep(1)
    
    return date

#dynamic 때문에 쓸 수가 없나?
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
    


def collect_reels_posts(driver,before,after):
    SCROLL_PAUSE_TIME = 2  
    last_height = driver.execute_script("return document.body.scrollHeight")
    all_posts = set() 
    
    likes, comments, watchers = 0,0,0
    count = 0
    stop = False
    while True:
        posts = driver.find_elements(By.CSS_SELECTOR, 'div._aajz')  
                # Identify new posts by checking difference
        new_posts = [post for post in posts if post not in all_posts]
        if new_posts:
            for post in new_posts:
                date = get_post_date(driver, post)
                result = [0,0,0]
                
                if date < after: #기간 전이면 break(이후 게시물은 없으니까)
                    stop = True
                    break
                elif date > before: #기간 후면 넘어가기
                    continue
                elif (date >= after and date <= before):
                    count += 1
                    values = []
                  
                    attrs = post.find_elements(By.CSS_SELECTOR, 'span.html-span')
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
                            
                likes += result[0]
                comments += result[1]
                watchers += result[2]
                
                print("중간점검",count, result[0], result[1], result[2])

        all_posts.update(posts)
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        time.sleep(SCROLL_PAUSE_TIME)

        # Check if we've reached the bottom
        new_height = driver.execute_script("return document.body.scrollHeight")
        if stop or new_height == last_height:
            break
        last_height = new_height

    return likes, comments, watchers, count

    
def scraping(df, before, after):    
    ids = []
    likes = []
    comments = []
    watches = []
    followers = []
    cnts = []
    start_dates = []
    end_dates = []
    
    row_start = 100
    row_end = 200
    peoples = df.iloc[row_start:row_end,0]
    
    for idx, name in enumerate(peoples):
        print(name)
        
        if name =='없음':
            ids.append(name)
            likes.append(0)
            comments.append(0)
            watches.append(0)
            followers.append(0)
            cnts.append(0)
            
            continue

        
        ids.append(name)
        url = f"https://www.instagram.com/{name}/reels"
        driver.get(url)
        time.sleep(1)
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'header span.html-span'))
        )
        headers = driver.find_elements(By.CSS_SELECTOR, 'header span.html-span')
        f = headers[1].get_attribute('textContent').strip()

        l, c, w, cnt = collect_reels_posts(driver, before, after)
            

        followers.append(f)
        likes.append(l)
        comments.append(c)
        watches.append(w)
        cnts.append(cnt)
    
        print(name, l, c, w, f, cnt)
        

    return ids, likes, comments, watches, followers, cnt


def main():

    peoples = pd.read_excel("files/ids.xlsx",sheet_name ="main sheet")
    df = pd.DataFrame()
     
    login()
    time.sleep(5)
    
    ##수정
    before = '2024-04-10'
    after = '2023-12-12'
    before = datetime.strptime(before, "%Y-%m-%d")
    after = datetime.strptime(after, "%Y-%m-%d")
        
    ids, likes, comments, watches, followers, cnts= scraping(peoples, before, after)
  
    driver.quit()
    
    df["id"] = ids
    df["릴스 개수"] = cnts
    df["좋아요 총개수"] = likes
    df["댓글 총개수"] = comments
    df["릴스 조회수"] = watches
    df["팔로워 수"] = followers


    print(df)
    
    df.to_excel('output3.xlsx')


if __name__ == "__main__":
    main()