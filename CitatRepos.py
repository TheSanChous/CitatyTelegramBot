import aiohttp
import config
import random
from bs4 import BeautifulSoup


class SearchError(BaseException):
    def __init__(self, message: str):
        self.message = message


async def get_random() -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get('https://citaty.info/random') as response:
            parser = BeautifulSoup(await response.text(), 'html.parser')
            return parser.find(class_="field field-name-body field-type-text-with-summary field-label-hidden").text


async def get_random_present():
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://millionstatusov.ru/aforizmy/page-{random.randint(0, 578)}.html') as response:
            parser = BeautifulSoup(await response.text(), 'html.parser')
            citat = random.choice(parser.find_all('div', class_='cont_text'))
            picture = citat.find('img', 'img-responsive img100')
            if picture != None:
               picture = 'https://millionstatusov.ru' + picture.attrs['src']
            result = {'text': citat.text, 'picture': picture}
            return result


async def search(query: str) -> list:
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://citaty.info/search/site/{query}') as response:
            parser = BeautifulSoup(await response.text(), 'html.parser')
            results = parser.find_all('div',
                                      class_="field field-name-body field-type-text-with-summary field-label-hidden")
            if len(results) == 0:
                raise SearchError(f'{query}')
            citats = [i.text for i in results]
            return citats
