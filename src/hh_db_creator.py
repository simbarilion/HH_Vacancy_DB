from typing import Optional

import psycopg2

from config import config
from src.logging_config import LoggingConfigClassMixin


class HeadHunterDataBase(LoggingConfigClassMixin):
    """Класс для создания базы данных с компаниями и вакансиями сайта HeadHunter.ru"""
    def __init__(self, dbname: Optional[str] = "headhunter_vacancies") -> None:
        """Конструктор класса"""
        super().__init__()
        self._base_dbname = "postgres"
        self._hh_dbname = dbname
        self._params = self._get_params()
        self.logger = self.configure()

    def get_hh_dbname(self) -> str:
        return self._hh_dbname

    def create_database(self) -> None:
        """Создает базу данных для хранения данных о компаниях и вакансиях сайта HeadHunter.ru"""
        with psycopg2.connect(**self._params, dbname=self._base_dbname) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self._hh_dbname,))
                is_exists = cur.fetchone()
                if is_exists:
                    cur.execute(f"DROP DATABASE {self._hh_dbname}")
                    self.logger.info(f"База данных {self._hh_dbname} удалена")
                cur.execute(f"CREATE DATABASE {self._hh_dbname}")
                self.logger.info(f"База данных {self._hh_dbname} создана")

    def create_table_hh_companies(self) -> None:
        """Создает таблицу для хранения данных о компаниях сайта HeadHunter.ru"""
        try:
            with psycopg2.connect(**self._params, dbname=self._hh_dbname) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                    CREATE TABLE hh_companies (
                        company_id SERIAL NOT NULL,
                        hh_employer_id VARCHAR NOT NULL UNIQUE,
                        employer_name VARCHAR(255) NOT NULL,
                        employer_url VARCHAR(255) NOT NULL,

                        CONSTRAINT pk_hh_companies_id PRIMARY KEY(company_id)
                        );
                    """)
            self.logger.info("Tаблица hh_companies успешно создана")
        except psycopg2.Error as e:
            self.logger.error(f"Ошибка при создании таблицы hh_companies: {e}")

    def create_table_hh_vacancies(self) -> None:
        """Создает таблицу для хранения данных о вакансиях компаний сайта HeadHunter.ru"""
        try:
            with psycopg2.connect(**self._params, dbname=self._hh_dbname) as conn:
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
                        );
                    """)
            self.logger.info("Tаблица hh_vacancies успешно создана")
        except psycopg2.Error as e:
            self.logger.error(f"Ошибка при создании таблицы hh_vacancies: {e}")

    def save_data_to_table_hh_companies(self, employers: list[dict]) -> None:
        """Сохранение данных о компаниях сайта HeadHunter.ru в базу данных"""
        try:
            with psycopg2.connect(**self._params, dbname=self._hh_dbname) as conn:
                with conn.cursor() as cur:
                    for emp in employers:
                        cur.execute(
                            """
                            INSERT INTO hh_companies (hh_employer_id, employer_name, employer_url)
                            VALUES (%s, %s, %s)
                            RETURNING company_id;
                            """,
                            (emp.get('employer_id'), emp.get('name'), emp.get('url'))
                        )

                    cur.execute("SELECT COUNT(*) FROM hh_companies")
                    amount = cur.fetchone()[0]
            self.logger.info(f"В таблицу hh_companies добавлено {amount} вакансий")
        except psycopg2.Error as e:
            self.logger.error(f"Ошибка при добавлении данных в таблицу hh_companies: {e}")

    def save_data_to_table_hh_vacancies(self, employers_vacancies: list[dict]) -> None:
        """Сохранение данных о вакансиях компаний сайта HeadHunter.ru в базу данных"""
        try:
            with psycopg2.connect(**self._params, dbname=self._hh_dbname) as conn:
                with conn.cursor() as cur:
                    for emp_vacs in employers_vacancies:
                        for hh_employer_id, vacancies in emp_vacs.items():
                            cur.execute("SELECT company_id FROM hh_companies WHERE hh_employer_id = %s",
                                        (hh_employer_id,))
                            company = cur.fetchone()
                            company_id = company[0]
                            for vac in vacancies:
                                cur.execute(
                                    """
                                    INSERT INTO hh_vacancies 
                                    (hh_vac_id, vac_name, vac_url, company_id, vac_area, salary_from, salary_to)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                                    RETURNING vacancy_id;
                                    """,
                                    (vac.get('vac_id'),
                                     vac.get('name'),
                                     vac.get('url'),
                                     company_id,
                                     vac.get('area'),
                                     vac.get('salary_from'),
                                     vac.get('salary_to')
                                     )
                                )

                    cur.execute("SELECT COUNT(*) FROM hh_vacancies")
                    amount = cur.fetchone()[0]
            self.logger.info(f"В таблицу hh_vacancies добавлено {amount} вакансий")
        except psycopg2.Error as e:
            self.logger.error(f"Ошибка при добавлении данных в таблицу hh_vacancies: {e}")

    def add_avg_salary_to_hh_vacancies(self) -> None:
        """Добавление и вычисление атрибута 'average_salary' в таблице 'hh_vacancies'"""
        try:
            with psycopg2.connect(**self._params, dbname=self._hh_dbname) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                    ALTER TABLE hh_vacancies ADD COLUMN IF NOT EXISTS average_salary REAL;""")
                    cur.execute("""
                    UPDATE hh_vacancies
                    SET average_salary = CASE
                        WHEN salary_from > 0 AND salary_to > 0 THEN (salary_from + salary_to) / 2
                        WHEN salary_from = 0 THEN salary_to
                        WHEN salary_to = 0 THEN salary_from
                        ELSE NULL
                    END;
                    """)
        except psycopg2.Error as e:
            self.logger.error(f"Ошибка при изменении таблицы hh_vacancies: {e}")

    @staticmethod
    def _get_params() -> dict:
        """Возвращает параметры подключения из database.ini"""
        return config()
