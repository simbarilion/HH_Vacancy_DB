from typing import Any, Optional

import psycopg2
from psycopg2.extensions import connection

from config import config
from src.logging_config import LoggingConfigClassMixin


class HeadHunterDataBase(LoggingConfigClassMixin):
    """Класс для создания базы данных с компаниями и вакансиями сайта HeadHunter.ru"""
    def __init__(self, dbname: str = "headhunter_vacancies") -> None:
        """Конструктор класса"""
        super().__init__()
        self._base_dbname: str = "postgres"
        self._hh_dbname = dbname
        self._params: dict = self._get_params()
        self.conn: Optional[connection] = None
        self.logger = self.configure()

    def __enter__(self) -> Any:
        """Открывает соединение с базой данных"""
        try:
            self.conn = psycopg2.connect(**self._params, dbname=self._hh_dbname)
            self.conn.autocommit = False
            self.logger.info("Соединение с базой данных открыто")
            return self
        except psycopg2.Error as e:
            self.logger.error(f"Ошибка подключения к базе данных: {e}")
            raise

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Закрывает соединение с базой данных"""
        if self.conn is not None:
            self.conn.close()
            self.logger.info("Соединение с базой данных закрыто")

    def get_hh_dbname(self) -> str:
        """Возвращает название базы данных с компаниями и вакансиями сайта HeadHunter.ru"""
        return self._hh_dbname

    def _execute(self, query: str, params: Any = None, fetch: bool = False) -> Any:
        """Вспомогательный метод для выполнения SQL-запросов"""
        try:
            if self.conn is not None:
                with self.conn.cursor() as cur:
                    cur.execute(query, params)
                    if fetch:
                        return cur.fetchall()
                    self.conn.commit()
        except psycopg2.Error as e:
            if self.conn is not None:
                self.conn.rollback()
            self.logger.error(f"ошибка при работе с базой данных: {e}")
            raise

    def create_database(self) -> None:
        """Создает базу данных для хранения данных о компаниях и вакансиях сайта HeadHunter.ru"""
        try:
            conn = psycopg2.connect(**self._params, dbname=self._base_dbname)
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self._hh_dbname,))
            is_exists = cur.fetchone()
            if is_exists:
                cur.execute(f"DROP DATABASE {self._hh_dbname}")
                self.logger.info(f"База данных {self._hh_dbname} удалена")
            cur.execute(f"CREATE DATABASE {self._hh_dbname}")
            self.logger.info(f"База данных {self._hh_dbname} создана")
        except psycopg2.Error as e:
            self.logger.error(f"Ошибка при создании базы данных: {e}")
            raise

    def create_table_hh_companies(self) -> None:
        """Создает таблицу для хранения данных о компаниях сайта HeadHunter.ru"""
        self._execute("""
            CREATE TABLE hh_companies (
                company_id SERIAL NOT NULL,
                hh_employer_id VARCHAR NOT NULL UNIQUE,
                employer_name VARCHAR(255) NOT NULL,
                employer_url VARCHAR(255) NOT NULL,

                CONSTRAINT pk_hh_companies_id PRIMARY KEY(company_id)
                );
            """)
        self.logger.info("Tаблица hh_companies успешно создана")

    def create_table_hh_vacancies(self) -> None:
        """Создает таблицу для хранения данных о вакансиях компаний сайта HeadHunter.ru"""
        self._execute("""
            CREATE TABLE hh_vacancies (
                vacancy_id SERIAL NOT NULL,
                hh_vac_id VARCHAR NOT NULL UNIQUE,
                vac_name VARCHAR(255) NOT NULL,
                vac_url VARCHAR(255) NOT NULL,
                company_id INT NOT NULL,
                vac_area VARCHAR(255),
                salary_from INT,
                salary_to INT,

                CONSTRAINT pk_hh_vacancies_id PRIMARY KEY(vacancy_id),

                CONSTRAINT fk_hh_vacancies_company_id FOREIGN KEY(company_id)
                REFERENCES hh_companies(company_id) ON DELETE CASCADE
                );
            """)
        self.logger.info("Tаблица hh_vacancies успешно создана")

    def save_data_to_table_hh_companies(self, employers: list[dict]) -> None:
        """Сохранение данных о компаниях сайта HeadHunter.ru в базу данных"""
        amount = 0
        try:
            if self.conn is not None:
                with self.conn.cursor() as cur:
                    for emp in employers:
                        cur.execute(
                            """
                            INSERT INTO hh_companies (hh_employer_id, employer_name, employer_url)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (hh_employer_id) DO NOTHING
                            RETURNING company_id;
                            """,
                            (emp.get('employer_id'), emp.get('name'), emp.get('url'))
                        )
                        if cur.fetchone():
                            amount += 1
                self.conn.commit()
            self.logger.info(f"В таблицу hh_companies добавлено {amount} компаний")
        except psycopg2.Error as e:
            if self.conn is not None:
                self.conn.rollback()
            self.logger.error(f"Ошибка при добавлении данных в таблицу hh_companies: {e}")
            raise

    def save_data_to_table_hh_vacancies(self, employers_vacancies: list[dict]) -> None:
        """Сохранение данных о вакансиях компаний сайта HeadHunter.ru в базу данных"""
        amount = 0
        try:
            if self.conn is not None:
                with self.conn.cursor() as cur:
                    for emp_vacs in employers_vacancies:
                        for hh_employer_id, vacancies in emp_vacs.items():
                            cur.execute("SELECT company_id FROM hh_companies WHERE hh_employer_id = %s",
                                        (hh_employer_id,))
                            company = cur.fetchone()
                            company_id = company[0] if company else None
                            if company_id is None:
                                continue
                            for vac in vacancies:
                                cur.execute(
                                    """
                                    INSERT INTO hh_vacancies
                                    (hh_vac_id, vac_name, vac_url, company_id, vac_area, salary_from, salary_to)
                                    VALUES (%s, %s, %s, %s, %s, COALESCE(%s, 0), COALESCE(%s, 0))
                                    ON CONFLICT (hh_vac_id) DO NOTHING
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
                                if cur.fetchone():
                                    amount += 1
                self.conn.commit()
            self.logger.info(f"В таблицу hh_vacancies добавлено {amount} вакансий")
        except psycopg2.Error as e:
            if self.conn is not None:
                self.conn.rollback()
            self.logger.error(f"Ошибка при добавлении данных в таблицу hh_vacancies: {e}")
            raise

    def add_avg_salary_to_hh_vacancies(self) -> None:
        """Добавление и вычисление атрибута 'average_salary' в таблице 'hh_vacancies'"""
        self._execute("""ALTER TABLE hh_vacancies ADD COLUMN IF NOT EXISTS average_salary REAL;""")
        self._execute("""
            UPDATE hh_vacancies
            SET average_salary = CASE
                WHEN salary_from > 0 AND salary_to > 0 THEN (salary_from + salary_to) / 2
                WHEN salary_from = 0 THEN salary_to
                WHEN salary_to = 0 THEN salary_from
                ELSE NULL
            END;
            """)
        self.logger.info("В таблицу hh_vacancies добавлен атрибут average_salary")

    @staticmethod
    def _get_params() -> dict:
        """Возвращает параметры подключения к базе данных"""
        return config()
