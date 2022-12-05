import shutil
import tempfile
from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.core.cache import cache
from ..models import Post, Group, Follow
from ..constants import POSTS_LIMIT, POSTS_LIMIT_TEST


User = get_user_model()

# Временная медиа папка
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B')
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=PostsViewsTests.small_gif,
            content_type='image/gif')
        cls.author = User.objects.create_user(username="test_author")
        cls.group = Group.objects.create(
            title="Тестовое название",
            description="Тестовое описание",
            slug="test_slug",
        )
        cls.post = Post.objects.create(
            text="test text",
            author=get_object_or_404(
                User,
                username=PostsViewsTests.author),
            group=get_object_or_404(Group, slug="test_slug"),
            image=cls.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_author = Client()
        self.authorized_author.force_login(PostsViewsTests.author)
        self.post_id = PostsViewsTests.post.id

    def test_posts_names_namespaces(self):
        templates_names = {
            "posts/index.html": reverse("posts:index"),
            "posts/group_list.html": reverse(
                "posts:group_posts", kwargs={"slug": "test_slug"}),
            "posts/profile.html": reverse(
                "posts:profile", kwargs={"username": "test_author"}),
            "posts/post_detail.html": reverse(
                "posts:post_detail", kwargs={"post_id": "1"}),
            "posts/create_post.html": reverse(
                "posts:post_edit", kwargs={"post_id": "1"})
        }
        for template, name in templates_names.items():
            with self.subTest(name=name):
                response = self.authorized_author.get(name)
                self.assertTemplateUsed(
                    response, template,
                    f"{name} не соотвествует {template}")
        response = self.authorized_author.get(reverse("posts:post_create"))
        self.assertTemplateUsed(
            response, "posts/create_post.html",
            f"{name} не соотвествует posts/create_post.html")

    def test_correct_context(self):
        template_names = {
            "posts:index": {},
            "posts:group_posts": {"slug": "test_slug"},
            "posts:profile": {"username": "test_author"},
            "posts:post_detail": {"post_id": f"{self.post_id}"},
        }
        for template, slug in template_names.items():
            response = self.authorized_author.get(reverse(
                template, kwargs=slug))
            if template == "posts:post_detail":
                first_object = response.context["post"]
            else:
                first_object = response.context["posts"][0]
            text = first_object.text
            author = str(first_object.author)
            check_context = {text: "test text", author: "test_author"}
            for field, info in check_context.items():
                with self.subTest(field=field):
                    self.assertEqual(
                        field, info,
                        f"context в {template} не совпадает с ожидаемым")

    def test_index_cache_working(self):
        cache.clear()
        main_page = reverse('posts:index')
        content1 = self.client.get(main_page).content
        PostsViewsTests.post.delete()
        content2 = self.client.get(main_page).content
        self.assertEqual(content1, content2)
        cache.clear()
        content3 = self.client.get(main_page).content
        self.assertNotEqual(content1, content3)


class PaginatorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="test_user_paginator")
        cls.author = User.objects.create_user(username="test_author_paginator")
        cls.group = Group.objects.create(
            title="test title", description="TESTTESTTEST", slug="test_slug")
        for post_number in range(1, 13):
            cls.post = Post.objects.create(
                text=f"test text post_number_{post_number}",
                author=get_object_or_404(User, username=PaginatorTests.author),
                group=get_object_or_404(Group, slug="test_slug"),)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PaginatorTests.user)
        self.template_names = {
            "posts:index": {},
            "posts:group_posts": {"slug": "test_slug"},
            "posts:profile": {"username": "test_author_paginator"},
        }

    def test_first_page_ten_posts(self):
        for template, slug in self.template_names.items():
            response = self.authorized_client.get(reverse(
                template, kwargs=slug))
            self.assertEqual(
                len(response.context["page_obj"]),
                POSTS_LIMIT,
                f"количество страниц в paginator {template} "
                "не совмпадает с ожидаемым",)

    def test_second_page_two_posts(self):
        for template, slug in self.template_names.items():
            response = self.authorized_client.get(reverse(
                template, kwargs=slug) + "?page=2")
            self.assertEqual(
                len(response.context["page_obj"]),
                POSTS_LIMIT_TEST,
                "количество страниц в вашем paginator "
                "не совмпадает с ожидаемым",)


class FollowViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test author')
        cls.user = User.objects.create_user(username='test user')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(FollowViewsTests.user)
        self.follow_count = Follow.objects.filter(
            user=FollowViewsTests.user,
            author=FollowViewsTests.author).count()

    def test_add_follower(self):
        response = self.authorized_client.get(reverse(
            "posts:profile_follow",
            kwargs={"username": f"{self.author}"}))
        self.assertRedirects(response, reverse(
            "posts:profile",
            kwargs={"username": f"{FollowViewsTests.author}"}))
        self.assertEqual(Follow.objects.filter(
            user=FollowViewsTests.user,
            author=FollowViewsTests.author).count(), self.follow_count + 1)

    def test_dont_follow_yourself(self):
        self.authorized_client.get(reverse(
            "posts:profile_follow",
            kwargs={"username": f"{self.user}"}))
        self.assertEqual(Follow.objects.filter(
            user=FollowViewsTests.user,
            author=FollowViewsTests.author).count(), self.follow_count)

    def test_delete_follower(self):
        response = self.authorized_client.get(reverse(
            "posts:profile_unfollow",
            kwargs={"username": f"{self.author}"}))
        self.assertRedirects(response, reverse(
            "posts:profile",
            kwargs={"username": f"{FollowViewsTests.author}"}))
        self.assertEqual(Follow.objects.filter(
            user=FollowViewsTests.user,
            author=FollowViewsTests.author).count(), self.follow_count)

    def test_following_authors_posts(self):
        response = self.authorized_client.get(reverse(
            "posts:follow_index"))
        posts = response.context["posts"]
        check_posts = True
        for post in posts:
            if post.author != FollowViewsTests.author:
                check_posts = False
                break
        self.assertTrue(check_posts)
