import unittest
from webtoolkit.socialdata import SocialData, SocialSourceResult


class TestSocialData(unittest.TestCase):
    def test_social_source_result_defaults(self):
        res = SocialSourceResult(name="test_source", ok=True)
        self.assertEqual(res.name, "test_source")
        self.assertTrue(res.ok)
        self.assertIsNone(res.error)

    def test_social_source_result_with_error(self):
        res = SocialSourceResult(name="test_source", ok=False, error="HTTP 404")
        self.assertEqual(res.name, "test_source")
        self.assertFalse(res.ok)
        self.assertEqual(res.error, "HTTP 404")

    def test_social_data_defaults(self):
        data = SocialData()
        self.assertIsNone(data.thumbs_up)
        self.assertIsNone(data.thumbs_down)
        self.assertIsNone(data.view_count)
        self.assertIsNone(data.rating)
        self.assertIsNone(data.upvote_ratio)
        self.assertIsNone(data.upvote_diff)
        self.assertIsNone(data.upvote_view_ratio)
        self.assertIsNone(data.stars)
        self.assertIsNone(data.followers_count)
        self.assertIsNone(data.errors)
        self.assertEqual(data.sources, [])

    def test_social_data_independent_sources_list(self):
        data1 = SocialData()
        data2 = SocialData()
        data1.sources.append(SocialSourceResult(name="source1", ok=True))
        self.assertEqual(len(data1.sources), 1)
        self.assertEqual(len(data2.sources), 0)

    def test_social_data_fields_population(self):
        source = SocialSourceResult(name="ytdlp", ok=True)
        data = SocialData(
            thumbs_up=100,
            thumbs_down=5,
            view_count=5000,
            rating=4.8,
            upvote_ratio=0.95,
            upvote_diff=95,
            upvote_view_ratio=0.02,
            stars=12.0,
            followers_count=1000,
            errors=["Warning: partial data"],
            sources=[source],
        )
        self.assertEqual(data.thumbs_up, 100)
        self.assertEqual(data.thumbs_down, 5)
        self.assertEqual(data.view_count, 5000)
        self.assertEqual(data.rating, 4.8)
        self.assertEqual(data.upvote_ratio, 0.95)
        self.assertEqual(data.upvote_diff, 95)
        self.assertEqual(data.upvote_view_ratio, 0.02)
        self.assertEqual(data.stars, 12.0)
        self.assertEqual(data.followers_count, 1000)
        self.assertEqual(data.errors, ["Warning: partial data"])
        self.assertEqual(data.sources, [source])

    def test_set_sources_success(self):
        data = SocialData()
        sources = [
            SocialSourceResult(name="src1", ok=True),
            SocialSourceResult(name="src2", ok=True),
        ]
        ret = data.set_sources(sources)
        self.assertIs(ret, data)
        self.assertEqual(data.sources, sources)
        self.assertIsNone(data.errors)

    def test_set_sources_with_errors(self):
        data = SocialData()
        sources = [
            SocialSourceResult(name="src1", ok=True),
            SocialSourceResult(name="src2", ok=False, error="timeout"),
        ]
        data.set_sources(sources)
        self.assertEqual(data.sources, sources)
        self.assertEqual(data.errors, ["timeout"])


if __name__ == "__main__":
    unittest.main()
