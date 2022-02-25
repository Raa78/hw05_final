from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    """Модель для сообществ."""

    title = models.CharField(
        max_length=200,
        verbose_name='Название группы',
        help_text='Группа, к которой относится пост',
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Уникальный URL',
        help_text='Уникальный URL группы',
    )
    description = models.TextField(
        verbose_name='Описание сообщества',
        help_text='Описание-тема группы',
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    """Модель для хранения всех постов."""

    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа к которой относится пост',
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True,
    )

    class Meta:
        ordering = [
            '-pub_date',
        ]

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    """Модель для создания комментариев к посту."""

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Текст поста',
        help_text='Укажите пост',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
        help_text='Укажите автора',
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Введите текст комментария',
    )
    created = models.DateTimeField(
        verbose_name='Дата создания комментария',
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            '-created',
        ]

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Подписан на автора',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'user',
                    'author',
                ],
                name='unique_follow',
            ),
        ]
