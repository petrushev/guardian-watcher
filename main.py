from os.path import abspath, dirname
from sys import argv
import json

from guardianwatcher import load_rss_list, fetch_all, gen_html

PROJECTPATH = dirname(abspath(__file__))

def main():
    rsslist = load_rss_list(argv[1])
    target_html = open(argv[2], 'w')

    saved_cache = PROJECTPATH + '/_cache_/saved'

    # load saved cache
    try:
        with open(saved_cache, 'r') as f:
            saved = json.loads(f.read())
    except Exception:
        saved = {}

    # fetch updates
    data = fetch_all(rsslist, saved=saved)

    # save cache
    with open(saved_cache, 'w') as f:
        f.write(json.dumps(data))

    with open(PROJECTPATH + '/static/header.html', 'r') as f:
        target_html.write(f.read())

    # generate html
    html = gen_html(data)
    target_html.write(html.encode('utf-8'))

    with open(PROJECTPATH + '/static/footer.html', 'r') as f:
        target_html.write(f.read())

    target_html.close()

main()
