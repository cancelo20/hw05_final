from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Дайте название группе')
    description = models.TextField(
        verbose_name='Описание',
        help_text='Опишите тему группы')
    slug = models.SlugField(
        unique=True,
        verbose_name='Название ссылки',
        help_text='Придумайте название ссылки группы')

    def __str__(self):
        return f'{self.title}'


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст',
        help_text='Напишите, что думаете')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор')
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts_of_group',
        verbose_name='Группа',
        help_text='Группа поста')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания')
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='posts/',
        blank=True)

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ['-pub_date']


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментарии')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментатор')
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания')
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Напишите комментарий')


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор')
