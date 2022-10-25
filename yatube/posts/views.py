from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm
from .utils import paginations


def index(request):
    posts = Post.objects.select_related('group').all()
    page_obj = paginations(request, posts)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.group_posts.all()
    page_obj = paginations(request, posts)
    context = {
        'posts': posts,
        'page_obj': page_obj,
        'group': group,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    all_posts = posts.count()
    following = Follow.objects.filter(
        user=request.user.id, author=author
    )
    # user.id не получается избавиться - иначе падают тесты
    # test_profile_paginator_view & test_profile_view_get
    # c ошибкой TypeError: 'AnonymousUser' object is not iterable
    page_obj = paginations(request, posts)
    context = {
        'author': author,
        'following': following,
        'page_obj': page_obj,
        'all_posts': all_posts,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    all_posts = post.author.posts.all().count()
    comments = post.comments.all()
    form = CommentForm()
    context = {
        'post': post,
        'all_posts': all_posts,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(
            request.POST,
            files=request.FILES or None,
        )
        if form.is_valid():
            form = form.save(commit=False)
            form.author = request.user
            form.save()
            return redirect(
                'posts:profile',
                form.author
            )
        return render(request, 'posts/create_post.html', {'form': form})
    form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect(
            'posts:post_detail', post_id
        )
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect(
            'posts:post_detail', post_id
        )
    return render(request, 'posts/create_post.html', {
        'form': form, 'is_edit': True, 'post': post
    })


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.select_related('author', 'group').filter(
        author__following__user=request.user)
    # я так и не понял как тут заменить author__following__user на user
    # если ставить user - страница ломается, т.к. у модели Post
    # нет user поля
    # как по другому без __ описать я не придумал
    page_obj = paginations(request, posts)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    follower = request.user
    if follower != author:
        Follow.objects.get_or_create(user=follower, author=author)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    Follow.objects.filter(
        user=request.user,
        author__username=username
    ).delete()
    return redirect('posts:profile', username)
