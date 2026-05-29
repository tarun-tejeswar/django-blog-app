from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    is_creator = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True,null=True)

    def __str__(self):
        return self.user.username
    
    

class BlogPost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    

def upload_blog_image(instance, filename):
    return f'blog_images/{instance.blog_post.id}/{filename}'

class BlogPostImage(models.Model):
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=upload_blog_image)

    def __str__(self):
        return f"Image for {self.blog_post.title}"