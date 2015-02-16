import collections
import csv
import random
from abc import ABCMeta, abstractmethod


class Banner:
    def __init__(self, url, prepaid, categories):
        self.url = url
        self.prepaid = prepaid
        self.categories = categories

    def __repr__(self):
        return ("<URL: %s, Prepaid: %s, Cats: %s>" %
                (self.url, self.prepaid, self.categories))


class BannerStoreBase(object):
    __metaclass__ = ABCMeta
    """
    `BannerStore` stores all available banners and organizes banner rotation.

    Parameters:
        `banners`: an iterable of dicts:
            {'url': url, 'prepaid': prepaid_views, 'categories': [categories]}

    Usage:
    >>> bs = BannerStore([...])
    >>> bs = BannerStore.load_from_file(open('config.csv'))
    >>> bs.select_banner(categories)
    """
    def __init__(self, banners):
        self._store = collections.defaultdict(set)
        self._load_banners(banners)

    def _load_banners(self, banners):
        for banner_params in banners:
            b = Banner(**banner_params)
            if not b.prepaid:
                continue
            for cat in b.categories:
                self._store[cat].add(b)

    def _get_banners_from_categories(self, categories):
        if not categories:
            categories = self._store.keys()

        return set.union(*(self._store[c] for c in categories))

    @abstractmethod
    def select_banner(self, categories):
        """
        Return prepaid banner from at least one of the `categories`.

        Details of banner selection strategy are specific to implementation.
        """
        pass

    @classmethod
    def load_from_file(cls, iterable):
        """
        Load banners from `iterable` of CSV-format strings.
        """
        def _banner_csv_reader(iterable):
            reader = csv.reader(iterable, delimiter=';')
            for row in reader:
                yield {
                    'url': row[0],
                    'prepaid': int(row[1]),
                    'categories': row[2:]
                }

        return cls(_banner_csv_reader(iterable))


class SimpleBannerStore(BannerStoreBase):
    """
    Basic implementation of banner store.
    """
    def select_banner(self, categories):
        available_banners = self._get_banners_from_categories(categories)

        while available_banners:
            banner = random.choice(tuple(available_banners))

            if banner.prepaid:
                banner.prepaid -= 1
                return banner

            available_banners.remove(banner)

        return None


class MaxUniqueBannerStore(BannerStoreBase):
    """
    Banner store implementation that minimizes chance of repeated banners.
    """
    last_banner = None

    def select_banner(self, categories):
        available_banners = self._get_banners_from_categories(categories)

        while available_banners:
            banner = random.choice(tuple(available_banners))

            # Return same banner only if it's the only one left
            if banner == self.last_banner and len(available_banners) > 1:
                continue

            if banner.prepaid:
                banner.prepaid -= 1
                self.last_banner = banner
                return banner

            available_banners.remove(banner)

        return None


class MinRequestsBannerStore(BannerStoreBase):
    """
    Banner store implementation that minimizes chance of returning None.
    """
    def select_banner(self, categories):
        available_banners = self._get_banners_from_categories(categories)

        if not available_banners:
            return None

        banner = max(available_banners, key=lambda b: b.prepaid)

        if banner.prepaid:
            banner.prepaid -= 1
            return banner

        return None
