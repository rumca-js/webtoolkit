import os
from webtoolkit import ContentText

from webtoolkit.tests.fakeinternet import FakeInternetTestCase


class ContentTextTest(FakeInternetTestCase):
    def test_guess_date_for_full_date(self):
        p = ContentText(
            "test",
        )

        text = p.htmlify()
        self.assertTrue(text)
