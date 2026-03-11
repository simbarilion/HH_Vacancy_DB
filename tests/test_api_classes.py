from json import JSONDecodeError
from unittest.mock import patch

import pytest
import requests

from src.api.api_classes import HeadHunterEmployersSource, HeadHunterVacanciesSource
from src.models.employer import Employer
from src.models.vacancy import Vacancy


def test__get_total_vacancies_one_page(api_vac_source, vacancy_json):
    """Проверяет ответ API с одной страницей для класса HeadHunterVacanciesSource"""
    with patch.object(HeadHunterVacanciesSource, "_get_response") as mock_get_response:
        mock_get_response.return_value = {
            "items": vacancy_json,
            "pages": 1
        }
        result = api_vac_source._get_employer_vacancies("12345")

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Vacancy)
        assert result[0].name == "Vacancy 1"
        assert result[0].salary_from == 1000
        assert result[0].salary_to == 2000
        assert result[0].area == "Москва"
        mock_get_response.assert_called_once()


def test__get_total_vacancies_pages(api_vac_source, vacancy_json):
    """Проверяет ответ API с несколькими страницами для класса HeadHunterVacanciesSource"""
    with patch.object(HeadHunterVacanciesSource, "_get_response") as mock_get_response:
        mock_get_response.return_value = {
            "items": vacancy_json,
            "pages": 2
        }
        result = api_vac_source._get_employer_vacancies("12345")

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0].name == "Vacancy 1"
    mock_get_response.assert_called()


def test__get_total_vacancies_json_error(api_vac_source):
    """Проверяет возникновение исключения JSONDecodeError для класса HeadHunterVacanciesSource"""
    with patch.object(HeadHunterVacanciesSource, "_get_response", side_effect=JSONDecodeError("err", "", 0)):
        with pytest.raises(JSONDecodeError):
            api_vac_source._get_employer_vacancies("12345")

def test__get_total_vacancies_status_error(api_vac_source):
    """Проверяет возникновение исключения requests.exceptions.RequestException для класса HeadHunterVacanciesSource"""
    with patch.object(HeadHunterVacanciesSource, "_get_response", side_effect=requests.exceptions.RequestException("err", "", 0)):
        with pytest.raises(requests.exceptions.RequestException):
            api_vac_source._get_employer_vacancies("12345")


def test__get_total_vacancies_none(api_vac_source):
    """Проверяет поведение класса HeadHunterVacanciesSource при пустом ответе"""
    with patch.object(HeadHunterVacanciesSource, "_get_response", return_value=None):
        result = api_vac_source._get_employer_vacancies("12345")
        assert result == []


def test_get_formatted_data(api_emp_source, employer_json):
    """Проверяет ответ API с одной страницей для класса HeadHunterEmployersSource"""
    with patch.object(HeadHunterEmployersSource, "_get_response") as mock_get_response:
        mock_get_response.return_value = {
            "id": "1",
            "name": "Employer 1",
            "alternate_url": "https://hh.ru/employer/1"
        }
        result = api_emp_source.get_formatted_data()

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Employer)
        assert result[0].name == "Employer 1"
        assert result[0].url == "https://hh.ru/employer/1"
        mock_get_response.assert_called_once()


def test_get_formatted_data_json_error(api_emp_source):
    """
    Проверяет обработку JSONDecodeError, requests.exceptions.RequestException
    для класса HeadHunterEmployersSource
    """
    with patch.object(HeadHunterEmployersSource, "_get_response", return_value=None):
        result = api_emp_source.get_formatted_data()

    assert result == []


def test_get_formatted_data_for_vacancies(api_vac_source, vacancy):
    """Проверяет преобразование данных из API HH о вакансиях"""
    with patch.object(HeadHunterVacanciesSource, "_get_employer_vacancies") as mock_get_vacancies:
        mock_get_vacancies.return_value = [vacancy]
        result = api_vac_source.get_formatted_data()

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Vacancy)
        assert result[0].name == "Vacancy 1"
        assert result[0].salary_from == 1000
        assert result[0].salary_to == 2000
        assert result[0].area == "Москва"
        mock_get_vacancies.assert_called()
