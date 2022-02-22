import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms

from ..models import Follow, Group, Post
from ..forms import PostForm

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Author')
        cls.noauthor = User.objects.create_user(username='NoAuthor')
        cls.another = User.objects.create_user(username='Another')
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
            slug='test-slug',
            description='Тестовое описание сообщества',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.author,
            group=cls.group,
            image=cls.uploaded,
        )
        cls.group_second = Group.objects.create(
            title='Тестовое название группы',
            slug='test-slug_second',
            description='Тестовое описание сообщества',
        )
        cls.templates_namespase_name_url_1 = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': cls.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': cls.author.username}
            ): 'posts/profile.html',
        }
        cls.templates_namespase_name_url_2 = {
            reverse(
                'posts:post_detail',
                kwargs={'post_id': cls.post.pk}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': cls.post.pk}
            ): 'posts/create_post.html',
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client(self.author)
        self.authorized_client.force_login(self.author)
        self.authorized_client_2 = Client(self.noauthor)
        self.authorized_client_2.force_login(self.noauthor)
        self.authorized_client_3 = Client(self.another)
        self.authorized_client_3.force_login(self.another)

    def check_context_post(self, post_object):
        """Набор проверок передаваемого контекста"""
        self.assertEqual(post_object.id, self.post.id)
        self.assertEqual(post_object.text, self.post.text)
        self.assertEqual(post_object.author, self.author)
        self.assertEqual(post_object.group, self.group)
        # Проверяем при выводе поста с картинкой
        # изображение передаётся в словаре context
        self.assertEqual(post_object.image, self.post.image)

    def test_posts_page_uses_correct_template(self):
        """При запросе к namespase:name
        применяется правельный шаблон.
        """
        templates_name_url_joint = {
            **self.templates_namespase_name_url_1,
            **self.templates_namespase_name_url_2
        }
        for reverse_name, template in templates_name_url_joint.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        post_object = response.context['page_obj'][0]
        self.check_context_post(post_object)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug})
        )
        post_object = response.context['page_obj'][0]

        self.check_context_post(post_object)
        # Фильтруем по групе
        self.assertEqual(post_object.pk, self.group.pk)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.author.username})
        )
        post_object = response.context['page_obj'][0]
        self.check_context_post(post_object)
        # Фильтруем по пользователю
        user_object = response.context['author']
        self.assertEqual(user_object.username, self.author.username)
        # Изображение передаётся в словаре context
        self.assertEqual(post_object.image, self.post.image)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk})
        )
        post_object = response.context['post']
        self.assertEqual(post_object.pk, self.post.pk)
        # Изображение передаётся в словаре context
        self.assertEqual(post_object.image, self.post.image)

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
                self.assertIsInstance(response.context['form'], PostForm)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertIsInstance(response.context['form'], PostForm)
        self.assertTrue(response.context.get('is_edit'))

    def test_post_new_show_index_group_profile(self):
        """Новый пост отображается на главной странице,
        на странице группы, в профайле автора."""
        for reverse_name in self.templates_namespase_name_url_1.keys():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertIn(self.post, response.context['page_obj'])

    def test_post_new_not_in_group(self):
        """Новый пост не находится в другой группе,
        где он не должен находиться."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group_second.slug})
        )
        self.assertNotIn(self.post, response.context['page_obj'])

    def test_create_follow_authorized(self):
        """Неавторизованный пользователь
        не может подписаться на автора.
        """
        follow_count = Follow.objects.count()
        response = self.client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.author}),
        )
        expected_redirect = reverse('users:login') + '?next=' + reverse(
            'posts:profile_follow', kwargs={'username': self.author}
        )
        self.assertEqual(Follow.objects.count(), follow_count)
        self.assertRedirects(response, expected_redirect)

    def test_follow_authorized(self):
        """Авторизованный пользователь может
        подписываться на других пользователей.
        """
        follow_count = Follow.objects.count()
        self.authorized_client_2.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.author}),
        )
        self.assertEqual(Follow.objects.count(), follow_count + 1)

    def test_not_follow_myself(self):
        """Авторизованный пользователь не может
        подписываться на себя.
        """
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.author.username}),
        )
        self.assertFalse(
            Follow.objects.filter(
                user=self.author,
                author=self.author,
            ).exists()
        )

    def test_unfollow_authorized(self):
        """Авторизованный пользователь может
        отписаться на других пользователей.
        """
        Follow.objects.get_or_create(
            user=self.noauthor,
            author=self.author
        )
        follow_count = Follow.objects.count()
        self.authorized_client_2.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.author}),
        )
        self.assertEqual(Follow.objects.count(), follow_count - 1)

    def test_follow_show_index(self):
        """Новая запись пользователя появляется
        в ленте тех, кто на него подписан
        и не появляется в ленте тех, кто не подписан.
        """
        self.authorized_client_2.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.author})
        )
        response = self.authorized_client_2.get(
            reverse('posts:follow_index'))
        self.assertIn(
            self.post,
            response.context.get('page_obj').object_list
        )
        response = self.authorized_client_3.get(reverse(
            'posts:follow_index'))
        self.assertNotIn(
            self.post,
            response.context.get('page_obj').object_list
        )

    def test_cache_index(self):
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        response_cached = response.content
        post = Post.objects.get(pk=1)
        post.delete()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.content, response_cached)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(
            username='Author2',
        )
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test_slug',
            description='Тестовое описание сообщества',
        )
        cls.namespase_name = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': cls.group.slug}),
            reverse('posts:profile', kwargs={'username': cls.author.username}),
        ]
        post_test = [
            Post(
                text=f'Тестовый пост №{i}',
                author=cls.author,
                group=cls.group
            ) for i in range(13)
        ]
        Post.objects.bulk_create(post_test)

    def setUp(self):
        self.guest_client = Client()

    def test_paginator_on_pages(self):
        """Тестирование паджинатора на страницах
        index, group_list, profile.
        """
        number_posts_first_page = 10
        number_posts_second_page = 3
        for reverse_name in self.namespase_name:
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(len(self.guest_client.get(
                    reverse_name).context.get('page_obj')),
                    number_posts_first_page
                )
                amount_page = {'page': 2}
                self.assertEqual(len(self.guest_client.get(
                    reverse_name, amount_page).context.get('page_obj')),
                    number_posts_second_page
                )
