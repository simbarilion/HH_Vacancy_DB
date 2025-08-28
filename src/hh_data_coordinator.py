from typing import Optional

from tabulate import tabulate

from src.api_classes import HeadHunterVacanciesSource, HeadHunterEmployersSource
from src.hh_db_creator import HeadHunterDataBase
from src.hh_db_manager import HeadHunterDataBaseManager


class HeadHunterDataCoordinator:
    def __init__(self, employers_id):
        """Конструктор класса HeadHunterDataCoordinator"""
        self.employers_id = employers_id
        self.hh_vacancies = self.get_hh_vacancies()
        self.hh_companies = self.get_hh_companies()

    def get_hh_vacancies(self):
        """Возвращает информацию о вакансиях с сайта HeadHunter.ru, полученные через API"""
        hh_vacancies = HeadHunterVacanciesSource(self.employers_id)
        return hh_vacancies.get_formatted_data()

    def get_hh_companies(self):
        """Возвращает информацию о компаниях с сайта HeadHunter.ru, полученные через API"""
        hh_companies = HeadHunterEmployersSource(self.employers_id)
        return hh_companies.get_formatted_data()

    def create_hh_database(self):
        """Создает объект класса HeadHunterDataBase"""
        hh_database = HeadHunterDataBase()
        hh_database.create_database()
        hh_database.create_table_hh_companies()
        hh_database.create_table_hh_vacancies()
        hh_database.save_data_to_table_hh_companies(self.hh_companies)
        hh_database.save_data_to_table_hh_vacancies(self.hh_vacancies)
        hh_database.add_avg_salary_to_hh_vacancies()

    def execute_query(self, choice, key_word: Optional[str]):
        """Возвращает данные из базы данных в соответствии с запросом"""
        hh_query_manager = HeadHunterDataBaseManager()
        queries = {
            1: hh_query_manager.get_companies_and_vacancies_count,
            2: hh_query_manager.get_all_vacancies,
            3: hh_query_manager.get_avg_salary,
            4: hh_query_manager.get_vacancies_with_higher_salary,
            5: lambda: hh_query_manager.get_vacancies_with_keyword(key_word),
        }

        result = queries.get(choice)
        return self.format_result(result, choice)

    @staticmethod
    def format_result(result, choice):
        """Возвращает данные в виде таблицы"""
        headers = {
            1: ["Компания", "Количество вакансий", "Ссылка"],
            2: ["Компания", "Вакансия", "Зарплата от", "Зарплата до", "Город", "Ссылка"],
            3: ["Компания", "Средняя зарплата (по открытым вакансиям)", "Ссылка"],
            4: ["Компания", "Вакансия", "Зарплата от", "Зарплата до", "Город", "Ссылка"],
            5: ["Компания", "Вакансия", "Зарплата от", "Зарплата до", "Город", "Ссылка"]
        }

        header = headers.get(choice)
        return tabulate(result, headers=header, tablefmt="fancy_grid")









