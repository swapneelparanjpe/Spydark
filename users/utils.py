from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
import mariadb
from wordcloud import WordCloud, STOPWORDS

def connect_mariadb():
    try:
        conn = mariadb.connect(
            user="root",
            password="mariaDB_dbms",
            host="localhost",
            database="crawlerdb")
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
    return conn


class Dashboard:
    def read_db(self, table):
        links = []
        conn = connect_mariadb()
        cur = conn.cursor()
        cur.execute("select * from {}".format(table))
        links_arr = cur.fetchall()
        hashtags = []
        for link in links_arr:
            links.append(link[0])
            # source = requests.get(link[0]).text
            # soup = BeautifulSoup(source, 'lxml')
            # meta_tags = soup.find_all("a", {"class":" xil3i"})
            # for meta_tag in meta_tags:
            #     try:
            #         hashtags.append(meta_tag.text[1:])
            #     except Exception:
            #         pass
        conn.close()
        # stopwords = set(STOPWORDS)
        # wordc = WordCloud(background_color="white", stopwords = stopwords)
        # wordc.generate("{}".format(hashtags))
        # wordc.to_file('users/static/users/words.png')

        return links

class LinkHarvest:
    def __init__(self, url, depth):
        self.url = url
        self.depth = depth

    def crawl(self):

        # def add_link(link):
        #     with conn:
        #         c.execute("INSERT INTO harvested_links VALUES (:link)", {'link':link})

        conn = connect_mariadb()
        cur = conn.cursor()
        cur.execute("create table if not exists surfacedb(link varchar (100))")
        cur.execute("truncate table surfacedb")

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
                    except Exception:
                        link = "http://" + anchor_tags['href'].split("http://")[1]

                    cur.execute("insert into surfacedb values (?)", (link,))
                    links.append(link)
                except Exception:
                    pass 
            conn.commit()
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
        self.chrome_options = Options()
        # self.chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome("chromedriver_win32\\chromedriver.exe")#, chrome_options=self.chrome_options)

    def instacrawl(self):
        
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
        for i in range(self.depth):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        link_elements = self.driver.find_elements_by_xpath("//*[@class='v1Nh3 kIKUG  _bz0w']/a")
        links = []
        conn = connect_mariadb()
        cur = conn.cursor()
        cur.execute("create table if not exists instagramdb(link varchar (100))")
        cur.execute("truncate table instagramdb")
        for link in link_elements:
            try:
                href = link.get_attribute('href')
                links.append(href)
                cur.execute("insert into instagramdb values (?)", (href,))
            except Exception:
                pass
            conn.commit()
        # self.driver.quit()
        conn.close()

        print(">>>>>>>>>>>PART 2 begins >>>>>>>>>>>>>>")
        hashtags = []
        for link in links:
            self.driver.get(link)
            meta_tags = self.driver.find_elements_by_class_name("xil3i")
            for meta_tag in meta_tags:
                try:
                    print(meta_tag)
                    hashtags.append(meta_tag.text)
                except Exception:
                    pass
        stopwords = set(STOPWORDS)
        wordc = WordCloud(background_color="white", stopwords = stopwords)
        wordc.generate("{}".format(hashtags))
        wordc.to_file('users/static/users/words.png')

        self.driver.quit()
        return links

class Twitter:
    def __init__(self, keyword, depth):
        self.keyword = keyword
        self.depth = depth
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome("chromedriver_win32\\chromedriver.exe", chrome_options=self.chrome_options)

    def twittercrawl(self):
        
        url = "https://twitter.com/search?q=%23" + self.keyword + "&src=typed_query"
        self.driver.get(url)
        for i in range(self.depth):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
        div_elements = self.driver.find_elements_by_xpath("//*[@id='react-root']/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div/section/div/div/div")
        print("DIV: ", div_elements)
        link_elements = []
        for div in div_elements:
            try:
                try:
                    link_elements.append(div.find_element_by_xpath("./div/div/article/div/div/div/div[2]/div[2]/div[2]/div[2]/div/div/div/div/a"))
                except:
                    link_elements.append(div.find_element_by_xpath("./div/div/article/div/div/div/div[2]/div[2]/div[1]/div/div/div[1]/a"))
            except Exception:
                pass
        print("LINK: ", link_elements)
        links = []
        for link in link_elements:
            try:
                href = link.get_attribute('href')
                links.append(href)
            except Exception:
                pass
        self.driver.quit()

        return links


            # //*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div/section/div/div/div[12]/div/div/article/div/div/div/div[2]/div[2]/div[2]/div[2]/div/div/div/div/a
            # //*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div/section/div/div/div[7]/div/div/article/div/div/div/div[2]/div[2]/div[2]/div[2]/div/div/div/div/a
            # //*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div/section/div/div/div[5]/div/div/article/div/div/div/div[2]/div[2]/div[1]/div/div/div[1]/a
            # //*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div/section/div/div/div[1]/div/div/article/div/div/div/div[2]/div[2]/div[1]/div/div/div[1]/a