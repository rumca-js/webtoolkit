from webtoolkit import ContentInterface, UrlInterface
from webtoolkit.response import PageResponseObject
from webtoolkit.tests.fakeinternet import FakeInternetTestCase


class UrlInterfaceTest(FakeInternetTestCase):
    def test_url_interface_inheritance(self):
        self.assertTrue(issubclass(UrlInterface, ContentInterface))

    def test_default_methods(self):
        class DummyUrl(UrlInterface):
            pass

        dummy = DummyUrl(url="https://example.com", contents="test")
        self.assertEqual(dummy.get_url(), "https://example.com")
        self.assertEqual(dummy.get_contents(), "test")
        self.assertIsNone(dummy.get_response())
        self.assertIsNone(dummy.get_general_response())
