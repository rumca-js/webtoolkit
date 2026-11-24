from webtoolkit import (
    RemoteServer,
)
from webtoolkit.utils.memorychecker import MemoryChecker

from webtoolkit.tests.fakeinternet import FakeInternetTestCase, MockRequestCounter

response_1 = {
          "Charset": "UTF-8",
          "Content-Length": 234991,
          "Content-Type": "text/html; charset=UTF-8",
          "Last-Modified": None,
          "Recognized-Content-Type": "text/html",
          "body_hash": "rgra43mMEmI5o2C9xYksWQ==",
          "crawl_time_s": 0.5448663234710693,
          "hash": "xVjumWuMdvCM4qRgygTUgA==",
          "headers": {
            "Accept-CH": "Sec-CH-Prefers-Color-Scheme",
            "Accept-Ranges": "none",
            "Alt-Svc": "h3=\":443\"; ma=2592000,h3-29=\":443\"; ma=2592000",
            "Cache-Control": "private, max-age=0",
            "Charset": "UTF-8",
            "Content-Length": None,
            "Content-Security-Policy-Report-Only": "object-src 'none';base-uri 'self';script-src 'nonce-RPtEuh-BasZcxVUbKmwNEA' 'strict-dynamic' 'report-sample' 'unsafe-eval' 'unsafe-inline' https: http:;report-uri https://csp.withgoogle.com/csp/gws/other-hp",
            "Content-Type": "text/html; charset=UTF-8",
            "Cross-Origin-Opener-Policy": "same-origin-allow-popups; report-to=\"gws\"",
            "Date": "Mon, 06 Oct 2025 06:49:41 GMT",
            "Expires": "-1",
            "Last-Modified": None,
            "P3P": "CP=\"This is not a P3P policy! See g.co/p3phelp for more info.\"",
            "Report-To": "{\"group\":\"gws\",\"max_age\":2592000,\"endpoints\":[{\"url\":\"https://csp.withgoogle.com/csp/report-to/gws/other\"}]}",
            "Server": "gws",
            "Set-Cookie": "AEC=AaJma5uTUO-h2zMWtpgVm8GSzmLj2vaBmtrc3nQYKG5o_SQdpY8H3gvSRck; expires=Sat, 04-Apr-2026 06:49:41 GMT; path=/; domain=.google.com; Secure; HttpOnly; SameSite=lax, __Secure-ENID=28.SE=QosmBx41caEH2gtolSMWk__fpUTlzAmiQccpRYkUJ-u2gT26DBxpPXFEY90sZd-p4jmPP88Yrf8EVkuDp7tcpfRvPU7c5WYcNBO7uhc3oyP1GcYuDVehfBRf30uWOyXYuqODMwJazwxnfx-TJHbSovvxt_cp44msrGViWeipWKEZvzzGzUIbskZPjfAyg5JiOBy2MaNnDwjvgW0cnJazn-I5y6xbSKIsCr6dZkxeo5DuSaAh-iGlz-MR1aOUWJ-uIA; expires=Thu, 05-Nov-2026 23:07:59 GMT; path=/; domain=.google.com; Secure; HttpOnly; SameSite=lax",
            "Strict-Transport-Security": "max-age=31536000",
            "Transfer-Encoding": "chunked",
            "Vary": "Accept-Encoding",
            "X-Frame-Options": "SAMEORIGIN",
            "X-XSS-Protection": "0"
        },
        "is_allowed": True,
        "is_invalid": False,
        "is_valid": True,
        "request_url": "https://google.com",
        "status_code": 200,
        "status_code_str": "HTTP_STATUS_OK(200)",
        "url": "https://www.google.com/",
        "text" : "<html></html",
}

response_2 = {
          "Charset": "UTF-8",
          "Content-Length": 234992,
          "Content-Type": "text/html; charset=UTF-8",
          "Last-Modified": None,
          "Recognized-Content-Type": "text/html",
          "body_hash": "Xgra43mMEmI5o2C9xYksWQ==",
          "crawl_time_s": 0.5448663234710693,
          "hash": "YVjumWuMdvCM4qRgygTUgA==",
          "headers": {
            "Accept-CH": "Sec-CH-Prefers-Color-Scheme",
            "Accept-Ranges": "none",
            "Alt-Svc": "h3=\":443\"; ma=2592000,h3-29=\":443\"; ma=2592000",
            "Cache-Control": "private, max-age=0",
            "Charset": "UTF-8",
            "Content-Length": None,
            "Content-Security-Policy-Report-Only": "object-src 'none';base-uri 'self';script-src 'nonce-RPtEuh-BasZcxVUbKmwNEA' 'strict-dynamic' 'report-sample' 'unsafe-eval' 'unsafe-inline' https: http:;report-uri https://csp.withgoogle.com/csp/gws/other-hp",
            "Content-Type": "text/html; charset=UTF-8",
            "Cross-Origin-Opener-Policy": "same-origin-allow-popups; report-to=\"gws\"",
            "Date": "Mon, 06 Oct 2025 06:49:41 GMT",
            "Expires": "-1",
            "Last-Modified": None,
            "P3P": "CP=\"This is not a P3P policy! See g.co/p3phelp for more info.\"",
            "Report-To": "{\"group\":\"gws\",\"max_age\":2592000,\"endpoints\":[{\"url\":\"https://csp.withgoogle.com/csp/report-to/gws/other\"}]}",
            "Server": "gws",
            "Set-Cookie": "AEC=AaJma5uTUO-h2zMWtpgVm8GSzmLj2vaBmtrc3nQYKG5o_SQdpY8H3gvSRck; expires=Sat, 04-Apr-2026 06:49:41 GMT; path=/; domain=.google.com; Secure; HttpOnly; SameSite=lax, __Secure-ENID=28.SE=QosmBx41caEH2gtolSMWk__fpUTlzAmiQccpRYkUJ-u2gT26DBxpPXFEY90sZd-p4jmPP88Yrf8EVkuDp7tcpfRvPU7c5WYcNBO7uhc3oyP1GcYuDVehfBRf30uWOyXYuqODMwJazwxnfx-TJHbSovvxt_cp44msrGViWeipWKEZvzzGzUIbskZPjfAyg5JiOBy2MaNnDwjvgW0cnJazn-I5y6xbSKIsCr6dZkxeo5DuSaAh-iGlz-MR1aOUWJ-uIA; expires=Thu, 05-Nov-2026 23:07:59 GMT; path=/; domain=.google.com; Secure; HttpOnly; SameSite=lax",
            "Strict-Transport-Security": "max-age=31536000",
            "Transfer-Encoding": "chunked",
            "Vary": "Accept-Encoding",
            "X-Frame-Options": "SAMEORIGIN",
            "X-XSS-Protection": "0"  
        },
        "is_allowed": True,
        "is_invalid": False,
        "is_valid": True,
        "request_url": "https://youtube.com",
        "status_code": 201,
        "status_code_str": "HTTP_STATUS_OK(201)",
        "url": "https://www.youtube.com/",
        "text" : "<html></html",
}


all_properties = [
  {
    "data": {
      "album": None,
      "author": None,
      "date_published": None,
      "description": None,
      "favicon": "https://www.gstatic.com/images/branding/searchlogo/ico/favicon.ico",
      "language": "pl",
      "link": "https://google.com",
      "link_archives": [
        "https://web.archive.org/web/*/https://google.com",
        "https://archive.ph/google.com"
      ],
      "link_canonical": "https://google.com",
      "link_request": "https://google.com",
      "meta description": None,
      "meta keywords": None,
      "meta title": None,
      "og:description": None,
      "og:image": None,
      "og:site_name": None,
      "og:title": None,
      "page_rating": 100,
      "schema:thumbnailUrl": None,
      "tags": None,
      "thumbnail": "https://google.com/images/branding/googleg/1x/googleg_standard_color_128dp.png",
      "title": "Google"
    },
    "name": "Properties"
  },
  {
    "data": {
        "Contents" : "xx",
    },
    "name": "Text"
  },
  {
    "data": {
      "crawler": "RequestsCrawler",
      "enabled": True,
      "headers": None,
      "name": "RequestsCrawler",
      "settings": {
        "accept_content_types": "all",
        "bytes_limit": 5000000,
        "full": None,
        "headers": False,
        "ping": False,
        "remote_server": "http://127.0.0.1:3000",
        "respect_robots_txt": True,
        "ssl_verify": True,
        "timeout_s": 30
      }
    },
    "name": "Settings"
  },
  {
    "data": {
        "https://google.com" : response_1
    },
    "name": "Streams"
  },
  {
    "data": response_1,
    "name": "Response"
  },
  {
    "data": {
      "Accept-CH": "Sec-CH-Prefers-Color-Scheme",
      "Accept-Ranges": "none",
      "Alt-Svc": "h3=\":443\"; ma=2592000,h3-29=\":443\"; ma=2592000",
      "Cache-Control": "private, max-age=0",
      "Charset": "UTF-8",
      "Content-Length": None,
      "Content-Security-Policy-Report-Only": "object-src 'none';base-uri 'self';script-src 'nonce-RPtEuh-BasZcxVUbKmwNEA' 'strict-dynamic' 'report-sample' 'unsafe-eval' 'unsafe-inline' https: http:;report-uri https://csp.withgoogle.com/csp/gws/other-hp",
      "Content-Type": "text/html; charset=UTF-8",
      "Cross-Origin-Opener-Policy": "same-origin-allow-popups; report-to=\"gws\"",
      "Date": "Mon, 06 Oct 2025 06:49:41 GMT",
      "Expires": "-1",
      "Last-Modified": None,
      "P3P": "CP=\"This is not a P3P policy! See g.co/p3phelp for more info.\"",
      "Report-To": "{\"group\":\"gws\",\"max_age\":2592000,\"endpoints\":[{\"url\":\"https://csp.withgoogle.com/csp/report-to/gws/other\"}]}",
      "Server": "gws",
      "Set-Cookie": "AEC=AaJma5uTUO-h2zMWtpgVm8GSzmLj2vaBmtrc3nQYKG5o_SQdpY8H3gvSRck; expires=Sat, 04-Apr-2026 06:49:41 GMT; path=/; domain=.google.com; Secure; HttpOnly; SameSite=lax, __Secure-ENID=28.SE=QosmBx41caEH2gtolSMWk__fpUTlzAmiQccpRYkUJ-u2gT26DBxpPXFEY90sZd-p4jmPP88Yrf8EVkuDp7tcpfRvPU7c5WYcNBO7uhc3oyP1GcYuDVehfBRf30uWOyXYuqODMwJazwxnfx-TJHbSovvxt_cp44msrGViWeipWKEZvzzGzUIbskZPjfAyg5JiOBy2MaNnDwjvgW0cnJazn-I5y6xbSKIsCr6dZkxeo5DuSaAh-iGlz-MR1aOUWJ-uIA; expires=Thu, 05-Nov-2026 23:07:59 GMT; path=/; domain=.google.com; Secure; HttpOnly; SameSite=lax",
      "Strict-Transport-Security": "max-age=31536000",
      "Transfer-Encoding": "chunked",
      "Vary": "Accept-Encoding",
      "X-Frame-Options": "SAMEORIGIN",
      "X-XSS-Protection": "0"
    },
    "name": "Headers"
  },
  {
    "data": [],
    "name": "Entries"
  }
]


all_properties_streams = [
  {
    "data": {
      "album": None,
      "author": None,
      "date_published": None,
      "description": None,
      "favicon": "https://www.gstatic.com/images/branding/searchlogo/ico/favicon.ico",
      "language": "pl",
      "link": "https://youtube.com",
      "link_archives": [
        "https://web.archive.org/web/*/https://google.com",
        "https://archive.ph/google.com"
      ],
      "link_canonical": "https://google.com",
      "link_request": "https://google.com",
      "meta description": None,
      "meta keywords": None,
      "meta title": None,
      "og:description": None,
      "og:image": None,
      "og:site_name": None,
      "og:title": None,
      "page_rating": 100,
      "schema:thumbnailUrl": None,
      "tags": None,
      "thumbnail": "https://google.com/images/branding/googleg/1x/googleg_standard_color_128dp.png",
      "title": "Google"
    },
    "name": "Properties"
  },
  {
    "data": {
        "Contents" : "xx",
    },
    "name": "Text"
  },
  {
    "data": {
      "crawler": "RequestsCrawler",
      "enabled": True,
      "headers": None,
      "name": "RequestsCrawler",
      "settings": {
        "accept_content_types": "all",
        "bytes_limit": 5000000,
        "full": None,
        "headers": False,
        "ping": False,
        "remote_server": "http://127.0.0.1:3000",
        "respect_robots_txt": True,
        "ssl_verify": True,
        "timeout_s": 30
      }
    },
    "name": "Settings"
  },
  {
    "data": {
      "https://google.com" : response_1,
      "https://youtube.com" : response_2
    },
    "name": "Streams"
  },
  {
    "data": response_2,
    "name": "Response"
  },
  {
    "data": {
      "Accept-CH": "Sec-CH-Prefers-Color-Scheme",
      "Accept-Ranges": "none",
      "Alt-Svc": "h3=\":443\"; ma=2592000,h3-29=\":443\"; ma=2592000",
      "Cache-Control": "private, max-age=0",
      "Charset": "UTF-8",
      "Content-Length": None,
      "Content-Security-Policy-Report-Only": "object-src 'none';base-uri 'self';script-src 'nonce-RPtEuh-BasZcxVUbKmwNEA' 'strict-dynamic' 'report-sample' 'unsafe-eval' 'unsafe-inline' https: http:;report-uri https://csp.withgoogle.com/csp/gws/other-hp",
      "Content-Type": "text/html; charset=UTF-8",
      "Cross-Origin-Opener-Policy": "same-origin-allow-popups; report-to=\"gws\"",
      "Date": "Mon, 06 Oct 2025 06:49:41 GMT",
      "Expires": "-1",
      "Last-Modified": None,
      "P3P": "CP=\"This is not a P3P policy! See g.co/p3phelp for more info.\"",
      "Report-To": "{\"group\":\"gws\",\"max_age\":2592000,\"endpoints\":[{\"url\":\"https://csp.withgoogle.com/csp/report-to/gws/other\"}]}",
      "Server": "gws",
      "Set-Cookie": "AEC=AaJma5uTUO-h2zMWtpgVm8GSzmLj2vaBmtrc3nQYKG5o_SQdpY8H3gvSRck; expires=Sat, 04-Apr-2026 06:49:41 GMT; path=/; domain=.google.com; Secure; HttpOnly; SameSite=lax, __Secure-ENID=28.SE=QosmBx41caEH2gtolSMWk__fpUTlzAmiQccpRYkUJ-u2gT26DBxpPXFEY90sZd-p4jmPP88Yrf8EVkuDp7tcpfRvPU7c5WYcNBO7uhc3oyP1GcYuDVehfBRf30uWOyXYuqODMwJazwxnfx-TJHbSovvxt_cp44msrGViWeipWKEZvzzGzUIbskZPjfAyg5JiOBy2MaNnDwjvgW0cnJazn-I5y6xbSKIsCr6dZkxeo5DuSaAh-iGlz-MR1aOUWJ-uIA; expires=Thu, 05-Nov-2026 23:07:59 GMT; path=/; domain=.google.com; Secure; HttpOnly; SameSite=lax",
      "Strict-Transport-Security": "max-age=31536000",
      "Transfer-Encoding": "chunked",
      "Vary": "Accept-Encoding",
      "X-Frame-Options": "SAMEORIGIN",
      "X-XSS-Protection": "0"
    },
    "name": "Headers"
  },
  {
    "data": [],
    "name": "Entries"
  }
]


class RemoteServerTest(FakeInternetTestCase):
    def setUp(self):
        self.restore_web_pages()
        self.ignore_memory = True

    def tearDown(self):
        self.restore_web_pages()

    def test_get_response__none(self):
        # call tested function
        response = RemoteServer.get_response(None)

        self.assertFalse(response)

    def test_read_properties_section___false(self):
        all_data = {
                "success" : False,
                "error" : "Somethings wrong",
        }

        # call tested function
        response = RemoteServer.read_properties_section("Response", all_data)

        self.assertFalse(response)

    def test_get_response(self):
        # call tested function
        response = RemoteServer.get_response(all_properties)

        self.assertTrue(response)
        self.assertEqual(response.url, "https://www.google.com/")
        self.assertTrue(response.is_valid())
        self.assertFalse(response.is_invalid())
        self.assertTrue(response.get_text())
        self.assertEqual(response.get_status_code(), 200)

    def test_get_response__streams(self):
        # call tested function
        response = RemoteServer.get_response(all_properties_streams)

        self.assertTrue(response)
        self.assertEqual(response.url, "https://www.youtube.com/")
        self.assertTrue(response.is_valid())
        self.assertFalse(response.is_invalid())
        self.assertTrue(response.get_text())
        self.assertEqual(response.get_status_code(), 201)

    def test_endpoint_methods_dispatch(self):
        self.ignore_memory = True
        server = RemoteServer("http://test-server:8080")
        calls = []

        def mock_call(link_call, request):
            calls.append((link_call, request.url))
            return {"success": True, "url": request.url}

        server.perform_remote_call = mock_call

        server.get_page_data(url="https://example.com")
        self.assertEqual(calls[-1], ("http://test-server:8080/api/get", "https://example.com"))

        server.get_head_data(url="https://example.com")
        self.assertEqual(calls[-1], ("http://test-server:8080/api/head", "https://example.com"))

        server.get_feeds(url="https://example.com")
        self.assertEqual(calls[-1], ("http://test-server:8080/api/feeds", "https://example.com"))

        server.get_social(url="https://example.com")
        self.assertEqual(calls[-1], ("http://test-server:8080/api/social", "https://example.com"))

        server.get_link(url="https://example.com")
        self.assertEqual(calls[-1], ("http://test-server:8080/api/link", "https://example.com"))

        server.get_scan_links(url="https://example.com")
        self.assertEqual(calls[-1], ("http://test-server:8080/api/scanlinks", "https://example.com"))

        server.get_scan_domains(url="https://example.com")
        self.assertEqual(calls[-1], ("http://test-server:8080/api/scandomains", "https://example.com"))

        server.get_archives(url="https://example.com")
        self.assertEqual(calls[-1], ("http://test-server:8080/api/archives", "https://example.com"))

        server.get_find(url="https://example.com")
        self.assertEqual(calls[-1], ("http://test-server:8080/api/find", "https://example.com"))

        server.remove_history_entry(url="https://example.com")
        self.assertEqual(calls[-1], ("http://test-server:8080/api/remove", "https://example.com"))

    def test_global_endpoints(self):
        self.ignore_memory = True
        from unittest.mock import patch, MagicMock

        server = RemoteServer("http://test-server:8080")
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = '{"items": [1, 2, 3]}'
        mock_resp.__enter__.return_value = mock_resp

        with patch("requests.get", return_value=mock_resp):
            info = server.get_info()
            self.assertEqual(info, {"items": [1, 2, 3]})

            history = server.get_history()
            self.assertEqual(history, {"items": [1, 2, 3]})

            clear = server.clear_history()
            self.assertEqual(clear, {"items": [1, 2, 3]})

    def test_endpoints_return_none_on_error(self):
        self.ignore_memory = True
        from unittest.mock import patch

        server = RemoteServer("http://test-server:8080")
        with patch("requests.get", side_effect=Exception("network down")):
            self.assertIsNone(server.get_info())
            self.assertIsNone(server.get_history())
            self.assertIsNone(server.clear_history())
            self.assertIsNone(server.get_page_data(url="https://example.com"))

