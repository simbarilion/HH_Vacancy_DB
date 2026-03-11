from tabulate import tabulate

from src.constants.query_type import QueryType
from src.database.hh_db_creator import HeadHunterDataBase
from src.database.hh_db_manager import HeadHunterDataBaseManager
from src.models.employer import Employer
from src.models.vacancy import Vacancy


class HeadHunterDBCreator:
    """Создает и заполняет БД"""
    def __init__(self, db_name: str):
        self._db_name = db_name
        self._db = HeadHunterDataBase(db_name)

    @property
    def db_name(self) -> str:
        """Возвращает название базы данных с компаниями и вакансиями сайта HeadHunter.ru"""
        return self._db_name

    def create_and_fill_db(self, companies: list[Employer], vacancies: list[Vacancy]):
        self._db.create_database()
        with self._db:
            self._db.create_table_hh_companies()
            self._db.create_table_hh_vacancies()
            self._db.save_data_to_table_hh_companies(companies)
            self._db.save_data_to_table_hh_vacancies(vacancies)


class HeadHunterDBManager:
    """Отправляет SELECT-запросы, возвращает результат в виде таблицы данных"""
    _HEADERS = {
        QueryType.COMPANIES_VACANCIES_COUNT: ["Компания", "Количество вакансий", "Ссылка"],
        QueryType.ALL_VACANCIES: ["Компания", "Вакансия", "Зарплата от", "Зарплата до", "Город", "Ссылка"],
        QueryType.AVG_SALARY: ["Компания", "Средняя зарплата (по открытым вакансиям)", "Ссылка"],
        QueryType.HIGHER_SALARY: ["Компания", "Вакансия", "Зарплата от", "Зарплата до", "Город", "Ссылка"],
        QueryType.KEYWORD_SEARCH: ["Компания", "Вакансия", "Зарплата от", "Зарплата до", "Город", "Ссылка"]
    }

    def __init__(self, db_name: str):
        self._manager = HeadHunterDataBaseManager(db_name)

    def open_connection(self):
        self._manager.open_connection()

    def close_connection(self):
        self._manager.close_connection()

    def execute_query(self, query_type: QueryType, key_word: str = "") -> str:
        """Возвращает данные из базы данных в соответствии с запросом"""
        queries = {
            QueryType.COMPANIES_VACANCIES_COUNT: self._manager.get_companies_and_vacancies_count,
            QueryType.ALL_VACANCIES: self._manager.get_all_vacancies,
            QueryType.AVG_SALARY: self._manager.get_avg_salary,
            QueryType.HIGHER_SALARY: self._manager.get_vacancies_with_higher_salary,
            QueryType.KEYWORD_SEARCH: lambda: self._manager.get_vacancies_with_keyword(key_word)  # type: ignore
        }

        query = queries[query_type]
        result = query()
        return self._format_result(result, query_type)

    def _format_result(self, result: list, choice: QueryType) -> str:
        """Возвращает данные в виде таблицы"""
        cleaned_result = [tuple("" if value == 0 else value for value in row) for row in result]

        header = self._HEADERS.get(choice, [])
        return tabulate(cleaned_result, headers=header, tablefmt="fancy_grid")
