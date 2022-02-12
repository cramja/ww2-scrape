import datetime
import hashlib
import json
import logging
import re
import tempfile
from os.path import exists
from typing import List
import spacy
from requests_html import HTMLSession
from werkzeug.urls import url_encode
import bs4
import firebase_admin
import requests
from bs4 import NavigableString
from bs4 import Tag
from firebase_admin import credentials
from firebase_admin import firestore

logging.basicConfig()
LOG = logging.getLogger(__name__)

nlp = spacy.load("en_core_web_md")
session = HTMLSession()

def _query_img(q) -> List[str]:
    resp = session.get(f"https://www.google.com/search?{url_encode({'q': q, 'tbm': 'isch', 'sclient': 'img'})}")
    resp.html.render()

    doc = bs4.BeautifulSoup(resp.html.html, 'html.parser')
    imgs = [
        tag.attrs["src"]
        for tag in doc.find_all(lambda r: r.name == "img"
                                          and "".join(r.attrs.get("class", "")).startswith("rg_")
                                          and r.attrs.get("src", "").startswith("data"))
    ]
    #session.close()
    return imgs

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


def _keywords(text, keywords):
    def is_country(t):
        t = t.lower()
        for term in ['fren', 'brit', 'us', 'germ', 'china', 'japan']:
            if t.startswith(term):
                return False
        return True
    parsed = {k.lower(): k for k in filter(is_country,
                  list(map(lambda kw: kw[0][4:] if kw[0].lower().startswith('the ') else kw[0], [(ent.text, ent.label_,) for ent in nlp(text).ents if
              ent.label_ not in {'DATE', 'ORDINAL', 'TIME', 'CARDINAL', 'GPE', 'NORG'}])))}
    kw = {k.lower(): k for k in keywords}
    result = []
    for key in parsed.keys():
        if key in kw:
            del kw[key]
        result.append(parsed[key])
    result.extend(list(kw.values()))
    return result



def _parse_date_tag(tag, submit):
    # date tags can contain multiple events. They're <br> separated
    def clean(text):
        return re.sub(r"^[0-9]*(-[0-9]+)?\W*:\W*", "", re.sub(r"\[\d+\]", "", text)).strip()
    start_day, text = tag.text.split(":", 1)
    end_day = None
    if "-" in start_day:
        start_day, end_day = start_day.split("-")

    links = []
    keywords = []
    text = ""
    for ele in tag.contents:
        if isinstance(ele, NavigableString):
            text += str(ele)
        elif ele.name == "a":
            rel = ele.get("href")
            if rel.startswith("/wiki/"):
                links.append(f"https://en.wikipedia.org{rel}")
            text += ele.text
            if ele.text.count(" ") < 3:
                keywords.append(ele.text)
        elif ele.name == "br":
            submit(start_day, end_day, clean(text), links, _keywords(clean(text), keywords))
            keywords = []
            links = []
            text = ""
        else:
            text += ele.text
    if text.strip():
        submit(start_day, end_day, clean(text), links, _keywords(clean(text), keywords))


def _parse_event_tag(tag, submit):
    # singular events in dd, list of events in ul (search for li's)
    if not isinstance(tag, Tag):
        return None
    event_html = [*tag.find_all("dd"), *tag.find_all("li")]
    for tag in event_html:
        try:
            _parse_date_tag(tag, submit)
        except:
            # TODO: handle inline elements
            LOG.debug(f"malformed line: {tag.text}")


def _scrape_wiki_for_dates(html):
    scrape_time = datetime.datetime.now().isoformat()

    months = {month: 1 + i for i, month in enumerate([
        "January", "February", "March", "April", "May", "June", "July",
        "August", "September", "October", "November", "December"])}

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
            def submit(start, end, text, links, keywords):
                start = f"{year}-{months[month]:02d}-{int(start):02d}"
                events.append({
                    "id": hashlib.md5(text.encode()).hexdigest()[:12],
                    "startDate": start,
                    "endDate": f"{year}-{months[month]:02d}-{int(end):02d}" if end else start,
                    "text": text,
                    "links": links,
                    "createTime": scrape_time,
                    "keywords": keywords,
                    "imgdat": _query_img(text if not keywords else " ".join(keywords))[0]
                })

            _parse_event_tag(tag, submit)
    return events


def scrape_wiki():
    urls = [f"https://en.wikipedia.org/wiki/Timeline_of_World_War_II_({year})" for year in range(1939, 1945)]
    events = []
    for url in urls:
        events.extend(_scrape_wiki_for_dates(_get_doc(url)))
    return events


def sync_firestore(cert, events):
    """
    https://firebase.google.com/docs/firestore/quickstart?authuser=0#python
    """
    app = firebase_admin.initialize_app(credentials.Certificate(cert))
    db = firestore.client(app)

    if isinstance(events, str):
        with open(events, 'r') as f:
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


if __name__ == "__main__":
    import time
    t = time.time()
    sync_firestore("/home/marc/workspace/scrape-wiki/server/event-editor-firebase-adminsdk-vtwqr-3a052c189f.json", scrape_wiki())
    print(time.time() - t)