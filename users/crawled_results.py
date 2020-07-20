from bs4 import BeautifulSoup
import requests
import sqlite3

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