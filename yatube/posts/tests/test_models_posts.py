from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Comment, Follow, Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст проверяет вывод первых 15 символов метода __str__',
        )

    def test_models_have_correct_object_group(self):
        """У модели Group корректно работает __str__."""
        group = PostModelTest.group
        expected_group = group.title
        self.assertEqual(expected_group, str(group))

    def test_models_have_correct_object_post(self):
        """У модели Post корректно работает __str__."""
        post = PostModelTest.post
        expected_text = post.text[:15]
        self.assertEqual(expected_text, str(post))

    def test_verbose_name_post(self):
        """Проверяем verbose_name в модели Posts."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name,
                    expected_value)

    def test_verbose_name_group(self):
        """Проверяем verbose_name в модели Group."""
        post = PostModelTest.group
        field_verboses = {
            'title': 'Название группы',
            'slug': 'Уникальный URL',
            'description': 'Описание сообщества',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name,
                    expected_value)

    def test_help_text_post(self):
        """Проверяем help_text в модели Posts."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа к которой относится пост',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text,
                    expected_value)

    def test_help_text_group(self):
        """Проверяем help_text в модели Group."""
        post = PostModelTest.group
        field_help_texts = {
            'title': 'Группа, к которой относится пост',
            'slug': 'Уникальный URL группы',
            'description': 'Описание-тема группы'
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text,
                    expected_value)


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_2 = User.objects.create_user(username='noauthor')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user_2,
            text='Текстовый коментарий к посту',
        )

    def test_models_have_correct_object_comment(self):
        """У модели Comment корректно работает __str__."""
        comment = CommentModelTest.comment
        expected_comment = self.comment.text[:15]
        self.assertEqual(expected_comment, str(comment))

    def test_verbose_name_comment(self):
        """Проверяем verbose_name в модели Comment."""
        comment = CommentModelTest.comment
        field_verboses = {
            'post': 'Текст поста',
            'author': 'Автор комментария',
            'text': 'Текст комментария',
            'created': 'Дата создания комментария',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    comment._meta.get_field(field).verbose_name,
                    expected_value)
 
    def test_help_text_comment(self):
        """Проверяем help_text в модели Comment."""
        comment = CommentModelTest.comment
        field_help_texts = {
            'post': 'Укажите пост',
            'author': 'Укажите автора',
            'text': 'Введите текст комментария',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    comment._meta.get_field(field).help_text,
                    expected_value)


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_2 = User.objects.create_user(username='noauthor')
        cls.follow = Follow.objects.create(
            user=cls.user_2,
            author=cls.user
        )

    def test_verbose_name_follow(self):
        """Проверяем verbose_name в модели Follow."""
        follow = FollowModelTest.follow
        field_verboses = {
            'user': 'Подписчик',
            'author': 'Подписан на автора',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    follow._meta.get_field(field).verbose_name,
                    expected_value)
