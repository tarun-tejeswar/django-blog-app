from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('edit_profile/', views.edit_profile_view, name='edit_profile'),
    path('become_creator/', views.become_creator_view, name='become_creator'),
    path('send-otp/', views.send_otp_view, name='send-otp'),
    path('verify-otp/', views.verify_otp_view, name='verify-otp'),
    path('create-blog/', views.create_blog_view, name='create-blog'),
    path('blog/<int:post_id>/', views.blog_detail_view, name='blog-detail'),
]