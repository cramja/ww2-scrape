import logging
import re
from typing import List

import bs4
import click
from quart import Quart
from quart import jsonify
from quart import request
from requests_html import AsyncHTMLSession
from werkzeug.urls import url_encode

from wiki import sync_firestore as sync_firestore_

app = Quart(__name__)
logging.basicConfig()
LOG = logging.getLogger(__name__)


@app.cli.command("sync-firestore")
@click.argument("cert")
@click.argument("events_file")
def sync_firestore(cert, events_file):
    sync_firestore_(cert, events_file)


async def query_img(q) -> List[str]:
    with AsyncHTMLSession() as session:
        resp = await session.get(f"https://www.google.com/search?{url_encode({'q': q, 'tbm': 'isch', 'sclient': 'img'})}")
        await resp.html.arender()

        doc = bs4.BeautifulSoup(resp.html.html, 'html.parser')
        imgs = [
            tag.attrs["src"]
            for tag in doc.find_all(lambda r: r.name == "img"
                                              and "".join(r.attrs.get("class", "")).startswith("rg_")
                                              and r.attrs.get("src", "").startswith("data"))
        ]
        return imgs


@app.route("/images")
async def get_images():
    query = request.args['q']
    # TODO: advanced cleaning

    query = re.sub(r"\.,-!\?", " ", query)
    query = " ".join(list(filter(lambda x: len(x) > 1, query.split(" "))))

    return jsonify({'q': query, 'imgs': await query_img(query)})


if __name__ == "__main__":
    app.run()
