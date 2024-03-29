import hashlib
from abc import ABC, abstractmethod
import logging
import inspect
from datetime import datetime
from bs4 import BeautifulSoup
from data import Flat
from typing import Optional
import traceback

def log_parse_result(func):
    def inner_handler(*args, **kwargs):
        try:
            res = func(*args, **kwargs)
        except Exception as e:
            logging.warning("Parse warning: unable to get %s at %s. Traceback: %s", func.__qualname__,
                            kwargs['link'], traceback.format_exc())

            res = None
            try:
                return_type = inspect.get_annotations(func)['return'].__name__
            except KeyError:
                return_type = None
            if return_type == 'str':
                res = 'Unable to retrieve data'
            elif return_type in ('int', 'float'):
                res = 0
            elif return_type == 'datetime':
                res = datetime.now()
            elif return_type == 'list':
                res = []
        return res
    return inner_handler


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


    @staticmethod
    @abstractmethod
    def parse_title(*, link: str, html: Optional[BeautifulSoup] = None, context: Optional[dict] = None) -> str:
        pass

    @staticmethod
    @abstractmethod
    def parse_price(*, link: str, html: Optional[BeautifulSoup] = None, context: Optional[dict] = None) -> int:
        pass

    @staticmethod
    @abstractmethod
    def parse_description(*, link: str, html: Optional[BeautifulSoup] = None, context: Optional[dict] = None) -> str:
        pass

    @staticmethod
    @abstractmethod
    def parse_pubdate(*, link: str, html: Optional[BeautifulSoup] = None, context: Optional[dict] = None) -> datetime:
        pass

    @staticmethod
    @abstractmethod
    def parse_areas(*, link: str, html: Optional[BeautifulSoup] = None, context: Optional[dict] = None) -> float:
        pass

    @staticmethod
    @abstractmethod
    def parse_city(*, link: str, html: Optional[BeautifulSoup] = None, context: Optional[dict] = None) -> str:
        pass

    @staticmethod
    @abstractmethod
    def parse_address(*, link: str, html: Optional[BeautifulSoup] = None, context: Optional[dict] = None) -> str:
        pass

    @staticmethod
    @abstractmethod
    def parse_region(*, link: str, html: Optional[BeautifulSoup] = None, context: Optional[dict] = None) -> str:
        pass

    @staticmethod
    @abstractmethod
    def parse_rooms(*, link: str, html: Optional[BeautifulSoup] = None, context: Optional[dict] = None) -> int:
        pass

    @staticmethod
    @abstractmethod
    def parse_exyear(*, link: str, html: Optional[BeautifulSoup] = None, context: Optional[dict] = None) -> int:
        pass

    @staticmethod
    @abstractmethod
    def parse_seller(*, link: str, html: Optional[BeautifulSoup] = None, context: Optional[dict] = None) -> str:
        pass

    @staticmethod
    @abstractmethod
    def parse_photo_links(*, link: str, html: Optional[BeautifulSoup] = None, context: Optional[dict] = None)\
            -> list[str]:
        pass
