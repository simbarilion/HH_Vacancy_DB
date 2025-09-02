from typing import Any, Optional

from tabulate import tabulate

from src.api_classes import HeadHunterEmployersSource, HeadHunterVacanciesSource
from src.hh_db_creator import HeadHunterDataBase
from src.hh_db_manager import HeadHunterDataBaseManager


class HeadHunterDataCoordinator:
    def __init__(self, employers_id: list, db_name: str):
        """Конструктор класса HeadHunterDataCoordinator"""
        self._employers_id = employers_id
        self._db_name = db_name
        self._hh_vacancies: list[dict] = self._get_hh_vacancies()
        self._hh_companies: list[dict] = self._get_hh_companies()
        self.hh_query_manager: Optional[HeadHunterDataBaseManager] = None

    def _get_hh_vacancies(self) -> list[dict]:
        """Возвращает информацию о вакансиях с сайта HeadHunter.ru, полученные через API"""
        hh_vacancies = HeadHunterVacanciesSource(self._employers_id)
        return hh_vacancies.get_formatted_data()

    def _get_hh_companies(self) -> list[dict]:
        """Возвращает информацию о компаниях с сайта HeadHunter.ru, полученные через API"""
        hh_companies = HeadHunterEmployersSource(self._employers_id)
        return hh_companies.get_formatted_data()

    def create_hh_database(self) -> None:
        """Создает объект класса HeadHunterDataBase"""
        hh_database = HeadHunterDataBase(self._db_name)
        hh_database.create_database()
        with hh_database:
            hh_database.create_table_hh_companies()
            hh_database.create_table_hh_vacancies()
            hh_database.save_data_to_table_hh_companies(self._hh_companies)
            hh_database.save_data_to_table_hh_vacancies(self._hh_vacancies)
            hh_database.add_avg_salary_to_hh_vacancies()

    def create_db_manager_obj(self) -> None:
        """Создает объект класса HeadHunterDataBaseManager, открывает соединение с базой данных"""
        self.hh_query_manager = HeadHunterDataBaseManager(self._db_name)
        self.hh_query_manager.open_connection()

    def execute_query(self, choice: int, key_word: Optional[str] = None) -> Any:
        """Возвращает данные из базы данных в соответствии с запросом"""
        if self.hh_query_manager is None:
            raise RuntimeError("Менеджер базы данных не создан")

        queries = {
            1: self.hh_query_manager.get_companies_and_vacancies_count,
            2: self.hh_query_manager.get_all_vacancies,
            3: self.hh_query_manager.get_avg_salary,
            4: self.hh_query_manager.get_vacancies_with_higher_salary,
            5: lambda: self.hh_query_manager.get_vacancies_with_keyword(key_word)  # type: ignore
        }

        query = queries[choice]
        result = query()
        return self._format_result(result, choice)

    @staticmethod
    def _format_result(result: list, choice: int) -> Any:
        """Возвращает данные в виде таблицы"""
        cleaned_result = [tuple("" if value == 0 else value for value in row) for row in result]

        headers = {
            1: ["Компания", "Количество вакансий", "Ссылка"],
            2: ["Компания", "Вакансия", "Зарплата от", "Зарплата до", "Город", "Ссылка"],
            3: ["Компания", "Средняя зарплата (по открытым вакансиям)", "Ссылка"],
            4: ["Компания", "Вакансия", "Зарплата от", "Зарплата до", "Город", "Ссылка"],
            5: ["Компания", "Вакансия", "Зарплата от", "Зарплата до", "Город", "Ссылка"]
        }

        header = headers.get(choice, [])
        return tabulate(cleaned_result, headers=header, tablefmt="fancy_grid")

    def close_db_manager_obj_connection(self) -> None:
        """Закрывает соединение с базой данных"""
        if self.hh_query_manager:
            self.hh_query_manager.close_connection()
