from bs4 import BeautifulSoup
import requests
import sqlite3
from selenium import webdriver
import time

class Dashboard:
    def read_db(self):
        links = []
        conn = sqlite3.connect("crawler_database.db")
        c = conn.cursor()
        c.execute('''SELECT links from harvested_links''')
        links_arr = c.fetchall()
        for link in links_arr:
            links.append(link[0])
        return links

class LinkHarvest:
    def __init__(self, url, depth):
        self.url = url
        self.depth = depth

    def crawl(self):

        def add_link(link):
            with conn:
                c.execute("INSERT INTO harvested_links VALUES (:link)", {'link':link})

        conn = sqlite3.connect("crawler_database.db")
        c = conn.cursor()
        #c.execute('''CREATE TABLE harvested_links (
        #            links text
        #            )''')
        try:
            c.execute('DELETE FROM harvested_links')
            conn.commit()
        except:
            pass


        source = requests.get(self.url).text
        soup = BeautifulSoup(source, 'lxml')
        no_pages = 1
        db_pointer = 0
        links = []

        while(no_pages <= self.depth):

            for anchor_tags in soup.find_all('a'):
                try:
                    try:
                        link = "https://" + anchor_tags['href'].split("https://")[1]  
                    except:
                        link = "http://" + anchor_tags['href'].split("http://")[1]

                    add_link(link)
                    links.append(link)
                except Exception as e:
                    pass 
            no_pages += 1
            db_pointer += 1
            source = requests.get(links[db_pointer]).text
            soup = BeautifulSoup(source, 'lxml')
        conn.close()
        
        return links

class Instagram:
    def __init__(self, keyword, depth):
        self.keyword = keyword
        self.depth = depth
        self.driver = webdriver.Chrome("chromedriver_win32\chromedriver.exe")

    def instacrawl(self):
        
        url = "https://www.instagram.com/explore/tags/" + self.keyword + "/"
        self.driver.get(url)
        for i in range(self.depth):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        link_elements = self.driver.find_elements_by_xpath("//*[@class='v1Nh3 kIKUG  _bz0w']/a")
        links = []
        for link in link_elements:
            try:
                href = link.get_attribute('href')
                links.append(href)
            except:
                pass
        self.driver.quit()

        return links

class Twitter:
    def __init__(self, keyword, depth):
        self.keyword = keyword
        self.depth = depth
        self.driver = webdriver.Chrome("chromedriver_win32\chromedriver.exe")

    def twittercrawl(self):
        
        url = "https://twitter.com/search?q=%23" + self.keyword + "&src=typed_query"
        self.driver.get(url)
        for i in range(self.depth):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
        div_elements = self.driver.find_elements_by_xpath("//*[@id='react-root']/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div/section/div/div/div/div")
        print("DIV: ", div_elements)
        link_elements = []
        for div in div_elements:
            link_elements.append(div.find_element_by_xpath("./div/div/article/div/div/div/div[2]/div[2]/div[1]/div/div/div[1]/a"))
        print("LINK: ", link_elements)
        links = []
        for link in link_elements:
            try:
                href = link.get_attribute('href')
                links.append(href)
            except:
                pass
        self.driver.quit()

        return links



            # //*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div/section/div/div/div/div[5]/div/div/article/div/div/div/div[2]/div[2]/div[1]/div/div/div[1]/a
            # //*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div/section/div/div/div/div[9]/div/div/article/div/div/div/div[2]/div[2]/div[1]/div/div/div[1]/a
            # //*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div/div/div/section/div/div/div/div[1]/div/div/article/div/div/div/div[2]/div[2]/div[1]/div/div/div[1]/a
            # //*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div/div/div/section/div/div/div/div[3]/div/div/article/div/div/div/div[2]/div[2]/div[1]/div/div/div[1]/a
            # //*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div/div/div/section/div/div/div/div[3]/div/div/article/div/div/div/div[2]/div[2]/div[1]/div/div/div[1]






        