from django.db import models
from django.utils.timezone import now
from django.utils.timesince import timesince
from django.contrib.auth.models import AbstractUser
import uuid
from django.core.validators import RegexValidator
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit


class User(AbstractUser):
    display_name = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w ]+$',  
                message="Username can only contain letters, numbers, underscores, and spaces.",
            )
        ],
        error_messages={
            'unique': "A user with that username already exists.",
        },
    )

    def __str__(self):
        return self.username

def generate_space_code():
    return uuid.uuid4().hex[:8].upper() 

class EventSpace(models.Model):
    name = models.CharField(max_length=255)

    original_cover_image = models.ImageField(
        upload_to='space_covers/', null=True, blank=True
    )

    cover_image = ImageSpecField(
        source='original_cover_image',
        processors=[ResizeToFit(1200, 800)],
        format='JPEG',
        options={'quality': 90},
    )

    space_code = models.CharField(max_length=8, unique=True, default=generate_space_code)
    donate_page_title = models.CharField(max_length=120, blank=True)
    donate_page_description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey('User', on_delete=models.CASCADE, related_name='created_spaces')
    members = models.ManyToManyField('User', related_name='joined_spaces', blank=True)

    def __str__(self):
        return self.name
    
class DonationFund(models.Model):
    card_title = models.CharField(max_length=55)
    card_description = models.CharField(max_length=255, blank=True, null=True)

    original_cover_image = models.ImageField(upload_to='donation_covers/', null=True, blank=True)

    card_cover_image = ImageSpecField(
        source='original_cover_image',
        processors=[ResizeToFit(800, 600)],
        format='JPEG',
        options={'quality': 80}
    )

    card_venmo_link = models.URLField(blank=True)
    card_dono_link = models.URLField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    creator = models.ForeignKey('User', on_delete=models.CASCADE, related_name='created_funds')
    event_space = models.ForeignKey('EventSpace', on_delete=models.CASCADE, blank=True, null=True, related_name='donation_funds')

class Post(models.Model):
    caption = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    event_space = models.ForeignKey(EventSpace, on_delete=models.CASCADE, blank=True, null=True, related_name='posts')
    author = models.ForeignKey('User', on_delete=models.CASCADE, related_name='posts')
    
    def __str__(self):
        return f'{self.caption}'
    
class PostImage(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='images')

    original_image = models.ImageField(upload_to='posts/', null=True, blank=True)

    image = ImageSpecField(
        source='original_image',
        processors=[ResizeToFit(1080, None)],
        format='JPEG',
        options={'quality': 85}
    )

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey('User', on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author.username} on Post {self.post.id}'