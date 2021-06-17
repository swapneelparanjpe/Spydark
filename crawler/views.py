from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import SearchURL, SearchKeyword, SearchKeywordPlt
from django.contrib.auth.decorators import login_required

from .utils import connect_gridfs, addhistory, SurfaceURL, Google, Instagram, Twitter
from dashboard.utils import Dashboard
from .darkweb_crawler import DarkWebCrawler
from .track_links import track_links_periodically, stop_tracking
from urllib.parse import quote

# for passing arguments in redirect
from django.urls import reverse
from urllib.parse import urlencode
from datetime import datetime
import time
from base64 import b64encode

database = None
collection = None
iterativeCrawledKeywords = []
crawled_dropdown_choices = []

platform_choice = None
selected_database = None
collection_choice = None
selected_collection = None
visited_keywords_choices = []
visited_links_choices = [] 

def get_global_variables():
    global database
    global collection
    global iterativeCrawledKeywords
    global crawled_dropdown_choices
    global platform_choice
    global selected_database
    global collection_choice
    global selected_collection
    global visited_keywords_choices
    global visited_links_choices

    return database, collection, iterativeCrawledKeywords, crawled_dropdown_choices, platform_choice, selected_database, collection_choice, selected_collection, visited_keywords_choices, visited_links_choices

@login_required
def welcome(request):
    msg = track_links_periodically(False)
    if msg != None:
        messages.info(request, f'{msg}')
    return render(request, 'crawler/welcome.html', {'title':"Home", 'msg':msg})

@login_required
def dashboard(request):
    global database
    global collection
    global iterativeCrawledKeywords
    global crawled_dropdown_choices
    global platform_choice
    global selected_database
    global collection_choice
    global selected_collection
    global visited_keywords_choices
    global visited_links_choices

    if request.method == "POST":
        if "show_link_data" in request.POST:
            link = request.POST["show_link_data"]

            fs = connect_gridfs(database)
            dash = Dashboard()
            document, image_urls = dash.get_link_data(link, collection, database) 
            imgs = []
            for image_url in image_urls:
                img_bytes = fs.get_last_version(filename=str(image_url[0])).read()
                imgs.append(quote(b64encode(img_bytes)))
            images = zip(imgs, image_urls)
            return render(request, 'crawler/dashboard.html', {'title':"Dashboard", 'document':document, 'images':images})

        else:
            database = None
            collection = None
            iterativeCrawledKeywords = []
            crawled_dropdown_choices = []

            platform_choice = None
            selected_database = None
            visited_keywords_choices = []

            collection_choice = None
            selected_collection = None
            visited_links_choices = []
        
    if database is None or collection is None:
        return render(request, 'crawler/404.html', {'title':"Dashboard"})
    dash = Dashboard()
    links = dash.read_db(database, collection)
    return render(request, 'crawler/dashboard.html', {'links':links, 'title':"Dashboard"})


@login_required
def surface(request):
    global iterativeCrawledKeywords
    # Form1 >>>>>>>>>>>>
    if request.method =='POST':
        form1 = SearchURL(request.POST)
        if form1.is_valid():
            iterativeCrawledKeywords = []
            url = form1.cleaned_data.get('url')
            pages = form1.cleaned_data.get('depth_url')
            if pages:
                depth = pages
            else:
                depth = 3

            messages.info(request, f'These are your results...')
            base_url = reverse('crawled')
            code = "surface_url"
            query_string =  urlencode({'url': url, 'depth':depth, 'code':code})
            url = '{}?{}'.format(base_url, query_string)
            return redirect(url)
    else:
        form1 = SearchURL()
    # <<<<<<<<<<<< Form1

    # Form2 >>>>>>>>>>>>
    if request.method =='POST':
        form2 = SearchKeywordPlt(request.POST)
        if form2.is_valid():
            iterativeCrawledKeywords = []
            keyword = form2.cleaned_data.get('keyword')
            platform = form2.cleaned_data.get('platform')
            pages = form2.cleaned_data.get('depth_key')
            isIterative = form2.cleaned_data.get('isIterative')
            if pages:
                depth = pages
            else:
                depth = 3 
            code = "surface_key"
            messages.info(request, f'These are your results...')
            base_url = reverse('crawled')
            query_string =  urlencode({'keyword': keyword, 'platform':platform, 'depth':depth,'isIterative':isIterative, 'code':code})
            url = '{}?{}'.format(base_url, query_string)
            return redirect(url)

    else:
        form2 = SearchKeywordPlt()        
    # <<<<<<<<<<<< Form2

    return render(request, 'crawler/surface.html', {'form1':form1, 'form2':form2, 'title':"Surface web Crawl"})
 
     
@login_required
def dark(request):
    global iterativeCrawledKeywords
    # Form1 >>>>>>>>>>>>
    if request.method =='POST':
        form1 = SearchURL(request.POST)
        if form1.is_valid():
            iterativeCrawledKeywords = []
            url = form1.cleaned_data.get('url')
            pages = form1.cleaned_data.get('depth_url')
            if pages:
                depth = pages
            else:
                depth = 3
            code = "dark_url"
            messages.info(request, f'These are your results...')
            base_url = reverse('crawled')
            query_string =  urlencode({'url': url, 'depth':depth, 'code':code})
            url = '{}?{}'.format(base_url, query_string)
            return redirect(url)
    else:
        form1 = SearchURL()
    # <<<<<<<<<<<< Form1

    # Form2 >>>>>>>>>>>>
    if request.method =='POST':
        form2 = SearchKeyword(request.POST)
        if form2.is_valid():
            iterativeCrawledKeywords = []
            keyword = form2.cleaned_data.get('keyword')
            pages = form2.cleaned_data.get('depth_key')
            isIterative = form2.cleaned_data.get('isIterative')
            if pages:
                depth = pages
            else:
                depth = 3 
            code = "dark_key"
            messages.info(request, f'These are your results...')
            base_url = reverse('crawled')
            query_string =  urlencode({'keyword': keyword, 'depth':depth, 'isIterative':isIterative, 'code':code})
            url = '{}?{}'.format(base_url, query_string)
            return redirect(url)
    else:
        form2 = SearchKeyword()
    # <<<<<<<<<<<< Form2

    return render(request, 'crawler/dark.html', {'form1':form1, 'form2':form2, 'title':"Dark web Crawl"})

# Crawling thorugh URLs    
@login_required
def crawled(request):
    start_time = datetime.now()
    code = request.GET.get('code')
    isIterative = request.GET.get('isIterative') == "True"

    global database
    global collection 
    global iterativeCrawledKeywords
    global crawled_dropdown_choices

    if code == 'surface_url':
        url = request.GET.get('url')
        depth = int(request.GET.get('depth'))
        crawler = SurfaceURL(url, depth)
        links, topFiveWords = crawler.surfacecrawl()
        database = "surfacedb"
        collection = url
        data = {"Platform": "Surface URL", "Seed URL": url, "Depth":depth}

    if code == 'surface_key':
        keyword = request.GET.get('keyword')
        depth = int(request.GET.get('depth'))
        platform = int(request.GET.get('platform'))
        collection = keyword

        if isIterative:
            iterativeCrawledKeywords.append(keyword)
        else: 
            iterativeCrawledKeywords = []

        if platform == 1:
            ggl = Google(keyword, depth)
            links, topFiveWords = ggl.googlecrawl()
            database = "googledb"
            data = {"Platform": "Google", "Keyword": keyword, "Depth":depth}

        if platform == 2:
            ig = Instagram(keyword, depth)
            links, topFiveWords = ig.instacrawl()
            database = "instagramdb"
            data = {"Platform": "Instagram", "Keyword": keyword, "Depth":depth}
            
        if platform == 3:
            tweet = Twitter(keyword, depth)
            links, topFiveWords = tweet.twittercrawl()
            database = "twitterdb"
            data = {"Platform": "Twitter", "Keyword": keyword, "Depth":depth}

    if code == 'dark_url':
        url = request.GET.get('url')
        depth = int(request.GET.get('depth'))
        dw_crawler = DarkWebCrawler()
        links, topFiveWords = dw_crawler.tor_crawler(url, depth, False)
        database = "dark-url-db"
        collection = url
        data = {"Platform": "Dark Web URL", "Seed URL": url, "Depth":depth}

    if code == 'dark_key':
        keyword = request.GET.get('keyword')
        depth = int(request.GET.get('depth'))
        dw_crawler = DarkWebCrawler()
        links, topFiveWords = dw_crawler.tor_crawler(keyword, depth, True)
        database = "dark-key-db"
        collection = keyword
        data = {"Platform": "Dark Web Keyword", "Keyword": keyword, "Depth":depth}
        if isIterative:
            iterativeCrawledKeywords.append(keyword)
        else: 
            iterativeCrawledKeywords = []
        
    addhistory(request.user.username, data)

    end_time = datetime.now()
    diff = end_time - start_time
    time_elapsed = str(diff)[2:11]

    # Get next iteration
    full_path = request.get_full_path()
    urlSub1 = full_path.split("=", 1)[0] + "="
    urlSub2 = "&" + full_path.split("&", 1)[1]

    wordUrls = []
    for word in topFiveWords:
        wordUrls.append(word.replace(" ", "+"))

    topWords = zip(topFiveWords, wordUrls)

    if len(iterativeCrawledKeywords) == 5:
        isIterative = False
    
    if len(iterativeCrawledKeywords)>0:
        crawled_dropdown_choices = []
        count = 0
        for iterativeCrawledKeyword in iterativeCrawledKeywords:
            crawled_dropdown_choices.append((count, iterativeCrawledKeyword))
            count += 1
        crawled_dropdown_choices.append((count, "All words together"))


    return render(request, 'crawler/crawled.html', {'links':links, 'no_of_links':len(links), 'time_elapsed':time_elapsed, 'isIterative':isIterative, 'topWords':topWords, 'urlSub1':urlSub1, 'urlSub2':urlSub2, 'title':"Crawling reults"})
    