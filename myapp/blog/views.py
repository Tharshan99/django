from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse

# Create your views here.
def index(request):
    blog_title = "My Blog"
    posts = [
        {'title' : 'Post 1', 'Content': 'Content of Post 1'},
        {'title' : 'Post 2', 'Content': 'Content of Post 2'},
        {'title' : 'Post 3', 'Content': 'Content of Post 3'},
        {'title' : 'Post 4', 'Content': 'Content of Post 4'},
    ]
    return render(request, "blog/index.html", {"blog_titles": blog_title, "postss" : posts})

def detail(request):
    return render(request, "blog/detail.html")

def old_url_redirect (request):
    return redirect(reverse("blog:new_page_url"))

def new_url_view(request):
    return HttpResponse("This is the new url view")