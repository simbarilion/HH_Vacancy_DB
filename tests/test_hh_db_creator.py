from unittest.mock import MagicMock, patch

import psycopg2
import pytest

from src.hh_db_creator import HeadHunterDataBase


def test_enter_success(db):
    mock_conn = MagicMock()
    with patch("psycopg2.connect", return_value=mock_conn):
        with db as data_base:
            assert data_base is db
            psycopg2.connect.assert_called_once()
            assert mock_conn.autocommit is False


def test_enter_fail(db):
    with patch("psycopg2.connect", side_effect=psycopg2.Error()):
        with pytest.raises(psycopg2.Error):
            with db:
                pass


def test_create_database_new(db):
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchone.return_value = None

    with patch("psycopg2.connect", return_value=mock_conn):
        db.create_database()

    mock_cursor.execute.assert_any_call(
        "SELECT 1 FROM pg_database WHERE datname = %s", ("test_hh_db",)
    )
    mock_cursor.execute.assert_any_call("CREATE DATABASE test_hh_db")


def test_create_database_exists(db):
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchone.return_value = (1,)

    with patch("psycopg2.connect", return_value=mock_conn):
        db.create_database()

    mock_cursor.execute.assert_any_call("DROP DATABASE test_hh_db")
    mock_cursor.execute.assert_any_call("CREATE DATABASE test_hh_db")


def test_create_database_error(db):
    with patch("psycopg2.connect", side_effect=psycopg2.Error()):
        with pytest.raises(psycopg2.Error):
            db.create_database()


@patch.object(HeadHunterDataBase, "_execute")
def test_create_table_hh_companies(mock_execute):
    db = HeadHunterDataBase("test_hh_db")
    db.logger.info = MagicMock()

    db.create_table_hh_companies()

    mock_execute.assert_called_once()
    sql = mock_execute.call_args[0][0]
    assert "CREATE TABLE hh_companies" in sql
    db.logger.info.assert_called_once_with("Tаблица hh_companies успешно создана")


@patch.object(HeadHunterDataBase, "_execute")
def test_create_table_hh_vacancies(mock_execute):
    db = HeadHunterDataBase("test_hh_db")
    db.logger.info = MagicMock()

    db.create_table_hh_vacancies()

    mock_execute.assert_called_once()
    sql = mock_execute.call_args[0][0]
    assert "CREATE TABLE hh_vacancies" in sql
    db.logger.info.assert_called_once_with("Tаблица hh_vacancies успешно создана")


@patch.object(HeadHunterDataBase, "_execute")
def test_add_avg_salary_to_hh_vacancies(mock_execute):
    db = HeadHunterDataBase("test_hh_db")
    db.logger.info = MagicMock()

    db.add_avg_salary_to_hh_vacancies()

    assert mock_execute.call_count == 2
    sql = mock_execute.call_args[0][0]
    assert "UPDATE hh_vacancies" in sql
    db.logger.info.assert_called_once_with("В таблицу hh_vacancies добавлен атрибут average_salary")


def test_save_data_to_table_hh_companies(db):
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
    mock_cursor.fetchone.side_effect = [(1,), None]
    db._conn = mock_conn
    db.logger.info = MagicMock()

    employers = [
        {"employer_id": "1", "name": "Company A", "url": "http://a.com"},
        {"employer_id": "2", "name": "Company B", "url": "http://b.com"},
    ]

    db.save_data_to_table_hh_companies(employers)

    assert mock_cursor.execute.call_count == 2
    mock_conn.commit.assert_called_once()
    db.logger.info.assert_called_once_with("В таблицу hh_companies добавлено 1 компаний")


def test_save_data_to_table_hh_companies_error(db):
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
    mock_cursor.fetchone.side_effect = psycopg2.Error()
    db._conn = mock_conn
    db.logger.error = MagicMock()

    employers = [
        {"employer_id": "1", "name": "Company A", "url": "http://a.com"},
        {"employer_id": "2", "name": "Company B", "url": "http://b.com"},
    ]

    with pytest.raises(psycopg2.Error):
        db.save_data_to_table_hh_companies(employers)

    mock_conn.rollback.assert_called_once()
    db.logger.error.assert_called_once()


def test_save_data_to_table_hh_vacancies(db, employers_vacancies):
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
    mock_cursor.fetchone.side_effect = [(1,), (10,), None]
    db._conn = mock_conn
    db.logger.info = MagicMock()

    db.save_data_to_table_hh_vacancies(employers_vacancies)

    assert mock_cursor.execute.call_count == 3
    mock_conn.commit.assert_called_once()
    db.logger.info.assert_called_once_with("В таблицу hh_vacancies добавлено 1 вакансий")


def test_save_data_to_table_hh_vacancies_error(db, employers_vacancies):
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
    mock_cursor.fetchone.side_effect = psycopg2.Error()
    db._conn = mock_conn
    db.logger.error = MagicMock()

    with pytest.raises(psycopg2.Error):
        db.save_data_to_table_hh_vacancies(employers_vacancies)

    mock_conn.rollback.assert_called_once()
    db.logger.error.assert_called_once()
