from django.contrib import admin

from .models import Title, Genre, Category, Review, Comment


class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'year',
        'description',
        'category',
    )
    filter_horizontal = ('genre',)
    search_fields = ('name', 'year', 'genre', 'category',)
    empty_value_display = '-пусто-'


class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    search_fields = ('name', 'slug',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    search_fields = ('name', 'slug',)


class ReviewsAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'title', 'author', 'pub_date', 'score')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'review', 'author', 'pub_date')


admin.site.register(Title, TitleAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Review, ReviewsAdmin)
admin.site.register(Comment, CommentAdmin)
