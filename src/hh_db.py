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
                            hh_company_id SERIAL NOT NULL,
                            employer_id VARCHAR,
                            employer_name VARCHAR(255) NOT NULL,
                            employer_url VARCHAR(255) NOT NULL,

                            CONSTRAINT pk_hh_companies_id PRIMARY KEY(employer_id)
                            )
                            """)
        conn.commit()
        conn.close()

    def create_table_hh_vacancies(self):
        conn = psycopg2.connect(**self.params, dbname=self.hh_dbname)
        with conn.cursor() as cur:
            cur.execute("""
                        CREATE TABLE hh_vacancies (
                            hh_vacancy_id SERIAL NOT NULL,
                            vac_id VARCHAR,
                            vac_name VARCHAR(255) NOT NULL,
                            vac_url VARCHAR(255) NOT NULL,
                            salary_from INT DEFAULT 0,
                            salary_to INT DEFAULT 0,
                            vac_area VARCHAR(255),
                            employer_id VARCHAR(255) NOT NULL,

                            CONSTRAINT pk_hh_vacancies_id PRIMARY KEY(vac_id),

                            CONSTRAINT fk_hh_vacancies_employer_id FOREIGN KEY(employer_id) 
                            REFERENCES hh_companies(employer_id) ON DELETE CASCADE
                            )
                            """)
        conn.commit()
        conn.close()
