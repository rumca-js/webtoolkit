import unittest
from webtoolkit.contentinterface import ContentInterface
from webtoolkit.handlers.handlerinterface import HandlerInterface
from webtoolkit.handlers.handlerhttppage import HttpPageHandler
from webtoolkit.socialdata import SocialData
from webtoolkit.tests.mocks import MockUrl


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
        hi.request = object()
        hi.streams = {"Default": object()}
        hi.close()
        self.assertFalse(hasattr(hi, "response"))
        self.assertIsNone(hi.request)
        self.assertEqual(hi.streams, {})

    def test_httphandler_close_nulls_p(self):
        h = HttpPageHandler(url="https://example.com")
        # simulate a fetched page object
        h.p = object()
        h.close()
        self.assertIsNone(h.p)
        self.assertFalse(hasattr(h, "response"))

    def test_httphandler_close_before_fetch_is_safe(self):
        h = HttpPageHandler(url="https://example.com")
        h.close()  # p is already None — must not raise
        self.assertIsNone(h.p)
        self.assertFalse(hasattr(h, "response"))

    def test_get_response_uses_streams(self):
        hi = HandlerInterface(url="https://example.com")
        mock_resp = object()
        hi.streams["https://example.com"] = mock_resp
        resp = hi.get_response()
        self.assertIs(resp, mock_resp)
        self.assertFalse(hasattr(hi, "response"))

    def test_get_responses_returns_all_streams(self):
        hi = HandlerInterface(url="https://example.com")
        resp1 = object()
        resp2 = object()
        hi.streams["https://example.com"] = resp1
        hi.streams["https://example.com/api"] = resp2
        responses = hi.get_responses()
        self.assertEqual(len(responses), 2)
        self.assertIn(resp1, responses)
        self.assertIn(resp2, responses)

    def test_get_streams_contains_all_fetched_urls(self):
        hi = HandlerInterface(url="https://example.com")
        hi.streams["https://example.com"] = object()
        hi.streams["https://example.com/aux"] = object()
        streams = hi.get_streams()
        self.assertIn("https://example.com", streams)
        self.assertIn("https://example.com/aux", streams)

    def test_get_response_pure_read_no_mutation(self):
        hi = HandlerInterface(url="https://example.com")
        self.assertIsNone(hi.get_response())
        self.assertEqual(hi.streams, {})

    def test_get_general_response_empty_streams_returns_none(self):
        hi = HandlerInterface(url="https://example.com")
        self.assertIsNone(hi.get_general_response())

    def test_get_general_response_no_url_returns_none(self):
        hi = HandlerInterface(url=None)
        self.assertIsNone(hi.get_general_response())

    def test_get_general_response_all_valid_streams(self):
        from webtoolkit.response import PageResponseObject
        hi = HandlerInterface(url="https://example.com")
        resp_primary = PageResponseObject(url="https://example.com", status_code=200)
        resp_aux = PageResponseObject(url="https://example.com/aux", status_code=200)
        hi.streams["https://example.com"] = resp_primary
        hi.streams["https://example.com/aux"] = resp_aux
        gen_resp = hi.get_general_response()
        self.assertIs(gen_resp, resp_primary)
        self.assertEqual(gen_resp.status_code, 200)

    def test_get_general_response_invalid_stream_returns_zero(self):
        from webtoolkit.response import PageResponseObject
        hi = HandlerInterface(url="https://example.com")
        resp_primary = PageResponseObject(url="https://example.com", status_code=200)
        resp_aux = PageResponseObject(url="https://example.com/aux", status_code=404)
        hi.streams["https://example.com"] = resp_primary
        hi.streams["https://example.com/aux"] = resp_aux
        gen_resp = hi.get_general_response()
        self.assertIsNotNone(gen_resp)
        self.assertEqual(gen_resp.status_code, 0)
        self.assertEqual(gen_resp.url, "https://example.com")

    def test_get_general_response_status_code_zero_returns_zero(self):
        from webtoolkit.response import PageResponseObject
        hi = HandlerInterface(url="https://example.com")
        resp_primary = PageResponseObject(url="https://example.com", status_code=200)
        resp_aux = PageResponseObject(url="https://example.com/aux", status_code=0)
        hi.streams["https://example.com"] = resp_primary
        hi.streams["https://example.com/aux"] = resp_aux
        gen_resp = hi.get_general_response()
        self.assertIsNotNone(gen_resp)
        self.assertEqual(gen_resp.status_code, 0)


if __name__ == "__main__":
    unittest.main()
