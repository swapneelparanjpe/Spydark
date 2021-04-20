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
import json
from googlesearch import search
from anytree import Node
from anytree.search import find_by_attr
from anytree.exporter import JsonExporter

def connect_mongodb(database, keyword):
    client = MongoClient("mongodb+srv://admin_db:kryptonite_DB12@crawling-cluster.exrzi.mongodb.net/surfacedb?retryWrites=true&w=majority")
    db = client[database]
    coll = db[keyword]
    return coll

def get_link_data(database, collection, link):
    coll = connect_mongodb(database, collection)
    document = coll.find_one({"Link":link})
    return list(document.items())[1:]

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
    topKeyValuePairs = list(wordc.words_.items())[:5]
    wordc.to_file('users/static/users/wc_img.png')
    wc_words.flush()
    wc_words.close()

    topFiveWords = []
    for topKeyValuePair in topKeyValuePairs:
        topFiveWords.append(topKeyValuePair[0])
    
    return topFiveWords


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
        try:
            links_texts.append([x["Link"], x["Page content"]])
        except Exception:
            pass
    return links_texts


def generate_wordcloud_dynamically(database, collections, crawled_choice):
    if database is None or collections is None:
        return False

    wc_words = open('users/static/users/wc_words.txt', 'w', encoding='utf-8')

    if crawled_choice < len(collections):

        coll = connect_mongodb(database, collections[crawled_choice])

        if database == "instagramdb" or database == "twitterdb":
            for x in coll.find():
                for hashtag in x["Hashtags"]:
                    wc_words.write(hashtag + "\n")

        elif database == "dark-key-db":
            for x in coll.find():
                try:
                    wc_words.write(x["Page content"] + "\n\n")
                except Exception:
                    pass

    else: 

        for collection in collections:

            coll = connect_mongodb(database, collection)

            if database == "instagramdb" or database == "twitterdb":
                for x in coll.find():
                    for hashtag in x["Hashtags"]:
                        wc_words.write(hashtag + "\n")

            elif database == "dark-key-db":
                for x in coll.find():
                    try:
                        wc_words.write(x["Page content"] + "\n\n")
                    except Exception:
                        pass

    _ = display_wordcloud(wc_words)


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
    
    def display_link_similarity(self, database, collections):
        if database is None or collections is None:
            return False
        
        links_all_dictionary = {}
        links_all = []
        no_of_links = []
        for collection in collections:
            links = []
            coll = connect_mongodb(database, collection)
            for x in coll.find():
                links.append(x["Link"])
                links_all.append(x["Link"])
            links_all_dictionary[collection] = links
            no_of_links.append(len(links))

        links_all = list(set(links_all))

        result_matrix = [[0 for _ in range(len(collections)+1)] for _ in range(len(links_all))]

        percentages = []

        all_count = 0
        for link, idx_link in zip(links_all, range(len(links_all))):
            for collection, idx_col in zip(collections, range(len(collections))):
                if link in links_all_dictionary[collection]:
                    result_matrix[idx_link][idx_col] = 1
            percentages.append(format(sum(100*result_matrix[idx_link])/len(collections), "0.2f") + "%")
            if sum(result_matrix[idx_link]) == len(collections):
                result_matrix[idx_link][-1] = 1
                all_count += 1
        
        return links_all, result_matrix, no_of_links, percentages, all_count

    def get_visited_keywords(self, platform_choice, link_or_content):
        database = None
        collection = None
        field = None
        if platform_choice == "1":
            database = "surfacedb"
            collection = "seed-urls-visited"
            field = "seed-url"
        elif platform_choice == "2":
            database = "instagramdb"
            collection = "keywords-visited"
            field = "keyword"
        elif platform_choice == "3":
            database = "twitterdb"
            collection = "keywords-visited"
            field = "keyword"
        elif platform_choice == "4":
            database = "dark-url-db"
            collection = "seed-urls-visited"
            field = "seed-url"
        else:
            database = "dark-key-db"
            collection = "keywords-visited"
            field = "Keyword"

        if link_or_content == "content":
            visited_keywords_choices = [(0,"--Select option--")]
            count = 1
        else:
            visited_keywords_choices = []
            count = 0

        coll = connect_mongodb(database, collection)
        for x in coll.find():
            visited_keywords_choices.append((count, x[field]))
            count += 1
        return database, visited_keywords_choices

    def get_visited_links(self, database, collection):
        if database is None or collection is None:
            return False
        visited_links_choices = [(0,"--Select option--")]
        count = 1
        coll = connect_mongodb(database, collection)
        for x in coll.find():
            visited_links_choices.append((count, x["Link"]))
            count += 1
        return visited_links_choices

    
    def get_page_content(self, link, collection, database):
        coll = connect_mongodb(database, collection)
        page_content = coll.find_one({"Link":link})["Page content"]
        return page_content

    def get_activity_period(self, link):
        coll = connect_mongodb("flagged-links", "darkweb-flagged")
        activity = coll.find_one({"Link":link})["Status"]
        percentage_activity = format(100*sum(activity)/len(activity), "0.2f")
        activity = json.dumps(activity)

        custom_activity = coll.find_one({"Link":link})["Custom"][0]
        custom_activity_matrix = []
        for key, value in custom_activity.items():
            custom_activity_matrix.append([key.split()[0], key.split()[1], "Active" if value else "Inactive"])

        return activity, percentage_activity, custom_activity_matrix

    def get_all_activity_period(self):
        coll = connect_mongodb("flagged-links", "darkweb-flagged")
        all_status = []
        max_length = -1
        custom_activity_all_matrix = []
        for x in coll.find():
            all_status.append(x["Status"][::-1])
            custom_activity_status = x["Custom"][0]
            custom_link_status_matrix = []
            for key, value in custom_activity_status.items():
                custom_link_status_matrix.append([key.split()[0], key.split()[1], "Active" if value else "Inactive"])
            custom_activity_all_matrix.append([x["Link"], len(custom_link_status_matrix)+1, custom_link_status_matrix])
            if len(x["Status"]) > max_length:
                max_length = len(x["Status"])

        active_links_period = []
        inactive_links_period = []
        for day in range(max_length):
            no_of_links = 0
            no_of_active_links = 0
            for status_idx in range(len(all_status)):
                try:
                    status = all_status[status_idx][day]
                    no_of_links += 1
                    no_of_active_links += status
                except Exception:
                    pass
            no_of_inactive_links = no_of_links - no_of_active_links
            active_links_period.append(no_of_active_links)
            inactive_links_period.append(no_of_inactive_links)

        percentage_activity = format(100*sum(active_links_period)/(sum(active_links_period) + sum(inactive_links_period)), "0.2f")
        active_links_period = json.dumps(active_links_period[::-1])
        inactive_links_period = json.dumps(inactive_links_period[::-1])
        return active_links_period, inactive_links_period, percentage_activity, custom_activity_all_matrix
        

    def get_unflagged_links(self, database, collection):
        if database is None or collection is None:
            return False

        flagged_links = []
        coll = connect_mongodb("flagged-links", "darkweb-flagged")
        for x in coll.find():
            flagged_links.append(x["Link"])

        unflagged_link_choices = []
        current_status = []
        count = 0
        coll = connect_mongodb(database, collection)
        for x in coll.find():
            if x["Link"] not in flagged_links:
                unflagged_link_choices.append((count, x["Link"]))
                current_status.append(x["Link status"])
                count += 1

        return unflagged_link_choices, current_status
        

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
            self.visitedcoll.insert_one({"seed-url":self.curr_link})
        
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
        wc_words = open('users/static/users/wc_words.txt', 'w', encoding='utf-8')

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

            parent = None
            link_count = 0
            for link in links:
                try:
                    print("Parsing link:", link)
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
                if link_count == 1:
                    parent = url
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
        wc_words = open('users/static/users/wc_words.txt', 'w', encoding='utf-8')

        if visited:
            for x in self.coll.find():
                links.append(x["Link"])
                for hashtag in x["Hashtags"]:
                    wc_words.write(hashtag + "\n")

        else:
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
        wc_words = open('users/static/users/wc_words.txt', 'w', encoding='utf-8')

        if visited:
            for x in self.coll.find():
                links.append(x["Link"])
                for hashtag in x["Hashtags"]:
                    wc_words.write(hashtag + "\n")
        
        else:
            
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
                    time.sleep(3)
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
                    print("Parsing failed: ", link)
                    continue
                self.coll.insert_one({"Link":link, "Posted by":account, "Image": images, "Caption":caption, "Hashtags":post_hashtags})
            self.driver.quit()
            self.visitedcoll.insert_one({"keyword":self.keyword})

        topFiveWords = display_wordcloud(wc_words)

        return links, topFiveWords