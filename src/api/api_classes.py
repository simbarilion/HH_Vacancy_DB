from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from json import JSONDecodeError
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from src.logging_config import LoggingConfigClassMixin
from src.models.employer import Employer
from src.models.vacancy import Vacancy


class BaseAPISource(ABC, LoggingConfigClassMixin):
    """Базовый класс для работы с API"""
    def __init__(self) -> None:
        super().__init__()
        self.logger = self.configure()
        self.session = requests.Session()

        retry = Retry(
            total=3,            # максимум 3 попытки
            backoff_factor=1,   # задержка между повторами
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry)  # определяет политику повторных попыток
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
        self.logger.info("HTTP session закрыта")

    def _get_response(
            self,
            url: str,
            headers: Optional[dict] = None,
            params: Optional[dict] = None
        ) -> Optional[dict]:
        """Выполняет GET запрос и возвращает JSON"""
        try:
            response = self.session.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            result = response.json()
            self.logger.info("Данные преобразованы в json-формат")
            return result
        except requests.exceptions.RequestException as err:
            self.logger.error(f"Ошибка запроса: {err}")
        except JSONDecodeError as err:
            self.logger.error(f"Ошибка декодирования JSON: {err}")
        return None

    @abstractmethod
    def get_formatted_data(self) -> list[dict]:
        """Возвращает список моделей данных"""
        pass


class HeadHunterVacanciesSource(BaseAPISource):
    """Получение вакансий работодателей HH"""
    URL = "https://api.hh.ru/vacancies"
    HEADERS = {"User-Agent": "api-test-agent"}
    BASE_PARAMS = {
        "per_page": 100,
        "only_with_salary": True,
        "currency": "RUR",
        "area": 113
    }
    def __init__(self, employers_id: list[str]) -> None:
        super().__init__()
        self._employers_id = employers_id

    def get_formatted_data(self) -> list[Vacancy]:
        """Получает вакансии всех работодателей"""
        vacancies: list[Vacancy] = []

        with ThreadPoolExecutor(max_workers=5) as executor:   # запускает до 5 worker-потоков
            results = executor.map(             # запросы идут параллельно
                self._get_employer_vacancies,
                self._employers_id
            )
            for employer_vacancies in results:
                vacancies.extend(employer_vacancies)
        self.logger.info(f"Всего получено {len(vacancies)} вакансий")
        return vacancies

    def _get_employer_vacancies(self, employer_id: str, max_pages: int = 5) -> list[Vacancy]:
        """Проходит по страницам API и собирает все вакансии"""
        result: list[Vacancy] = []
        for page in range(max_pages):
            params = {
                **self.BASE_PARAMS,
                "employer_id": employer_id,
                "page": page
            }
            data = self._get_response(url=self.URL, headers=self.HEADERS, params=params)
            if not data:
                self.logger.warning(f"Не удалось получить данные с API (страница {page})")
                break
            items = data.get("items", [])
            for vac in items:
                salary = vac.get("salary")
                if not salary or salary.get("currency") != "RUR":
                    continue
                result.append(
                    Vacancy(
                        vac_id=str(vac.get("id")),
                        name=vac.get("name", ""),
                        url=vac.get("alternate_url", ""),
                        salary_from=salary.get("from") or 0,
                        salary_to=salary.get("to") or 0,
                        area=vac.get("area", {}).get("name", ""),
                        employer_id=employer_id
                    )
                )
            if page >= data.get("pages", 0):
                break
        self.logger.info(f"Работодатель {employer_id}: {len(result)} вакансий")
        return result


class HeadHunterEmployersSource(BaseAPISource):
    """Получение информации о работодателях"""
    URL = "https://api.hh.ru/employers"
    HEADERS = {"User-Agent": "api-test-agent"}

    def __init__(self, employers_id: list[str]) -> None:
        """Конструктор для получения информации о компаниях через API"""
        super().__init__()
        self._employers_id = employers_id

    def get_formatted_data(self) -> list[Employer]:
        """Возвращает список работодателей"""
        employers: list[Employer] = []

        for employer_id in self._employers_id:
            url = f"{self.URL}/{employer_id}"
            data = self._get_response(url=url, headers=self.HEADERS)
            if not data:
                continue
            employers.append(
                Employer(
                    employer_id=str(data.get("id")),
                    name=data.get("name", ""),
                    url=data.get("alternate_url", "")
                )
            )
        self.logger.info(f"Получена информация о {len(employers)} компаниях")
        return employers
