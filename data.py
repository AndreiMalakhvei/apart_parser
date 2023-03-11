from datetime import datetime
from typing import Optional


class Flat:
    def __init__(self, link: Optional[str] = None, reference: Optional[str] = None, price: Optional[int] = None,
                 title: Optional[str] = None, description: Optional[str] = None, pubdate: Optional[datetime] = None,
                 areas: Optional[float] = None, city: Optional[str] = None, address: Optional[str] = None,
                 region: Optional[str] = None, rooms: Optional[int] = None, exyear: Optional[str] = None,
                 objhash: Optional[str] = None, seller: Optional[str] = None, photo_links: Optional[list[str]] = None,
                 photo_qty: Optional[int] = None):
        self.link = link
        self.reference = reference
        self.price = price
        self.title = title
        self.description = description
        self.pubdate = pubdate
        self.areas = areas
        self.city = city
        self.address = address
        self.region = region
        self.rooms = rooms
        self.exyear = exyear
        self.objhash = objhash
        self.seller = seller
        self.photo_links = photo_links
        self.photo_qty = photo_qty
        self.price_m = None
        if self.areas and self.price:
            self.price_m = self.price / self.areas
