from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm, SearchURL, SearchKeyword, SearchKeywordPlt
from django.contrib.auth.decorators import login_required

from .utils import addhistory, get_images, get_text, Dashboard, SurfaceURL, Instagram, Twitter
from .minicrawlbot import MiniCrawlbot
from .img_detect import detect_object
from .text_process import detect_text

# for passing arguments in redirect
from django.urls import reverse
from urllib.parse import urlencode
from datetime import datetime

database = None
collection = None

def register(request):
    if request.method =='POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.info(request, f'Account created for {username}! Log In now!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form':form, 'title':"Register Now"})    

@login_required
def welcome(request):
    return render(request, 'users/welcome.html', {'title':"Home"})

@login_required
def dashboard(request):
    dash = Dashboard()
    links = dash.read_db(database, collection)
    if links:
        return render(request, 'users/dashboard.html', {'links':links, 'title':"Dashboard"})
    else:
        return render(request, 'users/404.html', {'links':links, 'title':"Error page"})

@login_required
def active_links(request):
    dash = Dashboard()
    a, ia = dash.active_inactive(database, collection)
    return render(request, 'users/active_links.html', {'a':a, 'ia':ia, 'flag':True, 'title':"Active links"})

@login_required
def link_tree(request):
    dash = Dashboard()
    j = dash.create_tree(database, collection)
    return render(request, 'users/link_tree.html', {'json':j, 'title':"Link Tree"})

@login_required
def word_cloud(request):
    return render(request, 'users/wordclouddash.html', {'title':"Wordcloud"})


@login_required
def surface(request):
    # Form1 >>>>>>>>>>>>
    if request.method =='POST':
        form1 = SearchURL(request.POST)
        if form1.is_valid():
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
            keyword = form2.cleaned_data.get('keyword')
            platform = form2.cleaned_data.get('platform')
            pages = form2.cleaned_data.get('depth_key')
            if pages:
                depth = pages
            else:
                depth = 3 
            code = "surface_key"
            messages.info(request, f'These are your results...')
            base_url = reverse('crawled')
            query_string =  urlencode({'keyword': keyword, 'platform':platform, 'depth':depth, 'code':code})
            url = '{}?{}'.format(base_url, query_string)
            return redirect(url)

    else:
        form2 = SearchKeywordPlt()
    # <<<<<<<<<<<< Form2

    return render(request, 'users/surface.html', {'form1':form1, 'form2':form2, 'title':"Surface web Crawl"})
 
@login_required
def deep(request):
    # Form1 >>>>>>>>>>>>
    if request.method =='POST':
        form1 = SearchURL(request.POST)
        if form1.is_valid():
            url = form1.cleaned_data.get('url')
            pages = form1.cleaned_data.get('depth_url')
            if pages:
                depth = pages
            else:
                depth = 3
            messages.info(request, f'These are your results...')
            base_url = reverse('crawled')
            query_string =  urlencode({'url': url, 'depth':depth})
            url = '{}?{}'.format(base_url, query_string)
            return redirect(url)
    else:
        form1 = SearchURL()
    # <<<<<<<<<<<< Form1

    # Form2 >>>>>>>>>>>>
    if request.method =='POST':
        form2 = SearchKeyword(request.POST)
        if form2.is_valid():
            keyword = form2.cleaned_data.get('keyword')
            pages = form2.cleaned_data.get('depth_key')
            print("1: ", keyword, "2:", pages)
    else:
        form2 = SearchKeyword()
    # <<<<<<<<<<<< Form2

    return render(request, 'users/deep.html', {'form1':form1, 'form2':form2, 'title':"Deep web Crawl"})
    
@login_required
def dark(request):
    # Form1 >>>>>>>>>>>>
    if request.method =='POST':
        form1 = SearchURL(request.POST)
        if form1.is_valid():
            url = form1.cleaned_data.get('url')
            pages = form1.cleaned_data.get('depth_url')
            if pages:
                depth = pages
            else:
                depth = 3
            messages.info(request, f'These are your results...')
            base_url = reverse('crawled')
            query_string =  urlencode({'url': url, 'depth':depth})
            url = '{}?{}'.format(base_url, query_string)
            return redirect(url)
    else:
        form1 = SearchURL()
    # <<<<<<<<<<<< Form1

    # Form2 >>>>>>>>>>>>
    if request.method =='POST':
        form2 = SearchKeyword(request.POST)
        if form2.is_valid():
            keyword = form2.cleaned_data.get('keyword')
            pages = form2.cleaned_data.get('depth_key')
            if pages:
                depth = pages
            else:
                depth = 3 
            code = "dark_key"
            messages.info(request, f'These are your results...')
            base_url = reverse('crawled')
            query_string =  urlencode({'keyword': keyword, 'depth':depth, 'code':code})
            url = '{}?{}'.format(base_url, query_string)
            return redirect(url)
    else:
        form2 = SearchKeyword()
    # <<<<<<<<<<<< Form2

    return render(request, 'users/dark.html', {'form1':form1, 'form2':form2, 'title':"Dark web Crawl"})

# Crawling thorugh URLs    
@login_required
def crawled(request):
    start_time = datetime.now()
    code = request.GET.get('code')
    global database
    global collection 

    if code == 'surface_url':
        url = request.GET.get('url')
        depth = int(request.GET.get('depth'))
        crawler = SurfaceURL(url, depth)
        links = crawler.surfacecrawl()
        database = "surfacedb"
        collection = url
        data = {"Platform": "Surface URL", "Seed URL": url, "Depth":depth}

    if code == 'surface_key':
        keyword = request.GET.get('keyword')
        depth = int(request.GET.get('depth'))
        platform = int(request.GET.get('platform'))
        collection = keyword

        if platform == 1:
            ig = Instagram(keyword, depth)
            links = ig.instacrawl()
            database = "instagramdb"
            data = {"Platform": "Instagram", "Keyword": keyword, "Depth":depth}
            
        if platform == 2:
            tweet = Twitter(keyword, depth)
            links = tweet.twittercrawl()
            database = "twitterdb"
            data = {"Platform": "Twitter", "Keyword": keyword, "Depth":depth}

    if code == 'dark_key':
        keyword = request.GET.get('keyword')
        depth = int(request.GET.get('depth'))
        minicrawl = MiniCrawlbot()
        links = minicrawl.tor_crawler(keyword, depth)
        database = "dark-key-db"
        collection = keyword
        data = {"Platform": "Dark Web Keyword", "Keyword": keyword, "Depth":depth}
        
    addhistory(request.user.username, data)

    end_time = datetime.now()
    diff = end_time - start_time
    time_elapsed = str(diff)[2:11]
    return render(request, 'users/crawled.html', {'links':links, 'time_elapsed':time_elapsed, 'title':"Crawling reults"})


@login_required
def img_processing(request):
    links_images = get_images(database, collection)
    related_links = []
    for link_image in links_images:
        detected = False
        link, img_link = link_image
        print("Processing: ", link)
        if isinstance(img_link, str):
            detected = detect_object(img_link)
        elif isinstance(img_link, list):
            for img in img_link:
                detected = detect_object(img)
                if detected:
                    break
        if detected:
            related_links.append(link)

    return render(request, 'users/img_process.html', {'related_links':related_links, 'title':"Image Processing"})

@login_required
def text_processing(request):
    links_texts = get_text(database, collection)
    related_links = []
    for link_text in links_texts:
        detected = False
        link, text = link_text
        detected = detect_text(text)
        if detected:
            related_links.append(link)

    return render(request, 'users/text_process.html', {'related_links':related_links, 'title':"Text Processing"})