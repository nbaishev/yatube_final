from django.conf import settings
from django.test import TestCase

from posts.models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.NUMBER_OF_REPETITIONS = 100
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Т' * cls.NUMBER_OF_REPETITIONS,
        )

    def test_models_have_correct_object_names(self):
        """
        В поле __str__  объектов group, post записаны
        значения groups.title и post.text[:15]
        соответственно.
        """
        self.assertEqual(self.group.title, str(self.group))
        self.assertEqual(
            self.post.text[:settings.NUMBER_OF_CHARACTERS_IN_TEXT_OF_POST],
            str(self.post)
        )

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = self.post
        field_verboses = {
            'text': 'Текст',
            'created': 'Дата создания',
            'author': 'Автор',
            'group': 'Группа',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = self.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': ('Группа, к которой будет относиться пост'),
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)
