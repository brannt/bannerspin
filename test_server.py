import subprocess
import time
import unittest
import urllib
from main import HOST, PORT


class TestServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server_process = subprocess.Popen(['python', 'main.py'])
        # Dumb wait for server start
        time.sleep(0.5)

    @classmethod
    def tearDownClass(cls):
        cls.server_process.kill()

    def do_request(self, categories=None):
        url = "http://%s:%s/" % (HOST or '127.0.0.1', PORT)
        if categories:
            url += "?" + urllib.urlencode({'category[]': categories},
                                          doseq=True)
        return urllib.urlopen(url).read()

    def check_request(self, categories=None):
        resp = self.do_request(categories)
        self.assertIn("<img", resp)

    def test_no_categories(self):
        self.check_request()

    def test_one_category(self):
        self.check_request(['music'])

    def test_ten_categories(self):
        self.check_request(['music', 'pop', 'rock', 'abba', 'deep purple',
                           'show', 'britain', 'benny hill', 'sketches', 'tv'])

    def test_unpaid(self):
        resp = self.do_request(['fails'])
        self.assertIn("No paid banners", resp)


if __name__ == '__main__':
    unittest.main()
