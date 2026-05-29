import random
from django.core.cache import cache
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import logout
from .models import BlogPost, BlogPostImage, Profile
from django.core.mail import EmailMultiAlternatives


# Create your views here.
def home(request):
    posts = BlogPost.objects.all().order_by('-created_at')
    return render(request, 'blog_app/home.html', {'posts': posts})


def blog_detail_view(request, post_id):
    post = BlogPost.objects.get(id=post_id)
    images = post.images.all()
    return render(request, 'blog_app/blog_detail.html', {'post': post, 'images': images})


def create_blog_view(request):
    if not request.user.is_authenticated or not request.user.profile.is_creator:
        messages.error(request, 'You need to be a creator to create a blog post')
        return redirect('home')
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        images = request.FILES.getlist('images[]')
        print(f"Received {len(images)} images for the blog post.")
        blog_post = BlogPost.objects.create(author=request.user, title=title, content=content)
        for image in images:
            BlogPostImage.objects.create(blog_post=blog_post, image=image)
        blog_post.save()
        messages.success(request, 'Blog post created successfully')
        return redirect('home')
    return render(request, 'blog_app/create_blog.html')


def become_creator_view(request):
    if request.user.is_authenticated and request.user.profile.is_creator:
        return redirect('home')
    return render(request, 'blog_app/become_creator.html')


def send_otp_view(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You need to be logged in to become a creator')
        return redirect('login')
    
    user = request.user
    otp = random.randint(100000, 999999)
    
    cache.set(f'otp_{user.id}', otp, timeout=300)
    
    email_body = render_to_string('blog_app/otp_email.html', {'user': user, 'otp': otp}) 
    
    email = EmailMultiAlternatives(
        subject='Your OTP Code',
        body=f'Your OTP is {otp}',
        from_email='shoppingdemonx1@gmail.com',
        to=[user.email],
    )
    
    email.attach_alternative(email_body, "text/html")
    email.send()
    
    messages.success(request, 'OTP sent to your email. Please check your inbox.')
    
    return redirect('verify-otp')


def verify_otp_view(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You need to be logged in to verify OTP')
        return redirect('login')
    
    if request.method == 'POST':
        user = request.user
        entered_otp = request.POST.get('otp')
        cached_otp = cache.get(f'otp_{user.id}')
        
        if cached_otp and str(cached_otp) == entered_otp:
            profile = user.profile
            profile.is_creator = True
            profile.save()
            cache.delete(f'otp_{user.id}')
            messages.success(request, 'OTP verified successfully. You are now a creator!')
            email_body = render_to_string('blog_app/creator_welcome_email.html', {'user': user})
            email = EmailMultiAlternatives(
                subject='Welcome to Creator Community',
                body='Congratulations on becoming a creator!',
                from_email='shoppingdemonx1@gmail.com',
                to=[user.email],
            )
            email.attach_alternative(email_body, "text/html")
            email.send()
            return redirect('home')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
            return redirect('verify-otp')
    
    return render(request, 'blog_app/verify_otp.html')


def edit_profile_view(request):
    if request.method == 'POST':
        bio = request.POST.get('bio')
        profile_picture = request.FILES.get('profile_picture')
        
        profile, created = Profile.objects.get_or_create(user=request.user)
        profile.bio = bio
        if profile_picture:
            profile.profile_picture = profile_picture
        profile.save()
        messages.success(request, 'Profile updated successfully')
        return redirect('home')
    return render(request, 'blog_app/edit_profile.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in successfully')
            if Profile.objects.filter(user=user).exists():
                return redirect('home')
            else:
                return redirect('edit_profile')
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('login')
    return render(request, 'blog_app/login.html')


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'Logged out successfully')
    return redirect('home')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('passwd1')
        confirm_password = request.POST.get('passwd2')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('register')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('register')
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, 'Registration successful. Please login.')
        return redirect('login')
    return render(request, 'blog_app/register.html')