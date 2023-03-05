from parsers.parsers import Parser
from dbs.dbs import DataBase, PostgresqlDB, SQLDataBase
from tqdm import tqdm


class WebSiteHandler:

    def __init__(self, parser: Parser, sql_db: PostgresqlDB):
        self.parser = parser
        self.db = sql_db
        self.parser_sub = parser.parser_name

    def get_urls_list(self, page_from: int = 1, page_to: int = 1) -> list:
        url_list = self.parser.get_all_last_flats_links(page_from=page_from, page_to=page_to)
        return url_list

    def build_flats_list(self, urls_list: list) -> list:
        obj_list = self.parser.enrich_links_to_flats(urls_list)
        return obj_list

    def save_to_db_with_staticstorage(self, obj_list: list, sql_db: SQLDataBase, static_db: DataBase):
        for item in tqdm(obj_list, desc=f"Adding flats to database: {self.db.name} / {obj_list[0].reference}"):
            if not sql_db.check_if_exists(item):
                sql_db.save_flat_to_db(item)
                static_db.save_flat_to_db(item)

    def save_to_db(self, obj_list: list):
        for item in obj_list:
            if not self.db.check_if_exists(item):
                self.db.save_flat_to_db(item)

    def run(self, page_from: int = 1, page_to: int = 1):
        links_list = self.get_urls_list(page_from, page_to)
        objs_list = self.build_flats_list(links_list)
        self.db.batch_save_flat_to_db(objs_list)



