from django.contrib import admin
from .models import Post, Comment, UserProfile

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_date', 'updated_date')
    list_filter = ('created_date', 'author', 'tags')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_date'
    raw_id_fields = ('author',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'created_date')
    list_filter = ('created_date', 'author')
    search_fields = ('content', 'author__username', 'post__title')
    raw_id_fields = ('post', 'author')

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'bio']
    search_fields = ['user__username', 'bio']

admin.site.register(UserProfile, UserProfileAdmin)
