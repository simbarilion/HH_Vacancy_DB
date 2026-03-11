import pytest

from src.api.api_classes import HeadHunterEmployersSource, HeadHunterVacanciesSource
from src.database.hh_db_creator import HeadHunterDataBase
from src.database.hh_db_manager import HeadHunterDataBaseManager
from src.ui.user_interaction import UserInteraction


@pytest.fixture
def api_vac_source():
    """Фикстура для класса HeadHunterVacanciesSource"""
    return HeadHunterVacanciesSource(employers_id=["12345"])

def make_mock_response_json(items=None, pages=1):
    """Фикстура для мок-ответа API"""
    if items is None:
        items = []
    return {
        "items": items,
        "pages": pages
    }

@pytest.fixture
def vacancy_json():
    """Тестовая информация о вакансиях в JSON формате"""
    return [
            {
                "id": "1",
                "name": "Vacancy 1",
                "alternate_url": "https://hh.ru/vacancy/1",
                "salary": {"from": 1000, "to": 2000, "currency": "RUR"},
                "area": {"name": "Москва"}
            }
        ]



@pytest.fixture
def api_companies_source() -> HeadHunterEmployersSource:
    """Возвращает объект класса HeadHunterEmployersSource"""
    return HeadHunterEmployersSource(["1234", "5678"])


@pytest.fixture
def db() -> HeadHunterDataBase:
    """Возвращает объект класса HeadHunterDataBase"""
    return HeadHunterDataBase("test_hh_db")


@pytest.fixture
def db_manager() -> HeadHunterDataBaseManager:
    """Возвращает объект класса HeadHunterDataBaseManager"""
    return HeadHunterDataBaseManager("test_hh_db_manager")


@pytest.fixture
def user_interaction() -> UserInteraction:
    """Возвращает объект класса UserInteraction"""
    return UserInteraction()


@pytest.fixture
def row_vacancies() -> list[dict]:
    """Возвращает список словарей вакансий"""
    return [
        {
            "id": "123",
            "name": "Python Developer",
            "alternate_url": "http://example.com/vacancy/123",
            "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
            "employer": {
                "name": "FirstCompany",
                "alternate_url": "http://example.com/employer/1"
            },
            "area": {"name": "Москва"}
        },
        {
            "id": "345",
            "name": "Java Developer",
            "alternate_url": "http://example.com/vacancy/345",
            "salary": {"from": 150000, "to": 200000, "currency": "RUR"},
            "employer": {
                "name": "SecondCompany",
                "alternate_url": "http://example.com/employer/2"
            },
            "area": {"name": "Казань"}
        }
    ]


@pytest.fixture
def row_employers() -> dict:
    """Возвращает информацию о компании в виде словаря"""
    return {
        "id": "789",
        "name": "Купер",
        "alternate_url": "http://example.com/company/789",
        "area": "Москва"
    }


@pytest.fixture
def employers_vacancies() -> list[dict]:
    """Возвращает вакансии компании в виде списка словарей"""
    return [
        {"1234":
            [
                {"vac_id": "v1", "name": "Dev", "url": "http://dev.com", "area": "Москва", "salary_from": 100,
                 "salary_to": 200},
                {"vac_id": "v2", "name": "QA", "url": "http://qa.com", "area": "Казань", "salary_from": 0,
                 "salary_to": 150}]
         }
    ]


@pytest.fixture
def employers() -> list[dict]:
    return [
        {"employer_id": "1", "name": "Company A", "url": "http://a.com"},
        {"employer_id": "2", "name": "Company B", "url": "http://b.com"}
    ]
