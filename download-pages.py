#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab

import os
import time

from bs4 import BeautifulSoup
import requests
import re


base_url = "https://www.electronshik.ru/catalog"
prefix = "download"


def get_pages(max_page, section):
    page = 1
    section_dir = "%s/%s" % (prefix, section)
    os.system("rm -rfv %s" % (section_dir,))
    os.system("mkdir -pv %s" % (section_dir,))
    while page < max_page + 1:
        output_file = "%s/%s_page%s.html" % (section_dir, section, page)
        url = "%s/%s?page=%s" % (base_url, section, page)
        os.system("wget -O %s %s 1>&2" % (output_file, url))
        time.sleep(0.2)
        page = page + 1


for section in [line.rstrip('\n') for line in open('SECTIONS')]:

    url = "%s/%s" % (base_url, section)
    r = requests.get(url)

    soup = BeautifulSoup(r.text.encode('utf-8'), "lxml")

    i = soup.find('div', {'class': "pagination-info"})
    if not i:
        sys.exit("%s: no pagination-info" % (section,))

    m = re.match('Страница [0-9]+ из ([0-9]+),', i.text)
    max_page = int(m.group(1))

    get_pages(max_page, section)
