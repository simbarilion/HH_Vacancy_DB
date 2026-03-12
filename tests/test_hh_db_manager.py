from unittest.mock import MagicMock, patch

from src.database.hh_db_manager import HeadHunterDataBaseManager


def test_close_connection(db_manager):
    """Проверяет закрытие соединения с базой данных"""
    mock_conn = MagicMock()
    db_manager._conn = mock_conn
    db_manager.logger = MagicMock()

    db_manager.close_connection()
    db_manager.logger.info.assert_called_once_with("Соединение с базой данных закрыто")


def test_get_companies_and_vacancies_count(db_manager):
    """Проверяет получение списка компаний и количества вакансий"""
    fake_result = [("Company A", 5, "urlA"), ("Company B", 0, "urlB")]

    with patch.object(HeadHunterDataBaseManager, "_execute_query", return_value=fake_result) as mock_execute:
        result = db_manager.get_companies_and_vacancies_count()

    assert result == fake_result
    mock_execute.assert_called_once()
    query = mock_execute.call_args[0][0]
    assert "SELECT c.employer_name" in query
    assert "LEFT JOIN hh_vacancies" in query


def test_get_avg_salary(db_manager):
    """Проверяет получение средней зарплаты по вакансиям у каждой компании"""
    fake_result = [("Company A", 100000, "urlA"), ("Company B", 150000, "urlB")]

    with patch.object(HeadHunterDataBaseManager, "_execute_query", return_value=fake_result) as mock_execute:
        result = db_manager.get_avg_salary()

    assert result == fake_result
    mock_execute.assert_called_once()
    query = mock_execute.call_args[0][0]
    assert "SELECT c.employer_name, AVG(v.average_salary)" in query
    assert "LEFT JOIN hh_vacancies AS v" in query


def test_get_vacancies_with_higher_salary(db_manager):
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


def test_get_vacancies_with_keyword(db_manager):
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
