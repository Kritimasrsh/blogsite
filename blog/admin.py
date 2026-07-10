from django.contrib import admin
from .models import Post, Category, Tag

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "published", "created_at")
    list_filter = ("published", "category", "tags")
    search_fields = ("title", "content")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)