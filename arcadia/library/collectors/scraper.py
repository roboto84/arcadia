import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from pyuseragents import random as random_useragent
from bs4 import BeautifulSoup


class Scraper:
    @staticmethod
    def get_random_agent():
        random_agent: str = random_useragent()
        while 'Mobile' in random_agent:
            random_agent: str = random_useragent()
        return random_agent

    @staticmethod
    def generate_headers() -> dict:
        return {
            'user-agent': Scraper.get_random_agent(),
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-dest': 'document',
            'accept-language': 'en-US',
        }

    @staticmethod
    def format_url(url: str) -> str:
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'https://' + url
        return url

    @staticmethod
    def get_url_title(beautiful_soup: BeautifulSoup) -> dict:
        try:
            title_length = 60
            title = beautiful_soup.find('meta', property='og:title')
            if title:
                try:
                    content = title.attrs['content']
                except Exception:
                    content = None

                if content is not None:
                    return {
                        'type': 'OpenGraph',
                        'content': title['content'][:title_length]
                    }

            title = beautiful_soup.find('title')
            if title and title.text:
                return {
                    'type': 'Meta',
                    'content': title.text[:title_length].strip()
                }

            return {}
        except Exception as e:
            print(f'Exception was thrown', e)

    @staticmethod
    def get_url_description(beautiful_soup: BeautifulSoup) -> dict:
        try:
            description_length = 150
            description = beautiful_soup.find('meta', property='og:description')
            if description:
                try:
                    content = description.attrs['content']
                except Exception:
                    content = None

                if content is not None:
                    return {
                        'type': 'OpenGraph',
                        'content': description['content'][:description_length]
                    }

            description = beautiful_soup.find('meta', attrs={'name': 'description'})
            if description:
                try:
                    content = description.attrs['content']
                except Exception:
                    content = None

                if content is not None:
                    return {
                        'type': 'Meta',
                        'content': description['content'][:description_length]
                    }

            return {}
        except Exception as e:
            print(f'Exception was thrown', e)

    @staticmethod
    def get_url_image(beautiful_soup: BeautifulSoup) -> dict:
        try:
            max_image_size = 200
            image = beautiful_soup.find('meta', property='og:image')
            if image:
                try:
                    content = image.attrs['content']
                except Exception:
                    content = None

                if content is not None:
                    return {
                        'type': 'OpenGraph',
                        'href': image['content']
                    }

            images = beautiful_soup.find_all('link', rel='icon')
            largest_icon_href = ''
            largest_icon_size = 0
            largest_size = 0
            if images:
                for image in images:
                    try:
                        sizes = image.attrs['sizes']
                    except Exception:
                        sizes = None

                    if sizes is not None:
                        icons_size = int(image['sizes'][:image['sizes'].index('x')])
                        if max_image_size > icons_size > largest_size:
                            largest_size = icons_size
                            largest_icon_size = image['sizes']
                            largest_icon_href = image['href']
                    elif largest_icon_href == '':
                        largest_icon_size = ''
                        largest_icon_href = images[0]['href']

                return {
                    'type': 'Meta',
                    'size': largest_icon_size,
                    'href': largest_icon_href
                }

            return {}
        except Exception as e:
            print(f'Exception was thrown', e)

    @staticmethod
    def get_url_meta(url: str) -> dict:
        try:
            session = requests.Session()
            retry = Retry(total=3, connect=3, backoff_factor=0.5)
            adapter = HTTPAdapter(max_retries=retry)
            session.mount('http://', adapter)
            session.mount('https://', adapter)
            response = session.request(
                'GET', Scraper.format_url(url),
                headers=Scraper.generate_headers(),
                verify=True
            )

            if response:
                beautiful_soup: BeautifulSoup = BeautifulSoup(response.content, 'html.parser')
                package: dict = {
                    'title': Scraper.get_url_title(beautiful_soup),
                    'description': Scraper.get_url_description(beautiful_soup),
                    'image': Scraper.get_url_image(beautiful_soup)
                }
                return package
            else:
                print(f'API Status code: {response.status_code}')
        except TypeError as type_error:
            print(f'Received TypeError: {type_error}')
        except Exception as e:
            print(f'Exception was thrown', e)
        return {}
