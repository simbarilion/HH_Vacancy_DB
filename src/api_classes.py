from abc import ABC, abstractmethod
from json import JSONDecodeError
from typing import Any, Iterator

import requests

from src.logging_config import LoggingConfigClassMixin


class BaseAPISource(ABC, LoggingConfigClassMixin):
    """Абстрактный класс для получения данных через API"""
    def __init__(self):
        super().__init__()
        self._url = None
        self._headers = None
        self._params = None
        self.logger = self.configure()

    def _get_response(self) -> Iterator[dict]:
        """Делает GET-запрос к API, возвращает JSON-ответ для каждой страницы"""
        page = 0
        while True:
            self._params["page"] = page
            try:
                response = requests.get(self._url, headers=self._headers, params=self._params, timeout=10)
                response.raise_for_status()
                self.logger.info(f"Страница {page + 1} успешно получена")
                page_result = response.json()
                self.logger.info(f"Данные на странице {page + 1} преобразованы в json-формат")
                yield page_result
                total_pages = page_result.get("pages", 1)
                if page >= 4 or page + 1 >= total_pages:
                    break
                page += 1
            except requests.exceptions.RequestException as err:
                self.logger.error(f"Ошибка запроса на странице {page}: {err}")
                break
            except JSONDecodeError as err:
                self.logger.error(f"Ошибка преобразования данных в json-формат: {err}")
                break

    def _get_total_data(self) -> list:
        """Преобразует JSON-ответы для каждой страницы в единый список"""
        vacancies_data = []
        for page_result in self._get_response():
            data = page_result.get("items", [])
            vacancies_data.extend(data)
        return vacancies_data

    @abstractmethod
    def get_formatted_data(self) -> Any:
        """Получает данные через API и возвращает список словарей данных"""
        pass


class HeadHunterVacanciesSource(BaseAPISource):
    """Класс для получения через API данных сайта HeadHunter.ru о вакансиях по ключевому слову"""
    __slots__ = ("_url", "_headers", "_params")
    _url: str
    _headers: dict
    _params: dict

    def __init__(self) -> None:
        """Конструктор для получения вакансий через API"""
        super().__init__()
        self._url = "https://api.hh.ru/vacancies"
        self._headers = {"User-Agent": "api-test-agent"}
        self._params = {"text": "",
                         "page": 0,
                         "per_page": 100,
                         "only_with_salary": True,
                         "currency": "RUR",
                         "area": 113}

    def get_formatted_data(self) -> list[dict]:
        """Получает данные о вакансиях сайта HeadHunter и возвращает список словарей вакансий"""
        vacancies = self._get_total_data()
        self.logger.info(f"Собрано {len(vacancies)} вакансий")
        filtered = self.filter_vacancies(vacancies)
        return self.format_vacancies(filtered)

    @staticmethod
    def filter_vacancies(vacancies):
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
             "employer_url": str(vac.get("employer", {}).get("alternate_url") or ""),
             "area": str(vac.get("area", {}).get("name") or "")} for vac in vacancies_data]

        return vacancies
