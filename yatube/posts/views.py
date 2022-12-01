from django.conf import settings

from django.contrib.auth.decorators import login_required

from django.core.paginator import Paginator

from django.http import HttpRequest, HttpResponse

from django.shortcuts import get_object_or_404, redirect, render

from django.http import HttpResponse

from .forms import CommentForm, PostForm

from .models import Comment, Follow, Group, Post, User

from django.views.decorators.cache import cache_page

from .utpag import paginator

PER_PAGE = settings.PERPAGE
POST_TITLE = 30


@cache_page(20, key_prefix="index_page")
def index(request: HttpRequest) -> HttpResponse:
    """Модуль отвечающий за главную страницу."""
    posts = Post.objects.select_related('author', 'group')
    paginator = Paginator(posts, PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': 'Последние обновления на сайте',
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request: HttpRequest, slug: str) -> HttpResponse:
    """Модуль отвечающий за страницу сообщества."""
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author')
    paginator = Paginator(posts, PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
        'title': f'Записи сообщества {slug}',
        'gr_descr': group.description,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request: HttpRequest, username: str) -> HttpResponse:
    """Модуль отвечающий за личную страницу пользователя."""
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('group')
    post_list = author.posts.all()
    posts_count = post_list.count()
    paginator = Paginator(posts, PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    following = (
        request.user.is_authenticated
        and Follow.objects.filter(
            user=request.user,
            author=author,
        ).exists()
    )
    context = {
        'author': author,
        'posts_count': posts_count,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request: HttpRequest, post_id: int) -> HttpResponse:
    """Модуль отвечающий за просмотр отдельного поста."""
    post = get_object_or_404(
        Post.objects.select_related('group', 'author'), id=post_id)
    comments = Comment.objects.select_related("comments")
    posts_count = post.author.posts.count()
    comment_count = comments.count()
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'post_title': post.text[:POST_TITLE],
        'posts_count': posts_count,
        'form': form,
        'comments': comments,
        'comment_count': comment_count,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request: HttpRequest) -> HttpResponse:
    """Модуль отвечающий за страницу создания текста постов."""
    form = PostForm(request.POST or None, files=request.FILES or None)

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author.username)
    context = {'form': form, 'is_edit': False}
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request: HttpRequest, post_id: int) -> HttpResponse:
    """Модуль отвечающий за страницу редактирования текста постов."""
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )

    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    # Получите пост и сохраните его в переменную post.
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post.delete()
    return redirect('posts:profile', request.user)


@login_required
def follow_index(request):
    """Старница с постами авторов, на которых подписан текущий пользователь."""
    template_name = 'posts/follow.html'
    posts = Post.objects.filter(author__following__user=request.user).all()
    page_obj = paginator(posts, request, PER_PAGE)

    context = {
        'following': True,
        'page_obj': page_obj,
    }
    return render(request, template_name, context)


@login_required
def profile_follow(request, username):
    """Подписаться на автора."""
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    """Отписаться от автора."""
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', username=username)
