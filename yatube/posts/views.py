from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, Comment, Follow
from django.contrib.auth import get_user_model
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from .utils import paginator_page


User = get_user_model()


def index(request):
    posts = Post.objects.select_related(
        'group', 'author').all()
    page_obj = paginator_page(request, posts)
    context = {
        "posts": posts,
        "page_obj": page_obj}
    return render(request, "posts/index.html", context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts_of_group.filter(group=group)
    page_obj = paginator_page(request, posts)
    context = {
        "group": group,
        "posts": posts,
        "page_obj": page_obj}
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    profile_posts = author.posts.filter(author=author)
    page_obj = paginator_page(request, profile_posts)
    following = False
    follow_yourself = request.user != author
    if request.user.is_authenticated:
        following = True
    context = {
        "posts": profile_posts,
        "author": author,
        "page_obj": page_obj,
        "following": following,
        "follow_yourself": follow_yourself}
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    number_of_posts = Post.objects.filter(author=post.author).count()
    comments = Comment.objects.filter(post=post_id).order_by('-created')
    comment_form = CommentForm(request.POST or None)
    is_edit = True if post.author == request.user else False
    context = {
        "post": post,
        "number_of_posts": number_of_posts,
        "form": comment_form,
        "comments": comments,
        "is_edit": is_edit}
    return render(request, "posts/post_detail.html", context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None)
    if form.is_valid():
        new_form = form.save(commit=False)
        new_form.author = request.user
        new_form.save()
        return redirect("posts:profile", username=request.user.username)
    groups = Group.objects.all()
    context = {
        "form": form,
        "groups": groups,
        "is_edit": False}
    return render(request, "posts/create_post.html", context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user_check = get_object_or_404(Post, pk=post_id)
    if user_check.author != request.user:
        return redirect("posts:post_detail", post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    if form.is_valid():
        form.save()
        return redirect("posts:post_detail", post_id=post_id)
    context = {
        "form": form,
        "is_edit": True,
        "post": post}
    return render(request, "posts/create_post.html", context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
    return redirect("posts:post_detail", post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(
        author__following__user=request.user)
    page_obj = paginator_page(request, posts)
    context = {
        "posts": posts,
        "page_obj": page_obj}
    return render(request, "posts/follow.html", context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    Follow.objects.get_or_create(
        user=user, author=author) if author != request.user else None
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follower = Follow.objects.filter(user=request.user, author=author)
    follower.delete()
    return redirect('posts:profile', username=username)
