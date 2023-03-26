import requests
from bs4 import BeautifulSoup
from data import Flat
import re
from datetime import datetime
from tqdm import tqdm
from parsers.baseparser import Parser, log_parse_result
import logging
from typing import Optional


class RealtBS4Parser(Parser):
    def __init__(self):
        super().__init__()
        self.parser_name = "realt_by"

    def get_all_last_flats_links(self, page_from=1, page_to=1) -> list[str]:
        flat_links = []
        while page_from <= page_to:
            resp = requests.get(f'https://realt.by/sale/flats/?page={page_from}')

            html = BeautifulSoup(resp.content, 'html.parser')
            for a in tqdm(html.find_all('a', href=True, class_='teaser-title'),
                          desc=f'Getting links from page {page_from} ({self.parser_name})'):
                flat_links.append(a['href'])
            page_from += 1

        ready_links = list(filter(lambda el: 'object' in el, flat_links))
        return ready_links

    @staticmethod
    @log_parse_result
    def parse_title(*, html: Optional[BeautifulSoup] = None, context: Optional[dict] = None) -> str:
        title = html.find('h1', class_='order-1').text.strip()
        return title

    @staticmethod
    @log_parse_result
    def parse_price(*, html: Optional[BeautifulSoup] = None, context: Optional[dict] = None) -> int:
        raw_price = html.find('h2', class_='w-full')
        price = int(re.sub('[^0-9]', '', raw_price.text.strip()))
        return price

    @staticmethod
    @log_parse_result
    def parse_description(*, html: Optional[BeautifulSoup] = None, context: Optional[dict] = None) -> str:
        description = html.find('section', class_='bg-white').text.strip()
        return description

    @staticmethod
    @log_parse_result
    def parse_pubdate(*, html: Optional[BeautifulSoup] = None, context: Optional[dict] = None) -> datetime:
        pubdate = datetime.strptime(html.find('span', class_='mr-1.5').text.strip(), '%d.%m.%Y')
        return pubdate

    @staticmethod
    @log_parse_result
    def parse_areas(*, html: Optional[BeautifulSoup] = None, context: Optional[dict] = None) -> float:
        areas = float(context["Площадь общая"].split()[0])
        return areas

    @staticmethod
    @log_parse_result
    def parse_city(*, html: Optional[BeautifulSoup] = None, context: Optional[dict] = None) -> str:
        city = context["Населенный пункт"]
        return city

    @staticmethod
    @log_parse_result
    def parse_address(*, html: Optional[BeautifulSoup] = None, context: Optional[dict] = None) -> str:
        city = context["Улица"]
        return city

    @staticmethod
    @log_parse_result
    def parse_region(*, html: Optional[BeautifulSoup] = None, context: Optional[dict] = None) -> str:
        region = context["Район города"]
        return region

    @staticmethod
    @log_parse_result
    def parse_rooms(*, html: Optional[BeautifulSoup] = None, context: Optional[dict] = None) -> int:
        rooms = int(re.sub('[^0-9]', '', context["Количество комнат"]))
        return rooms

    @staticmethod
    @log_parse_result
    def parse_exyear(*, html: Optional[BeautifulSoup] = None, context: Optional[dict] = None) -> int:
        exyear = int(re.sub('[^0-9]', '', context["Количество комнат"]))
        return exyear

    @staticmethod
    @log_parse_result
    def parse_seller(*, html: Optional[BeautifulSoup] = None, context: Optional[dict] = None) -> str:
        agency_seller = html.find("a", attrs={"aria-label": "Ссылка на агентство"})
        contact_seller = html.find(class_=['md:w-1/2 lg:w-full lg:mt-4 md:mt-0 w-full mt-2'])
        owner_seller = html.find(class_=['w-full md:w-1/2 lg:w-full'])
        seller = None
        if agency_seller:
            seller = agency_seller.p.text
        elif contact_seller:
            seller = contact_seller.text.removesuffix('Контаткнное лицо')
        elif owner_seller:
            seller = owner_seller.text.removeprefix('Отдел продаж')
        else: raise AttributeError("custom error")
        return seller

    @staticmethod
    @log_parse_result
    def parse_photo_links(*, html: Optional[BeautifulSoup] = None, context: Optional[dict] = None) -> list[str]:
        images_tags = html.find_all('img', attrs={"data-nimg": "fill", "loading": "lazy"}, class_='blur-sm')
        photo_links = []
        for image in images_tags:
            photo_links.append(image['src'])
        return photo_links


    def enrich_links_to_flats(self, url_list: list[str]) -> list[Flat]:
        flats = []
        for link in tqdm(url_list, desc=f'Creating Flat objects from links ({self.parser_name})'):
            resp = requests.get(link)
            if resp.status_code != 200:
                logging.warning(f"{datetime.now}: got http response {resp.status_code} under {link}")
            html = BeautifulSoup(resp.content, 'html.parser')

            lst = html.find_all(class_="max-w-[282px]")
            dc = {item.text: item.next_sibling.text.strip() for item in lst}

            title = self.parse_title(html=html)
            price = self.parse_price(html=html)
            description = self.parse_description(html=html)
            pubdate = self.parse_pubdate(html=html)
            areas = self.parse_areas(context=dc)
            city = self.parse_city(context=dc)
            address = self.parse_address(context=dc)
            region = self.parse_region(context=dc)
            rooms = self.parse_rooms(context=dc)
            exyear = self.parse_exyear(context=dc)
            seller = self.parse_seller(html=html)
            photo_links = self.parse_photo_links(html=html)

            new_flat = self._create_new_flat_instance(title, price, description, pubdate, areas, city,address, region,
                                                      rooms, exyear, seller, photo_links, link)
            flats.append(new_flat)

        return flats


class GoHomeBS4Parser(Parser):
    def __init__(self):
        super().__init__()
        self.parser_name = "gohome_by"

    def get_all_last_flats_links(self, page_from=1, page_to=1) -> list[str]:
        flat_links = []
        while page_from <= page_to:
            resp = requests.get(f'https://gohome.by/sale/search/30?search[type]=1&search[map_latitude]=&search[map_longitude]=&'
                                f'search[map_zoom]=0&search[region]=1&search[area]=0&search[sq_all_from]=&search[sq_all_to]='
                                f'&search[cost_from]=&search[cost_to]=&search[with_photo]= {page_from}')

            html = BeautifulSoup(resp.content, 'html.parser')

            for a in tqdm(html.find_all('a', href=True, class_='name__link'),
                          desc=f'Getting links from page {page_from} ({self.parser_name})'):
                if a.next_element.text.strip()[0].isnumeric():
                    flat_links.append('https://gohome.by/' + a['href'])
            page_from += 1
        return flat_links

    @staticmethod
    @log_parse_result
    def parse_title(*, html: Optional[BeautifulSoup] = None, context: Optional[dict] = None) -> str:
        title = html.find("div", class_='left-side').text.strip()
        return title

    @staticmethod
    @log_parse_result
    def parse_price(*, html: Optional[BeautifulSoup] = None, context: Optional[dict] = None) -> int:
        price = int(re.sub('[^0-9]', '', html.find("div", class_='price big').text.strip()))
        return price

    @staticmethod
    @log_parse_result
    def parse_description(*, html: Optional[BeautifulSoup] = None, context: Optional[dict] = None) -> str:
        description = html.find('article').text
        return description

    @staticmethod
    @log_parse_result
    def parse_pubdate(*, html: Optional[BeautifulSoup] = None, context: Optional[dict] = None) -> datetime:
        pubdate = datetime.strptime(context["Дата обновления:"].strip(), '%d.%m.%Y')
        return pubdate

    @staticmethod
    @log_parse_result
    def parse_areas(*, html: Optional[BeautifulSoup] = None, context: Optional[dict] = None) -> float:
        areas = (float(context["Площадь общая:"].split()[0]))
        return areas

    @staticmethod
    @log_parse_result
    def parse_city(*, html: Optional[BeautifulSoup] = None, context: Optional[dict] = None) -> str:
        city = context['Населенный пункт:'].strip()
        return city

    @staticmethod
    @log_parse_result
    def parse_address(*, html: Optional[BeautifulSoup] = None, context: Optional[dict] = None) -> str:
        address = context['Улица, дом:'].strip()
        return address

    @staticmethod
    @log_parse_result
    def parse_region(*, html: Optional[BeautifulSoup] = None, context: Optional[dict] = None) -> str:
        region = context['Район:'].strip()
        return region

    @staticmethod
    @log_parse_result
    def parse_rooms(*, html: Optional[BeautifulSoup] = None, context: Optional[dict] = None) -> int:
        rooms = int(re.sub('[^0-9]', '', context['Комнат:']))
        return rooms

    @staticmethod
    @log_parse_result
    def parse_exyear(*, html: Optional[BeautifulSoup] = None, context: Optional[dict] = None) -> int:
        exyear = int(re.sub('[^0-9]', '', context['Год постройки:']))
        return exyear

    @staticmethod
    @log_parse_result
    def parse_seller(*, html: Optional[BeautifulSoup] = None, context: Optional[dict] = None) -> str:
        seller = list(html.find('div', class_='customize-svg-inline-icon login').parent.stripped_strings)[-1]
        return seller

    @staticmethod
    @log_parse_result
    def parse_photo_links(*, html: Optional[BeautifulSoup] = None, context: Optional[dict] = None) -> list[str]:
        images_tags = filter(lambda x: len(x.attrs['class']) == 1, html.find_all('div', class_="responsive-image"))
        photo_links = []
        for image in images_tags:
            photo_links.append('https://gohome.by' + image.next_element.next_element['data-zlazy'])
        return photo_links

    def enrich_links_to_flats(self, url_list: list[str]) -> list[Flat]:
        flats = []
        for link in tqdm(url_list, desc=f'Creating Flat objects from links ({self.parser_name})'):
            resp = requests.get(link)
            if resp.status_code != 200:
                logging.warning(f"{datetime.now}: got http response {resp.status_code} under {link}")
            html = BeautifulSoup(resp.content, 'html.parser')

            inf_lst = [list(x.stripped_strings) for x in html.find_all("li", class_="li-feature")]
            dc = {item[0]: item[1] for item in inf_lst if len(item) > 1}

            title = self.parse_title(html=html)
            price = self.parse_price(html=html)
            description = self.parse_description(html=html)
            pubdate = self.parse_pubdate(context=dc)
            areas = self.parse_areas(context=dc)
            city = self.parse_city(context=dc)
            address = self.parse_address(context=dc)
            region = self.parse_region(context=dc)
            rooms = self.parse_rooms(context=dc)
            exyear = self.parse_exyear(context=dc)
            seller = self.parse_seller(html=html)
            photo_links = self.parse_photo_links(html=html)

            new_flat = self._create_new_flat_instance(title, price, description, pubdate, areas, city, address, region,
                                                      rooms, exyear, seller, photo_links, link)
            flats.append(new_flat)

        return flats

if __name__ == "__main__":
    print('started')
    link = 'https://pbliga.com/'
    resp= requests.get(link)

    html = BeautifulSoup(resp.content, 'html.parser')
    print(type(html))
