import string
import random
import timeit
import time

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

DEFAULT_ATTEMPTS = 10000
SEED = time.clock()
BANNERS = 1000
MIN_PREPAID = 10
MAX_PREPAID = 500
CATEGORIES = 500


def make_categories(num=CATEGORIES):
    return ["".join(random.sample(string.ascii_lowercase, 8))
            for i in xrange(num)]


def make_requests(categories):
    gen = random.Random()
    gen.seed(SEED)
    while True:
        yield gen.sample(categories, gen.randrange(1, 11))


def make_banners(categories):
    banners = [{
        'url': str(i),
        'prepaid': random.randrange(MIN_PREPAID, MAX_PREPAID),
        'categories': random.sample(categories, random.randrange(1, 11))
    } for i in xrange(BANNERS)]
    print "Total prepaid: %d" % sum(b['prepaid'] for b in banners)
    return banners


def setup():
    random.seed(SEED)
    categories = make_categories()
    banners = make_banners(categories)
    return banners, categories


def count_non_uniques(bs_class, banners, categories, requests,
                      attempts=DEFAULT_ATTEMPTS):
    bs = bs_class(banners)
    non_uniques = 0
    last_banner = None
    for i in range(attempts):
        banner = bs.select_banner(next(requests))
        if banner is None:
            break
        if banner == last_banner:
            non_uniques += 1
        last_banner = banner
    return non_uniques


def count_requests_till_none(bs_class, banners, categories, requests):
    bs = bs_class(banners)
    i = 0
    while bs.select_banner(next(requests)):
        i += 1
    return i


def time_requests(bs_class, banners, categories, attempts=DEFAULT_ATTEMPTS):
    setup_code = """
from __main__ import *
bs = %s(%s)
requests = make_requests(categories)
""" % (bs_class.__name__, repr(banners))
    test_code = """
bs.select_banner(next(requests))
"""
    return timeit.timeit(test_code, setup=setup_code, number=attempts)


if __name__ == '__main__':
    banners, categories = setup()
    for bs_class in BANNERSTORE_CLASSES:
        print bs_class.__name__
        print "Request time: %d" % time_requests(bs_class, banners, categories)
        print "Non-uniques: %d" % count_non_uniques(
            bs_class, banners, categories, make_requests(categories))
        print "Requests till None: %s" % count_requests_till_none(
            bs_class, banners, categories, make_requests(categories))
