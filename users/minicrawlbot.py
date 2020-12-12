import requests
from lxml import html
import collections
import urllib.parse
from requests.exceptions import HTTPError
import time
from stem import Signal
from stem.control import Controller
from fake_useragent import UserAgent


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
            controller.authenticate(password="vjtifyp")
            controller.signal(Signal.NEWNYM)

    def is_alive(self, url):
        try:
            ua = UserAgent()
            user_agent = ua.random
            headers = {'User-Agent': user_agent}
            res = requests.get(url, proxies = self.proxies, headers = headers)
            res.raise_for_status()
        except HTTPError as http_err:
            print(" Page not found..." + url)
            return False
        except Exception as err:
            print("Page not found..." + url )
            return False
        else:
            print("Page has found....")     
            return True

    def tor_crawler(self, key, depth):

        query = '+'.join(key.split(' '))
        
        url = 'http://msydqstlz2kzerdg.onion/search/?q=' + query
        ua = UserAgent()
        user_agent = ua.random
        headers = {'User-Agent': user_agent}
        r = requests.get(url, proxies = self.proxies, headers = headers)
        body = html.fromstring(r.content)
        links = body.xpath('//h4/a/@href')
        
        
        seed_list = links
        found = set()
        
        '''main url queue'''
        urlq = collections.deque()
        for seed_url in seed_list :
            seed_url = seed_url.split('url=')[-1]
            urlq.append(seed_url)
            found.add(seed_url)
            print(seed_url)
            print("#"*20)

        # number of pages to visit in one crawling session
        countpage = 1

        # number of total links harvested during crawling
        countlink = 1
        

        try:	
            while (len(urlq) != 0 and countpage != depth) :
                
                '''pop url from queue'''
                url = urlq.popleft()
                        
                '''IP spoofing'''
                current_ip = self.get_current_ip()
                print("IP : {}".format(current_ip))
                print("{}. Crawling {}".format(str(countpage), url))
                

                '''if link is active, visit link '''
                if self.is_alive(url):
                    
                    countpage += 1
                    
                    '''user agent spoofing'''
                    ua = UserAgent()
                    user_agent = ua.random
                    headers = {'User-Agent': user_agent}
                    print("User Agent is : {}".format(user_agent))
                                
                    '''send request to chosen site'''
                    response = requests.get(url, proxies = self.proxies, headers = headers)
                    
                    body = html.fromstring(response.content)
                    
                                                
                    '''links availab on current web page'''
                    links = [urllib.parse.urljoin(response.url, url) for url in body.xpath('//a/@href')]
                    
                    for link in links:
                        if link not in found:
                            urlq.append(link)
                            found.add(link)
                            print (str(countlink) +"{:<5}".format(" ")+ link, end= "\n\n" )
                            countlink += 1

            
                '''Obtain new IP using TOR'''
                self.renew_tor_ip()
                time.sleep(wait_time)
                
            links = list(found)            
                    
        except Exception as e:
            print(str(e))
        
        return links

        