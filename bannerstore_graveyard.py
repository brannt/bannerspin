from bannerstore import *


class DumbBannerStore(BannerStoreBase):
    def select_banner(self, categories):
        if not categories:
            categories = self._store.keys()

        available_banners = set.union(*(self._store[c] for c in categories))

        while available_banners:
            banner = available_banners.pop()

            if banner.prepaid:
                banner.prepaid -= 1
                return banner

        return None


class SimpleBannerStore(BannerStoreBase):
    def select_banner(self, categories):
        if not categories:
            categories = self._store.keys()
        available_banners = (self._store[cat] for cat in categories)
        available_banners = set(itertools.chain(*available_banners))
        while available_banners:
            banner = random.choice(tuple(available_banners))
            if banner.prepaid:
                banner.prepaid -= 1
                return banner
            available_banners.remove(banner)

        return None


class SetFilterBannerStore(BannerStoreBase):
    def select_banner(self, categories):
        if not categories:
            categories = self._store.keys()
        available_banners = (self._store[cat] for cat in categories)
        available_banners = set(b for b in itertools.chain(*available_banners)
                                if b.prepaid)
        if not available_banners:
            return None
        banner = random.choice(tuple(available_banners))
        banner.prepaid -= 1
        return banner


class DequeBannerStore(BannerStoreBase):
    def __init__(self, banners):
        self._store = collections.defaultdict(collections.deque)
        self.load_banners(banners)

    def select_banner(self, categories):
        if not categories:
            categories = self._store.keys()
        categories = [cat for cat in categories if self._store[cat]]
        if not categories:
            return None
        category = random.choice(categories)
        banner = self._store[category].popleft()
        if banner.prepaid:
            banner.prepaid -= 1
            if banner.prepaid > 0:
                self._store[category].append(banner)
            return banner
        return None


class MaxUniqueDequeBannerStore(DequeBannerStore):
    def __init__(self, banners):
        super(MaxUniqueDequeBannerStore, self).__init__(banners)
        for cat_banners in self._store.values():
            random.shuffle(cat_banners)

    def select_banner(self, categories):
        if not categories:
            categories = self._store.keys()
        categories = [cat for cat in categories if self._store[cat]]
        if not categories:
            return None
        category = max(categories, key=len)
        banner = self._store[category].popleft()
        banner.prepaid -= 1
        if banner.prepaid > 0:
            self._store[category].append(banner)
        return banner
