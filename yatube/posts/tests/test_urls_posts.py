from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Author')
        cls.user = User.objects.create_user(username='NoAuthor')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание сообщества',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Текстовая группа'
        )
        cls.templates_names_url_for_all = {
            '/': 'posts/index.html',
            f'/group/{cls.group.slug}/': 'posts/group_list.html',
            f'/profile/{cls.author.username}/': 'posts/profile.html',
            f'/posts/{cls.post.pk}/': 'posts/post_detail.html',
        }
        cls.templates_names_url_for_author = {
            '/create/': 'posts/create_post.html',
            f'/posts/{cls.post.pk}/edit/': 'posts/create_post.html',
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client(self.author)
        self.authorized_client.force_login(self.author)
        self.authorized_client_2 = Client(self.user)
        self.authorized_client_2.force_login(self.user)

    def test_posts_url_exists_at_desired_location(self):
        """Страницы доступные любому пользователю."""
        for address in self.templates_names_url_for_all.keys():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_url_exists_at_desired_location_authorized(self):
        """Страницы доступные авторизованному пользователю."""
        for address in self.templates_names_url_for_author.keys():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_redirect_not_authorized(self):
        """Перенаправление неавторизованного пользователя
        на страницу авторизации.
        """
        response = self.client.get(
            reverse('posts:post_create')
        )
        expected_redirect = reverse('users:login') + '?next=' + reverse(
            'posts:post_create'
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response, expected_redirect
        )

    def test_posts_edit_for_no_author(self):
        """Страница редактирования поста
        'posts/<posts_id>/edit/' только для автором поста.
        """
        response = self.authorized_client_2.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk})
        )
        expected_redirect = reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.pk})
        self.assertRedirects(
            response, expected_redirect
        )

    def test_posts_urls_uses_correct_template_all(self):
        """URL-адресу соответствует шаблон доступный
        любому пользователю.
        """
        for address, template in self.templates_names_url_for_all.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_posts_urls_uses_correct_template_authorized(self):
        """URL-адресу соответствует шаблон доступный
        авторизованному пользователю.
        """
        for address, template in self.templates_names_url_for_author.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_follow_urls_uses_correct_template_authorized(self):
        """URL-адресу /follow/ соответствует шаблон доступный
        авторизованному пользователю.
        """
        response = self.authorized_client.get('/follow/')
        self.assertTemplateUsed(response, 'posts/follow.html')
