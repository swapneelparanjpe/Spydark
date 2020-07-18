from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm, SearchURL, SearchKeyword, SearchKeywordPlt
from django.contrib.auth.decorators import login_required
# for passing arguments in redirect
from django.urls import reverse
from urllib.parse import urlencode
# for beautiful soup
from bs4 import BeautifulSoup
import requests

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
    return render(request, 'users/profile.html')

@login_required
def surface(request):
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
            base_url = reverse('crawled')  # 1 /products/
            query_string =  urlencode({'url': url, 'depth':depth})  # 2 category=42
            url = '{}?{}'.format(base_url, query_string)  # 3 /products/?category=42
            return redirect(url)
            #return redirect('crawled', key=url)
    else:
        form1 = SearchURL()

    if request.method =='POST':
        form2 = SearchKeywordPlt(request.POST)
        if form2.is_valid():
            keyword = form2.cleaned_data.get('keyword')
            pages = form.cleaned_data.get('depth_key')
            print("1: ", keyword, "2:", pages)
    else:
        form2 = SearchKeywordPlt()

    return render(request, 'users/surface.html', {'form1':form1, 'form2':form2})
 
@login_required
def deep(request):
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
            base_url = reverse('crawled')  # 1 /products/
            query_string =  urlencode({'url': url, 'depth':depth})  # 2 category=42
            url = '{}?{}'.format(base_url, query_string)  # 3 /products/?category=42
            return redirect(url)
            #return redirect('crawled', key=url)
    else:
        form1 = SearchURL()

    if request.method =='POST':
        form2 = SearchKeyword(request.POST)
        if form2.is_valid():
            keyword = form2.cleaned_data.get('keyword')
            pages = form.cleaned_data.get('depth_key')
            print("1: ", keyword, "2:", pages)
    else:
        form2 = SearchKeyword()

    return render(request, 'users/deep.html', {'form1':form1, 'form2':form2})
    
@login_required
def dark(request):
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
            base_url = reverse('crawled')  # 1 /products/
            query_string =  urlencode({'url': url, 'depth':depth})  # 2 category=42
            url = '{}?{}'.format(base_url, query_string)  # 3 /products/?category=42
            return redirect(url)
            #return redirect('crawled', key=url)
    else:
        form1 = SearchURL()

    if request.method =='POST':
        form2 = SearchKeyword(request.POST)
        if form2.is_valid():
            keyword = form2.cleaned_data.get('keyword')
            pages = form.cleaned_data.get('depth_key')
            print("1: ", keyword, "2:", pages)
    else:
        form2 = SearchKeyword()

    return render(request, 'users/dark.html', {'form1':form1, 'form2':form2})

# Crawling thorugh URLs    
@login_required
def crawled(request):
    url = request.GET.get('url')
    depth = int(request.GET.get('depth'))

    source = requests.get(url).text
    soup = BeautifulSoup(source, 'lxml')
    no_pages = 1
    db_pointer = 0
    links = []
    
    while(no_pages <= depth):

        for anchor_tags in soup.find_all('a'):
            try:
                try:
                    link = "https://" + anchor_tags['href'].split("https://")[1]  
                except:
                    link = "http://" + anchor_tags['href'].split("http://")[1]
                links.append(link)
            except Exception as e:
                pass 
        no_pages += 1
        db_pointer += 1
        source = requests.get(links[db_pointer]).text
        soup = BeautifulSoup(source, 'lxml')
        
    return render(request, 'users/crawled.html', {'links':links})