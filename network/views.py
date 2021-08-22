from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django import forms
import datetime

from .models import User, Post, Like, Follow

class PostForm(forms.Form):
    post = forms.CharField(min_length=1, 
                            max_length=255, 
                            label="", 
                            widget=forms.TextInput(attrs={
                                'autocomplete': 'off',
                                'placeholder': 'Make a Post'
                            }
                            ))


def index(request):
    total_posts = Post.objects.all()
    pagenum = 1

    if request.user.is_authenticated:
        likes = Like.objects.filter(user=request.user)
        likes = [like.post.id for like in likes]
    else:
        likes = ""
    if request.method == "POST":
        pagenum = int(request.POST["pagenum"])
        num = (pagenum - 1) * 10
        ten_posts = Post.objects.order_by("-post_timestamp")[num:pagenum*10]  # if on page 1, display posts 0-9, if on page 2, display posts 10-19, etc.
    else:     
        ten_posts = Post.objects.order_by("-post_timestamp")[:10]

    context = {
            "posts": ten_posts,
            "total_posts": len(total_posts),
            "pagenum": pagenum,
            "page_posts": len(ten_posts),
            "likes": likes
        }

    return render(request, "network/index.html", context)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@login_required(login_url="login")
def new_view(request):
    # GET request directs to page, POST request submits the form on that page
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.cleaned_data["post"]
            p = Post(user=request.user, content=post)
            p.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/post.html", {"form": PostForm()})


def profile_view(request, id):
    # get/display user info from DB, display user's posts, render profile.html
    total_posts = Post.objects.filter(user=id)
    pagenum = 1
    num_of_followers = len(Follow.objects.filter(followed=id))  # get users who have me listed as someone they follow
    ppl_followed = len(Follow.objects.filter(follower=id))  # get users for whom I am listed as a follower
    viewed_user = User.objects.get(pk=id)
    
    try_follow = Follow.objects.filter(followed=viewed_user.id, follower=request.user.id)
    if try_follow.exists():
        following = True
    else:
        following = False
    if request.user.is_authenticated:
        likes = Like.objects.filter(user=request.user)
        likes = [like.post.id for like in likes]
    else:
        likes = ""
    if request.method == "POST":
        pagenum = int(request.POST["pagenum"])
        num = (pagenum - 1) * 10
        posts = Post.objects.filter(user=id).order_by("-post_timestamp")[num:pagenum*10]
    else:
        posts = Post.objects.filter(user=id).order_by("-post_timestamp")[:10]

    context = {
        "posts": posts,
        "followers": num_of_followers,
        "followed": ppl_followed,
        "viewed_user": viewed_user,
        "total_posts": len(total_posts),
        "pagenum": pagenum,
        "page_posts": len(posts),
        "likes": likes, 
        "following": following
    }

    return render(request, "network/profile.html", context)


@login_required(login_url="login")
def following_view(request):
    # view posts by users the current user is following
    pagenum = 1

    follows = Follow.objects.filter(follower=request.user.id)
    users_followed = [follow.followed.id for follow in follows]
    posts = [Post.objects.filter(user=user) for user in users_followed]
    
    likes = Like.objects.filter(user=request.user)
    likes = [like.post.id for like in likes]
    
    follow_posts = []
    for post in posts:
        for p in post:
            follow_posts.append(p)

    follow_posts.sort(key=lambda x: x.post_timestamp, reverse=True)

    if request.method == "POST":
        pagenum = int(request.POST["pagenum"])
        num = (pagenum - 1) * 10
        ten_posts = follow_posts[num:pagenum*10]
    else:
        ten_posts = follow_posts[:10]

    context = {
        "posts": ten_posts,
        "pagenum": pagenum,
        "total_posts": len(follow_posts),
        "page_posts": len(ten_posts),
        "likes": likes
    }

    return render(request, "network/following.html", context)


@login_required(login_url="login")
def edit_view(request, id):
    # edit the content of the post
    if request.method == "POST":
        content = request.POST["post-content"]
        post = Post.objects.get(pk=id)
        post.content = content
        post.edit_timestamp = datetime.datetime.now()
        post.save()

        timestamp = post.edit_timestamp
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        if len(str(timestamp.minute)) > 2:
            minute = f"0{timestamp.minute}"
        else:
            minute = timestamp.minute
        final_timestamp = f"{months[timestamp.month-1]} {timestamp.day}, {timestamp.year}, {timestamp.hour}:{minute}"

        return JsonResponse({'content': post.content, 'timestamp': final_timestamp}) 


@login_required(login_url="login")
def like_view(request, id):
    # like a post
    if request.method == "POST":
        user_id = request.user.id  
        post = Post.objects.get(pk=id)  
        user = User.objects.get(pk=user_id)  

        # check if user has already liked the post; if so, delete the like and decrement the like count
        try_like = Like.objects.filter(post=post, user=user)
        if try_like.exists():
            try_like.delete()
            post.likes -= 1
            post.save()
        
        else:
            # otherwise, create Like object and increment Post.like
            like = Like(post=post, user=user)
            post.likes += 1
            like.save()
            post.save()
        
        return JsonResponse({'result': post.likes}) 


@login_required(login_url="login")
def follow_view(request, id):
    # follow the user 
    if request.method == "POST":
        user = User.objects.get(pk=id)
        
        # if the current user has already followed the user, delete the Follow
        try_follow = Follow.objects.filter(followed=user, follower=request.user)
        if try_follow.exists():
            try_follow.delete()
            result = "removed"
        else:
            # otherwise, add a Follow
            follow = Follow(followed=user, follower=request.user)
            follow.save()
            result = "added"

        return JsonResponse({'result': result})


