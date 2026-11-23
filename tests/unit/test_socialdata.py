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

    def test_from_dict_none_or_empty(self):
        self.assertEqual(SocialData.from_dict(None), SocialData())
        self.assertEqual(SocialData.from_dict({}), SocialData())
        self.assertEqual(SocialData.from_dict("invalid"), SocialData())

    def test_from_dict_metrics(self):
        d = {
            "thumbs_up": 10,
            "thumbs_down": 1,
            "view_count": 100,
            "rating": 4.0,
            "stars": 5.0,
            "followers_count": 50,
        }
        res = SocialData.from_dict(d)
        self.assertEqual(res.thumbs_up, 10)
        self.assertEqual(res.thumbs_down, 1)
        self.assertEqual(res.view_count, 100)
        self.assertEqual(res.rating, 4.0)
        self.assertEqual(res.stars, 5.0)
        self.assertEqual(res.followers_count, 50)
        self.assertIsNone(res.errors)
        self.assertEqual(res.sources, [])

    def test_from_dict_with_sources_and_errors(self):
        d = {
            "view_count": 200,
            "sources": [
                {"name": "youtube", "ok": True, "error": None},
                {"name": "returndislike", "ok": False, "error": "rate limited"},
            ],
            "errors": ["rate limited"],
        }
        res = SocialData.from_dict(d)
        self.assertEqual(res.view_count, 200)
        self.assertEqual(len(res.sources), 2)
        self.assertEqual(res.sources[0].name, "youtube")
        self.assertTrue(res.sources[0].ok)
        self.assertEqual(res.sources[1].name, "returndislike")
        self.assertFalse(res.sources[1].ok)
        self.assertEqual(res.errors, ["rate limited"])

    def test_from_dict_already_social_data(self):
        orig = SocialData(stars=10.0)
        self.assertIs(SocialData.from_dict(orig), orig)

    def test_to_dict(self):
        data = SocialData(stars=5.0, view_count=100)
        d = data.to_dict()
        self.assertIsInstance(d, dict)
        self.assertEqual(d["stars"], 5.0)
        self.assertEqual(d["view_count"], 100)
        self.assertIn("sources", d)
        self.assertIn("errors", d)

    def test_to_dict_with_sources(self):
        data = SocialData(thumbs_up=10)
        data.set_sources([SocialSourceResult(name="yt", ok=True)])
        d = data.to_dict()
        self.assertEqual(d["sources"][0]["name"], "yt")
        self.assertTrue(d["sources"][0]["ok"])


if __name__ == "__main__":
    unittest.main()
