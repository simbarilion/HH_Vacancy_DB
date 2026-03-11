from tabulate import tabulate

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
        1: ["Компания", "Количество вакансий", "Ссылка"],
        2: ["Компания", "Вакансия", "Зарплата от", "Зарплата до", "Город", "Ссылка"],
        3: ["Компания", "Средняя зарплата (по открытым вакансиям)", "Ссылка"],
        4: ["Компания", "Вакансия", "Зарплата от", "Зарплата до", "Город", "Ссылка"],
        5: ["Компания", "Вакансия", "Зарплата от", "Зарплата до", "Город", "Ссылка"]
    }

    def __init__(self, db_name: str):
        self._manager = HeadHunterDataBaseManager(db_name)

    def open_connection(self):
        self._manager.open_connection()

    def close_connection(self):
        self._manager.close_connection()

    def execute_query(self, query_id: int, key_word: str = "") -> str:
        """Возвращает данные из базы данных в соответствии с запросом"""
        queries = {
            1: self._manager.get_companies_and_vacancies_count,
            2: self._manager.get_all_vacancies,
            3: self._manager.get_avg_salary,
            4: self._manager.get_vacancies_with_higher_salary,
            5: lambda: self._manager.get_vacancies_with_keyword(key_word)  # type: ignore
        }

        query = queries[query_id]
        result = query()
        return self._format_result(result, query_id)

    def _format_result(self, result: list, choice: int) -> str:
        """Возвращает данные в виде таблицы"""
        cleaned_result = [tuple("" if value == 0 else value for value in row) for row in result]

        header = self._HEADERS.get(choice, [])
        return tabulate(cleaned_result, headers=header, tablefmt="fancy_grid")
