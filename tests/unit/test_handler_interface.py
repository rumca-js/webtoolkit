import unittest
from webtoolkit.contentinterface import ContentInterface
from webtoolkit.handlers.handlerinterface import HandlerInterface
from webtoolkit.handlers.handlerhttppage import HttpPageHandler
from webtoolkit.socialdata import SocialData


class TestHandlerInterfaceSocialData(unittest.TestCase):
    def test_content_interface_get_social_data_raises(self):
        ci = ContentInterface(url="https://example.com", contents="test")
        with self.assertRaises(NotImplementedError):
            ci.get_social_data()

    def test_handler_interface_get_social_data_default(self):
        hi = HandlerInterface(url="https://example.com")
        social = hi.get_social_data()
        self.assertIsInstance(social, SocialData)
        self.assertIsNone(social.thumbs_up)
        self.assertIsNone(social.thumbs_down)
        self.assertIsNone(social.view_count)
        self.assertIsNone(social.rating)
        self.assertIsNone(social.upvote_ratio)
        self.assertIsNone(social.upvote_diff)
        self.assertIsNone(social.upvote_view_ratio)
        self.assertIsNone(social.stars)
        self.assertIsNone(social.followers_count)
        self.assertIsNone(social.errors)
        self.assertEqual(social.sources, [])

    def test_handler_interface_get_social_data_with_getters(self):
        class CustomHandler(HandlerInterface):
            def get_thumbs_up(self):
                return 42

            def get_view_count(self):
                return 1000

            def get_user_stars(self):
                return 5.0

        h = CustomHandler(url="https://example.com")
        social = h.get_social_data()
        self.assertIsInstance(social, SocialData)
        self.assertEqual(social.thumbs_up, 42)
        self.assertEqual(social.view_count, 1000)
        self.assertEqual(social.stars, 5.0)
        self.assertIsNone(social.thumbs_down)

    def test_handlerinterface_close_nulls_state(self):
        hi = HandlerInterface(url="https://example.com")
        hi.response = object()
        hi.request = object()
        hi.streams = {"Default": object()}
        hi.close()
        self.assertIsNone(hi.response)
        self.assertIsNone(hi.request)
        self.assertEqual(hi.streams, {})

    def test_httphandler_close_nulls_p(self):
        h = HttpPageHandler(url="https://example.com")
        # simulate a fetched page object
        h.p = object()
        h.response = object()
        h.close()
        self.assertIsNone(h.p)
        self.assertIsNone(h.response)

    def test_httphandler_close_before_fetch_is_safe(self):
        h = HttpPageHandler(url="https://example.com")
        h.close()  # p and response are already None — must not raise
        self.assertIsNone(h.p)
        self.assertIsNone(h.response)


if __name__ == "__main__":
    unittest.main()
