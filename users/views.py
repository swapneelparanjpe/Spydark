from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm, SearchURL, SearchKeyword, SearchKeywordPlt
from django.contrib.auth.decorators import login_required
from .crawled_results import LinkHarvest
# for passing arguments in redirect
from django.urls import reverse
from urllib.parse import urlencode


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
def profile(request):
    return render(request, 'users/dashboard.html')

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
            query_string =  urlencode({'url': url, 'depth':depth})
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
            pages = form.cleaned_data.get('depth_key')
            print("1: ", keyword, "2:", pages)
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
            pages = form.cleaned_data.get('depth_key')
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
            pages = form.cleaned_data.get('depth_key')
            print("1: ", keyword, "2:", pages)
    else:
        form2 = SearchKeyword()
    # <<<<<<<<<<<< Form2

    return render(request, 'users/dark.html', {'form1':form1, 'form2':form2})

# Crawling thorugh URLs    
@login_required
def crawled(request):
    url = request.GET.get('url')
    depth = int(request.GET.get('depth'))

    crawler = LinkHarvest(url, depth)
    links = crawler.crawl() 

    return render(request, 'users/crawled.html', {'links':links})