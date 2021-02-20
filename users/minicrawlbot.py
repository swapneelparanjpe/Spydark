import requests
from lxml import html
import collections
import urllib.parse
from requests.exceptions import HTTPError
import time
from stem import Signal
from stem.control import Controller
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from .utils import connect_mongodb, display_wordcloud
import os

class MiniCrawlbot:
    
    def __init__(self):
        import warnings
        warnings.filterwarnings("ignore")
        try:
            import requests.packages.urllib3
            requests.packages.urllib3.disable_warnings()
        except Exception:
            pass

        '''add time delay between each request to avoid DOS attack'''
        self.wait_time = 1
        
        '''socks proxies required for TOR usage'''
        self.proxies = {'http' : 'socks5h://127.0.0.1:9050', 'https' : 'socks5h://127.0.0.1:9050'}

    def get_current_ip(self):
        try:
            r = requests.get('http://httpbin.org/ip', proxies = self.proxies)
        except Exception as e:
            print (str(e))
        else:
            return r.text.split(",")[-1].split('"')[3]

    def renew_tor_ip(self):
        with Controller.from_port(port = 9051) as controller:
            controller.authenticate(password="ToRhCPw17$")
            controller.signal(Signal.NEWNYM)

    def is_alive(self, url):
        try:
            ua = UserAgent()
            user_agent = ua.random
            headers = {'User-Agent': user_agent}
            response = requests.get(url, proxies = self.proxies, headers = headers, timeout = 15)
            response.raise_for_status()
        except HTTPError as http_err:
            print(" Page not found..." + url)
            return False, None
        except Exception as err:
            print("Page not found..." + url )
            return False, None
        else:
            print("Page has found....")     
            return True, response

    def tor_crawler(self, key, depth):

        query = str('+'.join(key.split(' ')))

        visitedcoll = connect_mongodb("dark-key-db", "keywords-visited")
        coll = connect_mongodb("dark-key-db", key)

        visited = False
        for _ in visitedcoll.find({"Keyword":key}):
            visited = True

        links = []
        wc_words = open('users/static/users/wc_words.txt', 'w', encoding='utf-8')
        
        if visited:
            for x in coll.find():
                links.append(x["Link"])
                try:
                    wc_words.write(x["Page content"] + "\n\n")
                except Exception:
                    pass
        
        else:
            os.startfile("C:\Tor Browser\Browser\\firefox.exe")
            time.sleep(10)
            print("Tor Browser started")
            
            url = 'http://msydqstlz2kzerdg.onion/search?q=' + query
            ua = UserAgent()
            user_agent = ua.random
            headers = {'User-Agent': user_agent}
            r = requests.get(url, proxies = self.proxies, headers = headers)
            body = html.fromstring(r.content)
            s = BeautifulSoup(r.text, 'lxml')
            print(">>>>>>>>>", s.find("title").text.strip())
            links_found = body.xpath('//h4/a/@href')      

            links = ["http://msydqstlz2kzerdg.onion/"]
            urlq = collections.deque()
            
            seed_links = 0
            for link_found in links_found :
                link = link_found.split('url=')[-1]
                if link not in links:
                    urlq.append(link)
                    links.append(link)
                    seed_links += 1
                    print(link)
                    print("#"*20)
                if seed_links>=100:
                    break
                
            links_per_page = [1, len(links)-1]

            # number of pages to visit in one crawling session
            countpage = 0

            # number of total links harvested during crawling
            countlink = 1
            
            inactive_links = []

            try:	
                cnt = 1
                while (len(urlq) != 0 and countpage != depth) :
                    
                    '''pop url from queue'''
                    url = urlq.popleft()
                            
                    '''IP spoofing'''
                    current_ip = self.get_current_ip()
                    print("IP : {}".format(current_ip))
                    print("{}. Crawling {}".format(str(countpage+1), url))

                    cnt += 1
                    if cnt <= 6 :
                        inactive_links.append(url)
                        print("Inactive link")
                        continue
                    
                    link_active, response = self.is_alive(url)
                    '''if link is active, visit link '''

                    if link_active :
                        
                        countpage += 1
                        
                        '''user agent spoofing'''
                        # ua = UserAgent()
                        # user_agent = ua.random
                        # headers = {'User-Agent': user_agent}
                        # print("User Agent is : {}".format(user_agent))
                            
                        '''send request to chosen site'''
                        # response = requests.get(url, proxies = self.proxies, headers = headers)
                        
                        body = html.fromstring(response.content)
                        
                                                    
                        '''links available on current web page'''
                        links_found = [urllib.parse.urljoin(response.url, url) for url in body.xpath('//a/@href')]
                        
                        no_of_links = 0

                        for link in links_found:
                            if link not in links:
                                urlq.append(link)
                                links.append(link)
                                print (str(countlink) +"{:<5}".format(" ")+ link, end= "\n\n" )
                                countlink += 1
                                no_of_links += 1

                        links_per_page.append(no_of_links)

                    else:
                        inactive_links.append(url)
                        print("Inactive link")

                    '''Obtain new IP using TOR'''
                    self.renew_tor_ip()                
                    time.sleep(self.wait_time)
                                
            except Exception as e:
                print(str(e))

            print("Total links to parse:", len(links))
            print(">>>>>>>>PART 2>>>>>>>>>>>>>>")

            parent = None
            link_count = 1
            idx = 1
            parent_idx = -1

            for link in links:
                try:
                    current_ip = self.get_current_ip()
                    print("IP : {}".format(current_ip))
                    ua = UserAgent()
                    user_agent = ua.random
                    headers = {'User-Agent': user_agent}
                    print(link_count, "-> Parsing:", link)

                    source = requests.get(link, proxies = self.proxies, headers = headers, timeout = 15).text
                    curr_page = BeautifulSoup(source, 'lxml')
                    title = curr_page.find("title").text.strip()
                    text = ' '.join(curr_page.text.split())
                    wc_words.write(text + "\n\n")
                    active = True
                    print("Found")
                except Exception:
                    print("Not found")
                    active = False
                print("Parent:", parent)
                if active:
                    coll.insert_one({"Link":link, "Title":title, "Page content":text, "Parent link":parent, "Link status":"Active"})
                else:
                    coll.insert_one({"Link":link, "Parent link":parent, "Link status":"Inactive"})
                
                link_count += 1
                if sum(links_per_page[:idx])<link_count:
                    parent_idx += 1
                    parent = links[parent_idx]
                    idx += 1
                while parent in inactive_links:
                    parent_idx += 1
                    parent = links[parent_idx]

                self.renew_tor_ip()                
                time.sleep(self.wait_time)
                
            visitedcoll.insert_one({"Keyword":key})

        display_wordcloud(wc_words)

        return links

        