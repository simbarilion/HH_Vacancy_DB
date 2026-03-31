from concurrent.futures import ThreadPoolExecutor

from src.api.base_api_class import BaseAPISource
from src.models.employer import Employer
from src.models.vacancy import Vacancy


class HeadHunterVacanciesSource(BaseAPISource):
    """Получение вакансий работодателей HH"""

    URL = "https://api.hh.ru/vacancies"
    HEADERS = {"User-Agent": "api-test-agent"}
    BASE_PARAMS = {"per_page": 100, "only_with_salary": True, "currency": "RUR", "area": 113}

    def __init__(self, employers_id: list[str]) -> None:
        super().__init__()
        self._employers_id = employers_id

    def get_formatted_data(self) -> list[Vacancy]:
        """Получает вакансии всех работодателей"""
        vacancies: list[Vacancy] = []

        with ThreadPoolExecutor(max_workers=5) as executor:  # запускает до 5 worker-потоков
            results = executor.map(self._get_employer_vacancies, self._employers_id)  # запросы идут параллельно
            for employer_vacancies in results:
                vacancies.extend(employer_vacancies)
        self.logger.info(f"Всего получено {len(vacancies)} вакансий")
        return vacancies

    def _get_employer_vacancies(self, employer_id: str, max_pages: int = 5) -> list[Vacancy]:
        """Проходит по страницам API и собирает все вакансии"""
        try:
            result: list[Vacancy] = []
            for page in range(max_pages):
                params = {**self.BASE_PARAMS, "employer_id": employer_id, "page": page}
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
                            employer_id=employer_id,
                        )
                    )
                if page + 1 >= data.get("pages", 0):
                    break
            self.logger.debug(f"Работодатель {employer_id}: {len(result)} вакансий")
            return result
        finally:
            self._close_session()


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
        try:
            for employer_id in self._employers_id:
                url = f"{self.URL}/{employer_id}"
                data = self._get_response(url=url, headers=self.HEADERS)
                if not data:
                    continue
                employers.append(
                    Employer(employer_id=str(data.get("id")), name=data.get("name", ""), url=data.get("alternate_url", ""))
                )
            self.logger.info(f"Получена информация о {len(employers)} компаниях")
            return employers
        finally:
            self._close_session()
