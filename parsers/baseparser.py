import hashlib
from abc import ABC, abstractmethod
from datetime import datetime

from data import Flat


class Parser(ABC):

    def __init__(self):
        self.parser_name = "PARSER NAME"

    @abstractmethod
    def get_all_last_flats_links(self, page_from: int = 0, page_to: int = 1) -> list[str]:
        pass

    @abstractmethod
    def enrich_links_to_flats(self, urls_list: list[str]) -> list[Flat]:
        pass

    def _create_new_flat_instance(self, title: str, price: int, description: str, pubdate: datetime, areas: float,
                                  city: str, address: str, region: str, rooms: int, exyear: int,
                                  seller: str, photo_links: list[str], link: str) -> Flat:
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
        new_flat.photo_links = photo_links
        new_flat.photo_qty = len(photo_links)
        new_flat.link = link
        new_flat.reference = self.parser_name
        return new_flat
