from django.test import TestCase
from ..models import Post, Group
from django.contrib.auth import get_user_model


User = get_user_model()


class PostModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="test user")
        cls.post = Post.objects.create(
            text="Тестовый текст поста", author=cls.user)

    def test_Post_have_correct_object_names(self):
        post = PostModelTests.post
        post_check = post.__str__()
        post_result = post.text[:15]
        self.assertEqual(
            post_check,
            post_result,
            "метод __str__ работает не коректно для модели Post",)

    def test_Post_verbose_names(self):
        post = PostModelTests.post
        field_verbose_names = {
            "text": "Текст",
        }
        for field, value in field_verbose_names.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name,
                    value,
                    f"verbose_name работает не корретно "
                    f"в модели Post, значения {field}",)

    def test_Post_help_text(self):
        post = PostModelTests.post
        field_help_text = {"text": "Напишите, что думаете"}
        for field, value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text,
                    value,
                    f"help_text работает не корректно "
                    f"в модели Post, значения {field}",)


class GroupModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="test user")
        cls.group = Group.objects.create(
            title="Тестовый заголовок",
            slug="Тестовый слизень",
            description="Тестовое описание",)

    def test_Group_have_correct_objects_names(self):
        group = GroupModelTests.group
        group_check = group.__str__()
        group_result = group.title
        self.assertEqual(
            group_check,
            group_result,
            "метод __str__ работает не коректно для модели Group",)

    def test_Group_verbose_names(self):
        group = GroupModelTests.group
        field_vebose_names = {
            "title": "Название",
            "slug": "Название ссылки",
            "description": "Описание",
        }
        for field, value in field_vebose_names.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name,
                    value,
                    f"verbose_name работает не корретно "
                    f"в модели Group, значения {field}",)

    def test_Group_help_text(self):
        group = GroupModelTests.group
        field_help_text = {
            "title": "Дайте название группе",
            "slug": "Придумайте название ссылки группы",
            "description": "Опишите тему группы",
        }
        for field, value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).help_text,
                    value,
                    f"help_text работает не корретно "
                    f"в модели Group, значения {field}",)
