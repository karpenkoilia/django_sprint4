from django.contrib import admin
from .models import Category, Post, Location, Comments

admin.site.register(Category)
admin.site.register(Post)
admin.site.register(Location)
admin.site.register(Comments)
