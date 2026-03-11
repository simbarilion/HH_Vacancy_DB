from json import JSONDecodeError
from typing import Any
from unittest.mock import MagicMock, patch

from requests import HTTPError, Response

from src.api.api_classes import HeadHunterEmployersSource, HeadHunterVacanciesSource


def make_mock_response_json(items: list[dict], pages: int) -> MagicMock:
    """Возвращает фейковый Response в формате json"""
    mock_resp = MagicMock(spec=Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "items": items,
        "pages": pages
    }
    return mock_resp


@patch("src.api_classes.requests.get")
def test__get_total_vacancies_one_page(mock_get: Any, api_vac_source: HeadHunterVacanciesSource) -> None:
    """Проверяет ответ API с одной страницей для класса HeadHunterVacanciesSource"""
    mock_get.return_value = make_mock_response_json(items=[{"id": 1, "name": "Vacancy 1"}], pages=1)

    result = api_vac_source._get_total_vacancies()

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["name"] == "Vacancy 1"
    mock_get.assert_called_once()


@patch("src.api_classes.requests.get")
def test__get_total_vacancies_pages(mock_get: Any, api_vac_source: HeadHunterVacanciesSource) -> None:
    """Проверяет ответ API с несколькими страницами для класса HeadHunterVacanciesSource"""
    mock_get.return_value = make_mock_response_json(items=[{"id": 1, "name": "Vacancy 1"}], pages=2)

    result = api_vac_source._get_total_vacancies()

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["name"] == "Vacancy 1"
    mock_get.assert_called()


def test__get_total_vacancies_json_error(api_vac_source: HeadHunterVacanciesSource) -> None:
    """Проверяет возникновение исключения JSONDecodeError для класса HeadHunterVacanciesSource"""
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = 200
    mock_response.json.side_effect = JSONDecodeError("err", "", 0)

    with patch("requests.get", return_value=mock_response):
        result = api_vac_source._get_total_vacancies()

    assert result == []
    mock_response.raise_for_status.assert_called_once()
    mock_response.json.assert_called_once()


def test__get_total_vacancies_status_error(api_vac_source: HeadHunterVacanciesSource) -> None:
    """Проверяет возникновение исключения HTTPError для класса HeadHunterVacanciesSource"""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = HTTPError()

    with patch("requests.get", return_value=mock_response):
        result = api_vac_source._get_total_vacancies()

    assert result == []
    mock_response.raise_for_status.assert_called_once()


def test__get_companies(api_companies_source: HeadHunterEmployersSource) -> None:
    """Проверяет ответ API с одной страницей для класса HeadHunterEmployersSource"""
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = 200
    mock_response.json.return_value = {"id": 1, "name": "Company 1"}

    with patch("requests.get", return_value=mock_response):
        result = api_companies_source._get_response("url", headers={"User": "user"}, params=None)

    assert result == {"id": 1, "name": "Company 1"}
    mock_response.raise_for_status.assert_called_once()
    mock_response.json.assert_called_once()


def test__get_companies_json_error(api_companies_source: HeadHunterEmployersSource) -> None:
    """Проверяет возникновение исключения JSONDecodeError для класса HeadHunterEmployersSource"""
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = 200
    mock_response.json.side_effect = JSONDecodeError("err", "", 0)

    with patch("requests.get", return_value=mock_response):
        result = api_companies_source.get_formatted_data()

    assert result == []
    mock_response.raise_for_status.assert_called()


def test__get_companies_status_error(api_companies_source: HeadHunterEmployersSource) -> None:
    """Проверяет возникновение исключения HTTPError для класса HeadHunterEmployersSource"""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = HTTPError()

    with patch("requests.get", return_value=mock_response):
        result = api_companies_source.get_formatted_data()

    assert result == []
    mock_response.raise_for_status.assert_called()


def test_format_vacancies(row_vacancies: list[dict]) -> None:
    """Проверяет форматирование данных о вакансиях"""
    source = HeadHunterVacanciesSource(["1234", "5678"])
    vacancies = source.format_vacancies(row_vacancies)

    assert len(vacancies) == 2

    assert vacancies[0]["vac_id"] == "123"
    assert vacancies[0]["name"] == "Python Developer"
    assert vacancies[0]["url"] == "http://example.com/vacancy/123"
    assert vacancies[0]["salary_from"] == 100000
    assert vacancies[0]["salary_to"] == 150000
    assert vacancies[0]["area"] == "Москва"


def test_format_employers(row_employers: dict) -> None:
    """Проверяет форматирование данных о компаниях"""
    source = HeadHunterEmployersSource(["1234", "5678"])
    companies = source.format_employers(row_employers)

    assert len(companies) == 3

    assert companies["employer_id"] == "789"
    assert companies["name"] == "Купер"
    assert companies["url"] == "http://example.com/company/789"


def test_get_formatted_data(api_vac_source: HeadHunterVacanciesSource) -> None:
    """Проверяет форматирование данных о вакансиях компаний"""
    api_vac_source._get_total_vacancies = MagicMock(side_effect=[
        [{"id": "1", "salary": {"currency": "RUR", "from": 100, "to": 200}}],  # для первой компании
        [{"id": "2", "salary": {"currency": "USD", "from": 50, "to": 100}}]   # для второй
    ])
    api_vac_source.filter_vacancies = (MagicMock
                                       (side_effect=lambda x: [v for v in x if v["salary"]["currency"] == "RUR"]))
    api_vac_source.format_vacancies = (MagicMock
                                       (side_effect=lambda x: [{"vac_id": v["id"]} for v in x]))

    result = api_vac_source.get_formatted_data()

    assert api_vac_source._get_total_vacancies.call_count == 2
    assert result == [{"1234": [{"vac_id": "1"}]}, {"5678": []}]
