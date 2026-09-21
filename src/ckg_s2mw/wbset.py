#! /usr/bin/env python
#
# Copyright (C) 2025 Darron Broad
# All rights reserved.
#
# This file is part of ckg_s2mw.
#
# ckg_s2mw is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation.
#
# ckg_s2mw is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with ckg_s2mw. If not, see http://www.gnu.org/licenses/
#
import argparse
import csv
import json
import os
import re
import sys
import xmltodict

from wikibaseintegrator.wbi_config import config as wbi_config

from dotenv import load_dotenv

from cps_wb.wikibase import WB
from cps_wb.wikilabel import WikiLabel

from wikibaseintegrator.datatypes import Item, String, URL
from wikibaseintegrator.models import Qualifiers, References, Reference

# akamaitechnologies hangs unless it recognises the User-Agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134."

# IPCC glossary base URL
GLOSSARY = "https://apps.ipcc.ch/glossary/"

# Handles
wb = None # WikiBase

# Properties
P = {}

# Objects
Q = {}

# Work
PUBLICATION = None
ALIAS = None
TAGS = {}
SERIES = {}
CHAPTERS = {}
BOOKS = {}

def main():
    global P, Q, wb, PUBLICATION, ALIAS

    parser = argparse.ArgumentParser()

    parser.add_argument("file", type=str, help="XML file", nargs='?')

    args = parser.parse_args()

    load_dotenv(os.getcwd() + os.sep + ".env")

    if not os.getenv("WB_URL"):
        raise Exception("MB_URL is missing")

    if not os.getenv("WB_USERNAME"):
        raise Exception("WB_USERNAME is missing")

    if not os.getenv("WB_PASSWORD"):
        raise Exception("WB_PASSWORD is missing")

    if not args.file:
        raise Exception("XML file is missing")

    wbi_config["DEFAULT_LANGUAGE"] = "en"
    wbi_config["WIKIBASE_URL"] = os.getenv("WB_URL")
    wbi_config["MEDIAWIKI_API_URL"] = os.getenv("WB_URL") + "w/api.php"
    wbi_config["USER_AGENT"] = USER_AGENT

    ##################################################################
    # Login to Wikibase
    #
    wb = WB(os.getenv("WB_USERNAME"), os.getenv("WB_PASSWORD"))

    ##################################################################
    # Custom Wikibase properties
    #
    # MEDIAWIKI URL
    P["WIKI"] = wb.property([WikiLabel("Wiki", "Wiki URL", "en")], "url")

    # IPCC SOURCE URL
    P["SOURCE"] = wb.property([WikiLabel("Source", "Source URL", "en"),
        WikiLabel("Ursprung", "Ursprung URL", "de")], "url")

    # IPCC SOURCE PDF
    P["PDF"] = wb.property([WikiLabel("PDF", "PDF URL", "en")], "url")

    # Date
    P["DATE"] = wb.property([WikiLabel("Date", "Date String", "en"),
        WikiLabel("Datum", "Datum Zeichenkette", "de")], "string")

    # OPENALEX
    P["OPENALEX"] = wb.property([WikiLabel("OPENALEX", "ID String", "en")], "string")

    # DOI
    P["DOI"] = wb.property([WikiLabel("DOI", "ID String", "en")], "string")

    # DOI
    P["LICENSE"] = wb.property([WikiLabel("LICENSE", "License String", "en")], "string")

    # TAG
    P["TAG"] = wb.property([WikiLabel("Has TAG", "Has subject or topic", "en")], "wikibase-item")

    ##################################################################
    # ROOT OBJECTS
    #
    Q["CAT"] = wb.item([WikiLabel("Category", "Subject or topic tag", "en", ["Subject", "TAG", "Keyword"])], wait=True)
    Q["WORK"] = wb.item([WikiLabel("Work", "Abstract creation", "en")], wait=True)

    claims = [Item(prop_nr=wb.PInstanceOf, value=Q["WORK"])]
    Q["PUB"] = wb.item([WikiLabel("Publication", "Written work", "en")], claims, wait=True)

    Q["SERIES"]  = wb.item([WikiLabel("Series", "Sequence of written works", "en", ["Volumes"])], wait=True)
    Q["BOOK"]    = wb.item([WikiLabel("Book", "Work of fiction or nonfiction", "en", ["Volume"])], wait=True)
    Q["CHAPTER"] = wb.item([WikiLabel("Chapter", "Division of a written work", "en", ["Segment", "Section"])], wait=True)

    ##################################################################
    # PARSE XML
    #
    with open(args.file, mode='r', encoding='utf-8') as file:
        data = xmltodict.parse(file.read())

    # ABSTRACT WORK
    work = data.get('work', {})

    # IPCC PUBLICATION CYCLE
    publication = work.get('publication', {})

    print(f"PUBLICATION ID:          {publication.get('@id')}")
    print(f"PUBLICATION TITLE:       {publication.get('title')}")
    print(f"PUBLICATION DESCRIPTION: {publication.get('description')}")

    ALIAS = publication.get('@id')

    claims = [Item(prop_nr=wb.PInstanceOf, value=Q["PUB"])]
    labels = [WikiLabel(publication.get('title'), publication.get('description'), "en", [ALIAS])]

    PUBLICATION = wb.item(labels, claims, wait=True)

    print("-" * 10)

    # IPCC PUBLICATION SERIES (WGII etc)
    series_list = get_list(publication, 'series')
    for series in series_list:
        add_series(series)

def get_list(data, *keys):
    # Get list of dictionaries generated by xmltodict

    # Locate inner element
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key)
        else:
            return []

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        return [data]

    return []

def add_cats(taglist):
    global TAGS

    if taglist:
        tags = re.split(r'\s*;\s*', taglist)
        for tag in tags:
            claims = [Item(prop_nr=wb.PInstanceOf, value=Q["CAT"])]
            labels = [WikiLabel(tag, f"Subject or topic tag: {tag}", "en")]

            TAGS[tag] = wb.item(labels, claims, wait=True)

        return tags

    return None

def add_series(series):
    global SERIES, CHAPTERS

    tags = add_cats(series.get('tags'))

    series_id = series.get('@id')
    series_title = series.get('title')
    series_description = series.get('description')

    alias = f"{ALIAS}; {series_id}"
    labels = [WikiLabel(series_title, series_description, "en", [alias])]

    claims = [Item(prop_nr=wb.PInstanceOf, value=Q["SERIES"])]
    claims.append(Item(prop_nr=wb.PPartOf, value=PUBLICATION))
    claims.append(String(prop_nr=P["DOI"], value=series.get('doi')))
    claims.append(String(prop_nr=P["LICENSE"], value=series.get('license')))
    claims.append(String(prop_nr=P["DATE"], value=series.get('date')))

    if tags:
        for tag in tags:
            claims.append(Item(prop_nr=P["TAG"], value=TAGS[tag]))

    SERIES[series_title] = wb.item(labels, claims, wait=True)

    chapters = get_list(series, 'front_matter', 'chapter')
    for chapter in chapters:

        tags = add_cats(chapter.get('tags'))

        chapter_id = chapter.get('@id')
        chapter_title = chapter.get('title')

        alias = f"{ALIAS}; {series_id}; F:{chapter_id}"
        labels = [WikiLabel(chapter_title, series_description, "en", [alias])]

        claims = [Item(prop_nr=wb.PInstanceOf, value=Q["CHAPTER"])]
        claims.append(Item(prop_nr=wb.PPartOf, value=SERIES[series_title]))

        claims.append(URL(prop_nr=P["WIKI"], value=chapter.get('wiki')))
        claims.append(URL(prop_nr=P["SOURCE"], value=chapter.get('source')))
        claims.append(URL(prop_nr=P["PDF"], value=chapter.get('pdf')))
        claims.append(String(prop_nr=P["DOI"], value=chapter.get('doi')))
        claims.append(String(prop_nr=P["OPENALEX"], value=chapter.get('openalex')))

        if tags:
            for tag in tags:
                claims.append(Item(prop_nr=P["TAG"], value=TAGS[tag]))

        CHAPTERS[chapter_title] = wb.item(labels, claims, wait=True)

    books = get_list(series, 'books', 'book')
    for book in books:

        tags = add_cats(book.get('tags'))

        book_id = book.get('@id')
        book_title = book.get('title')

        alias = f"{ALIAS}; {series_id}; B:{book_id}"
        labels = [WikiLabel(book_title, series_description, "en", [alias])]

        claims = [Item(prop_nr=wb.PInstanceOf, value=Q["BOOK"])]
        claims.append(Item(prop_nr=wb.PPartOf, value=SERIES[series_title]))

        if tags:
            for tag in tags:
                claims.append(Item(prop_nr=P["TAG"], value=TAGS[tag]))

        BOOKS[book_title] = wb.item(labels, claims, wait=True)

        chapters = get_list(book, 'chapters', 'chapter')
        for chapter in chapters:

            tags = add_cats(chapter.get('tags'))

            chapter_id = chapter.get('@id')
            chapter_title = chapter.get('title')

            alias = f"{ALIAS}; {series_id}; B:{book_id}; C:{chapter_id}"
            labels = [WikiLabel(chapter_title, series_description, "en", [alias])]

            claims = [Item(prop_nr=wb.PInstanceOf, value=Q["CHAPTER"])]
            claims.append(Item(prop_nr=wb.PPartOf, value=BOOKS[book_title]))
            claims.append(URL(prop_nr=P["WIKI"], value=chapter.get('wiki')))
            claims.append(URL(prop_nr=P["SOURCE"], value=chapter.get('source')))
            claims.append(URL(prop_nr=P["PDF"], value=chapter.get('pdf')))
            claims.append(String(prop_nr=P["DOI"], value=chapter.get('doi')))
            claims.append(String(prop_nr=P["OPENALEX"], value=chapter.get('openalex')))

            if tags:
                for tag in tags:
                    claims.append(Item(prop_nr=P["TAG"], value=TAGS[tag]))

            CHAPTERS[chapter_title] = wb.item(labels, claims, wait=True)

if __name__=="__main__":
    main()

# vim: shiftwidth=4 tabstop=4 softtabstop=4 expandtab
