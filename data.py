class Flat:
    def __init__(self, link=None, reference=None, price=None, title=None, description=None, pubdate=None,
                 areas=None, city=None, address=None, region=None, rooms=None, exyear=None, objhash=None,
                 seller=None, photo_links=None, photo_qty=None):
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

