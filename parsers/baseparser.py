from abc import ABC, abstractmethod


class Parser(ABC):

    # def __init__(self):
    #     self.ready_links = []
    #     self.flats = []


    @abstractmethod
    def get_all_last_flats_links(self, page_from: int=0, page_to: int=1) -> list:
        pass

    @abstractmethod
    def enrich_links_to_flats(self, urls_list) -> list:
        pass
