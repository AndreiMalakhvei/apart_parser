from parsers.parsers import Parser
from dbs.dbs import DataBase, SQLDataBase
from tqdm import tqdm


class WebSiteHandler:

    def __init__(self):
        self.url_list = []
        self.obj_list = []

    def get_urls_list(self, parser: Parser, page_from: int = 1, page_to: int = 1) -> list:
        self.url_list = parser.get_all_last_flats_links(page_from=page_from, page_to=page_to)
        return self.url_list

    def build_flats_list(self, parser: Parser, urls_list: list) -> list:
        self.obj_list = parser.enrich_links_to_flats(urls_list)
        return self.obj_list

    def save_to_db(self, obj_list: list, sql_db: SQLDataBase, static_db: DataBase):
        for item in tqdm(obj_list, desc=f"Adding flats to database: {sql_db.name} / {obj_list[0].reference}"):
            if not sql_db.check_if_exists(item):
                sql_db.save_flat_to_db(item)
                static_db.save_flat_to_db(item)

    def save_to_db_no_firestorage(self, obj_list: list, sql_db: SQLDataBase):
        for item in obj_list:
            if not sql_db.check_if_exists(item):
                sql_db.save_flat_to_db(item)



