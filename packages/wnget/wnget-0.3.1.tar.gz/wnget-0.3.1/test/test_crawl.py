from wnget.crawl import Crawler


class Test:
    def setup_method(self, test_method):
        self.c = Crawler()

    def teardown_method(self, test_method):
        pass

    def test_get_title(self):
        pass

    def test_get_content(self):
        pass

    def test_process_nav(self):
        pass

    def test_crawl(self):
        pass
