from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.urls import reverse
import logging
from blog.models import Post, AboutUs
from django.http import Http404
from django.core.paginator import Paginator
from .forms import ContactForm, RegisterForm, LoginForm, ForgotPasswordForm, ResetPasswordForm
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from blog import models
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import send_mail

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

def contact(request):
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
            return render(request, "blog/contact.html", {"form": form, "success_message" : success_message})
        else:
            logger.debug("Form is not valid")
        return render(request, "blog/contact.html", {"form": form, "name" : name, "email" : email, "message" : message})
    return render(request, "blog/contact.html")

def about(request):
    about_content = AboutUs.objects.first()
    if about_content is None or not about_content.contentc:
        about_content = "Default content goes here." #Default content
    else:
        about_content = about_content.contentc
    return render(request, "blog/about.html", {"about_content" : about_content})

def register(request):
    form = RegisterForm()
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False) #save data to database
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Registration successful. You can log in now.")
            return redirect('blog:login')
        else:
            print('Form is not valid')
    return render(request, "blog/register.html", {"form" : form})

def login(request):
    if request.method == "POST":
        #login form
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                print("Login Success!")
                return redirect('blog:dashboard')
            
        else:
            print("Form is not valid")
    else:
        form = LoginForm()
        print("Form is not valid")
    return render(request, "blog/login.html", {"form" : form})

def dashboard(request):
    blog_title = "My Posts"
    return render(request, "blog/dashboard.html", {"blogtitle" : blog_title})

def logout(request):
    auth_logout(request)
    return redirect("blog:index")

def forgot_password(request):
    form = ForgotPasswordForm()
    if request.method == "POST":
        #forgot password form
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)
            #send email to reset password
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            current_site = get_current_site(request)
            domain = current_site.domain
            subject = "Password Reset Request"
            message = render_to_string('blog/reset_password_email.html', {
                'domain': domain,
                'uid' : uid,
                'token' : token
            })
            send_mail(subject, message, 'noreply@kandait.com', [email])
            messages.success(request, 'Email has been sent successfully. Please check your inbox.')
    return render(request, "blog/forgot_password.html", {"form" : form})

def reset_password(request, uidb64, token):
    form = ResetPasswordForm()
    if request.method == "POST":
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            try:
                uid = urlsafe_base64_decode(uidb64)
                user = User.objects.filter(pk=uid)
            except(TypeError, ValueError, OverflowError, User.DoesNotExist):
                user = None
            
            if user is not None and default_token_generator.make_token(user, token):
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Your password has been reset successfully.')
                return redirect('blog:login')
            else:
                messages.error(request, 'The password reset link is invalid or has expired.')
    return render(request, "blog/reset_password.html", {'form' : form})