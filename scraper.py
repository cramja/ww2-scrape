from typing import List

import bs4
import requests
import tempfile
from os.path import exists
import hashlib
import json
import logging

logging.basicConfig()
LOG = logging.getLogger(__name__)


def get_docs(urls: List[str]):
    return {url: get_doc(url) for url in urls}


def get_doc(url: str) -> str:
    cache_key = f'{tempfile.gettempdir()}/{hashlib.md5(url.encode()).hexdigest()}.wiki'
    if exists(cache_key):
        with open(cache_key, 'r') as f:
            body = f.read()
            if body.startswith(url + "\n"):
                return body[len(url)+1:]

    res = requests.get(url)
    res.raise_for_status()
    with open(cache_key, 'w') as f:
        f.writelines([url, '\n', res.text])
    return res.text


def scrape_wiki_for_dates(html) -> dict:
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
                    # TODO: handle date ranges
                    day, text = tag.text.split(":", 1)
                    events.append({
                        "timestamp": f"{year}-{months[month]:02d}-{int(day):02d}",
                        "text": text.strip(),
                        "html": str(tag)
                    })
                except:
                    # TODO: handle inline elements
                    LOG.debug(f"malformed line: {tag.text}")

    return events

if __name__ == '__main__':
    urls = [f"https://en.wikipedia.org/wiki/Timeline_of_World_War_II_({year})" for year in range(1939, 1945)]
    events = []
    for url in urls:
        events.extend(scrape_wiki_for_dates(get_doc(url)))
    print(json.dumps(events, indent=2))