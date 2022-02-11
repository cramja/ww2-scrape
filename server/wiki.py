import hashlib
import json
import logging
import re
import tempfile
from os.path import exists
from typing import List

import bs4
import firebase_admin
import requests
from firebase_admin import credentials
from firebase_admin import firestore

logging.basicConfig()
LOG = logging.getLogger(__name__)


def _get_docs(urls: List[str]):
    return {url: _get_doc(url) for url in urls}


def _get_doc(url: str) -> str:
    cache_key = f'{tempfile.gettempdir()}/{hashlib.md5(url.encode()).hexdigest()}.wiki'
    if exists(cache_key):
        with open(cache_key, 'r') as f:
            body = f.read()
            if body.startswith(url + "\n"):
                return body[len(url) + 1:]

    res = requests.get(url)
    res.raise_for_status()
    with open(cache_key, 'w') as f:
        f.writelines([url, '\n', res.text])
    return res.text


def _scrape_wiki_for_dates(html) -> dict:
    # TODO: handle li variant

    months = ["January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December"]
    months = {month: 1 + i for i, month in enumerate(months)}

    doc = bs4.BeautifulSoup(html, 'html.parser')
    container = doc.find(id="mw-content-text").contents[0]
    events = []

    year = int(doc.find(id="firstHeading").text[-5:][:-1])
    month = None
    for tag in container.contents:
        if month is None:
            if tag.name == 'h2':
                month = tag.span.attrs["id"]
        elif tag.name == 'h2':
            if tag.span.attrs["id"] in months:
                month = tag.span.attrs["id"]
            else:
                break
        else:
            event_html = tag.find("dd")
            if event_html != -1:
                try:
                    start_day, text = tag.text.split(":", 1)
                    end_day = None
                    if "-" in start_day:
                        start_day, end_day = start_day.split("-")
                    start_day = f"{year}-{months[month]:02d}-{int(start_day):02d}"
                    end_day = f"{year}-{months[month]:02d}-{int(end_day):02d}" if end_day else start_day

                    links = []
                    for link in tag.find_all("a"):
                        ref = link.get("href")
                        if ref.startswith("/wiki/"):
                            links.append(f"https://en.wikipedia.org/{ref}")

                    text = re.sub(r"\[\d+\]", "", text.strip())
                    events.append({
                        "id": hashlib.md5(text.encode()).hexdigest()[:12],
                        "startDate": start_day,
                        "endDate": end_day,
                        "text": text,
                        "links": links
                    })
                except:
                    # TODO: handle inline elements
                    LOG.debug(f"malformed line: {tag.text}")

    return events


def scrape_wiki():
    urls = [f"https://en.wikipedia.org/wiki/Timeline_of_World_War_II_({year})" for year in range(1939, 1945)]
    events = []
    for url in urls:
        events.extend(_scrape_wiki_for_dates(_get_doc(url)))
    return json.dumps(events, indent=2)


def sync_firestore(cert, events_file):
    """
    https://firebase.google.com/docs/firestore/quickstart?authuser=0#python
    """
    app = firebase_admin.initialize_app(credentials.Certificate(cert))
    db = firestore.client(app)

    with open(events_file, 'r') as f:
        events = json.load(f)

    updated, checked = 0, 0
    for event in events:
        doc_ref = db.collection(u'events').document(event["id"])

        if doc_ref.get().to_dict() != event:
            doc_ref.set(event)
            updated += 1
        else:
            checked += 1
        if (updated + checked) % 10 == 0:
            print(f"updated {updated} and checked {checked} of {len(events)}")
