from typing import Any
from unittest.mock import MagicMock, patch

import psycopg2
import pytest

from src.database.hh_db_manager import HeadHunterDataBaseManager


@patch("psycopg2.connect")
def test_open_connection(mock_connect: Any, db_manager: HeadHunterDataBaseManager) -> None:
    """Проверяет успешное соединение с базой данных"""
    mock_conn = MagicMock()
    db_manager.logger = MagicMock()
    mock_connect.return_value = mock_conn

    db_manager.open_connection()
    mock_connect.assert_called_once()
    db_manager.logger.info.assert_called_once_with("Соединение с базой данных открыто")


@patch("psycopg2.connect")
def test_open_connection_fail(mock_connect: Any, db_manager: HeadHunterDataBaseManager) -> None:
    """Проверяет неуспешное соединение с базой данных"""
    db_manager.logger = MagicMock()
    mock_connect.side_effect = psycopg2.Error()

    with pytest.raises(psycopg2.Error):
        db_manager.open_connection()
    db_manager.logger.error.assert_called_once_with("Ошибка подключения к базе данных: ")


def test_close_connection(db_manager: HeadHunterDataBaseManager) -> None:
    """Проверяет закрытие соединения с базой данных"""
    mock_conn = MagicMock()
    db_manager._conn = mock_conn
    db_manager.logger = MagicMock()

    db_manager.close_connection()
    db_manager.logger.info.assert_called_once_with("Соединение с базой данных закрыто")


def test_execute_query_success(db_manager: HeadHunterDataBaseManager) -> None:
    """Проверяет успешное выполнение запроса к базе данных"""
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
    mock_cursor.fetchall.return_value = [("row1", "row2")]

    db_manager._conn = mock_conn
    db_manager.logger = MagicMock()

    query = "SELECT * FROM test"
    result = db_manager._execute_query(query, None)

    assert result == [("row1", "row2")]
    mock_cursor.execute.assert_called_once_with(query, None)
    db_manager.logger.info.assert_called_once()


def test_execute_query_no_connection(db_manager: HeadHunterDataBaseManager) -> None:
    """Проверяет выполнение запроса к базе данных при закрытом соединении"""
    db_manager._conn = None
    with pytest.raises(RuntimeError, match="Соединение с базой данных не открыто"):
        db_manager._execute_query("SELECT * FROM test")


def test_execute_query_error(db_manager: HeadHunterDataBaseManager) -> None:
    """Проверяет неуспешное выполнение запроса к базе данных"""
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
    mock_cursor.execute.side_effect = psycopg2.Error()

    db_manager._conn = mock_conn
    db_manager.logger = MagicMock()
    with pytest.raises(psycopg2.Error):
        db_manager._execute_query("SELECT * FROM test")
    db_manager.logger.error.assert_called_once_with("Ошибка при выполнении запроса: ")


def test_get_companies_and_vacancies_count(db_manager: HeadHunterDataBaseManager) -> None:
    """Проверяет получение списка компаний и количества вакансий"""
    fake_result = [("Company A", 5, "urlA"), ("Company B", 0, "urlB")]

    with patch.object(HeadHunterDataBaseManager, "_execute_query", return_value=fake_result) as mock_execute:
        result = db_manager.get_companies_and_vacancies_count()

    assert result == fake_result
    mock_execute.assert_called_once()
    query = mock_execute.call_args[0][0]
    assert "SELECT c.employer_name" in query
    assert "LEFT JOIN hh_vacancies" in query


def test_get_all_vacancies(db_manager: HeadHunterDataBaseManager) -> None:
    """Проверяет получение списка всех вакансий"""
    fake_result = [("Company A", "Vac 1", 100000, 130000, "Казань", "url1"),
                   ("Company B", "Vac 2", 150000, 180000, "Москва", "url2")]

    with patch.object(HeadHunterDataBaseManager, "_execute_query", return_value=fake_result) as mock_execute:
        result = db_manager.get_all_vacancies()

    assert result == fake_result
    mock_execute.assert_called_once()
    query = mock_execute.call_args[0][0]
    assert "SELECT c.employer_name, v.vac_name" in query
    assert "JOIN hh_vacancies as v ON c.company_id" in query


def test_get_avg_salary(db_manager: HeadHunterDataBaseManager) -> None:
    """Проверяет получение средней зарплаты по вакансиям у каждой компании"""
    fake_result = [("Company A", 100000, "urlA"), ("Company B", 150000, "urlB")]

    with patch.object(HeadHunterDataBaseManager, "_execute_query", return_value=fake_result) as mock_execute:
        result = db_manager.get_avg_salary()

    assert result == fake_result
    mock_execute.assert_called_once()
    query = mock_execute.call_args[0][0]
    assert "SELECT c.employer_name, AVG(v.average_salary)" in query
    assert "LEFT JOIN hh_vacancies AS v" in query


def test_get_vacancies_with_higher_salary(db_manager: HeadHunterDataBaseManager) -> None:
    """Проверяет получение списка вакансий с зарплатой выше средней"""
    fake_result = [("Company A", "Vac 1", 100000, 130000, "Казань", "url1"),
                   ("Company B", "Vac 2", 150000, 180000, "Москва", "url2")]

    with patch.object(HeadHunterDataBaseManager, "_execute_query", return_value=fake_result) as mock_execute:
        result = db_manager.get_vacancies_with_higher_salary()

    assert result == fake_result
    mock_execute.assert_called_once()
    query = mock_execute.call_args[0][0]
    assert "SELECT c.employer_name, v.vac_name, v.salary_from" in query
    assert "JOIN (SELECT AVG(average_salary) AS avg_salary" in query


def test_get_vacancies_with_keyword(db_manager: HeadHunterDataBaseManager) -> None:
    """Проверяет получение списка вакансий по ключевому слову в названии"""
    fake_result = [("Company A", "Vac 1", 100000, 130000, "Казань", "url1"),
                   ("Company B", "Vac 2", 150000, 180000, "Москва", "url2")]

    with patch.object(HeadHunterDataBaseManager, "_execute_query", return_value=fake_result) as mock_execute:
        result = db_manager.get_vacancies_with_keyword("Vac")

    assert result == fake_result
    mock_execute.assert_called_once()
    query = mock_execute.call_args[0][0]
    assert "SELECT c.employer_name, v.vac_name, v.salary_from" in query
    assert "WHERE v.vac_name ILIKE %s" in query
