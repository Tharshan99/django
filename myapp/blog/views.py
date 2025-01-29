from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
import logging
from blog.models import Post
from django.http import Http404
from django.core.paginator import Paginator
from .forms import ContactForm


# Create your views here.

# posts = [
#         {'id':1, 'title' : 'Post 1', 'Content': 'Content of Post 1'},
#         {'id':2, 'title' : 'Post 2', 'Content': 'Content of Post 2'},
#         {'id':3, 'title' : 'Post 3', 'Content': 'Content of Post 3'},
#         {'id':4, 'title' : 'Post 4', 'Content': 'Content of Post 4'},
#     ]

def index(request):
    blog_title = "My Blog"

    # getting data from post model
    all_posts = Post.objects.all()

    #Pagination
    paginator = Paginator(all_posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "blog/index.html", {"blog_titles": blog_title, "page_object" : page_obj})

def detail(request, slug):
    #getting static data
    # post = next((item for item in posts if item['id'] == int(post_id)), None)
    
    try:
        #getting data from model by post id
        post = Post.objects.get(slug=slug)
        related_posts = Post.objects.filter(category=post.category).exclude(slug=slug)
    
    except Post.DoesNotExist:
        raise Http404("Post Does not exits")

    # logger = logging.getLogger("TESTING")
    # logger.debug(f'post variable is {post}')
    return render(request, "blog/detail.html", {'post': post, 'related_posts' : related_posts})

def details(request):
    return render(request, "blog/detail.html")

def old_url_redirect (request):
    return redirect(reverse("blog:new_page_url"))

def new_url_view(request):
    return HttpResponse("This is the new url view")

def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        logger = logging.getLogger("TESTING")
        if form.is_valid():
            logger.debug(f'POST Data is {form.cleaned_data['name']} {form.cleaned_data['email']} {form.cleaned_data['message']}')
            success_message = "Your mail has been sent successfully!"
            logger.debug(success_message)
            return render(request, "blog/contact.html", {"form": form, "success message" : success_message})
        else:
            logger.debug("Form is not valid")
        return render(request, "blog/contact.html", {"form": form, "name" : name, "email" : email, "message" : message})
    return render(request, "blog/contact.html")
