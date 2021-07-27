from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Post(models.Model):
    user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="posts_made")
    content = models.TextField(blank=True, null=True)
    post_timestamp = models.DateTimeField(auto_now_add=True)
    edit_timestamp = models.DateTimeField(blank=True, null=True)
    likes = models.IntegerField(default=0, null=True, blank=True)


class Like(models.Model):
    post = models.ForeignKey(
        "Post", on_delete=models.CASCADE, related_name="user_likes")
    user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="likes_made")
    timestamp = models.DateTimeField(auto_now_add=True)


class Follow(models.Model):
    followed = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="following")
    follower = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="followers")
    timestamp = models.DateTimeField(auto_now_add=True)
