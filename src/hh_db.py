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
        """Создает базу данных для хранения данных о компаниях и вакансиях сайта HeadHunter.ru"""
        with psycopg2.connect(**self.params, dbname=self.base_dbname) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.hh_dbname,))
                is_exists = cur.fetchone()
                if is_exists:
                    cur.execute(f"DROP DATABASE {self.hh_dbname}")
                cur.execute(f"CREATE DATABASE {self.hh_dbname}")

    def create_table_hh_companies(self) -> None:
        """Создает таблицу для хранения данных о компаниях сайта HeadHunter.ru"""
        with psycopg2.connect(**self.params, dbname=self.hh_dbname) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                CREATE TABLE hh_companies (
                    company_id SERIAL NOT NULL,
                    hh_employer_id VARCHAR NOT NULL UNIQUE,
                    employer_name VARCHAR(255) NOT NULL,
                    employer_url VARCHAR(255) NOT NULL,

                    CONSTRAINT pk_hh_companies_id PRIMARY KEY(company_id)
                    )
                """)

    def create_table_hh_vacancies(self) -> None:
        """Создает таблицу для хранения данных о вакансиях сайта HeadHunter.ru"""
        with psycopg2.connect(**self.params, dbname=self.hh_dbname) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                CREATE TABLE hh_vacancies (
                    vacancy_id SERIAL NOT NULL,
                    hh_vac_id VARCHAR NOT NULL UNIQUE,
                    vac_name VARCHAR(255) NOT NULL,
                    vac_url VARCHAR(255) NOT NULL,
                    salary_from INT DEFAULT 0,
                    salary_to INT DEFAULT 0,
                    vac_area VARCHAR(255),
                    company_id INT NOT NULL,

                    CONSTRAINT pk_hh_vacancies_id PRIMARY KEY(vacancy_id),

                    CONSTRAINT fk_hh_vacancies_company_id FOREIGN KEY(company_id) 
                    REFERENCES hh_companies(company_id) ON DELETE CASCADE
                    )
                """)
