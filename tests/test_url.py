from datetime import datetime

from webtoolkit import UrlLocation, Url

from tests.fakeinternet import FakeInternetTestCase, MockRequestCounter


class UrlTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_get_response(self):
        u = Url("https://linkedin.com")
        response = u.get_response()

        self.assertTrue(response)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.text)

    def test_get_properties__html(self):
        u = Url("https://linkedin.com")
        properties = u.get_properties()

        self.assertTrue(properties)
        self.assertIn("title", properties)
        self.assertIn("description", properties)
        self.assertIn("link", properties)

    def test_get_social_properties(self):
        u = Url("https://github.com/rumca-js/Django-link-archive")
        properties = u.get_social_properties()

        self.assertTrue(properties)
        self.assertIn("stars", properties)

    def test_get_hash(self):
        u = Url("https://linkedin.com")
        response = u.get_response()

        self.assertTrue(response.get_hash())

    def test_get_body_hash(self):
        u = Url("https://linkedin.com")
        response = u.get_response()

        self.assertTrue(response.body_hash)
