from abc import ABC, abstractmethod
from json import JSONDecodeError
from typing import Any, Optional

import requests

from src.logging_config import LoggingConfigClassMixin


class BaseAPISource(ABC, LoggingConfigClassMixin):
    """Абстрактный класс для получения данных через API"""
    def __init__(self) -> None:
        """Конструктор для получения вакансий через API"""
        super().__init__()
        self.logger = self.configure()

    def _get_response(self, url: str, headers: dict, params: Optional[dict]) -> Any:
        """Делает GET-запрос к API, возвращает JSON-ответ"""
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            self.logger.info("GET-запрос успешно обработан")
            result = response.json()
            self.logger.info("Данные преобразованы в json-формат")
        except requests.exceptions.RequestException as err:
            self.logger.error(f"Ошибка запроса: {err}")
            return {}
        except JSONDecodeError as err:
            self.logger.error(f"Ошибка преобразования данных в json-формат: {err}")
            return {}
        else:
            return result

    @abstractmethod
    def get_formatted_data(self) -> list[dict]:
        """Получает данные через API и возвращает список словарей данных"""
        pass


class HeadHunterVacanciesSource(BaseAPISource):
    """Класс для получения через API данных сайта HeadHunter.ru о вакансиях отдельных работодателей"""
    def __init__(self, employers_id: list[str]) -> None:
        """Конструктор для получения вакансий через API"""
        super().__init__()
        self._employers_id = employers_id
        self._url = "https://api.hh.ru/vacancies"
        self._headers = {"User-Agent": "api-test-agent"}
        self._params = {"employer_id": "",
                        "page": 0,
                        "per_page": 100,
                        "only_with_salary": True,
                        "currency": "RUR",
                        "area": 113}

    def get_formatted_data(self) -> list[dict]:
        """Получает данные о вакансиях сайта HeadHunter от отдельных компаний и возвращает список словарей вакансий"""
        employers_vacancies = []
        for employer_id in self._employers_id:
            self._params["employer_id"] = employer_id
            vacancies = self._get_total_vacancies()
            self.logger.info(f"Собрано {len(vacancies)} вакансий")
            filtered = self.filter_vacancies(vacancies)
            formatted = self.format_vacancies(filtered)
            self.logger.info(f"Отформатировано {len(formatted)} вакансий")
            emp_vacancies = {employer_id: formatted}
            employers_vacancies.append(emp_vacancies)
        return employers_vacancies

    def _get_total_vacancies(self, max_pages: int = 5) -> list[dict]:
        """Проходит по страницам API и собирает все вакансии"""
        total_data = []
        page = 0
        while True:
            self._params["page"] = page
            page_result = self._get_response(self._url, headers=self._headers, params=self._params)
            if not page_result:
                self.logger.warning(f"Не удалось получить данные с API (страница {page})")
                break
            data = page_result.get("items", [])
            total_data.extend(data)
            total_pages = page_result.get("pages", 1)
            if page + 1 >= total_pages or page + 1 >= max_pages:
                break
            page += 1
        return total_data

    @staticmethod
    def filter_vacancies(vacancies: list[dict]) -> list[dict]:
        """Фильтрует вакансии, в которых заработная плата в рублях"""
        return [vac for vac in vacancies if vac["salary"] and vac["salary"]["currency"] == "RUR"]

    @staticmethod
    def format_vacancies(vacancies_data: list[dict]) -> list[dict]:
        """Формирует список словарей вакансий"""
        vacancies = [
            {"vac_id": str(vac.get("id") or ""),
             "name": str(vac.get("name") or ""),
             "url": str(vac.get("alternate_url") or ""),
             "salary_from": vac.get("salary", {}).get("from"),
             "salary_to": vac.get("salary", {}).get("to"),
             "employer_name": str(vac.get("employer", {}).get("name") or ""),
             "area": str(vac.get("area", {}).get("name") or "")} for vac in vacancies_data]
        return vacancies


class HeadHunterEmployersSource(BaseAPISource):
    """Класс для получения через API данных сайта HeadHunter.ru об отдельных компаниях"""
    def __init__(self, employers_id: list[str]) -> None:
        """Конструктор для получения информации о компаниях через API"""
        super().__init__()
        self._employers_id = employers_id
        self._url = "https://api.hh.ru/employers"
        self._headers = {"User-Agent": "api-test-agent"}

    def get_formatted_data(self) -> list[dict]:
        """Получает данные о компаниях сайта HeadHunter и возвращает список словарей компаний"""
        employers = []
        for employer_id in self._employers_id:
            url = f"{self._url}/{employer_id}"
            employer_inform = self._get_response(url, headers=self._headers, params=None)
            if employer_inform:
                formatted = self.format_employers(employer_inform)
                employers.append(formatted)
        self.logger.info(f"Собрана информация о {len(employers)} компаниях")
        return employers

    @staticmethod
    def format_employers(emp: dict) -> dict:
        """Формирует информацию о компании в словарь"""
        employer = {
            "employer_id": str(emp.get("id") or ""),
            "name": str(emp.get("name") or ""),
            "url": str(emp.get("alternate_url") or "")
        }
        return employer
