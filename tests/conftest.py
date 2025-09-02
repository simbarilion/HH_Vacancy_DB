import pytest

from src.api_classes import HeadHunterVacanciesSource, HeadHunterEmployersSource


@pytest.fixture
def api_vac_source():
    return HeadHunterVacanciesSource(["1234", "5678"])


@pytest.fixture
def api_companies_source():
    return HeadHunterEmployersSource(["1234", "5678"])


@pytest.fixture
def row_vacancies() -> list[dict]:
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
    return {
            "id": "789",
            "name": "Купер",
            "alternate_url": "http://example.com/company/789",
            "area": "Москва"
        }
