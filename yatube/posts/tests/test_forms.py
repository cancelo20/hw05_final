import shutil
import tempfile
from django.test import TestCase, Client, override_settings
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.urls import reverse
from ..models import Post, Comment


User = get_user_model()

# Временная медиа папка
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsFormsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.post = Post.objects.create(
            text="text text",
            author=get_object_or_404(
                User,
                username=PostsFormsTest.user))

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.post_id = PostsFormsTest.post.id
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsFormsTest.user)
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B')
        self.uploaded_create = SimpleUploadedFile(
            name='create_post.gif',
            content=self.small_gif,
            content_type='image/gif')

        self.uploaded_edit = SimpleUploadedFile(
            name='edit_post.gif',
            content=self.small_gif,
            content_type='image/gif')

    def test_create_post_form_added_new_post(self):
        post_count = Post.objects.count()
        form_data = {
            "text": "BIG TEST TEXT",
            "image": self.uploaded_create}
        response = self.authorized_client.post(
            reverse(
                "posts:post_create"),
            data=form_data,
            follow=True)
        self.assertRedirects(response, reverse(
            "posts:profile",
            kwargs={"username": "test_user"}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(Post.objects.filter(
            text="BIG TEST TEXT",
            image="posts/create_post.gif").exists())

    def test_edit_post_changes_post(self):
        post_count = Post.objects.count()
        form_data = {
            "text": "small test text",
            "image": self.uploaded_edit}
        response = self.authorized_client.post(
            reverse(
                "posts:post_edit",
                kwargs={"post_id": f"{self.post_id}"}),
            data=form_data,
            follow=True,)
        self.assertRedirects(response, reverse(
            "posts:post_detail",
            kwargs={"post_id": f"{self.post_id}"}))
        self.assertEqual(Post.objects.count(), post_count)
        self.assertTrue(Post.objects.filter(
            text="small test text",
            image="posts/edit_post.gif").exists())

    def test_add_comment_autorized_user(self):
        comment_count = Comment.objects.filter(
            post=PostsFormsTest.post.id).count()
        form_data = {
            "post": get_object_or_404(
                Post, pk=PostsFormsTest.post.id),
            "author": get_object_or_404(
                User, username=PostsFormsTest.user),
            "text": "TEST COMMENT TEXT"}
        response = self.authorized_client.post(reverse(
            "posts:add_comment",
            kwargs={"post_id": f"{self.post_id}"}),
            data=form_data,
            follow=True)
        self.assertRedirects(response, reverse(
            "posts:post_detail",
            kwargs={"post_id": f"{self.post_id}"}))
        self.assertEqual(Comment.objects.filter(
            post=PostsFormsTest.post.id).count(), comment_count + 1)
        self.assertTrue(Comment.objects.filter(
            text="TEST COMMENT TEXT",
            post=get_object_or_404(
                Post, pk=PostsFormsTest.post.id)))
