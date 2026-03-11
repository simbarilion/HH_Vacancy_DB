from src.api.api_classes import HeadHunterVacanciesSource, HeadHunterEmployersSource
from src.models.employer import Employer
from src.models.vacancy import Vacancy


class HeadHunterAPI:
    """Получение данных с HH.ru через API"""
    def __init__(self, employers_id: list[str]):
        self._employers_id = employers_id

    def get_vacancies(self) -> list[Vacancy]:
        with HeadHunterVacanciesSource(self._employers_id) as hh_vac:
            return hh_vac.get_formatted_data()

    def get_companies(self) -> list[Employer]:
        with HeadHunterEmployersSource(self._employers_id) as hh_comp:
            return hh_comp.get_formatted_data()
