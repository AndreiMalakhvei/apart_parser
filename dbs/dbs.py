from abc import ABC, abstractmethod
import firebase_admin
from firebase_admin import credentials, storage
from data import Flat
import requests
import psycopg2


class DataBase(ABC):
    @abstractmethod
    def save_flat_to_db(self, flat: Flat):
        pass


class SQLDataBase(DataBase):

    @abstractmethod
    def check_if_exists(self, flat: Flat):
        pass


class FireStorage(DataBase):

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(FireStorage, cls).__new__(cls)
            cls.instance.create_connection_to_db()
            cls.instance.name = "FireStorage"
        return cls.instance

    def save_flat_to_db(self, flat):
        if flat.images_list:
            for num, image in enumerate(flat.images_list):
                fileName = f"{flat.objhash}/{num}.jpg"
                img_data = requests.get(image).content
                blob = self.bucket.blob(fileName)
                blob.upload_from_string(img_data)

    def create_connection_to_db(self):
        self.cred = credentials.Certificate("dbs/realt-255b2-firebase-adminsdk-8e4p8-fd37fc570b.json")
        if not firebase_admin._apps:
            firebase_admin.initialize_app(self.cred, {'storageBucket': 'realt-255b2.appspot.com'})
        self.bucket = storage.bucket()


class PostgresqlDB(SQLDataBase):

    DBNAME = 'appartdb'
    USER = 'postgres'
    PASSWORD = 'admin'
    HOST = '127.0.0.1'

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(PostgresqlDB, cls).__new__(cls)
            cls.instance.name = "PostgreSQL"
            cls.instance.create_flats_table()
        return cls.instance

    def create_flats_table(self):
        with psycopg2.connect(dbname=PostgresqlDB.DBNAME, user=PostgresqlDB.USER, password=PostgresqlDB.PASSWORD,
                              host=PostgresqlDB.HOST) as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS flats(
                        id serial PRIMARY KEY,
                    link CHARACTER VARYING(300) UNIQUE NOT NULL,
                    reference CHARACTER VARYING(30),
                    price INTEGER,
                    title CHARACTER VARYING(1000),                        
                    pubdate TIMESTAMP WITH TIME ZONE,
                    areas NUMERIC(7, 2),
                    city CHARACTER VARYING(30),
                    address CHARACTER VARYING(100),
                    region CHARACTER VARYING(30),
                    rooms INTEGER,
                    exyear INTEGER,
                    seller CHARACTER VARYING(100),
                    is_tg_posted BOOLEAN DEFAULT FALSE,
                    is_archived BOOLEAN DEFAULT FALSE,
                    objhash CHARACTER VARYING(50) UNIQUE,
                    photo_qty INTEGER,
                    photo_links  TEXT,
                    description TEXT
                    
                        )''')

    def check_if_exists(self, flat: Flat):
        with psycopg2.connect(dbname=PostgresqlDB.DBNAME, user=PostgresqlDB.USER, password=PostgresqlDB.PASSWORD,
                              host=PostgresqlDB.HOST) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM flats WHERE city = %s AND address = %s AND seller = %s AND areas = %s AND rooms = %s",
                    (flat.city, flat.address, flat.seller, flat.areas, flat.rooms))
                qryres = cur.fetchall()
                if qryres:
                    return True
        return False


    def save_flat_to_db(self, flat):
        with psycopg2.connect(dbname=PostgresqlDB.DBNAME, user=PostgresqlDB.USER, password=PostgresqlDB.PASSWORD,
                              host=PostgresqlDB.HOST) as conn:
            with conn.cursor() as cur:
                cur.execute('''
                        INSERT INTO flats (link, reference, price, title, description, pubdate,areas,city,address,region,rooms,
                        exyear,seller, objhash, photo_links, photo_qty) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
                        ON CONFLICT (link) DO UPDATE 
                        SET 
                        link = EXCLUDED.link, 
                        price = EXCLUDED.price, 
                        title = EXCLUDED.title, 
                        description = EXCLUDED.description, 
                        pubdate = EXCLUDED.pubdate,
                        areas = EXCLUDED.areas,
                        city = EXCLUDED.city,
                        address = EXCLUDED.address,
                        region = EXCLUDED.region,
                        rooms = EXCLUDED.rooms,
                        exyear = EXCLUDED.exyear,
                        seller=EXCLUDED.seller,
                        objhash=EXCLUDED.objhash,
                        photo_links=EXCLUDED.photo_links                 
                         ''',
                            (flat.link, flat.reference, flat.price, flat.title, flat.description, flat.pubdate,
                             flat.areas, flat.city, flat.address, flat.region, flat.rooms, flat.exyear,
                             flat.seller, flat.objhash, ','.join(flat.photo_links), flat.photo_qty)
                            )
    @staticmethod
    def get_all_not_posted_flats(parser_types):
        with psycopg2.connect(dbname=PostgresqlDB.DBNAME, user=PostgresqlDB.USER, password=PostgresqlDB.PASSWORD,
                              host=PostgresqlDB.HOST) as conn:
            with conn.cursor() as cur:
                cur.execute('''
                        SELECT link, reference, price, title, description, pubdate, photo_links, id FROM flats
                        WHERE (is_tg_posted = false or is_tg_posted IS NULL) 
                        and reference IN %(parser_types)s
                     ''',
                            {'parser_types': tuple(parser_types)}
                            )
                return cur.fetchall()

    @staticmethod
    def update_is_posted_state(ids):
        with psycopg2.connect(dbname=PostgresqlDB.DBNAME, user=PostgresqlDB.USER, password=PostgresqlDB.PASSWORD,
                              host=PostgresqlDB.HOST) as conn:
            with conn.cursor() as cur:
                cur.execute('''
                        UPDATE flats SET
                        is_tg_posted = true
                        WHERE id = ANY(%s)
                     ''',
                            [ids, ]
                            )