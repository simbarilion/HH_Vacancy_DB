from typing import Optional

import psycopg2

from config import config
from src.logging_config import LoggingConfigClassMixin


class HeadHunterDataBaseManager(LoggingConfigClassMixin):
    """Класс для создания запросов к базе данных с компаниями и вакансиями сайта HeadHunter.ru"""
    def __init__(self) -> None:
        """Конструктор класса"""
        super().__init__()
        self._hh_dbname = "headhunter_vacancies"
        self._params = self._get_params()
        self.logger = self.configure()

    def _execute_query(self, query: str | tuple, params: Optional[str] = None) -> list:
        """Выполняет запрос к базе данных и возвращает результат"""
        try:
            with psycopg2.connect(**self._params, dbname=self._hh_dbname) as conn:
                with conn.cursor() as cur:
                    cur.execute(query, params)
                    rows = cur.fetchall()
            self.logger.info(f"Запрос к базе данных {self._hh_dbname} выполнен успешно")
            return rows  # type: ignore
        except psycopg2.Error as e:
            self.logger.error(f"Ошибка при выполнении запроса: {e}")
            return []

    def get_companies_and_vacancies_count(self) -> list:
        """Получает список всех компаний и количество вакансий у каждой компании"""
        query = """
                SELECT c.employer_name, COUNT(v.vacancy_id) AS vacancies_count, c.employer_url 
                FROM hh_companies AS c
                JOIN hh_vacancies AS v ON c.company_id = v.company_id
                GROUP BY c.employer_name
                ORDER BY c.employer_name;
                """
        return self._execute_query(query)

    def get_all_vacancies(self) -> list:
        """Получает список всех вакансий"""
        query = """
                SELECT c.employer_name, v.vac_name, v.salary_from, v.salary_to, v.vac_area, v.vac_url
                FROM hh_companies as c
                JOIN hh_vacancies as v ON c.company_id = v.company_id
                ORDER BY c.employer_name, v.vac_name;
                """
        return self._execute_query(query)

    def get_avg_salary(self) -> list:
        """Получает среднюю зарплату по вакансиям у каждой компании"""
        query = """
                SELECT c.employer_name, AVG(v.average_salary) AS average_salary, c.employer_url 
                FROM hh_vacancies AS v
                JOIN hh_companies AS c ON c.company_id = v.company_id
                GROUP BY c.employer_name
                ORDER BY average_salary DESC;
                """
        return self._execute_query(query)

    def get_vacancies_with_higher_salary(self) -> list:
        """Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям"""
        query = """
                SELECT c.employer_name, v.vac_name, v.salary_from, v.salary_to, v.vac_area, v.vac_url
                FROM hh_vacancies AS v
                JOIN hh_companies AS c ON c.company_id = v.company_id
                WHERE v.average_salary > (SELECT AVG(v.average_salary) FROM hh_vacancies)
                ORDER BY average_salary DESC;
                """
        return self._execute_query(query)

    def get_vacancies_with_keyword(self, key_word: str) -> list:
        """Получает список всех вакансий по ключевому слову в названии"""
        query = ("""
                SELECT c.employer_name, v.vac_name, v.salary_from, v.salary_to, v.vac_area, v.vac_url
                FROM hh_vacancies AS v
                JOIN hh_companies AS c ON c.company_id = v.company_id
                WHERE v.vac_name ILIKE %s""",
                 ('%' + key_word + '%',))
        return self._execute_query(query, key_word)

    @staticmethod
    def _get_params() -> dict:
        """Возвращает параметры подключения из database.ini"""
        return config()
