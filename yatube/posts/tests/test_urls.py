from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase

from posts.models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.author = User.objects.create_user(username='Author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
        )
        cls.URLS_FOR_ALL = [
            '/', f'/posts/{cls.post.pk}/',
            f'/profile/{cls.user}/', f'/group/{cls.group.slug}/',
        ]
        cls.URLS_FOR_AUTHOR = [
            f'/posts/{cls.post.pk}/edit/',
        ]
        cls.URLS_FOR_AUTHORIZED = [
            '/create/',
        ]

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(self.author)
        cache.clear()

    def test_urls_exists_at_desired_location(self):
        """Страницы доступны пользователям."""
        for address in self.URLS_FOR_ALL:
            response = self.guest_client.get(address)
            self.assertEqual(response.status_code, HTTPStatus.OK.value)
        for address in self.URLS_FOR_AUTHORIZED:
            response = self.authorized_client.get(address)
            self.assertEqual(response.status_code, HTTPStatus.OK.value)
        for address in self.URLS_FOR_AUTHOR:
            response = self.author_client.get(address)
            self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_unexisting_url(self):
        """Ссылка на несуществующую страницу возвращает ошибку 404."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND.value)

    def test_urls_redirect_anonymous_on_auth_login(self):
        """Страницы по адресам /create/, /posts/id/edit/
        перенаправит анонимного пользователя на страницу
        логина.
        """
        for address in self.URLS_FOR_AUTHORIZED:
            response = self.guest_client.get(address, follow=True)
            self.assertRedirects(response, '/auth/login/?next=/create/')
        for address in self.URLS_FOR_AUTHOR:
            response = self.guest_client.get(address, follow=True)
            self.assertRedirects(
                response,
                f'/auth/login/?next=/posts/{self.post.pk}/edit/'
            )

    def test_urls_redirect_authorized_not_author_on_post_detail(self):
        """Страницы по адресу /posts/id/edit/
        перенаправит авторизованного пользователя
        не являющегося автором на страницу
        поста.
        """
        for address in self.URLS_FOR_AUTHOR:
            response = self.authorized_client.get(address, follow=True)
            self.assertRedirects(response, f'/posts/{self.post.pk}/')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
            '/profile/Author/': 'posts/profile.html',
            '/group/test-slug/': 'posts/group_list.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertTemplateUsed(response, template)
