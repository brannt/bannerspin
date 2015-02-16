import unittest
from copy import deepcopy
from StringIO import StringIO

from bannerstore import (
    SimpleBannerStore,
    MaxUniqueBannerStore,
    MinRequestsBannerStore
)

BANNERSTORE_CLASSES = [
    SimpleBannerStore,
    MaxUniqueBannerStore,
    MinRequestsBannerStore
]

DEFAULT_BANNERS = [
    {'url': 'http://banners.com/banner1.jpg', 'prepaid': 500,
            'categories': ['music', 'pop', 'michael jackson']},
    {'url': 'http://banners.com/banner2.jpg', 'prepaid': 3300,
            'categories': ['music', 'pop', 'abba']},
    {'url': 'http://banners.com/banner3.jpg', 'prepaid': 1500,
            'categories': ['music', 'rock', 'deep purple']}
]

DEFAULT_BANNERS_CSV = """http://banners.com/banner1.jpg;500;music;pop;michael jackson
http://banners.com/banner2.jpg;3300;music;pop;abba
http://banners.com/banner3.jpg;1500;music;rock;deep purple
"""

EXAMPLE_URL = "http://example.com/image.jpg"
EXAMPLE_PREPAID = 1000
EXAMPLE_CATEGORIES = ["test"]


class BannerStoreTestCase(unittest.TestCase):
    def __init__(self, methodName='runTest', bannerstore_class=BANNERSTORE_CLASSES[0],
                 *args, **kwargs):
        super(BannerStoreTestCase, self).__init__(methodName, *args, **kwargs)
        self.bannerstore_class = bannerstore_class

    def run(self, *args, **kwargs):
        super(BannerStoreTestCase, self).run(*args, **kwargs)


class TestSingleBanner(BannerStoreTestCase):
    def make_bs_for_single_banner(self, url=EXAMPLE_URL,
                                  prepaid=EXAMPLE_PREPAID, categories=None):
        return self.bannerstore_class(
            [dict(url=url, prepaid=prepaid, categories=categories)]
        )

    def select_single_banner(self, url=EXAMPLE_URL, prepaid=EXAMPLE_PREPAID,
                             categories=None, request_categories=None):
        if categories is None:
            categories = EXAMPLE_CATEGORIES
        if request_categories is None:
            request_categories = categories

        bs = self.make_bs_for_single_banner(
            url, prepaid, categories
        )
        return bs.select_banner(request_categories)

    def check_single_banner(self, url=EXAMPLE_URL, prepaid=EXAMPLE_PREPAID,
                            categories=None, request_categories=None):
        banner = self.select_single_banner(
            url, prepaid, categories, request_categories
        )
        self.assertEqual(banner.url, url)
        self.assertEqual(banner.prepaid, prepaid - 1)
        return banner  # for further checks

    def test_it_works(self):
        banner = self.check_single_banner(
            request_categories=EXAMPLE_CATEGORIES
        )
        self.assertTrue(set(EXAMPLE_CATEGORIES) & set(banner.categories))

    def test_empty_categories(self):
        self.check_single_banner(request_categories=[])

    def test_cant_get_unpaid_banner(self):
        self.assertIsNone(self.select_single_banner(prepaid=0))

    def test_prepaid_changes_persist(self):
        bs = self.make_bs_for_single_banner(
            prepaid=2, categories=EXAMPLE_CATEGORIES
        )
        banner = bs.select_banner(EXAMPLE_CATEGORIES)
        self.assertEqual(banner.prepaid, 1)
        banner = bs.select_banner(EXAMPLE_CATEGORIES)
        self.assertEqual(banner.prepaid, 0)
        banner = bs.select_banner(EXAMPLE_CATEGORIES)
        self.assertIsNone(banner)


class TestBannerStore(BannerStoreTestCase):
    def setUp(self):
        self.bs = self.bannerstore_class(DEFAULT_BANNERS)

    def test_select_by_single_cat(self):
        banner = self.bs.select_banner(["music"])
        self.assertIn("music", banner.categories)

    def test_select_by_all_matching_cats(self):
        cats = ["music", "michael jackson"]
        banner = self.bs.select_banner(cats)
        self.assertTrue(set(cats) | set(banner.categories))

    def test_select_by_some_matching_cats(self):
        cats = ["pop", "deep purple"]
        banner = self.bs.select_banner(cats)
        self.assertTrue(set(cats) | set(banner.categories))

    def test_select_when_some_unpaid(self):
        banners = deepcopy(DEFAULT_BANNERS)
        banners[0]['prepaid'] = 1

        bs = self.bannerstore_class(banners)
        bs.select_banner(["michael jackson"])

        banner = bs.select_banner(["pop"])
        self.assertIsNotNone(banner)
        self.assertGreaterEqual(banner.prepaid, 0)

    def test_all_unpaid_banners(self):
        banners = deepcopy(DEFAULT_BANNERS)
        for b in banners:
            b['prepaid'] = 1

        bs = self.bannerstore_class(banners)

        for i in range(len(DEFAULT_BANNERS)):
            banner = bs.select_banner(['music'])
            self.assertIsNotNone(banner)
            self.assertGreaterEqual(banner.prepaid, 0)

        banner = bs.select_banner(['music'])
        self.assertIsNone(banner)


class TestLoadBanners(BannerStoreTestCase):
    def test_it_works(self):
        bs = self.bannerstore_class.load_from_file(
            StringIO(DEFAULT_BANNERS_CSV)
        )
        for banner in DEFAULT_BANNERS:
            # last category is unique in test data
            b = bs.select_banner(banner['categories'][-1:])
            self.assertEquals(b.url, banner['url'])
            self.assertEquals(b.prepaid, banner['prepaid'] - 1)
            self.assertEquals(b.categories, banner['categories'])


if __name__ == '__main__':
    test_loader = unittest.defaultTestLoader

    # Run all tests for each provided class
    root_suite = unittest.TestSuite()
    for bs_class in BANNERSTORE_CLASSES:
        sub_suite = unittest.TestSuite()
        for tc_class in [TestSingleBanner, TestBannerStore, TestLoadBanners]:
            testcases = test_loader.getTestCaseNames(tc_class)
            for tc in testcases:
                sub_suite.addTest(tc_class(tc, bannerstore_class=bs_class))
        root_suite.addTest(sub_suite)

    unittest.TextTestRunner().run(root_suite)
