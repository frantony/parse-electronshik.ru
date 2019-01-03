#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab

import os
import re

import sys
#reload(sys)
#sys.setdefaultencoding('utf-8')

from bs4 import BeautifulSoup

import sqlite3

DEBUG = 0


def parse_table(item_table):

    tbody = item_table.find('tbody')
    if not tbody:
        sys.exit("%s: no tbody" % (html_filename,))

    conn = sqlite3.connect(db_filename)

    rows = tbody.find_all('tr')
    for row in rows:
        cols = row.find_all('td')

        c0 = cols[0]

        hit = c0.find('span', {'class': "part_special_mark_hit"})
        if not hit:
            continue

        name = c0["data-name"]
        producer_code = c0["data-producer_code"]

        number = cols[1].text.strip()
        price = cols[2].text.strip()
        price = re.sub(",.*$", "", price)
        price = re.sub("\xa0", "", price)
        days = cols[3].text.strip()
        days = re.sub(u" \u0434\u043d\.$", "", days)

        if DEBUG:
            print("%s %s    <%s>    <%s>    <%s>\n" % (name, producer_code, number, price, days),)

        c = conn.cursor()
        try:
            c.execute("INSERT INTO components VALUES (?, ?, ?)", (name, producer_code, price,))
        except sqlite3.IntegrityError as e:
            # column name is not unique
            print('sqlite error: ', e.args[0])
            print((name, producer_code, price,))
        conn.commit()

    conn.close()


def parse_grid(grid):

    cells = grid.find_all('div', { 'class': 'product-cell' })

    conn = sqlite3.connect(db_filename)

    for i in cells:
        pch = i.find('div', { 'class': 'product-cell-hover' })

        hit = pch.find('span', {'class': "part_special_mark_hit"})
        if not hit:
            continue

        name = pch["data-name"]
        producer_code = pch["data-producer_code"]

        gis = i.find('div', { 'class': 'grid_in_stock' })

        number = gis.text.strip()
        number = re.sub(" шт$", "", number)

        gp = i.find('div', { 'class': 'grid_price' })
        sc = gp.find('span', { 'class': 'integer' })
        price = sc.text.strip()
        price = re.sub("[^0-9]", "", price)

        if DEBUG:
            print("%s %s    <%s>    <%s>\n" % (name, producer_code, number, price),)

        c = conn.cursor()
        req = "INSERT INTO components VALUES ('%s', '%s', %s)" % (name, producer_code, price,)
        print(req)
        c.execute(req)

    conn.commit()
    conn.close()


def parse_one_file(db_filename, html_filename):
    with open(html_filename) as fp:
        s = fp.read()
        soup = BeautifulSoup(s.encode('utf-8'), "lxml")

    i = soup.find('table', {'id': "item-table"})
    if not i:
        items = soup.find('div', {'class': "section-items"})
        if not items:
            sys.exit("%s: no section-items" % (html_filename,))
        parse_grid(items)
    else:
        parse_table(i)


db_filename = sys.argv[1]
html_filename = sys.argv[2]
print(html_filename)
parse_one_file(db_filename, html_filename)
