from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.templates_names_url = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }

    def test_about_url_exists_at_desired_location(self):
        """Адреса /about/author и /about/author
        доступны всем пользователям."""
        for address in self.templates_names_url.keys():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_urls_uses_correct_template(self):
        """URL-адресу соответствует шаблон."""
        for address, template in self.templates_names_url.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)


class StaticViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.templates_namespase_name_url = {
            'about:author': 'about/author.html',
            'about:tech': 'about/tech.html',
        }

    def test_about_page_accessible_by_name(self):
        """URL, генерируемый при помощи имени namespase:name, доступен."""
        for name in self.templates_namespase_name_url.keys():
            with self.subTest(name=name):
                response = self.guest_client.get(reverse(name))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_page_uses_correct_template(self):
        """При запросе к namespase:name
        применяется правельный шаблон.
        """
        for name, template in self.templates_namespase_name_url.items():
            with self.subTest(name=name):
                response = self.guest_client.get(reverse(name))
                self.assertTemplateUsed(response, template)
