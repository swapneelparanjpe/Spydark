from django.shortcuts import render

def home(request):
    return render(request, 'launcher/home.html', {'title':"Home"})

def about(request):
    return render(request, 'launcher/about.html', {'title':"About"})