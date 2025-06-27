from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
import nested_admin

from .models import (
    User,  
    EventSpace,
    Post,
    PostImage,
    Comment,
    DonationFund
)

class PostImageInline(nested_admin.NestedStackedInline):
    model = PostImage
    fields = ['original_image']
    extra = 0

class PostInline(nested_admin.NestedStackedInline):
    model = Post
    fields = ['caption', 'author'] 
    inlines = [PostImageInline]
    extra = 0

class PostAdmin(nested_admin.NestedModelAdmin): 
    inlines = [PostImageInline]
    list_display = ['id', 'author', 'event_space', 'created_at']
    search_fields = ['caption', 'author__username']
    list_filter = ['event_space']

class DonationFundAdmin(nested_admin.NestedModelAdmin):
    list_display = ['card_title', 'event_space', 'creator', 'created_at']
    search_fields = ['card_title', 'event_space__name', 'creator__username']
    list_filter = ['event_space', 'created_at']

class EventSpaceAdmin(nested_admin.NestedModelAdmin):
    inlines = [PostInline]
    list_display = ['name', 'creator', 'space_code', 'created_at']
    fields = ('name', 'original_cover_image', 'space_code', 'creator', 'members', 'donate_page_title', 'donate_page_description')
    filter_horizontal = ('members',) 

class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'text', 'created_at']
    search_fields = ['text', 'author__username']
    list_filter = ['created_at']

class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'display_name', 'email', 'is_staff']
    search_fields = ['username', 'display_name', 'email']
    list_filter = ['is_staff', 'is_superuser']

admin.site.register(User, UserAdmin)
admin.site.register(EventSpace, EventSpaceAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(DonationFund, DonationFundAdmin)
admin.site.register(Comment, CommentAdmin)
