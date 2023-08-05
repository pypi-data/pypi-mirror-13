
# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4
from datetime import datetime

from six.moves.urllib.parse import quote
import lxml.html

from ox.cache import read_url


base = "https://kat.cr"
UNITS = {
    'KB': 1024,
    'MB': 1024 * 1024,
    'GB': 1024 * 1024 * 1024,
}

def find_movies(query=None, imdb=None, max_results=10):
    if imdb:
        url = base + "/usearch/imdb:%s/" % imdb
    else:
        url = base + "/usearch/%s/" % quote(query)
    results = []
    data = read_url(url)
    doc = lxml.html.document_fromstring(data)
    tables = doc.xpath("//table[contains(@class, 'data')]")
    if not tables:
        return results
    table = tables[0]
    for row in table.xpath(".//tr"):
        if row.attrib.get('class') == 'firstr':
            continue
        r = {}
        for a in row.xpath('.//a'):
            if a.attrib['href'].startswith('magnet'):
                r['magnet'] = a.attrib['href']
            if a.attrib['href'].endswith('.html'):
                r['url'] = base + a.attrib['href']
        spans = row.xpath('.//td')
        r['files'] = int(spans[2].text.strip())
        r['seeder'] = int(spans[4].text.strip())
        r['leacher'] = int(spans[5].text.strip())
        unit = spans[1].xpath('.//span')[0].text.strip()
        r['size'] = int(float(spans[1].text.strip()) * UNITS.get(unit, 1))
        r['date'] = datetime.strptime(spans[3].attrib['title'], "%d %b %Y, %H:%M")
        texts = [a.text_content() for a in spans[0].xpath('.//a')]
        r['title'] = texts[-4].strip()
        r['uploader'] = texts[-3].strip()
        r['type'] = texts[-2].strip()
        r['group'] = texts[-1].strip()
        results.append(r)
    return results
