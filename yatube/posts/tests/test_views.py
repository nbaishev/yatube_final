import shutil
import tempfile
from time import sleep

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms

from posts.forms import PostForm
from posts.models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='posts/small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post_with_group = Post.objects.create(
            author=cls.user,
            text='Пост с группой',
            image=uploaded,
            group=cls.group,
        )
        sleep(0.01)
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def post_exist(self, response, group=False):
        if 'page_obj' in response.context:
            post = response.context['page_obj'][0]
        else:
            post = response.context['post']
        self.assertEqual(
            post.author, self.post.author
        )
        if group:
            self.assertEqual(post.text, self.post_with_group.text)
            self.assertEqual(
                post.group.title, self.group.title
            )
            self.assertEqual(
                post.group.description, self.group.description
            )
            return
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.image, self.post.image)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        cache.clear()
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    args={self.group.slug}):
                        'posts/group_list.html',
            reverse('posts:profile',
                    args={self.user}):
                        'posts/profile.html',
            reverse('posts:post_detail',
                    args={self.post.pk}):
                        'posts/post_detail.html',
            reverse('posts:post_edit',
                    args={self.post.pk}):
                        'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        # sleep(20)
        response = self.authorized_client.get(reverse('posts:index'))
        self.post_exist(response)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:group_list', args={self.group.slug}))
        self.post_exist(response, True)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:profile', args={self.user}))
        self.post_exist(response)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail', args={self.post_with_group.pk}))
        self.post_exist(response, True)

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertIsInstance(response.context.get('form'), PostForm)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': f'{self.post.pk}'}))
        self.assertIsInstance(response.context.get('is_edit'), bool)
        self.assertEqual(response.context.get('is_edit'), True)
        self.assertIsInstance(response.context.get('form'), PostForm)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_index_cache(self):
        """Тестирование кеша главной страницы."""
        new_post = Post.objects.create(
            author=self.user,
            text='Пост для проверки работы кеша',
            group=self.group
        )
        response_1 = self.authorized_client.get(
            reverse('posts:index')
        )
        response_content_1 = response_1.content
        new_post.delete()
        response_2 = self.authorized_client.get(
            reverse('posts:index')
        )
        response_content_2 = response_2.content
        self.assertEqual(response_content_1, response_content_2)
        cache.clear()
        response_3 = self.authorized_client.get(
            reverse('posts:index')
        )
        response_content_3 = response_3.content
        self.assertNotEqual(response_content_2, response_content_3)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ALL_POSTS_COUNT_FOR_TEST = 13
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        paginator_objects = []
        for i in range(cls.ALL_POSTS_COUNT_FOR_TEST):
            new_post = Post(
                author=cls.user,
                text=f'Тестовый пост №{i}',
                group=cls.group,
            )
            sleep(0.01)
            paginator_objects.append(new_post)
        cls.posts = Post.objects.bulk_create(paginator_objects)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_paginator_correct_context(self):
        """Проверка работы пагинатора."""
        urls_with_paginator = [
            reverse('posts:index'),
            reverse('posts:group_list', args={self.group.slug}),
            reverse('posts:profile', args={self.user}),
        ]
        for address in urls_with_paginator:
            cache.clear()
            response_1 = self.authorized_client.get(address)
            response_2 = self.authorized_client.get(
                address + '?page=2'
            )
            post_0_on_first_page = response_1.context['page_obj'][0]
            post_0_on_second_page = response_2.context['page_obj'][0]
            self.assertEqual(
                len(response_1.context['page_obj']), settings.POSTS_PER_PAGE
            )
            self.assertEqual(
                len(response_2.context['page_obj']),
                self.ALL_POSTS_COUNT_FOR_TEST - settings.POSTS_PER_PAGE
            )
            self.assertEqual(
                post_0_on_first_page.text,
                self.posts[self.ALL_POSTS_COUNT_FOR_TEST - 1].text
            )
            self.assertEqual(
                post_0_on_second_page.text,
                self.posts[self.ALL_POSTS_COUNT_FOR_TEST - 1
                           - settings.POSTS_PER_PAGE].text
            )
