import aiohttp
import config
import random
from bs4 import BeautifulSoup


class SearchError(BaseException):
    def __init__(self, message: str):
        self.message = message


async def get_picture_by_themes(themes: list) -> str:
    themes_string = "-".join(themes)
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://ru.depositphotos.com/stock-photos/{themes_string}.html") as response:
            parser = BeautifulSoup(await response.text(), 'html.parser')
            url = ""
            try:
                url = parser.find("a", class_="file-container__link").find("img", class_="file-container__image").attrs["src"]
            finally:
                return url


async def get_random() -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://citaty.info/random") as response:
            parser = BeautifulSoup(await response.text(), 'html.parser')
            result = parser.find('div', class_="node__content")
            content_html = result.find('div', class_="field field-name-body field-type-text-with-summary field-label-hidden")
            themes_content = result.find(class_="node__topics")
            themes = None
            if themes_content is not None:
                themes = [i.text for i in themes_content.find_all('div', class_="field-item")]
            quote = {"content": content_html.text.strip(), "themes": themes}
            return quote


async def search(query: str) -> list:
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://citaty.info/search/site/{query}') as response:
            parser = BeautifulSoup(await response.text(), 'html.parser')
            results = parser.find_all('div', class_="node__content")
            if len(results) == 0:
                raise SearchError(f'{query}')
            quotes = []
            for i in results:
                content = i.find('div', class_="field field-name-body field-type-text-with-summary field-label-hidden").text.strip()
                themes_content = i.find(class_="node__topics")
                themes = None
                if themes_content is not None:
                    themes = [j.text for j in themes_content.find_all(class_="field-item")]
                quotes.append({"content": content, "themes": themes})
            return quotes


async def get_for_instagram() -> list:
    async with aiohttp.ClientSession() as session:
        async with session.get('https://allcitations.ru/tema/instagram') as response:
            parser = BeautifulSoup(await response.text(), 'html.parser')
            results = parser.find_all('div', class_="cittext")
            quotes = []
            for i in results:
                themes = i.find("cat_tags")
                if themes is not None:
                    themes = [i.text for i in themes.find_all("a")]
                quotes.append({"content": i.text, "themes":themes})
            return quotes




#async def get_random_present():
#    async with aiohttp.ClientSession() as session:
#        async with session.get(f'https://millionstatusov.ru/aforizmy/page-{random.randint(0, 578)}.html') as response:
#            parser = BeautifulSoup(await response.text(), 'html.parser')
#            quote = random.choice(parser.find_all('div', class_='cont_text'))
#            picture = quote.find('img', 'img-responsive img100')
#            if picture is not None:
#                picture = 'https://millionstatusov.ru' + picture.attrs['src']
#            result = {"content": str(quote.text).strip(), "picture": picture}
#            return result

