import requests
from lxml.html import fromstring, tostring
from sys import argv
from datetime import datetime
from operator import itemgetter
from werkzeug.utils import escape

def load_rss_list(list_path):
    """Load list of rss urls from a file"""
    list_ = []
    with open(list_path, 'r') as f:
        for line in f:
            rss_name, rss = line.split('|')
            rss_name = rss_name.strip()
            rss = rss.strip()
            list_.append((rss_name, rss))
    return list_

def fetch_rss(rss):
    """Fetch and parse a given rss"""
    html = requests.get(rss).content
    doc = fromstring(html)
    items = doc.cssselect("channel item")
    for item in items:
        stamp = item.cssselect('date')[0].text
        date_, time_ = stamp.split('T')
        time_ = time_.split('Z')[0]
        yield (date_, time_,
               item.cssselect("title")[0].text_content().split('|')[0],
               item.cssselect("guid" )[0].text)

def fetch_all(rsslist, saved = None):
    """Fetch all rss feeds in list, and update the `saved` data"""
    if saved is None:
        data = {}
    else:
        data = saved

    for rss_name, rss in rsslist:
        for date_, time_, title, url in fetch_rss(rss):
            if date_ not in data:
                data[date_] = {}

            if url in data[date_]:
                tags = data[date_][url][2] #saved tags
                if rss_name not in tags: tags.append(rss_name)
            else:
                tags = [rss_name]

            data[date_][url] = (time_, title, tags)

    return data

def gen_html(data):
    """Generate partial html table from saved data"""
    data = data.items()
    data.sort(key=itemgetter(0), reverse=True)

    html = ""

    today = datetime.utcnow().date()

    start_div = True
    for date, items in data:
        date = datetime.strptime(date, '%Y-%m-%d').date()
        diffdate = today - date
        if diffdate.days == 0:
            date = 'today'
        elif diffdate.days == 1:
            date = 'yesterday'
        else:
            date = date.strftime('%d %B, %Y')

        html = html + """
  <div class="daily" >
    <h3>%s</h3>""" % date

        items = [(time_, title, url, tags)
                 for url, (time_, title, tags) in items.iteritems()]
        items.sort(key=itemgetter(0), reverse=True)

        for time_, title, url, tags in items:
            html = html + """
    <div class="article">
      <span>
        %s
        <a href="%s" target="_blank" >%s</a>
      </span>""" % (time_[:5], url, escape(title.split('|')[0], True))

            for tag in tags:
                html = html + """
      <span class="hidden rssname">%s</span> """ % tag

            html = html + """
    </div>"""

        html = html + """
  </div>"""

        start_div = not start_div

    return html
