from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
from datetime import datetime
from wordcloud import WordCloud, STOPWORDS
from pymongo import MongoClient
import re

from anytree import Node
from anytree.search import find_by_attr
from anytree.exporter import JsonExporter


def connect_mongodb(database, keyword):
    client = MongoClient("mongodb+srv://admin_db:kryptonite_DB12@crawling-cluster.exrzi.mongodb.net/surfacedb?retryWrites=true&w=majority")
    db = client[database]
    coll = db[keyword]
    return coll


def addhistory(user, data):
    coll = connect_mongodb("user-history", user)
    now = datetime.now()
    history = {"Date": now.strftime("%d/%m/%Y"), "Time":now.strftime("%H:%M")}
    history.update(data)
    if coll.count()>=10:
        coll.find_one_and_delete({})
    coll.insert_one(history)

def display_wordcloud(wc_words):
    print("Generating Wordcloud...")
    stopwords = set(STOPWORDS)
    wordc = WordCloud(background_color="white", width=700, height=350, stopwords = stopwords)
    wc_words.seek(0)
    wordc.generate(open('users/static/users/wc_words.txt', encoding='utf-8').read())
    wordc.to_file('users/static/users/wc_img.png')
    wc_words.flush()
    wc_words.close()


def get_images(database, collection):
    if database is None or collection is None:
        return False
    links_images = []
    coll = connect_mongodb(database, collection)
    for x in coll.find():
        links_images.append([x["Link"], x["Image"]])
    return links_images

def get_text(database, collection):
    if database is None or collection is None:
        return False
    links_texts = []
    coll = connect_mongodb(database, collection)
    for x in coll.find():
        links_texts.append([x["Link"], x["Page content"]])
    return links_texts


class Dashboard:
    def read_db(self, database, collection):
        if database is None or collection is None:
            return False
        links = []
        coll = connect_mongodb(database, collection)
        for x in coll.find():
            links.append(x["Link"])
        return links

    def active_inactive(self, database, collection):
        if database is None or collection is None:
            return False
        coll = connect_mongodb(database, collection)
        active_links = coll.find({"Link status":"Active"}).count()        
        inactive_links = coll.find({"Link status":"Inactive"}).count()  
        return active_links, inactive_links

    def create_tree(self, database, collection):
        if database is None or collection is None:
            return False
        if database == "instagramdb" or database == "twitterdb":
            return False
        root = None
        coll = connect_mongodb(database, collection)
        for x in coll.find():
            link = x["Link"]
            parent = x["Parent link"]
            if parent:
                p = find_by_attr(root, parent)
                Node(link, parent = p)
            else:
                root = Node(link)
                
        exporter = JsonExporter(indent=2)
        j = exporter.export(root)
        return j


class SurfaceURL:
    def __init__(self, url, depth):
        self.curr_link = url
        self.depth = depth
        self.visitedcoll = connect_mongodb("surfacedb", "seed-urls-visited")
        self.coll = connect_mongodb("surfacedb", self.curr_link)

    def surfacecrawl(self):

        visited = False
        for _ in self.visitedcoll.find({"seed-url":self.curr_link}):
            visited = True

        wc_words = open('users/static/users/wc_words.txt', 'w', encoding='utf-8')

        if visited:
            links = []
            for x in self.coll.find():
                links.append(x["Link"])
                try:
                    wc_words.write(x["Page content"] + "\n\n")
                except Exception:
                    pass
                
        else:
            self.visitedcoll.insert_one({"seed-url":self.curr_link})
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

            parent = None
            link_count = 1
            idx = 1
            parent_idx = -1
            for link in links:
                try:
                    source = requests.get(link).text
                    curr_page = BeautifulSoup(source, 'lxml')
                    title = curr_page.find('title').text
                    text = ' '.join(curr_page.text.split())
                    wc_words.write(text + "\n\n")
                    success = True
                except Exception:
                    success = False
                if success:
                    self.coll.insert_one({"Link":link, "Title":title, "Page content":text, "Parent link":parent, "Successfully parsed":success})
                else:
                    self.coll.insert_one({"Link":link, "Parent link":parent, "Successfully parsed":success})
                link_count += 1
                if sum(links_per_page[:idx])<link_count:
                    parent_idx += 1
                    parent = links[parent_idx]
                    idx += 1
        
        display_wordcloud(wc_words)
        
        return links


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
        wc_words = open('users/static/users/wc_words.txt', 'w', encoding='utf-8')

        if visited:
            for x in self.coll.find():
                links.append(x["Link"])
                for hashtag in x["Hashtags"]:
                    wc_words.write(hashtag + "\n")

        else:
            self.visitedcoll.insert_one({"keyword":self.keyword})
            self.chrome_options = Options()
            # self.chrome_options.add_argument("--headless")
            self.driver = webdriver.Chrome("chromedriver_win32\\chromedriver.exe")#, chrome_options=self.chrome_options)
            
            self.driver.get("https://www.instagram.com/")
            time.sleep(5)
            input_fields = self.driver.find_elements_by_xpath("//input")
            count = 0
            for input_field in input_fields:
                name = input_field.get_attribute("name")
                if name == 'username':
                    input_field.send_keys("s_kurumkar99")
                    count += 1
                elif name == 'password':
                    input_field.send_keys("Sarveshkur99")
                    count += 1
                if count == 2:
                    break
            submit_btn = self.driver.find_element_by_xpath("//button[@type='submit']")
            submit_btn.send_keys(Keys.ENTER)
            time.sleep(5)

            url = "https://www.instagram.com/explore/tags/" + self.keyword + "/"
            self.driver.get(url)
            for _ in range(self.depth):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                link_elements = self.driver.find_elements_by_xpath("//*[@class='v1Nh3 kIKUG  _bz0w']/a")
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
                    self.driver.get(link)
                    account = self.driver.find_elements_by_xpath("//*[@id='react-root']/section/main/div/div[1]/article/div[3]/div[1]/ul/div/li/div/div/div[2]/h2/div/span/a")[0].get_attribute('href')
                    caption = self.driver.find_element_by_xpath("//*[@id='react-root']/section/main/div/div[1]/article/div[3]/div[1]/ul/div/li/div/div/div[2]/span").text.split("#")[0]
                    image = self.driver.find_element_by_class_name("FFVAD").get_attribute('src')
                    try:
                        location = self.driver.find_element_by_xpath("//*[@id='react-root']/section/main/div/div[1]/article/header/div[2]/div[2]/div[2]/a").text
                    except Exception:
                        location = None
                    hashtags_found = self.driver.find_elements_by_class_name("xil3i")
                    for hashtag_found in hashtags_found:
                        post_hashtags.append(hashtag_found.text)
                        wc_words.write(hashtag_found.text + "\n")
                except Exception:
                    print("Parsing failed: ", link)
                    continue
                self.coll.insert_one({"Link":link, "Posted by":account, "Location":location, "Image":image, "Caption":caption, "Hashtags":post_hashtags})
            self.driver.quit()

        display_wordcloud(wc_words)

        return links


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
        wc_words = open('users/static/users/wc_words.txt', 'w', encoding='utf-8')

        if visited:
            for x in self.coll.find():
                links.append(x["Link"])
                for hashtag in x["Hashtags"]:
                    wc_words.write(hashtag + "\n")
        
        else:
            self.visitedcoll.insert_one({"keyword":self.keyword})
            self.chrome_options = Options()
            # self.chrome_options.add_argument("--headless")
            self.driver = webdriver.Chrome("chromedriver_win32\\chromedriver.exe")#, chrome_options=self.chrome_options)

            url = "https://twitter.com/search?q=%23" + self.keyword + "&src=typed_query"
            self.driver.get(url)
            for _ in range(self.depth):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                anchor_tags = self.driver.find_elements_by_tag_name('a')
                for anchor_tag in anchor_tags:
                    href = anchor_tag.get_attribute("href")
                    if ("/status/" in href) and ("/photo/" not in href) and (href not in links):
                        links.append(href)

            for link in links:
                post_hashtags = []
                images = [] 
                try:
                    self.driver.get(link)
                    time.sleep(2)
                    account = link.split("/status/")[0]
                    img_elements = self.driver.find_elements_by_tag_name("img")
                    for image in img_elements:
                        if image.get_attribute("alt") == "Image":
                            images.append(image.get_attribute("src"))
                    caption_element = self.driver.find_element_by_xpath("//*[@id='react-root']/div/div/div[2]/main/div/div/div/div/div/div[2]/div/section/div/div/div[1]/div/div/article/div/div/div/div[3]/div[1]/div/div")
                    caption = caption_element.text
                    for span in caption_element.find_elements_by_xpath("./span"):
                        hashtag = re.findall("#[a-zA-Z0-9]+", span.text)
                        if len(hashtag) == 1:
                            post_hashtags.append(hashtag[0])
                            wc_words.write(hashtag[0] + "\n")
                except Exception:
                    continue
                self.coll.insert_one({"Link":link, "Posted by":account, "Image": images, "Caption":caption, "Hashtags":post_hashtags})
            self.driver.quit()

        display_wordcloud(wc_words)

        return links