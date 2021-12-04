import requests
from bs4 import BeautifulSoup
import pandas as pd


def get_all_pages(url):
    r = requests.get(url)
    pges = []

    if r.status_code == 200:
        soup: BeautifulSoup = BeautifulSoup(r.content, "html.parser")

        for page_a in soup.select("span > a"):
            pges.append(page_a.get('href'))

    return pges[-2].split('=')[-1]


def get_all_content(url):
    r = requests.get(url)

    links = []

    if r.status_code == 200:
        soup: BeautifulSoup = BeautifulSoup(r.content, "html.parser")

        for link in soup.find_all(attrs={"class": "entry-item-card entry-content"}):
            links.append(link.get('href'))

    return links


def get_content(url):
    r = requests.get(url)

    blockquote_text = None
    title = None
    keywords = None
    description = None
    publish_date = None
    id = None
    url_prop = None
    source = None
    lang = None
    type = None

    if r.status_code == 200:
        soup: BeautifulSoup = BeautifulSoup(r.content, "html.parser")

        title = soup.title.string

        blockquote = soup.find_all("blockquote")
        if blockquote:
            blockquote_text = blockquote[0].text

        meta = soup.find_all(attrs={"name": "keywords"})
        keywords = meta[0]['content']

        description_meta = soup.find_all(attrs={"name": "description"})
        description = description_meta[0]['content']

        publish_date_soup = soup.find_all(attrs={"class": "publish-date"})
        publish_date = publish_date_soup[0].string

        id_soup = soup.find_all(attrs={"property": "fb:app_id"})
        id = id_soup[0]['content']

        url_soup = soup.find_all(attrs={"property": "og:url"})
        url_prop = url_soup[0]['content']

        source_soup = soup.select("h1 > a")
        source = source_soup[0].string

        lang = soup.html['lang']

        type_soup = soup.find_all(attrs={"data-pin-nopin": True})
        if type_soup:
            if int(type_soup[0]['data-height']) <= 110:
                type_selc = soup.select("figure > figcaption")
                if type_selc:
                    type = type_selc[0].string
            else:
                type = type_soup[0]['data-image-id'].replace('.png', '')
        else:
            type_selc = soup.select("figure > figcaption")
            if type_selc:
                type = type_selc[0].string

    return [
        id,
        title,
        blockquote_text,
        keywords,
        description,
        publish_date,
        url_prop,
        source,
        type,
        lang
    ]


if __name__ == '__main__':
    # pages_links = get_content('https://www.aosfatos.org/noticias/nao-o-exercito-nao-esta-fiscalizando-o-senado-noticia-e-falsa/')
    # print(pages_links)
    filename = 'fake_news_v1.csv'

    URL = 'https://www.aosfatos.org/noticias/e-falso-que-policia-espancou-mulher-por-entrar-em-shopping-na-franca-sem' \
          '-passaporte-da-vacina/ '
    NET_URL = 'https://www.aosfatos.org/noticias/nas-redes/'
    BASE_URL = 'https://www.aosfatos.org'

    pages_links = []
    data = []

    max_pages = get_all_pages(NET_URL)

    for page in [x + 1 for x in range(int(max_pages))]:
        pages_links += get_all_content(f'{NET_URL}?page={page}')

    for link in pages_links:
        data.append(get_content(BASE_URL + link))

    df = pd.DataFrame(data, columns=[
            'id', 'Title', 'Text', 'Keywords', 'Description', 'Publish_date', 'URL', 'Source', 'type', 'Lang'
        ]
    )

    df.to_csv(filename, index=False, header=True, mode='a')
