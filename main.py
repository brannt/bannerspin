from server import BannerServer
from bannerstore import SimpleBannerStore

HOST = ''
PORT = 10500
CSV = 'test.csv'
BANNERSTORE_CLASS = SimpleBannerStore

if __name__ == '__main__':
    with open(CSV, 'rb') as csvfile:
        bs = BANNERSTORE_CLASS.load_from_file(csvfile)
    server = BannerServer(HOST, PORT, banner_store=bs)
    server.serve_forever()
