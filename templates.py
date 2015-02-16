BASE = """
<html>
    <head>
        <title>Banner Spin!</title>
    </head>
    <body>
        %(body)s
    </body>
</html>
"""

MAIN = BASE % {'body': "<img src=\"%(url)s\" />"}
ERROR = BASE % {'body': "No paid banners found for these categories"}
