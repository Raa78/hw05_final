from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def index(request):
    """Обработчик запросов на главной странице."""
    posts = Post.objects.all()
    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    templates = 'posts/index.html'
    title = 'Главная страница'
    context = {
        'page_obj': page_obj,
        'title': title,
    }
    return render(request, templates, context)


def group_posts(request, slug):
    """Обработчик запросов на странице сообществ."""
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    templates = 'posts/group_list.html'
    title = 'Записи сообщества:'
    context = {
        'group': group,
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, templates, context)


def profile(request, username):
    """Обработчик запросов профайла пользователя."""
    author = get_object_or_404(User, username=username)
    count_posts = author.posts.count()
    posts = author.posts.all()
    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template = 'posts/profile.html'
    title = 'Профайл пользователя'
    following = (request.user.is_authenticated and Follow.objects.filter(
        user=request.user,
        author=author).exists()
    )
    context = {
        'author': author,
        'count_posts': count_posts,
        'page_obj': page_obj,
        'title': title,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    """Обработчик страницы отдельного поста."""
    post = get_object_or_404(Post, id=post_id)
    posts_count = post.author.posts.count()
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    template = 'posts/post_detail.html'
    context = {
        'post': post,
        'posts_count': posts_count,
        'comments': comments,
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    """Обработчик страницы создания поста."""
    form = PostForm(request.POST or None)
    template = 'posts/create_post.html'
    title = 'Новый пост'
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user.username)

    context = {
        'form': form,
        'title': title,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    """Обработчик страницы ректирования поста."""
    post = get_object_or_404(Post, pk=post_id)
    template = 'posts/create_post.html'
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    """Обработчик добавления коментария к посту."""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Обработчик страницы со списком постов автора
    на которого подписан пользователь.
    """
    posts = Post.objects.filter(
        author__following__user=request.user
    )
    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Обработчик подписки на автора."""
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(
            user=request.user,
            author=author,
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    """Обработчик отписки от автора."""
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.filter(
            user=request.user,
            author=author,
        ).delete()
    return redirect('posts:profile', username=username)
