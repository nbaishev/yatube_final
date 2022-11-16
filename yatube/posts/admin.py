from django.contrib import admin

from .models import Comment, Follow, Group, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Поля в админке постов."""

    list_display = ('pk', 'text', 'created', 'author', 'group',)
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('created',)
    empty_value_display = '-пусто-'


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """Поля в админке групп."""

    list_display = ('pk', 'title', 'slug',)
    search_fields = ('title',)
    empty_value_display = '-пусто-'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Поля в админке комментариев."""

    list_display = ('pk', 'text', 'author',)
    search_fields = ('author',)
    empty_value_display = '-пусто-'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Поля в админке подписок."""

    list_display = ('pk', 'user', 'author',)
    search_fields = ('user',)
    empty_value_display = '-пусто-'
