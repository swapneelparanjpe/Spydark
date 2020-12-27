from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm, SearchURL, SearchKeyword, SearchKeywordPlt
from django.contrib.auth.decorators import login_required
from .utils import Dashboard, SurfaceURL, Instagram, Twitter
from .minicrawlbot import MiniCrawlbot

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
    return render(request, 'users/register.html', {'form':form})    

@login_required
def welcome(request):
    return render(request, 'users/welcome.html')

@login_required
def dashboard(request):
    dash = Dashboard()
    links = dash.read_db(database, collection)
    if links:
        return render(request, 'users/dashboard.html', {'links':links})
    else:
        return render(request, 'users/404.html', {'links':links})


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

    return render(request, 'users/surface.html', {'form1':form1, 'form2':form2})
 
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

    return render(request, 'users/deep.html', {'form1':form1, 'form2':form2})
    
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

    return render(request, 'users/dark.html', {'form1':form1, 'form2':form2})

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

    if code == 'surface_key':
        keyword = request.GET.get('keyword')
        depth = int(request.GET.get('depth'))
        platform = int(request.GET.get('platform'))
        collection = keyword

        if platform == 1:
            ig = Instagram(keyword, depth)
            links = ig.instacrawl()
            database = "instagramdb"
            
        if platform == 2:
            tweet = Twitter(keyword, depth)
            links = tweet.twittercrawl()
            database = "twitterdb"

    if code == 'dark_key':
        keyword = request.GET.get('keyword')
        depth = int(request.GET.get('depth'))

        minicrawl = MiniCrawlbot()
        links = minicrawl.tor_crawler(keyword, depth)
        
    end_time = datetime.now()
    diff = end_time - start_time
    time_elapsed = str(diff)[2:11]

    return render(request, 'users/crawled.html', {'links':links, 'time_elapsed':time_elapsed})