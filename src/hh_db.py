import psycopg2

from config import config
from src.logging_config import LoggingConfigClassMixin


class HeadHunterDataBase(LoggingConfigClassMixin):
    """Класс для создания базы данных с компаниями и вакансиями сайта HeadHunter.ru"""
    def __init__(self) -> None:
        super().__init__()
        self.base_dbname = "postgres"
        self.hh_dbname = "headhunter_vacancies"
        self.params = self.get_params()
        self.logger = self.configure()

    @staticmethod
    def get_params() -> dict:
        return config()

    def create_database(self) -> None:
        """Создает базу данных и таблицы для сохранения данных о каналах и видео"""
        conn = psycopg2.connect(**self.params, dbname=self.base_dbname)
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.hh_dbname,))
            is_exists = cur.fetchone()
            if is_exists:
                cur.execute(f"DROP DATABASE {self.hh_dbname}")

        cur.execute(f"CREATE DATABASE {self.hh_dbname}")
        conn.close()

    def create_table_hh_companies(self):
        conn = psycopg2.connect(**self.params, dbname=self.hh_dbname)
        with conn.cursor() as cur:
            cur.execute("""
                        CREATE TABLE hh_companies (
                            hh_companies_id SERIAL PRIMARY KEY,
                            employer_id VARCHAR NOT NULL FOREIGN KEY REFERENCES,
                            name VARCHAR(255) NOT NULL,
                            url VARCHAR(255) NOT NULL
                            )
                            """)
        conn.commit()
        conn.close()

    def create_table_hh_vacancies(self):
        conn = psycopg2.connect(**self.params, dbname=self.hh_dbname)
        with conn.cursor() as cur:
            cur.execute("""
                        CREATE TABLE hh_vacancies (
                            hh_vacancies_id SERIAL PRIMARY KEY,
                            vac_id VARCHAR NOT NULL,
                            name VARCHAR(255) NOT NULL,
                            url VARCHAR(255) NOT NULL,
                            salary_from,
                            salary_to,
                            employer_name FOREIGN KEY REFERENCES,
                            area VARCHAR(255)
                            )
                            """)
        conn.commit()
        conn.close()
