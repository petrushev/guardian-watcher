import requests
from lxml.html import fromstring, tostring
from sys import argv
from datetime import datetime
import json
from operator import itemgetter
from werkzeug.utils import escape

def load_rss_list(list_path):
    """Load list of rss urls from a file"""
    with open(list_path, 'r') as f:
        return [line.split('|')[1].strip()
                for line in f]

def fetch_rss(rss):
    """Fetch and parse a given rss"""
    html = requests.get(rss).content
    doc = fromstring(html)
    items = doc.cssselect("channel item")
    for item in items:
        stamp = item.cssselect('date')[0].text
        date_ = stamp.split('T')[0]
        time_ = stamp.split('T')[1].split('Z')[0]
        yield (date_, time_,
               item.cssselect("title")[0].text_content(),
               item.cssselect("guid" )[0].text)

def fetch_all(rsslist, saved = None):
    """Fetch all rss feeds in list, and update the `saved` data"""
    if saved is None:
        dates = {}
    else:
        dates = saved

    for rss in rsslist:
        for date_, time_, title, url in fetch_rss(rss):
            if date_ not in dates:
                dates[date_] = {}

            dates[date_][url] = (time_, title)

    return dates

def gen_html(dates):
    """Generate partial html table from saved data"""
    dates = dates.items()
    dates.sort(key=itemgetter(0), reverse=True)

    html = ""

    today = datetime.utcnow().date()

    start_div = True
    for date, items in dates:
        date = datetime.strptime(date, '%Y-%m-%d').date()
        diffdate = today - date
        if diffdate.days == 0:
            date = 'today'
        elif diffdate.days == 1:
            date = 'yesterday'
        else:
            date = date.strftime('%d %B, %Y')

        if start_div:
            html = html + """<div class="fullblock">"""

        html = html + """
<div class="daily" >
  <h3>%s</h3>""" % date
        items = [(time_, title, url)
                 for url, (time_, title) in items.iteritems()]
        items.sort(key=itemgetter(0), reverse=True)
        for time_, title, url in items:
            html = html + """
  <div class="article">
    <span>
      %s
      <a href="%s" target="article" >%s</a>
    </span>
  </div>""" % (time_[:5], url, escape(title, True))

        html = html + """
</div>"""

        if not start_div: html = html + "</div>"

        start_div = not start_div

    return html
