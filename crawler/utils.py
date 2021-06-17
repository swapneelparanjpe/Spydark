from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
from datetime import datetime
from wordcloud import WordCloud, STOPWORDS
from pymongo import MongoClient
from gridfs import GridFS
from googlesearch import search
import re


INSTAGRAM_USERNAME = "<username>"
INSTAGRAM_PASSWORD = "<password>"

MONGODB_CONNECTION = "<driver_code>"
CHROMEDRIVER_PATH = "chromedriver_win32\\chromedriver.exe"

def connect_mongodb(database, keyword):
    client = MongoClient(MONGODB_CONNECTION)
    db = client[database]
    coll = db[keyword]
    return coll

def connect_gridfs(database):
    client = MongoClient(MONGODB_CONNECTION)
    db = client[database]
    fs = GridFS(db)
    return fs

def store_images_in_db(database, images):
    fs = connect_gridfs(database)
    coll = connect_mongodb(database, "fs.files")
    for image in images:
        contents = requests.get(image[0]).content
        img_doc = coll.find_one({"filename":str(image[0])})
        if img_doc is not None:
            fs.delete(img_doc["_id"])
        fs.put(contents, filename=str(image[0]))

def addhistory(user, data):
    coll = connect_mongodb("user-history", user)
    now = datetime.now()
    history = {"Date": now.strftime("%d/%m/%Y"), "Time":now.strftime("%H:%M")}
    history.update(data)
    if coll.count()>=10:
        coll.find_one_and_delete({})
    coll.insert_one(history)

def display_wordcloud(wc_words, isLink = False):
    print("Generating Wordcloud...")
    stopwords = set(STOPWORDS)
    wordc = WordCloud(background_color="white", width=700, height=350, stopwords = stopwords)
    wc_words.seek(0)
    
    if isLink:
        wordc.generate(open('crawler/static/crawler/wc_words_link.txt', encoding='utf-8').read())
        wordc.to_file('crawler/static/crawler/wc_img_link.png')
    else:
        wordc.generate(open('crawler/static/crawler/wc_words.txt', encoding='utf-8').read())
        wordc.to_file('crawler/static/crawler/wc_img.png')

    topKeyValuePairs = list(wordc.words_.items())[:5]

    wc_words.flush()
    wc_words.close()

    topFiveWords = []
    for topKeyValuePair in topKeyValuePairs:
        topFiveWords.append(topKeyValuePair[0])
    
    return topFiveWords        

class SurfaceURL:
    def __init__(self, url, depth):
        self.seed_url = url
        self.curr_link = url
        self.depth = depth
        self.visitedcoll = connect_mongodb("surfacedb", "seed-urls-visited")
        self.coll = connect_mongodb("surfacedb", self.curr_link)

    def surfacecrawl(self):

        visited = False
        for _ in self.visitedcoll.find({"seed-url":self.curr_link}):
            visited = True

        wc_words = open('crawler/static/crawler/wc_words.txt', 'w', encoding='utf-8')

        if visited:
            links = []
            for x in self.coll.find():
                links.append(x["Link"])
                try:
                    wc_words.write(x["Page content"] + "\n\n")
                except Exception:
                    pass
                
        else:
            source = requests.get(self.curr_link).text
            curr_page = BeautifulSoup(source, 'lxml')
            no_pages = 1
            read_ptr = 0
            
            links = [self.curr_link]
            visited = []
            links_per_page = [1]

            while(no_pages <= self.depth):
                visited.append(self.curr_link)
                num_of_links = 0
                for anchor_tag in curr_page.find_all('a'):
                    try:
                        link = anchor_tag['href']
                        if link not in links:
                            links.append(link)
                            num_of_links += 1
                    except Exception:
                        pass 
                links_per_page.append(num_of_links)
                no_pages += 1

                while self.curr_link in visited:
                    read_ptr += 1
                    self.curr_link = links[read_ptr]
                source = requests.get(self.curr_link).text
                curr_page = BeautifulSoup(source, 'lxml') 

            print("Total links to parse:", len(links))
            print(">>>>>>>>PART 2>>>>>>>>>>>>>>")

            driver = webdriver.Chrome(CHROMEDRIVER_PATH)

            # TODO: Can try headless webdriver ->
            # chrome_options = Options()
            # chrome_options.add_argument("--headless")
            # driver = webdriver.Chrome(CHROMEDRIVER_PATH, chrome_options=chrome_options)

            parent = None
            link_count = 1
            idx = 1
            parent_idx = -1
            for link in links:
                print(link_count, "->", link)
                try:
                    source = requests.get(link).text
                    curr_page = BeautifulSoup(source, 'lxml')
                    title = curr_page.find('title').text
                    text = ' '.join(curr_page.text.split())
                    wc_words.write(text + "\n\n")
                    driver.get(link)
                    images = list(set([(str(element.get_attribute('src')), False) for element in driver.find_elements_by_tag_name('img')]))
                    store_images_in_db("surfacedb", images)
                    success = True
                except Exception as e:
                    print(str(e))
                    success = False
                if success:
                    print("Found")
                    self.coll.insert_one({"Link":link, "Title":title, "Page content":text, "Images": images, "Parent link":parent, "Successfully parsed":success})
                else:
                    print("Not found")
                    self.coll.insert_one({"Link":link, "Parent link":parent, "Successfully parsed":success})
                link_count += 1
                if sum(links_per_page[:idx])<link_count:
                    parent_idx += 1
                    parent = links[parent_idx]
                    idx += 1
            driver.quit()
            self.visitedcoll.insert_one({"seed-url":self.seed_url})
        
        topFiveWords = display_wordcloud(wc_words)
        
        return links, topFiveWords


class Google:

    def __init__(self, keyword, depth):
        self.keyword = keyword
        self.depth = depth
        self.visitedcoll = connect_mongodb("googledb", "keywords-visited")
        self.coll = connect_mongodb("googledb", self.keyword)

    def googlecrawl(self):

        visited = False
        for _ in self.visitedcoll.find({"keyword":self.keyword}):
            visited = True

        links = []
        wc_words = open('crawler/static/crawler/wc_words.txt', 'w', encoding='utf-8')

        if visited:
            for x in self.coll.find():
                links.append(x["Link"])
                try:
                    wc_words.write(x["Page content"] + "\n\n")
                except Exception:
                    pass
        
        else:
            
            url = "https://google.com/search?q={}".format('+'.join(self.keyword.split(' ')))
            links_found_on_google = list(search(self.keyword, num=25*(self.depth), stop=25*(self.depth), pause=4.0))
            links = [url] + links_found_on_google

            driver = webdriver.Chrome(CHROMEDRIVER_PATH)

            # TODO: Can try headless webdriver ->
            # chrome_options = Options()
            # chrome_options.add_argument("--headless")
            # driver = webdriver.Chrome(CHROMEDRIVER_PATH, chrome_options=chrome_options)

            parent = None
            link_count = 0
            for link in links:
                print(link_count, "->", link)
                try:
                    source = requests.get(link, timeout = 20).text
                    curr_page = BeautifulSoup(source, 'lxml')
                    title = curr_page.find('title').text
                    text = ' '.join(curr_page.text.split())
                    wc_words.write(text + "\n\n")
                    driver.get(link)
                    images = list(set([(element.get_attribute('src'), False) for element in driver.find_elements_by_tag_name('img')]))
                    store_images_in_db("googledb", images)
                    success = True
                except Exception:
                    success = False
                if success:
                    print("Found")
                    self.coll.insert_one({"Link":link, "Title":title, "Page content":text, "Images": images, "Parent link":parent, "Successfully parsed":success})
                else:
                    print("Not found")
                    self.coll.insert_one({"Link":link, "Parent link":parent, "Successfully parsed":success})
                
                link_count += 1
                if link_count == 1:
                    parent = url
            driver.quit()
            self.visitedcoll.insert_one({"keyword":self.keyword})

        topFiveWords = display_wordcloud(wc_words)
        
        return links, topFiveWords


class Instagram:

    def __init__(self, keyword, depth):
        self.keyword = keyword
        self.depth = depth
        self.visitedcoll = connect_mongodb("instagramdb", "keywords-visited")
        self.coll = connect_mongodb("instagramdb", self.keyword)

    def instacrawl(self):

        visited = False
        for _ in self.visitedcoll.find({"keyword":self.keyword}):
            visited = True
        
        links = []
        wc_words = open('crawler/static/crawler/wc_words.txt', 'w', encoding='utf-8')

        if visited:
            for x in self.coll.find():
                links.append(x["Link"])
                for hashtag in x["Hashtags"]:
                    wc_words.write(hashtag + "\n")

        else:
            driver = webdriver.Chrome(CHROMEDRIVER_PATH)

            # TODO: Can try headless webdriver ->
            # chrome_options = Options()
            # chrome_options.add_argument("--headless")
            # driver = webdriver.Chrome(CHROMEDRIVER_PATH, chrome_options=chrome_options)
            
            driver.get("https://www.instagram.com/")
            time.sleep(5)
            input_fields = driver.find_elements_by_xpath("//input")
            count = 0
            for input_field in input_fields:
                name = input_field.get_attribute("name")
                if name == 'username':
                    input_field.send_keys(INSTAGRAM_USERNAME)
                    count += 1
                elif name == 'password':
                    input_field.send_keys(INSTAGRAM_PASSWORD)
                    count += 1
                if count == 2:
                    break
            submit_btn = driver.find_element_by_xpath("//button[@type='submit']")
            submit_btn.send_keys(Keys.ENTER)
            time.sleep(5)

            url = "https://www.instagram.com/explore/tags/" + self.keyword + "/"
            driver.get(url)
            for _ in range(self.depth):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                link_elements = driver.find_elements_by_xpath("//*[@class='v1Nh3 kIKUG  _bz0w']/a")
                for link in link_elements:
                    try:
                        href = link.get_attribute('href')
                        if href not in links:
                            links.append(href)
                    except Exception:
                        pass
            
            
            for link in links:
                post_hashtags = []
                try:
                    driver.get(link)
                    account = driver.find_elements_by_xpath("//*[@id='react-root']/section/main/div/div[1]/article/div[3]/div[1]/ul/div/li/div/div/div[2]/h2/div/span/a")[0].get_attribute('href')
                    caption = driver.find_element_by_xpath("//*[@id='react-root']/section/main/div/div[1]/article/div[3]/div[1]/ul/div/li/div/div/div[2]/span").text.split("#")[0]
                    image = list(set([(str(driver.find_element_by_class_name("FFVAD").get_attribute('src')), False)]))
                    store_images_in_db("instagramdb", image)
                    try:
                        location = driver.find_element_by_xpath("//*[@id='react-root']/section/main/div/div[1]/article/header/div[2]/div[2]/div[2]/a").text
                    except Exception:
                        location = None
                    hashtags_found = driver.find_elements_by_class_name("xil3i")
                    for hashtag_found in hashtags_found:
                        post_hashtags.append(hashtag_found.text)
                        wc_words.write(hashtag_found.text + "\n")
                except Exception:
                    print("Parsing failed: ", link)
                    continue
                self.coll.insert_one({"Link":link, "Posted by":account, "Location":location, "Images":image, "Caption":caption, "Hashtags":post_hashtags})
            driver.quit()
            self.visitedcoll.insert_one({"keyword":self.keyword})

        topFiveWords = display_wordcloud(wc_words)

        return links, topFiveWords


class Twitter:
    def __init__(self, keyword, depth):
        self.keyword = keyword
        self.depth = depth
        self.visitedcoll = connect_mongodb("twitterdb", "keywords-visited")
        self.coll = connect_mongodb("twitterdb", self.keyword)

    def twittercrawl(self):

        visited = False
        for _ in self.visitedcoll.find({"keyword":self.keyword}):
            visited = True

        links = []
        wc_words = open('crawler/static/crawler/wc_words.txt', 'w', encoding='utf-8')

        if visited:
            for x in self.coll.find():
                links.append(x["Link"])
                for hashtag in x["Hashtags"]:
                    wc_words.write(hashtag + "\n")
        
        else:
            
            driver = webdriver.Chrome(CHROMEDRIVER_PATH)

            # TODO: Can try headless webdriver ->
            # chrome_options = Options()
            # chrome_options.add_argument("--headless")
            # driver = webdriver.Chrome(CHROMEDRIVER_PATH, chrome_options=chrome_options)

            url = "https://twitter.com/search?q=%23" + self.keyword + "&src=typed_query"
            driver.get(url)
            for _ in range(self.depth):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                anchor_tags = driver.find_elements_by_tag_name('a')
                for anchor_tag in anchor_tags:
                    href = anchor_tag.get_attribute("href")
                    if ("/status/" in href) and ("/photo/" not in href) and (href not in links):
                        links.append(href)

            for link in links:
                post_hashtags = []
                images = [] 
                try:
                    driver.get(link)
                    time.sleep(3)
                    account = link.split("/status/")[0]
                    img_elements = driver.find_elements_by_tag_name("img")
                    for image in img_elements:
                        if image.get_attribute("alt") == "Image":
                            images.append((str(image.get_attribute("src")), False))
                    caption_element = driver.find_element_by_xpath("//*[@id='react-root']/div/div/div[2]/main/div/div/div/div/div/div[2]/div/section/div/div/div[1]/div/div/article/div/div/div/div[3]/div[1]/div/div")
                    caption = caption_element.text
                    for span in caption_element.find_elements_by_xpath("./span"):
                        hashtag = re.findall("#[a-zA-Z0-9]+", span.text)
                        if len(hashtag) == 1:
                            post_hashtags.append(hashtag[0])
                            wc_words.write(hashtag[0] + "\n")
                    images = list(set(images))
                    store_images_in_db("twitterdb", images)
                except Exception:
                    print("Parsing failed: ", link)
                    continue
                self.coll.insert_one({"Link":link, "Posted by":account, "Images": images, "Caption":caption, "Hashtags":post_hashtags})
            driver.quit()
            self.visitedcoll.insert_one({"keyword":self.keyword})

        topFiveWords = display_wordcloud(wc_words)

        return links, topFiveWords