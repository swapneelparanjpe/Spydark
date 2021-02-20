from django.shortcuts import render
from django.http import HttpResponse
def home(request):
    return render(request, 'crawler/home.html', {'title':"Home"})

def about(request):
    return render(request, 'crawler/about.html', {'title':"About"})