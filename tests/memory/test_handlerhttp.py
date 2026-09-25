import gc
from webtoolkit import (
   HtmlPage,
   RssPage,
   HttpPageHandler,
   HTTP_STATUS_CODE_SERVER_ERROR,
   HTTP_STATUS_OK,
)
from webtoolkit.utils.memorychecker import MemoryChecker

from webtoolkit.tests.fakeinternet import FakeInternetTestCase
from webtoolkit.tests.mocks import MockRequestCounter, MockUrl


class HttpPageHandlerMemoryTest(FakeInternetTestCase):
    def setUp(self):
        self.disable_web_pages()

        self.ignore_memory = False
        self.memory_checker = MemoryChecker()
        memory_increase = self.memory_checker.get_memory_increase()

    def tearDown(self):
        MockRequestCounter.reset()
        gc.collect()

        if not self.ignore_memory:
            memory_increase = self.memory_checker.get_memory_increase()
            self.assertEqual(memory_increase, 0)

    def test_get_response__html(self):
        for i in range(1, 500):
            test_link = "https://linkedin.com"
            url = MockUrl(test_link)
            request = url.get_init_request()

            handler = HttpPageHandler(test_link, request=request, url_builder = MockUrl)
            response = handler.get_response()
            url.close()
