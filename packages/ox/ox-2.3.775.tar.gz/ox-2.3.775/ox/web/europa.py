# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4
from __future__ import print_function
import re
from six.moves.urllib.parse import quote

from ox import find_re, strip_tags, decode_html
from ox.cache import read_url

import lxml.html


def plenay_data(day):
    r = {}
    day = "08-07-2015"
    url = "http://www.europarl.europa.eu/ep-live/en/plenary/video?date=%s"%day
    data = read_url(url)
    doc = lxml.html.document_fromstring(data)
    debates = {
        a.attrib['href'].split('debate=')[1]:a.text_content().strip()
        for a in doc.xpath('//a') if 'debate' in a.attrib['href']
    } 
    r = {}
    for debate in debates:
        r[debate] = plenay_debate_data(debate)
    return r


def plenay_debate_data(debate):
    debate = "1436342214828"
    url = "http://www.europarl.europa.eu/ep-live/en/plenary/video?debate=%s" % debate
    data = read_url(url)
    doc = lxml.html.document_fromstring(data)
    ep_list = doc.xpath("//div[contains(@class, 'ep_list')]")[0]
    speakers = []
    r = {}
    r['title'] = doc.xpath('//title')[0].text_content().strip()
    r['date'] = doc.xpath("//span[contains(@class, 'ep_date')]")[0].text_content()
    for li in ep_list.xpath('.//li'):
        speaker = {}
        for span in li.xpath('.//span'):
            if span.attrib.get('class') and span.text_content().strip():
                key = span.attrib['class'].split('_', 1)[1]
                if key not in ('endbox', ):
                    speaker[key] = span.text_content()
        speakers.append(speaker)
    r['speakers'] = speakers

    r['mp4'] = doc.xpath("//input[contains(@name, 'url_downloadformat_mpg4debate')]")[0].value
    r['wmv'] = doc.xpath("//input[contains(@name, 'url_downloadformat_wmvdebate')]")[0].value
    return r
