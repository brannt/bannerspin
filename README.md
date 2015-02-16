# bannerspin
A small banner system I built for an interview task

The banners are stored in a CSV file in following format:

`Image URL;prepaid shows amount;category1;category2;category3; … ;category N`

On a GET request that includes 0 to 10 categories:

http://bannerspin.com/?category[]=rock&category[]=pop

the service returns HTML with a banner that belongs to at least one category (or to any category if no categories were included in request)


Additionally develop:
- an algorithm that reduces the probability of showing the same banner twice in a row;
- an algorithm that reduces the probability that there will be no available banners for request.

# Contents
- `bannerstore.py` - banner store algorithm implementations
- `benchmark_bannerstore.py` - benchmarks for the algorithms
- `main.py` - runner and entry point
- `server.py` - server implementation
- `templates.py` - HTML templates for the server
- `test_server.py` - e2e server tests
- `test_bannerstore.py` - unit tests for banner store (not currently runnable via `python -m unittest discover`, run the script directly `python test_bannerstore.py`

