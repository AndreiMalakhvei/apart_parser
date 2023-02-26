import requests
from bs4 import BeautifulSoup
from data import Flat
import re
from datetime import datetime
import hashlib
from databases import PostgreDB
from tqdm import tqdm

from parsers.baseparser import Parser


class RealtByParser(Parser):
    def __init__(self):
        super().__init__()
        self.parser_name = "bs4 for realt.by"

    def get_all_last_flats_links(self, page_from=0, page_to=1):
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

    def enrich_links_to_flats(self, url_list):
        flats = []
        for link in tqdm(url_list[:5], desc=f'Creating Flat objects from links ({self.parser_name})'):
            resp = requests.get(link)
            html = BeautifulSoup(resp.content, 'html.parser')
            try:
                title = html.find('h1', class_='order-1').text.strip()
            except AttributeError as e:
                title = 'NO TITLE PROVIDED'
            raw_price = html.find('h2', class_='w-full')
            if raw_price is not None:
                price = int(re.sub('[^0-9]', '', raw_price.text.strip()))
            else:
                price = 0
            description = html.find('section', class_='bg-white').text.strip()
            try:
                pubdate = datetime.strptime(html.find('span', class_='mr-1.5').text.strip(), '%d.%m.%Y')
            except Exception as e:
                pubdate = datetime.now()

            agency_seller = html.find("a", attrs={"aria-label": "Ссылка на агентство"})
            contact_seller = html.find(class_=['md:w-1/2 lg:w-full lg:mt-4 md:mt-0 w-full mt-2'])
            owner_seller = html.find(class_=['w-full md:w-1/2 lg:w-full'])

            if agency_seller:
                seller = agency_seller.p.text
            elif contact_seller:
                seller = contact_seller.text.removesuffix('Контаткнное лицо')
            elif owner_seller:
                seller = owner_seller.text.removeprefix('Отдел продаж')
            else:
                seller = "NONE??!!"

            lst = html.find_all(class_="max-w-[282px]")
            dc = {item.text: item.next_sibling.text.strip() for item in lst}
            areas = (float(dc["Площадь общая"].split()[0]) if dc.get("Площадь общая", 0) else 0)
            city = dc.get("Населенный пункт", "")
            address = dc.get("Улица", "") + " " + dc.get("Номер дома", "")
            region = dc.get("Район города", "")
            rooms = int(re.sub('[^0-9]', '', dc.get("Количество комнат", 0)))
            exyear = int(re.sub('[^0-9]', '', dc.get("Год постройки", 0)))

            images_tags = html.find_all('img', class_="blur-sm scale-105", alt="Изображение слайдера",
                                         attrs={"loading": "lazy"})
            images_list = []
            for image in images_tags:
                images_list.append(image['src'])

            new_flat = (Flat(
                title=title,
                price=price,
                description=description,
                pubdate=pubdate,
                areas=areas,
                city=city,
                address=address,
                region=region,
                rooms=rooms,
                exyear=exyear,
                seller=seller
                ))
            objhash = hashlib.md5(bytearray(str(new_flat.__dict__), 'utf-8'))
            hd = objhash.hexdigest()
            new_flat.objhash = str(hd)
            new_flat.images_list = images_list
            new_flat.link = link
            new_flat.reference = self.parser_name
            flats.append(new_flat)

        return flats


class GoHomeParser(Parser):
    def __init__(self):
        super().__init__()
        self.parser_name = "bs4 for gohome.by"

    def get_all_last_flats_links(self, page_from=0, page_to=1):
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

    def enrich_links_to_flats(self, url_list):
        flats = []
        for link in tqdm(url_list[:5], desc=f'Creating Flat objects from links ({self.parser_name})'):
            resp = requests.get(link)
            html = BeautifulSoup(resp.content, 'html.parser')

            title = html.find("div", class_='left-side').text.strip()
            try:
                price = int(re.sub('[^0-9]', '', html.find("div", class_='price big').text.strip()))
            except (TypeError, ValueError):
                price = 0

            description = html.find('article').text

            inf_lst = [list(x.stripped_strings) for x in html.find_all("li", class_="li-feature")]
            dc = {item[0]: item[1] for item in inf_lst if len(item) > 1}



            areas = (float(dc["Площадь общая:"].split()[0]) if dc.get("Площадь общая:", 0) else 0)
            try:
                rooms = int(re.sub('[^0-9]', '', dc['Комнат:']))
            except Exception as e:
                rooms = 0
            try:
                pubdate = datetime.strptime(dc["Дата обновления:"].strip(), '%d.%m.%Y')
            except Exception as e:
                pubdate = datetime.now()

            city = dc.get('Населенный пункт:', "").strip()
            address  = dc.get('Улица, дом:', "").strip()
            region = dc.get('Район:', "").strip()

            try:
                exyear = int(re.sub('[^0-9]', '', dc['Год постройки:']))
            except Exception as e:
                exyear = 0

            seller = list(html.find('div', class_='customize-svg-inline-icon login').parent.stripped_strings)[-1]

            images_tags = filter(lambda x: len(x.attrs['class']) == 1, html.find_all('div', class_="responsive-image"))
            images_list = []

            for image in images_tags:
                images_list.append('https://gohome.by' + image.next_element.next_element['data-zlazy'])

            new_flat = (Flat(
                title=title,
                price=price,
                description=description,
                pubdate=pubdate,
                areas=areas,
                city=city,
                address=address,
                region=region,
                rooms=rooms,
                exyear=exyear,
                seller=seller
            ))
            objhash = hashlib.md5(bytearray(str(new_flat.__dict__), 'utf-8'))
            hd = objhash.hexdigest()
            new_flat.objhash = str(hd)
            new_flat.images_list = images_list
            new_flat.link = link
            new_flat.reference = self.parser_name
            flats.append(new_flat)

        return flats

if __name__ == "__main__":
    pars = GoHomeParser()
    pars.get_all_last_flats_links(page_to=0)
    # for i in pars.ready_links:
    #     print(i)
    flatsl = pars.enrich_links_to_flats()
    db = PostgreDB()
    db.create_flats_table()
    for i in tqdm(flatsl, desc='Adding records to DB'):
        db.insert_flat(i)