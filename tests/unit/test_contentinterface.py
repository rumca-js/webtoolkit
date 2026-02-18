import os
from webtoolkit import ContentInterface
from webtoolkit.utils.memorychecker import MemoryChecker

from webtoolkit.tests.fakeinternet import FakeInternetTestCase


wall_street_journal_date_full_date = """
<!DOCTYPE html>
<html lang="en-US">
	<head>
		<meta charSet="utf-8"/>
        "2024-01-11 02:00"
}</script>
</html>
"""

wall_street_journal_date_human_date = """
<!DOCTYPE html>
<html lang="en-US">
	<head>
		<meta charSet="utf-8"/>
        "Jan 10 2024 02:00","article_publish_orig":"2024-01-17 02:00","article_type":"Middle East News","article_video_count":1,"article_word_count":1798,"cms_name":"WSJ Authoring Production","is_column":false,"listing_impression_id":"","page_access":"paid","page_section":"World","page_sponsored_name":"","page_subsection":"Middle East","page_title":"Israel’s War in Gaza Enters Its Most Perilous Phase Yet - WSJ","previous_section":"","stack_name":"Olympia","taxonomy_applies":true,"taxonomy_array":[{"codeType":"thing","score":"0.75","value":"world|europe||"},{"codeType":"thing","score":"0.24","value":"world|middle-east||"}],"taxonomy_primary":"world|middle-east","taxonomy_primary_score":"1","taxonomy_primary_source":"manual","vix":"","user_exp":"","user_ref":"","user_tags":"","user_type":""}</script>
}</script>
</html>
"""

wall_street_journal_date_human_date_dot = """
<!DOCTYPE html>
<html lang="en-US">
	<head>
		<meta charSet="utf-8"/>
        "Jan. 09 2024 02:00","article_publish_orig":"2024-01-17 02:00","article_type":"Middle East News","article_video_count":1,"article_word_count":1798,"cms_name":"WSJ Authoring Production","is_column":false,"listing_impression_id":"","page_access":"paid","page_section":"World","page_sponsored_name":"","page_subsection":"Middle East","page_title":"Israel’s War in Gaza Enters Its Most Perilous Phase Yet - WSJ","previous_section":"","stack_name":"Olympia","taxonomy_applies":true,"taxonomy_array":[{"codeType":"thing","score":"0.75","value":"world|europe||"},{"codeType":"thing","score":"0.24","value":"world|middle-east||"}],"taxonomy_primary":"world|middle-east","taxonomy_primary_score":"1","taxonomy_primary_source":"manual","vix":"","user_exp":"","user_ref":"","user_tags":"","user_type":""}</script>
}</script>
</html>
"""

wall_street_journal_date_human_date_one_digit = """
<!DOCTYPE html>
<html lang="en-US">
	<head>
		<meta charSet="utf-8"/>
        "Jan. 9 2024 02:00","article_publish_orig":"2024-01-17 02:00","article_type":"Middle East News","article_video_count":1,"article_word_count":1798,"cms_name":"WSJ Authoring Production","is_column":false,"listing_impression_id":"","page_access":"paid","page_section":"World","page_sponsored_name":"","page_subsection":"Middle East","page_title":"Israel’s War in Gaza Enters Its Most Perilous Phase Yet - WSJ","previous_section":"","stack_name":"Olympia","taxonomy_applies":true,"taxonomy_array":[{"codeType":"thing","score":"0.75","value":"world|europe||"},{"codeType":"thing","score":"0.24","value":"world|middle-east||"}],"taxonomy_primary":"world|middle-east","taxonomy_primary_score":"1","taxonomy_primary_source":"manual","vix":"","user_exp":"","user_ref":"","user_tags":"","user_type":""}</script>
    </head>
</html>
"""

wall_street_journal_date_human_date_ue_format = """
<!DOCTYPE html>
<html lang="en-US">
	<head>
		<meta charSet="utf-8"/>
        "09 jan. 2024 02:00"
    </head>
</html>
"""


class ContentInterfacePageTest(FakeInternetTestCase):
    def setUp(self):
        self.ignore_memory = False
        self.memory_checker = MemoryChecker()
        memory_increase = self.memory_checker.get_memory_increase()
        #print(f"Memory increase {memory_increase} setup")

    def tearDown(self):
        if not self.ignore_memory:
            memory_increase = self.memory_checker.get_memory_increase()
            self.assertEqual(memory_increase, 0)
            print(f"Memory increase {memory_increase}")

    def test_guess_date_for_full_date(self):
        # TODO why?
        self.ignore_memory = True

        p = ContentInterface(
            "https://linkedin.com/test",
            wall_street_journal_date_full_date,
        )

        date = p.guess_date()
        self.assertTrue(date)
        self.assertEqual(date.isoformat(), "2024-01-11T00:00:00+00:00")

    def test_guess_date_for_human_date(self):
        p = ContentInterface(
            "https://linkedin.com/test",
            wall_street_journal_date_human_date,
        )

        date = p.guess_date()
        self.assertTrue(date)
        self.assertEqual(date.isoformat(), "2024-01-10T00:00:00+00:00")

    def test_guess_date_for_human_date_dot(self):
        p = ContentInterface(
            "https://linkedin.com/test",
            wall_street_journal_date_human_date_dot,
        )

        date = p.guess_date()
        self.assertTrue(date)
        self.assertEqual(date.isoformat(), "2024-01-09T00:00:00+00:00")

    def test_guess_date_for_human_date_one_digit(self):
        p = ContentInterface(
            "https://linkedin.com/test",
            wall_street_journal_date_human_date_one_digit,
        )

        date = p.guess_date()
        self.assertTrue(date)
        self.assertEqual(date.isoformat(), "2024-01-09T00:00:00+00:00")

    def test_guess_date_for_human_date_ue_format(self):
        p = ContentInterface(
            "https://linkedin.com/test",
            wall_street_journal_date_human_date_ue_format,
        )

        date = p.guess_date()
        self.assertTrue(date)
        self.assertEqual(date.isoformat(), "2024-01-09T00:00:00+00:00")

    def test_get_link_rating__normal(self):
        p = ContentInterface(
            "https://linkedin.com/test",
            wall_street_journal_date_human_date_dot,
        )

        rating = p.get_link_rating()
        self.assertTrue(rating)

    def test_get_link_rating__onion(self):
        p = ContentInterface(
            "https://testsomethingsomethig.onion",
            wall_street_journal_date_human_date_dot,
        )

        rating = p.get_link_rating()
        self.assertTrue(rating)
