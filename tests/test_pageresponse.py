import json
from pathlib import Path

from webtoolkit.utils.dateutils import DateUtils
from webtoolkit.tests.fakeinternetcontents import (
    webpage_with_real_rss_links
)

from webtoolkit import (
    PageRequestObject,
    PageResponseObject,
    RssPage,
    HtmlPage,

    response_to_json,
    json_to_response,
    response_to_file,
    file_to_response,

    HTTP_STATUS_CODE_SERVER_ERROR,
    HTTP_STATUS_CODE_SERVER_TOO_MANY_REQUESTS,
    HTTP_STATUS_CODE_EXCEPTION,
)

from webtoolkit.tests.fakeinternet import FakeInternetTestCase, MockRequestCounter


class PageResponseObjectTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_get_content_type(self):
        headers = {"Content-Type": "text/html"}
        response = PageResponseObject(
            "https://test.com", "", status_code=200, headers=headers
        )

        # call tested function
        self.assertEqual(response.get_content_type(), "text/html")

    def test_is_valid(self):
        headers = {"Content-Type": "text/html"}
        response = PageResponseObject(
            "https://test.com", "", status_code=100, headers=headers
        )
        # call tested function
        self.assertFalse(response.is_valid())

        headers = {"Content-Type": "text/html"}
        response = PageResponseObject(
            "https://test.com", "", status_code=199, headers=headers
        )
        # call tested function
        self.assertFalse(response.is_valid())

        headers = {"Content-Type": "text/html"}

        response = PageResponseObject(
            "https://test.com", "", status_code=200, headers=headers
        )

        # call tested function - ok status is OK
        self.assertTrue(response.is_valid())

        response = PageResponseObject(
            "https://test.com", "", status_code=299, headers=headers
        )
        # call tested function - redirect status is OK
        self.assertTrue(response.is_valid())

        response = PageResponseObject(
            "https://test.com", "", status_code=300, headers=headers
        )
        # call tested function - redirect status is OK
        self.assertTrue(response.is_valid())

        response = PageResponseObject(
            "https://test.com", "", status_code=304, headers=headers
        )
        # call tested function - redirect status is OK
        self.assertTrue(response.is_valid())

        response = PageResponseObject(
            "https://test.com", "", status_code=399, headers=headers
        )
        # call tested function - redirect status is OK
        self.assertTrue(response.is_valid())

        response = PageResponseObject(
            "https://test.com", "", status_code=400, headers=headers
        )
        # call tested function
        self.assertFalse(response.is_valid())

        response = PageResponseObject(
            "https://test.com", "", status_code=401, headers=headers
        )
        # call tested function
        self.assertFalse(response.is_valid())

        response = PageResponseObject(
            "https://test.com", "", status_code=402, headers=headers
        )
        # call tested function
        self.assertFalse(response.is_valid())

        response = PageResponseObject(
            "https://test.com", "", status_code=403, headers=headers
        )
        # call tested function
        self.assertFalse(response.is_valid())

        response = PageResponseObject(
            "https://test.com", "", status_code=404, headers=headers
        )
        # call tested function
        self.assertFalse(response.is_valid())

        response = PageResponseObject(
            "https://test.com", "", status_code=405, headers=headers
        )
        # call tested function
        self.assertFalse(response.is_valid())

        response = PageResponseObject(
            "https://test.com", "", status_code=500, headers=headers
        )
        # call tested function
        self.assertFalse(response.is_valid())

        response = PageResponseObject(
            "https://test.com", "", status_code=HTTP_STATUS_CODE_SERVER_ERROR, headers=headers
        )
        # call tested function
        self.assertFalse(response.is_valid())

        response = PageResponseObject(
            "https://test.com", "", status_code=HTTP_STATUS_CODE_SERVER_TOO_MANY_REQUESTS, headers=headers
        )
        # call tested function
        self.assertFalse(response.is_valid())

    def test_is_invalid(self):
        headers = {"Content-Type": "text/html"}
        response = PageResponseObject(
            "https://test.com", "", status_code=100, headers=headers
        )
        # call tested function
        self.assertTrue(response.is_invalid())

        headers = {"Content-Type": "text/html"}
        response = PageResponseObject(
            "https://test.com", "", status_code=199, headers=headers
        )
        # call tested function
        self.assertTrue(response.is_invalid())

        headers = {"Content-Type": "text/html"}

        response = PageResponseObject(
            "https://test.com", "", status_code=200, headers=headers
        )

        # call tested function - ok status is OK
        self.assertFalse(response.is_invalid())

        response = PageResponseObject(
            "https://test.com", "", status_code=300, headers=headers
        )
        # call tested function - redirect status is OK
        self.assertFalse(response.is_invalid())

        response = PageResponseObject(
            "https://test.com", "", status_code=301, headers=headers
        )
        # call tested function - redirect status is OK
        self.assertFalse(response.is_invalid())

        response = PageResponseObject(
            "https://test.com", "", status_code=304, headers=headers
        )
        # call tested function - redirect status is OK
        self.assertFalse(response.is_invalid())

        response = PageResponseObject(
            "https://test.com", "", status_code=399, headers=headers
        )
        # call tested function - redirect status is OK
        self.assertFalse(response.is_invalid())

        response = PageResponseObject(
            "https://test.com", "", status_code=400, headers=headers
        )
        # call tested function
        self.assertTrue(response.is_invalid())

        response = PageResponseObject(
            "https://test.com", "", status_code=401, headers=headers
        )
        # call tested function
        self.assertTrue(response.is_invalid())

        response = PageResponseObject(
            "https://test.com", "", status_code=402, headers=headers
        )
        # call tested function
        self.assertTrue(response.is_invalid())

        response = PageResponseObject(
            "https://test.com", "", status_code=403, headers=headers
        )
        # call tested function
        self.assertFalse(response.is_invalid()) # sometimes 403 indicates browser problem

        response = PageResponseObject(
            "https://test.com", "", status_code=404, headers=headers
        )
        # call tested function
        self.assertTrue(response.is_invalid())

        response = PageResponseObject(
            "https://test.com", "", status_code=405, headers=headers
        )
        # call tested function
        self.assertTrue(response.is_invalid())

        response = PageResponseObject(
            "https://test.com", "", status_code=500, headers=headers
        )
        # call tested function
        self.assertTrue(response.is_invalid())

        response = PageResponseObject(
            "https://test.com", "", status_code=HTTP_STATUS_CODE_EXCEPTION, headers=headers
        )
        # call tested function
        self.assertTrue(response.is_invalid())

        response = PageResponseObject(
            "https://test.com", "", status_code=HTTP_STATUS_CODE_SERVER_ERROR, headers=headers
        )
        # call tested function
        self.assertFalse(response.is_invalid())

        response = PageResponseObject(
            "https://test.com", "", status_code=HTTP_STATUS_CODE_SERVER_TOO_MANY_REQUESTS, headers=headers
        )
        # call tested function
        self.assertFalse(response.is_invalid())

    def test_get_encoding__quotes(self):
        headers = {"Content-Type": 'text/html; charset="UTF-8"'}
        response = PageResponseObject(
            "https://test.com", "", status_code=200, headers=headers
        )

        self.assertEqual(response.get_encoding(), "UTF-8")

    def test_get_encoding__no_quotes(self):
        headers = {"Content-Type": "text/html; charset=UTF-8"}
        response = PageResponseObject(
            "https://test.com", "", status_code=200, headers=headers
        )

        self.assertEqual(response.get_encoding(), "UTF-8")

    def test_is_content__html(self):
        headers = {"Content-Type": "text/html; charset=UTF-8"}
        response = PageResponseObject(
            "https://test.com", "", status_code=200, headers=headers
        )

        self.assertTrue(response.is_content_html())
        self.assertFalse(response.is_content_rss())

    def test_is_content__rss(self):
        headers = {"Content-Type": "text/rss; charset=UTF-8"}
        response = PageResponseObject(
            "https://test.com", "", status_code=200, headers=headers
        )

        self.assertTrue(response.is_content_rss())
        self.assertFalse(response.is_content_html())

    def test_get_hash__text(self):
        headers = {"Content-Type": "text/rss; charset=UTF-8"}
        response = PageResponseObject(
            "https://test.com", "", status_code=200, text="test", headers=headers
        )

        self.assertTrue(response.get_hash())

    def test_get_hash__binary(self):
        headers = {"Content-Type": "text/rss; charset=UTF-8"}
        response = PageResponseObject(
            "https://test.com", status_code=200, binary=b"test", headers=headers
        )

        self.assertTrue(response.get_hash())

    def test_get_body_hash__text(self):
        headers = {"Content-Type": "text/html; charset=UTF-8"}
        response = PageResponseObject(
            "https://test.com", "", status_code=200, text=webpage_with_real_rss_links, headers=headers
        )

        self.assertTrue(response.get_hash())
        self.assertTrue(response.get_body_hash())
        self.assertNotEqual(response.get_hash(), response.get_body_hash())

    def test_get_last_modified(self):
        date_str = DateUtils.get_datetime_now_iso()

        headers = {"Content-Type": "text/rss; charset=UTF-8",
                   "Last-Modified" : date_str}

        response = PageResponseObject(
            "https://test.com", status_code=200, binary=b"test", headers=headers
        )

        self.assertTrue(response.get_last_modified())

    def test_is_captcha_protected__false(self):
        date_str = DateUtils.get_datetime_now_iso()

        headers = {"Content-Type": "text/rss; charset=UTF-8",
                   "Last-Modified" : date_str}

        response = PageResponseObject(
            "https://test.com", status_code=200, text="<html></html>", headers=headers
        )

        self.assertFalse(response.is_captcha_protected())

    def test_is_captcha_protected__true(self):
        date_str = DateUtils.get_datetime_now_iso()

        headers = {"Content-Type": "text/rss; charset=UTF-8",
                   "Last-Modified" : date_str}

        response = PageResponseObject(
            "https://test.com", status_code=200, text="<html>https://recaptcha/api.js</html>", headers=headers
        )

        self.assertTrue(response.is_captcha_protected())

    def test_get_page__rsspage(self):
        date_str = DateUtils.get_datetime_now_iso()

        headers = {"Content-Type": "text/rss; charset=UTF-8",
                   "Last-Modified" : date_str}

        response = PageResponseObject(
            "https://test.com", status_code=200, text="<rss></rss>", headers=headers
        )

        self.assertEqual(type(response.get_page()), RssPage)

    def test_get_page__htmlpage(self):
        date_str = DateUtils.get_datetime_now_iso()

        headers = {"Content-Type": "text/html; charset=UTF-8",
                   "Last-Modified" : date_str}

        response = PageResponseObject(
            "https://test.com", status_code=200, text="<html><body></body></html>", headers=headers
        )

        self.assertEqual(type(response.get_page()), HtmlPage)


class PageResponseToJsonTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test_response_to_json__403_no_text(self):
        headers = {"Content-Type": "text/rss; charset=UTF-8"}
        response = PageResponseObject(
            "https://test.com", "", status_code=403, headers=headers
        )

        # call tested function
        json_map = response_to_json(response)

        self.assertTrue(json_map)
        self.assertIn("is_valid", json_map)
        self.assertIn("status_code", json_map)
        self.assertIn("status_code_str", json_map)
        self.assertIn("crawl_time_s", json_map)
        self.assertIn("Content-Type", json_map)
        self.assertIn("Recognized-Content-Type", json_map)
        self.assertIn("Content-Length", json_map)
        self.assertIn("Charset", json_map)
        self.assertIn("hash", json_map)
        self.assertIn("body_hash", json_map)
        self.assertNotIn("streams", json_map)

        self.assertEqual(json_map["is_valid"], False)
        self.assertEqual(json_map["status_code"], 403)
        self.assertEqual(json_map["Content-Type"], "text/rss; charset=UTF-8")
        self.assertEqual(json_map["Recognized-Content-Type"], "text/rss")
        self.assertEqual(json_map["Charset"], "UTF-8")
        self.assertEqual(json_map["hash"], None)
        self.assertEqual(json_map["body_hash"], None)

    def test_response_to_json__404_no_text(self):
        headers = {"Content-Type": "text/rss; charset=UTF-8"}
        response = PageResponseObject(
            "https://test.com", "", status_code=404, headers=headers
        )

        # call tested function
        json_map = response_to_json(response)

        self.assertTrue(json_map)
        self.assertIn("is_valid", json_map)
        self.assertIn("status_code", json_map)
        self.assertIn("status_code_str", json_map)
        self.assertIn("crawl_time_s", json_map)
        self.assertIn("Content-Type", json_map)
        self.assertIn("Recognized-Content-Type", json_map)
        self.assertIn("Content-Length", json_map)
        self.assertIn("Charset", json_map)
        self.assertIn("hash", json_map)
        self.assertIn("body_hash", json_map)
        self.assertNotIn("streams", json_map)

        self.assertEqual(json_map["is_valid"], False)
        self.assertEqual(json_map["status_code"], 404)
        self.assertEqual(json_map["Content-Type"], "text/rss; charset=UTF-8")
        self.assertEqual(json_map["Recognized-Content-Type"], "text/rss")
        self.assertEqual(json_map["Charset"], "UTF-8")
        self.assertEqual(json_map["hash"], None)
        self.assertEqual(json_map["body_hash"], None)

    def test_response_to_json__valid_text_no_streams(self):
        headers = {"Content-Type": "text/rss; charset=UTF-8"}
        response = PageResponseObject(
            "https://test.com", "", status_code=200, text="test", headers=headers
        )

        # call tested function
        json_map = response_to_json(response)

        self.assertTrue(json_map)
        self.assertIn("is_valid", json_map)
        self.assertIn("status_code", json_map)
        self.assertIn("status_code_str", json_map)
        self.assertIn("crawl_time_s", json_map)
        self.assertIn("Content-Type", json_map)
        self.assertIn("Recognized-Content-Type", json_map)
        self.assertIn("Content-Length", json_map)
        self.assertIn("Charset", json_map)
        self.assertIn("hash", json_map)
        self.assertIn("body_hash", json_map)
        self.assertIn("text", json_map)
        self.assertNotIn("streams", json_map)

        self.assertEqual(json_map["is_valid"], True)
        self.assertEqual(json_map["status_code"], 200)
        self.assertEqual(json_map["Content-Type"], "text/rss; charset=UTF-8")
        self.assertEqual(json_map["Recognized-Content-Type"], "text/rss")
        self.assertEqual(json_map["Charset"], "UTF-8")
        self.assertNotEqual(json_map["hash"], None)
        self.assertNotEqual(json_map["body_hash"], None)

    def test_response_to_json__valid_binary_no_streams(self):
        headers = {"Content-Type": "text/rss; charset=UTF-8"}
        response = PageResponseObject(
            "https://test.com", status_code=200, binary=b"01010", headers=headers
        )

        # call tested function
        json_map = response_to_json(response)

        self.assertTrue(json_map)
        self.assertIn("is_valid", json_map)
        self.assertIn("status_code", json_map)
        self.assertIn("status_code_str", json_map)
        self.assertIn("crawl_time_s", json_map)
        self.assertIn("Content-Type", json_map)
        self.assertIn("Recognized-Content-Type", json_map)
        self.assertIn("Content-Length", json_map)
        self.assertIn("Charset", json_map)
        self.assertIn("hash", json_map)
        self.assertIn("body_hash", json_map)
        self.assertIn("text", json_map)
        self.assertNotIn("streams", json_map)

        self.assertEqual(json_map["is_valid"], True)
        self.assertEqual(json_map["status_code"], 200)
        self.assertEqual(json_map["Content-Type"], "text/rss; charset=UTF-8")
        self.assertEqual(json_map["Recognized-Content-Type"], "text/rss")
        self.assertEqual(json_map["Charset"], "UTF-8")
        self.assertNotEqual(json_map["hash"], None)
        self.assertNotEqual(json_map["body_hash"], None)

    def test_response_to_json__valid_text_streams(self):
        headers = {"Content-Type": "text/rss; charset=UTF-8"}
        response = PageResponseObject(
            "https://test.com", "", status_code=200, text="test", headers=headers
        )

        # call tested function
        json_map = response_to_json(response, with_streams=True)

        self.assertTrue(json_map)
        self.assertIn("is_valid", json_map)
        self.assertIn("status_code", json_map)
        self.assertIn("status_code_str", json_map)
        self.assertIn("crawl_time_s", json_map)
        self.assertIn("Content-Type", json_map)
        self.assertIn("Recognized-Content-Type", json_map)
        self.assertIn("Content-Length", json_map)
        self.assertIn("Charset", json_map)
        self.assertIn("hash", json_map)
        self.assertIn("body_hash", json_map)
        self.assertIn("text", json_map)
        self.assertIn("streams", json_map)

        self.assertEqual(json_map["is_valid"], True)
        self.assertEqual(json_map["status_code"], 200)
        self.assertEqual(json_map["Content-Type"], "text/rss; charset=UTF-8")
        self.assertEqual(json_map["Recognized-Content-Type"], "text/rss")
        self.assertEqual(json_map["Charset"], "UTF-8")
        self.assertNotEqual(json_map["hash"], None)
        self.assertNotEqual(json_map["body_hash"], None)

    def test_response_to_json__with_request(self):
        test_link = "https://test.com"

        headers = {"Content-Type": "text/rss; charset=UTF-8"}
        response = PageResponseObject(
            url=test_link, status_code=200, text="test", headers=headers,
        )
        request = PageRequestObject(url=test_link)
        response.set_request(request)

        # call tested function
        json_map = response_to_json(response, with_streams=True)

        self.assertTrue(json_map)
        self.assertIn("is_valid", json_map)
        self.assertIn("request", json_map)

        self.assertEqual(json_map["is_valid"], True)
        self.assertEqual(json_map["request"]["url"], test_link)

        # check if is serializable

        string = json.dumps(json_map)
        self.assertTrue(string)


class JsonToPageResponseTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

    def test__valid(self):
        json_data = {
            "status_code" : 200,
        }

        response = json_to_response(json_data)
        self.assertTrue(response.is_valid())

    def test__not_valid(self):
        json_data = {
            "status_code" : 404,
        }

        response = json_to_response(json_data)
        self.assertFalse(response.is_valid())

    def test__url(self):
        json_data = {
            "url" : "https://test.com",
        }

        response = json_to_response(json_data)
        self.assertEqual(response.url, "https://test.com")

    def test__request_url(self):
        json_data = {
            "request_url" : "https://test.com",
        }

        response = json_to_response(json_data)
        self.assertEqual(response.request_url, "https://test.com")

    def test__text(self):
        json_data = {
            "text" : "<html></html>",
        }

        response = json_to_response(json_data)
        self.assertEqual(response.text, "<html></html>")

    def test__headers(self):
        json_data = {
            "headers" : {
                "Content-Type" : "test/content/type",
            }
        }

        response = json_to_response(json_data)
        self.assertEqual(response.get_content_type(), "test/content/type")

    def test__response_to_file(self):
        path = Path("test_response.txt")

        json_data = {
            "status_code" : 200,
            "url" : "https://test.com",
            "request_url" : "https://test.com",
            "text" : "<html></html>",
            "headers" : {
                "Content-Type" : "test/content/type",
            }
        }

        response = json_to_response(json_data)

        if path.exists():
            path.unlink()

        self.assertFalse(path.exists())

        # call tested function
        response_to_file(response, "test_response.txt")

        self.assertTrue(path.exists())

        path.unlink()

    def test__response_with_request(self):
        json_data = {
            "url" : "https://test.com",
            "text" : "<html></html>",
            "request" : {
                "url" : "https://page-request.com",
                "crawler_name" : "PageRequestCrawler",
            }
        }

        response = json_to_response(json_data)
        self.assertEqual(response.text, "<html></html>")

        self.assertTrue(response.request)
        self.assertTrue(response.request.url, "https://page-request.com")
        self.assertTrue(response.request.crawler_name, "PageRequestCrawler")
