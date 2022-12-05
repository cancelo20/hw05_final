from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from ..models import Post, Group
from ..constants import RESPONSE_CODE_200, RESPONSE_CODE_404


User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username="test_author")
        cls.post = Post.objects.create(
            text="test text",
            author=get_object_or_404(
                User,
                username=PostsURLTests.author),)
        cls.group = Group.objects.create(
            title="Тестовое название",
            description="Тестовое описание",
            slug="test_slug",)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.user = User.objects.create_user(username="test_user")
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(PostsURLTests.author)
        self.post_id = PostsURLTests.post.id

    def test_posts_for_all_exists_desired_location(self):
        urls = [
            "/",
            "/group/test_slug/",
            "/profile/test_user/",
            f"/posts/{self.post_id}/",
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(
                    response.status_code,
                    RESPONSE_CODE_200,
                    f"При запросе к {url}  не возвращается код 200",)

    def test_posts_for_all_uses_correct_templates(self):
        urls_templates = {
            "/": "posts/index.html",
            "/group/test_slug/": "posts/group_list.html",
            "/profile/test_user/": "posts/profile.html",
            f"/posts/{self.post_id}/": "posts/post_detail.html",
        }
        for url, template in urls_templates.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(
                    response,
                    template,
                    f"url - {url} не соотвествует"
                    "template - {template}",)

    def test_posts_for_authorized_exists_desired_location(self):
        url = "/create/"
        response = self.authorized_client.get(url)
        self.assertEqual(
            response.status_code,
            RESPONSE_CODE_200,
            f"При запросе к {url} не возвращается код 200",)

    def test_posts_for_authorized_uses_correct_templates(self):
        url = "/create/"
        template = "posts/create_post.html"
        response = self.authorized_client.get(url)
        self.assertTemplateUsed(
            response, template,
            f"url - {url} не соотвествует template - {template}")

    def test_posts_for_author_exists_desire_location(self):
        url = f"/posts/{self.post_id}/edit/"
        response = self.authorized_author.get(url)
        self.assertEqual(
            response.status_code,
            RESPONSE_CODE_200,
            f"При запросе к {url} не возвращается код 200",)

    def test_posts_for_author_uses_correct_templates(self):
        url = f"/posts/{self.post_id}/edit/"
        template = "posts/create_post.html"
        response = self.authorized_author.get(url)
        self.assertTemplateUsed(
            response, template,
            f"url - {url} не соотвествует template - {template}")

    def test_no_name_page_respond_404(self):
        url = "/no_name_page/"
        response = self.guest_client.get(url)
        self.assertEqual(
            response.status_code,
            RESPONSE_CODE_404,
            "При запросе к несуществующей странице"
            "не возвращается код 404",)
