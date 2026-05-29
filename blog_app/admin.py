from django.contrib import admin
from .models import Profile,BlogPost,BlogPostImage

# Register your models here.
admin.site.register(Profile)
admin.site.register(BlogPost)
admin.site.register(BlogPostImage)
