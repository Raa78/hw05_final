import shutil
import tempfile

from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Comment, Group, Post
from ..forms import CommentForm

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Author')
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.author,
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            author=cls.author,
            text='Тестовый пост',
            post=cls.post
        )
        cls.form = CommentForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_create_post(self):
        """Валидная форма создает запись в БД."""
        posts_count = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': self.post.text,
            'image': self.uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:profile',
                kwargs={'username': self.author.username})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(self.uploaded, form_data['image'])
        self.assertTrue(
            Post.objects.filter(
                group=form_data['group'],
                text=form_data['text'],
                image=Post.objects.first().image,
            ).exists()
        )

    def test_create_post_guest(self):
        """Проверка создания поста
        неавторизованным пользователем.
        """
        posts_count = Post.objects.count()
        form_data = {
            'text': self.post.text,
            'author': self.author,
            'group': self.group.id,
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('users:login') + '?next=' + reverse('posts:post_create'))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post(self):
        """Валидная форма изменяет запись в БД."""
        posts_count = Post.objects.count()
        form_data = {
            'text': self.post.text,
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response, reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk})
        )
        self.assertTrue(
            Post.objects.filter(
                id=self.post.pk,
                text=form_data['text'],
                group=form_data['group'],
            ).exists()
        )


class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Author')
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.author,
            group=cls.group
        )
        cls.comment = Comment.objects.create(
            author=cls.author,
            text='Тестовый пост',
            post=cls.post
        )
        cls.form = CommentForm()
        cls.form_data = {
            'text': 'Тестовый комментарий',
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_create_comments_authorized(self):
        """Cоздает комментарий только авторизованный пользователь."""
        comment_count = Comment.objects.count()
        self.authorized_client.post(reverse(
            'posts:add_comment',
            kwargs={'post_id': self.post.pk}),
            data=self.form_data,
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)

    def test_create_comments_authorized(self):
        """Неавторизованный пользователь
        не может создать комментарий.
        """
        comment_count = Comment.objects.count()
        response = self.guest_client.post(reverse(
            'posts:add_comment',
            kwargs={'post_id': self.post.pk}),
            data=self.form_data,
            follow=True,
        )
        expected_redirect = reverse('users:login') + '?next=' + reverse(
            'posts:add_comment', kwargs={'post_id': self.post.pk}
        )
        self.assertEqual(Comment.objects.count(), comment_count)
        self.assertRedirects(response, expected_redirect)

    def test_add_comments(self):
        """Комментарий появляется на странице поста."""
        response = self.authorized_client.post(reverse(
            'posts:add_comment',
            kwargs={'post_id': self.post.pk}),
            data=self.form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.pk})
        )
        self.assertTrue(
            Comment.objects.filter(
                text='Тестовый комментарий',
            ).exists()
        )
