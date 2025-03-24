from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.PostListView.as_view(), name='home'),
    path('blog/', views.BlogListView.as_view(), name='blog'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('post/new/', views.PostCreateView.as_view(), name='post_create'),
    path('post/<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('post/<slug:slug>/edit/', views.PostUpdateView.as_view(), name='post_update'),
    path('post/<slug:slug>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    path('post/<slug:slug>/like/', views.post_like, name='post_like'),
    path('post/<slug:slug>/comment/', views.add_comment, name='add_comment'),
    path('tag/<slug:tag_slug>/', views.PostListView.as_view(), name='post_list_by_tag'),
    path('search/', views.post_search, name='post_search'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('blogs/', views.BlogListView.as_view(), name='blog_list'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='blog/password_change.html'), 
         name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='blog/password_change_done.html'), 
         name='password_change_done'),
    path('blogger/<str:username>/', views.BloggerDetailView.as_view(), name='blogger_detail'),
    path('bloggers/', views.BloggerView.as_view(), name='bloggers'),
    path('blogger/<str:username>/edit/', views.BloggerEditView.as_view(), name='blogger_edit'),
    path('blogger/<str:username>/delete/', views.BloggerDeleteView.as_view(), name='blogger_delete'),
] 