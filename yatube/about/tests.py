from http import HTTPStatus

from django.test import Client, TestCase


class AboutURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.URLS_FOR_ALL = [
            '/about/author/',
            '/about/tech/',
        ]

    def test_urls_exists_at_desired_location(self):
        """Страницы доступны пользователям."""
        for address in self.URLS_FOR_ALL:
            response = self.guest_client.get(address)
            self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
