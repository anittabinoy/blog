from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login, logout
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, Count, Sum
from taggit.models import Tag
from .models import Post, Comment, UserProfile
from .forms import UserRegisterForm, PostForm, CommentForm, UserProfileForm, UserUpdateForm
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect

class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    ordering = ['-created_date']
    paginate_by = 5

    def post(self, request, *args, **kwargs):
        if 'login' in request.POST:
            login_form = AuthenticationForm(data=request.POST)
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                messages.success(request, 'You have been successfully logged in!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
        elif 'register' in request.POST:
            register_form = UserRegisterForm(request.POST)
            if register_form.is_valid():
                user = register_form.save()
                UserProfile.objects.create(user=user)
                login(request, user)
                messages.success(request, 'Your account has been created! You are now logged in.')
                return redirect('home')
            else:
                messages.error(request, 'Please correct the errors below.')
        elif 'logout' in request.POST:
            logout(request)
            messages.success(request, 'You have been logged out successfully!')
            return redirect('home')
        return self.get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        tag_slug = self.kwargs.get('tag_slug')
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = Tag.objects.annotate(
            num_times=Count('taggit_taggeditem_items')
        ).order_by('-num_times')[:10]
        context['recent_posts'] = Post.objects.order_by('-created_date')[:5]
        
        if not self.request.user.is_authenticated:
            context['login_form'] = AuthenticationForm()
            context['register_form'] = UserRegisterForm()
        
        return context

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        return context

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('home')
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Your account has been created! You are now logged in.')
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'blog/profile.html')

@login_required
def profile_edit(request):
    # Get or create the user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'blog/profile_edit.html', context)

@login_required
def post_like(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect('post_detail', slug=slug)

@login_required
def add_comment(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Your comment has been added!')
            return redirect('post_detail', slug=slug)
    return redirect('post_detail', slug=slug)

def post_search(request):
    query = request.GET.get('q')
    if query:
        posts = Post.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(author__username__icontains=query)
        ).distinct()
    else:
        posts = []
    return render(request, 'blog/search_results.html', {'posts': posts, 'query': query})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'You have been successfully logged in!')
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'blog/login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            messages.success(request, 'Your account has been created! Please login to continue.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'blog/register.html', {'form': form})

class BlogListView(ListView):
    model = Post
    template_name = 'blog/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 6
    ordering = ['-created_date']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_posts'] = Post.objects.order_by('-created_date')[:5]
        return context

class BloggerDetailView(ListView):
    model = Post
    template_name = 'blog/blogger_detail.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        self.blogger = get_object_or_404(User, username=self.kwargs['username'])
        return Post.objects.filter(author=self.blogger).order_by('-created_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['blogger'] = self.blogger
        context['total_posts'] = self.get_queryset().count()
        context['total_likes'] = sum(post.total_likes for post in self.get_queryset())
        return context

class BloggersListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'blog/bloggers_list.html'
    context_object_name = 'bloggers'
    paginate_by = 12

    def get_queryset(self):
        return User.objects.filter(post__isnull=False).distinct().order_by('-date_joined')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for blogger in context['bloggers']:
            blogger.post_count = blogger.post_set.count()
            blogger.total_likes = sum(post.total_likes for post in blogger.post_set.all())
        return context

class BloggerView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'blog/bloggers.html'
    context_object_name = 'bloggers'
    paginate_by = 10

    def get_queryset(self):
        return User.objects.annotate(
            post_count=Count('post')
        ).filter(post_count__gt=0).order_by('-date_joined')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add user's posts
        if self.request.user.is_authenticated:
            user_posts = Post.objects.filter(author=self.request.user).order_by('-created_date')
            context['user_posts'] = user_posts
            
            # Calculate total likes for current user
            total_likes = 0
            for post in user_posts:
                if isinstance(post.total_likes, int):
                    total_likes += post.total_likes
            context['user_total_likes'] = total_likes

        # Calculate total likes for each blogger
        for blogger in context['bloggers']:
            posts = Post.objects.filter(author=blogger)
            total_likes = 0
            for post in posts:
                if isinstance(post.total_likes, int):
                    total_likes += post.total_likes
            blogger.total_likes = total_likes

        return context

class BloggerEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    template_name = 'blog/blogger_edit.html'
    fields = ['username', 'email', 'first_name', 'last_name']
    
    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_form'] = UserProfileForm(instance=self.object.userprofile)
        return context
    
    def form_valid(self, form):
        profile_form = UserProfileForm(self.request.POST, self.request.FILES, instance=self.object.userprofile)
        if profile_form.is_valid():
            profile_form.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        messages.success(self.request, 'Profile updated successfully!')
        return reverse_lazy('bloggers')
    
    def test_func(self):
        user = self.get_object()
        return self.request.user == user or self.request.user.is_staff

class BloggerDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = User
    success_url = reverse_lazy('bloggers')
    
    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Account deleted successfully.')
        return super().delete(request, *args, **kwargs)
    
    def test_func(self):
        user = self.get_object()
        return self.request.user == user or self.request.user.is_staff
