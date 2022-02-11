import re
from typing import List

import bs4
from quart import Quart
from quart import jsonify
from quart import request
from requests_html import AsyncHTMLSession
from werkzeug.urls import url_encode

app = Quart(__name__)


async def query_img(q) -> List[str]:
    session = AsyncHTMLSession()
    resp = await session.get(f"https://www.google.com/search?{url_encode({'q': q, 'tbm': 'isch', 'sclient': 'img'})}")
    await resp.html.arender()

    doc = bs4.BeautifulSoup(resp.html.html, 'html.parser')
    imgs = [
        tag.attrs["src"]
        for tag in doc.find_all(lambda r: r.name == "img"
                                          and "".join(r.attrs.get("class", "")).startswith("rg_")
                                          and r.attrs.get("src", "").startswith("data"))
    ]
    await session.close()
    return imgs


@app.route("/images")
async def get_images():
    query = request.args['q']
    # TODO: advanced cleaning
    query = re.sub(r"\.,-!\?", " ", query)
    query = " ".join(list(filter(lambda x: len(x) > 1, query.split(" "))))
    app.logger.info(f"query={query}")
    return jsonify({'q': query, 'imgs': await query_img(query)})


if __name__ == "__main__":
    app.run()
